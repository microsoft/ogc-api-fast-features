import os
from json import loads
from typing import Final
from uuid import uuid4

import pytest

from oaff.app.data.sources.postgresql.stac_hybrid.settings import OAFF_SCHEMA_NAME
from oaff.testing.data.load.db import update_db
from oaff.testing.integration_tests.common import reconfigure
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_mply_4326_basic,
    insert_table_pnt_4326_basic,
    table_mply_4326,
    table_pnt_4326,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
JSON_URL: Final = "/collections?format=json"


def setup_module():
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "1"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)
    update_db(f'TRUNCATE TABLE "{OAFF_SCHEMA_NAME}".collections', SOURCE_NAME)


def test_collections_partial_override(test_app):
    insert_table_mply_4326_basic(SOURCE_NAME)
    insert_table_pnt_4326_basic(SOURCE_NAME)
    collection_id = str(uuid4())
    title = str(uuid4())
    description = str(uuid4())
    keywords = '{{"{0}", "{1}"}}'.format(str(uuid4()), str(uuid4()))
    license = str(uuid4())
    providers = f'[{{"url": "{str(uuid4())}", "name": "{str(uuid4())}"}}]'
    extent = '{"spatial": {"bbox": [[-76.711405, 39.197233, -76.529674, 39.372]]}, "temporal": {"interval": [["2017-01-01T00:00:00.000000Z", "2017-12-31T23:59:59.999999Z"]]}}'  # noqa: E501
    collection_schema_name = "public"
    collection_table_name = table_mply_4326
    update_db(
        f"""
        INSERT INTO {OAFF_SCHEMA_NAME}.collections (
            id, title, description, keywords, license,
            providers, extent, schema_name, table_name
        ) VALUES (
            '{collection_id}'
          , '{title}'
          , '{description}'
          , '{keywords}'
          , '{license}'
          , '{providers}'
          , '{extent}'
          , '{collection_schema_name}'
          , '{collection_table_name}'
        )
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    overridden = list(
        filter(
            lambda collection: collection["id"] == collection_id,
            response_content["collections"],
        )
    )[0]
    assert overridden["title"] == title
    assert overridden["description"] == description
    assert overridden["extent"] == loads(extent)
    # ensure non-overridden table's derived properties still provided
    original = list(
        filter(
            lambda collection: collection["title"] == table_pnt_4326,
            response_content["collections"],
        )
    )[0]
    assert original["title"] == table_pnt_4326
    assert original["description"] is None
    original_bbox = original["extent"]["spatial"]["bbox"][0]
    assert original_bbox[0] == pytest.approx(0, 0.000001)
    assert original_bbox[1] == pytest.approx(1, 0.000001)
    assert original_bbox[2] == pytest.approx(0, 0.000001)
    assert original_bbox[3] == pytest.approx(1, 0.000001)
    assert original["extent"]["temporal"]["interval"] == [[None, None]]
