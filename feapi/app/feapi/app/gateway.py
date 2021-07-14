from typing import Dict, Type

from feapi.app.configuration.data import cleanup as cleanup_config, discover
from feapi.app.configuration.frontend_configuration import FrontendConfiguration
from feapi.app.configuration.frontend_interface import set_frontend_configuration
from feapi.app.request_handlers.collection import Collection as CollectionRequestHandler
from feapi.app.request_handlers.collection_items import (
    CollectionsItems as CollectionsItemsRequestHandler,
)
from feapi.app.request_handlers.collections_list import (
    CollectionsList as CollectionsListRequestHandler,
)
from feapi.app.request_handlers.common.request_handler import RequestHandler
from feapi.app.request_handlers.conformance import (
    Conformance as ConformanceRequestHandler,
)
from feapi.app.request_handlers.feature import Feature as FeatureRequestHandler
from feapi.app.request_handlers.landing_page import (
    LandingPage as LandingPageRequestHandler,
)
from feapi.app.requests.common.request_type import RequestType
from feapi.app.responses.response import Response

handlers: Dict[str, RequestHandler] = {
    LandingPageRequestHandler.type_name(): LandingPageRequestHandler(),
    CollectionsListRequestHandler.type_name(): CollectionsListRequestHandler(),
    CollectionRequestHandler.type_name(): CollectionRequestHandler(),
    CollectionsItemsRequestHandler.type_name(): CollectionsItemsRequestHandler(),
    FeatureRequestHandler.type_name(): FeatureRequestHandler(),
    ConformanceRequestHandler.type_name(): ConformanceRequestHandler(),
}


async def handle(request: Type[RequestType]) -> Response:
    return await handlers[request.__class__.__name__].handle(request)


async def configure(frontend_configuration: FrontendConfiguration) -> None:
    set_frontend_configuration(frontend_configuration)
    await discover()


async def cleanup() -> None:
    await cleanup_config()
