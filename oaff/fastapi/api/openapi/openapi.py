from typing import Callable

from fastapi.applications import FastAPI
from fastapi.requests import Request

from oaff.fastapi.api.openapi.vnd_response import VndResponse


def get_openapi_handler(app: FastAPI) -> Callable[[Request], VndResponse]:
    def handler(_: Request):
        # OpenAPI spec must be modified because FastAPI doesn't support
        # encoding style: https://github.com/tiangolo/fastapi/issues/283
        definition = app.openapi().copy()
        for path in definition["paths"].values():
            if "get" in path:
                for parameter in path["get"]["parameters"]:
                    if "style" not in parameter:
                        parameter["style"] = "form"

        # This API actually expects BBOX as a string but OGC spec requires
        # array with form-style, which is not possible in FastAPI.
        # Continue to accept string but pretend it's form-style array.
        # End result is the same. String BBOX param is validated by regex.
        collection_items_bbox_param = list(
            filter(
                lambda parameter: parameter["name"] == "bbox",
                definition["paths"]["/collections/{collection_id}/items"]["get"][
                    "parameters"
                ],
            )
        )[0]
        collection_items_bbox_param["schema"] = {
            "type": "array",
            "minItems": 4,
            "maxItems": 6,
            "items": {
                "type": "number",
            },
        }

        return VndResponse(definition)

    return handler
