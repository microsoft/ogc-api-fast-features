from typing import List, Optional, Type

from pydantic import BaseModel

from feapi.app.configuration.frontend_interface import get_frontend_configuration
from feapi.app.data.sources.common.layer import Layer
from feapi.app.data.sources.common.provider import Provider
from feapi.app.requests.common.request_type import RequestType
from feapi.app.responses.models.extent import Extent
from feapi.app.responses.models.item_type import ItemType
from feapi.app.responses.models.link import Link, LinkRel
from feapi.app.responses.response_format import ResponseFormat
from feapi.app.responses.response_type import ResponseType


class Collection(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    extent: Optional[Extent] = None
    itemType: ItemType
    links: List[Link]
    license: Optional[str] = None
    keywords: Optional[List[str]] = None
    providers: Optional[List[Provider]] = None

    @classmethod
    def from_layer(cls, layer: Layer, request: Type[RequestType]):
        return cls(
            id=layer.id,
            title=layer.title,
            description=layer.description,
            extent=Extent.from_layer(layer) if Extent.has_extent(layer) else None,
            itemType=ItemType.FEATURE,
            links=[
                Link(
                    href="".join(
                        [
                            request.root,
                            f"{get_frontend_configuration().get_items_path(layer.id)}",
                            f"?format={format.name}",
                        ]
                    ),
                    rel=LinkRel.ITEMS,
                    type=format[ResponseType.DATA],
                    title=layer.title,
                )
                for format in ResponseFormat
            ],
            license=layer.license,
            keywords=layer.keywords,
            providers=layer.providers,
        )


class CollectionJson(Collection):
    def add_format_links(self, format_links: List[Link]) -> None:
        self.links.extend(format_links)

    def jsonable(self):
        return {
            **dict(self),
            **{
                "extent": self.extent.jsonable() if self.extent is not None else None,
                "links": [dict(link) for link in self.links],
                "providers": [dict(provider) for provider in self.providers]
                if self.providers
                else None,
            },
        }


class CollectionHtml(Collection):
    format_links: List[Link] = []
