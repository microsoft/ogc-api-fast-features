from abc import ABC, abstractmethod
from http import HTTPStatus
from json import dumps
from typing import Any, Final, List, Type

from oaff.app.configuration.frontend_interface import get_frontend_configuration
from oaff.app.i18n.translations import gettext_for_locale
from oaff.app.requests.common.request_type import RequestType
from oaff.app.responses.data_response import DataResponse
from oaff.app.responses.error_response import ErrorResponse
from oaff.app.responses.models.link import Link, LinkRel
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat
from oaff.app.responses.templates.templates import get_rendered_html


class RequestHandler(ABC):
    @abstractmethod
    async def handle(self, request: Type[RequestType]) -> Type[Response]:
        pass

    def get_links_for_self(
        self,
        request: Type[RequestType],
    ) -> List[Link]:
        url_modifier = get_frontend_configuration().endpoint_format_switcher
        return [
            Link(
                href=url_modifier(request.url, response_format),
                rel=LinkRel.SELF
                if request.format == response_format
                else LinkRel.ALTERNATE,
                type=response_format[request.type],
                # variable substitution explained
                # https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module/     # noqa: E501
                title=gettext_for_locale(request.locale)("This document")
                if request.format == response_format
                else gettext_for_locale(request.locale)(
                    "This document (%s)" % response_format[request.type]
                ),
            )
            for response_format in ResponseFormat
        ]

    def raw_to_response(
        self,
        response: Any,
        request: Type[RequestType],
    ) -> DataResponse:
        return DataResponse(
            mime_type=request.format[request.type],
            encoded_response=response,
        )

    def object_to_response(
        self,
        object: Any,
        request: Type[RequestType],
    ) -> DataResponse:
        format_to_response: Final = {
            ResponseFormat.json.name: self.object_to_json_response,
            ResponseFormat.html.name: self.object_to_html_response,
        }
        return format_to_response[request.format.name](object, request)

    def object_to_json_response(
        self,
        object: Any,
        request: Type[RequestType],
    ) -> DataResponse:
        jsonable_method = getattr(object, "jsonable", None)
        if callable(jsonable_method):
            object = jsonable_method()
        return DataResponse(
            mime_type=ResponseFormat.json[request.type],
            encoded_response=dumps(object),
        )

    def object_to_html_response(
        self,
        object: Any,
        request: Type[RequestType],
    ) -> DataResponse:
        return DataResponse(
            mime_type=ResponseFormat.html[request.type],
            encoded_response=get_rendered_html(
                f"{request.__class__.__name__}", object, request.locale
            ),
        )

    def collection_404(self, collection_id: str) -> ErrorResponse:
        return self._get_404(f"Collection {collection_id} not found")

    def feature_404(self, collection_id: str, feature_id: str) -> ErrorResponse:
        return self._get_404(f"Feature {collection_id}/{feature_id} not found")

    def _get_404(self, detail: str = "") -> ErrorResponse:
        return ErrorResponse(status_code=HTTPStatus.NOT_FOUND, detail=detail)
