from abc import ABC, abstractmethod
from typing import Any, List, Type
from uuid import uuid4

from pygeofilter.ast import Node

from oaff.app.data.retrieval.feature_provider import FeatureProvider
from oaff.app.data.retrieval.feature_set_provider import FeatureSetProvider
from oaff.app.data.retrieval.item_constraints import ItemConstraints
from oaff.app.data.sources.common.layer import Layer


class DataSource(ABC):
    def __init__(self, name: str):
        self._id = str(uuid4())
        self.name = name

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def get_layers(self) -> List[Layer]:
        pass

    @abstractmethod
    async def get_feature_set_provider(
        self,
        layer: Layer,
        constraints: ItemConstraints = None,
        ast: Type[Node] = None,
    ) -> Type[FeatureSetProvider]:
        pass

    @abstractmethod
    async def get_feature_provider(
        self,
        layer: Layer,
    ) -> Type[FeatureProvider]:
        pass

    async def get_crs_identifier(self, layer: Layer) -> Any:
        return f"{layer.geometry_crs_auth_name}:{layer.geometry_crs_auth_code}"

    @abstractmethod
    async def disconnect(self) -> None:
        pass
