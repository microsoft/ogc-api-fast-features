from logging import getLogger
from typing import Final, Type
from urllib.parse import quote

from feapi.app.configuration.data import get_data_source, get_layer
from feapi.app.configuration.frontend_interface import get_frontend_configuration
from feapi.app.request_handlers.common.request_handler import RequestHandler
from feapi.app.requests.feature import Feature as FeatureRequestType
from feapi.app.responses.models.link import Link, LinkRel
from feapi.app.responses.response import Response
from feapi.app.responses.response_format import ResponseFormat
from feapi.app.responses.response_type import ResponseType

LOGGER: Final = getLogger(__file__)


class Feature(RequestHandler):
    @classmethod
    def type_name(cls) -> str:
        return FeatureRequestType.__name__

    async def handle(self, request: FeatureRequestType) -> Type[Response]:
        layer = get_layer(request.collection_id)
        if layer is None:
            return self.feature_404(request.collection_id, request.feature_id)
        data_source = get_data_source(layer.data_source_id)
        feature_provider = await data_source.get_feature_provider(
            layer,
        )
        format_links = self.get_links_for_self(request)
        if request.format == ResponseFormat.json:
            response = await feature_provider.as_geojson(
                request.feature_id,
                format_links
                + [
                    Link(
                        href="".join(
                            [
                                request.root,
                                f"{get_frontend_configuration().api_url_base}/",
                                f"collections/{quote(request.collection_id)}",
                                f"?format={format.name}",
                            ]
                        ),
                        rel=LinkRel.COLLECTION,
                        type=format[ResponseType.METADATA],
                        title=layer.title,
                    )
                    for format in ResponseFormat
                ],
            )
            return (
                self.raw_to_response(
                    response,
                    request,
                )
                if response is not None
                else self.feature_404(request.collection_id, request.feature_id)
            )
        elif request.format == ResponseFormat.html:
            response = await feature_provider.as_html_compatible(
                request.feature_id,
                format_links,
            )
            return (
                self.object_to_response(
                    response,
                    request,
                )
                if response is not None
                else self.feature_404(request.collection_id, request.feature_id)
            )
