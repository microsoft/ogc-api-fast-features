from typing import Any, Dict

from feapi.app.responses.response import Response


class DataResponse(Response):
    mime_type: str
    encoded_response: Any  # could be HTML str, GPKG bytes etc
    additional_headers: Dict[str, str] = dict()
