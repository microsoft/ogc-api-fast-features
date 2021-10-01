from typing import Type

from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.conformance import Conformance as ConformanceRequest
from oaff.app.responses.models.conformance import ConformanceHtml, ConformanceJson
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat


class ConformanceRequestHandler(RequestHandler):
    @classmethod
    def type_name(cls) -> str:
        return ConformanceRequest.__name__

    async def handle(self, request: ConformanceRequest) -> Type[Response]:
        conform_list = [
            "http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        ]

        if request.format == ResponseFormat.html:
            return self.object_to_html_response(
                ConformanceHtml(
                    conformsTo=conform_list,
                    format_links=self.get_links_for_self(request),
                ),
                request,
            )
        elif request.format == ResponseFormat.json:
            return self.object_to_json_response(
                ConformanceJson(
                    conformsTo=conform_list,
                ),
                request,
            )
