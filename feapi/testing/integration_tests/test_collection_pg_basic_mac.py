import json
import os
from typing import Final
from uuid import uuid4

from bs4 import BeautifulSoup

from feapi.app.data.sources.postgresql.stac_hybrid.settings import FEAPI_SCHEMA_NAME
from feapi.testing.data.load.db import update_db
from feapi.testing.integration_tests.common import reconfigure
from feapi.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_mply_4326_basic,
    table_mply_4326,
    truncate_common,
)

BASE_URL: Final = "/collections/{0}?format="
JSON_URL: Final = f"{BASE_URL}json"
HTML_URL: Final = f"{BASE_URL}html"
SOURCE_NAME: Final = "stac"


collection_id: Final = str(uuid4())
license_text: Final = str(uuid4())
full_extent: Final = {
    "spatial": {"bbox": [[-76.711405, 39.197233, -76.529674, 39.372]]},
    "temporal": {"interval": [[None, None]]},
}
spatial_extent: Final = {"spatial": full_extent["spatial"]}
temporal_extent: Final = {"temporal": full_extent["temporal"]}
full_extent_json: Final = json.dumps(full_extent)
spatial_extent_json: Final = json.dumps(spatial_extent)
temporal_extent_json: Final = json.dumps(temporal_extent)
keywords: Final = [str(uuid4()), str(uuid4())]
keywords_sql: Final = '{"' + '", "'.join(keywords) + '"}'
providers: Final = [
    {
        "url": str(uuid4()),
        "name": str(uuid4()),
        "roles": [str(uuid4()), str(uuid4())],
    },
    {
        "url": str(uuid4()),
        "name": str(uuid4()),
        "roles": None,
    },
]
providers_json: Final = json.dumps(providers)


def setup_module():
    drop_common(SOURCE_NAME)
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "1"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def setup_function():
    insert_table_mply_4326_basic(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)
    update_db(f'TRUNCATE TABLE "{FEAPI_SCHEMA_NAME}".collections', SOURCE_NAME)


def test_configured_license_json(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, license,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{license_text}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert test_app.get(JSON_URL.format(collection_id)).json()["license"] == license_text


def test_configured_license_html(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, license,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{license_text}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert (
        BeautifulSoup(
            str(test_app.get(HTML_URL.format(collection_id)).content), "html.parser"
        ).find("div", attrs={"class": "license-container"})
        is not None
    )


def test_configured_keywords_json(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, keywords,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{keywords_sql}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert test_app.get(JSON_URL.format(collection_id)).json()["keywords"] == keywords


def test_configured_keywords_html(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, keywords,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{keywords_sql}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert (
        BeautifulSoup(
            str(test_app.get(HTML_URL.format(collection_id)).content), "html.parser"
        ).find("div", attrs={"class": "keywords-container"})
        is not None
    )


def test_configured_providers_json(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, providers,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{providers_json}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert test_app.get(JSON_URL.format(collection_id)).json()["providers"] == providers


def test_configured_providers_html(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, providers,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{providers_json}'
          , '{full_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert (
        BeautifulSoup(
            str(test_app.get(HTML_URL.format(collection_id)).content), "html.parser"
        ).find("div", attrs={"class": "providers-container"})
        is not None
    )


def test_spatial_extent_override(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, providers,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{providers_json}'
          , '{spatial_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert (
        test_app.get(JSON_URL.format(collection_id)).json()["extent"]["spatial"]
        == spatial_extent["spatial"]
    )
    assert test_app.get(JSON_URL.format(collection_id)).json()["extent"]["temporal"][
        "interval"
    ] == [[None, None]]


def test_temporal_extent_override(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, providers,
            extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{providers_json}'
          , '{temporal_extent_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert test_app.get(JSON_URL.format(collection_id)).json()["extent"]["spatial"][
        "bbox"
    ] == [[0, 0, 1, 1]]
    assert (
        test_app.get(JSON_URL.format(collection_id)).json()["extent"]["temporal"]
        == temporal_extent["temporal"]
    )


def test_extent_no_override(test_app):
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, providers,
            schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{providers_json}'
          , 'public'
          , '{table_mply_4326}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    assert test_app.get(JSON_URL.format(collection_id)).json()["extent"]["spatial"][
        "bbox"
    ] == [[0, 0, 1, 1]]
    assert test_app.get(JSON_URL.format(collection_id)).json()["extent"]["temporal"][
        "interval"
    ] == [[None, None]]
