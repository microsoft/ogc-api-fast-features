from logging import getLogger
from typing import Final, Type

from oaff.app.configuration.data import get_layers
from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.collections_list import CollectionsList
from oaff.app.responses.models.collection import CollectionHtml, CollectionJson
from oaff.app.responses.models.collections import CollectionsHtml, CollectionsJson
from oaff.app.responses.response import Response
from oaff.app.responses.response_format import ResponseFormat

LOGGER: Final = getLogger(__file__)


class CollectionsList(RequestHandler):  # type: ignore[no-redef]
    @classmethod
    def type_name(cls) -> str:
        return CollectionsList.__name__

    async def handle(self, request: CollectionsList) -> Type[Response]:
        format_links = self.get_links_for_self(request)
        if request.format == ResponseFormat.html:
            collections = [
                CollectionHtml.from_layer(layer, request) for layer in get_layers()
            ]
            return self.object_to_html_response(
                CollectionsHtml(collections=collections, format_links=format_links),
                request,
            )
        elif request.format == ResponseFormat.json:
            collections = [
                CollectionJson.from_layer(layer, request) for layer in get_layers()
            ]
            return self.object_to_json_response(
                CollectionsJson(collections=collections, links=format_links),
                request,
            )
