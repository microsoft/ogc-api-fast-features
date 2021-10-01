from abc import ABC, abstractmethod
from typing import List, Type

from oaff.app.data.sources.common.data_source import DataSource


class DataSourceManager(ABC):
    @abstractmethod
    def get_data_sources(self) -> List[Type[DataSource]]:
        pass
