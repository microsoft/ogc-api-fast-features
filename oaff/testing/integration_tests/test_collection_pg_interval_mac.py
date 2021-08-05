import os
from datetime import datetime
from typing import Final
from uuid import uuid4

from pytz import timezone

from oaff.app.data.sources.postgresql.stac_hybrid.settings import OAFF_SCHEMA_NAME
from oaff.app.util import datetime_as_rfc3339
from oaff.testing.data.load.db import update_db
from oaff.testing.integration_tests.common import reconfigure
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_2_instants_utc_with,
    table_pnt_4326_2_instants_utc,
    temporal_config,
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


def test_interval_range_utc(test_app):
    range_declared_start = timezone("UTC").localize(datetime(2017, 1, 1))
    range_declared_end = timezone("UTC").localize(
        datetime(2017, 12, 31, 23, 59, 59, 999999)
    )
    range_1_start_utc = timezone("UTC").localize(datetime(2020, 8, 4, 15, 2, 59))
    range_1_end_utc = timezone("UTC").localize(datetime(2021, 8, 4, 15, 2, 59))
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    collection_id = str(uuid4())
    extent = f'{{"spatial": {{"bbox": [[-76.711405, 39.197233, -76.529674, 39.372]]}}, "temporal": {{"interval": [["{datetime_as_rfc3339(range_declared_start)}", "{datetime_as_rfc3339(range_declared_end)}"]]}}}}'  # noqa: E501
    collection_schema_name = "public"
    collection_table_name = table_pnt_4326_2_instants_utc

    update_db(
        f"""
        INSERT INTO {OAFF_SCHEMA_NAME}.collections (
            id, title, description, keywords, license,
            providers, extent, schema_name, table_name,
            temporal
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{{"{str(uuid4())}"}}'
          , '{str(uuid4())}'
          , '[{{"url": "{str(uuid4())}", "name": "{str(uuid4())}"}}]'
          , '{extent}'
          , '{collection_schema_name}'
          , '{collection_table_name}'
          , '{temporal_config[collection_table_name]}'
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
    assert len(overridden["extent"]["temporal"]["interval"]) == 1
    assert overridden["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(range_declared_start),
        datetime_as_rfc3339(range_declared_end),
    ]
