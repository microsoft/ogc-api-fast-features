from abc import ABC, abstractmethod
from typing import Callable, List

from oaff.app.responses.models.collection_items_html import CollectionItemsHtml
from oaff.app.responses.models.link import Link


class FeatureSetProvider(ABC):
    """
    Allow different data sources to customise how they return features in a given format.
    One approach is to convert all source data to a common format, and then convert from
    that common format to the target format.
    If the source format and the target format are equivalent, or if a data source has
    specialised functionality to provide data in the target format, it may be
    significantly faster to bypass a common format conversion.
    """

    @abstractmethod
    async def as_geojson(
        self, links: List[Link], page_links_provider: Callable[[int, int], List[Link]]
    ) -> str:
        pass

    @abstractmethod
    async def as_html_compatible(
        self, links: List[Link], page_links_provider: Callable[[int, int], List[Link]]
    ) -> CollectionItemsHtml:
        pass
