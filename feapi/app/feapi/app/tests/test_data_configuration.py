import os
from asyncio import get_event_loop
from typing import Type
from unittest.mock import patch
from uuid import uuid4

from feapi.app.configuration.data import get_layer, get_layers
from feapi.app.configuration.frontend_configuration import FrontendConfiguration
from feapi.app.data.retrieval.feature_provider import FeatureProvider
from feapi.app.data.retrieval.feature_set_provider import FeatureSetProvider
from feapi.app.data.sources.common.data_source import DataSource
from feapi.app.data.sources.common.layer import Layer
from feapi.app.gateway import cleanup, configure
from feapi.app.responses.response_format import ResponseFormat
from feapi.app.responses.response_type import ResponseType
from feapi.app.settings import ENV_VAR_PREFIX


def setup_module():
    os.environ[f"{ENV_VAR_PREFIX}DATA_SOURCE_TYPES"] = "postgresql"


def teardown_module():
    del os.environ[f"{ENV_VAR_PREFIX}DATA_SOURCE_TYPES"]


def teardown_function():
    get_event_loop().run_until_complete(cleanup())


@patch("feapi.app.data.sources.postgresql.postgresql_manager.PostgresqlManager")
def test_empty(PostgresqlManagerMock):
    PostgresqlManagerMock.return_value.get_data_sources.return_value = []
    get_event_loop().run_until_complete(
        configure(
            FrontendConfiguration(
                asset_url_base="",
                api_url_base="",
                endpoint_format_switcher=_endpoint_format_switcher,
                next_page_link_generator=_next_page_link_generator,
                prev_page_link_generator=_prev_page_link_generator,
                openapi_path_html="/html",
                openapi_path_json="/json",
            )
        )
    )
    assert len(get_layers()) == 0


@patch("feapi.app.data.sources.postgresql.postgresql_manager.PostgresqlManager")
def test_with_layers(PostgresqlManagerMock):

    PostgresqlManagerMock.return_value.get_data_sources.return_value = [
        _TestDataSource1(str(uuid4())),
        _TestDataSource2(str(uuid4())),
    ]
    get_event_loop().run_until_complete(
        configure(
            FrontendConfiguration(
                asset_url_base="",
                api_url_base="",
                endpoint_format_switcher=_endpoint_format_switcher,
                next_page_link_generator=_next_page_link_generator,
                prev_page_link_generator=_prev_page_link_generator,
                openapi_path_html="/html",
                openapi_path_json="/json",
            )
        )
    )
    assert len(get_layers()) == 3
    for lyrnum in [1, 2, 3]:
        assert get_layer(f"layer{lyrnum}").title == f"title{lyrnum}"
        assert get_layer(f"layer{lyrnum}").description == f"description{lyrnum}"
        assert len(get_layer(f"layer{lyrnum}").bboxes) == 1
        assert get_layer(f"layer{lyrnum}").bboxes[0] == [
            int(f"{lyrnum}1"),
            int(f"{lyrnum}2"),
            int(f"{lyrnum}3"),
            int(f"{lyrnum}4"),
        ]


def _endpoint_format_switcher(
    url: str, format: ResponseFormat, type: ResponseType
) -> str:
    return url


def _next_page_link_generator(url: str) -> str:
    return url


def _prev_page_link_generator(url: str) -> str:
    return url


class _TestDataSource1(DataSource):
    async def get_layers(self):
        return [
            Layer(
                id="layer1",
                title="title1",
                description="description1",
                bboxes=[[11, 12, 13, 14]],
                intervals=[[None, None]],
                data_source_id=self.id,
                geometry_crs_auth_name="EPSG",
                geometry_crs_auth_code=3857,
                temporal_attributes=[],
            ),
            Layer(
                id="layer2",
                title="title2",
                description="description2",
                bboxes=[[21, 22, 23, 24]],
                intervals=[[None, None]],
                data_source_id=self.id,
                geometry_crs_auth_name="EPSG",
                geometry_crs_auth_code=4326,
                temporal_attributes=[],
            ),
        ]

    async def disconnect(self):
        pass

    async def get_feature_set_provider(self) -> Type[FeatureSetProvider]:
        pass

    async def get_feature_provider(self) -> Type[FeatureProvider]:
        pass

    async def initialize(self):
        pass


class _TestDataSource2(DataSource):
    async def get_layers(self):
        return [
            Layer(
                id="layer3",
                title="title3",
                description="description3",
                bboxes=[[31, 32, 33, 34]],
                intervals=[[None, None]],
                data_source_id=self.id,
                geometry_crs_auth_name="EPSG",
                geometry_crs_auth_code=3857,
                temporal_attributes=[],
            )
        ]

    async def disconnect(self):
        pass

    async def get_feature_set_provider(self) -> Type[FeatureSetProvider]:
        pass

    async def get_feature_provider(self) -> Type[FeatureProvider]:
        pass

    async def initialize(self):
        pass
