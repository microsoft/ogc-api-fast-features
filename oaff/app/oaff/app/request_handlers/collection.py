from logging import getLogger
from typing import Final, Type

from oaff.app.configuration.data import get_layer
from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.collection import Collection as CollectionRequestType
from oaff.app.responses.models.collection import CollectionHtml, CollectionJson
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat

LOGGER: Final = getLogger(__file__)


class Collection(RequestHandler):
    @classmethod
    def type_name(cls) -> str:
        return CollectionRequestType.__name__

    async def handle(self, request: CollectionRequestType) -> Type[Response]:
        layer = get_layer(request.collection_id)
        if layer is None:
            return self.collection_404(request.collection_id)
        format_links = self.get_links_for_self(request)
        if request.format == ResponseFormat.html:
            collection = CollectionHtml.from_layer(layer, request)
            collection.format_links = format_links
            return self.object_to_html_response(
                collection,
                request,
            )
        elif request.format == ResponseFormat.json:
            collection = CollectionJson.from_layer(layer, request)
            collection.add_format_links(format_links)
            return self.object_to_json_response(
                collection,
                request,
            )
