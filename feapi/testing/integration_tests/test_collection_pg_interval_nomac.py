import os
from datetime import datetime
from typing import Any, Dict, Final

from pytz import timezone

from feapi.app.util import datetime_as_rfc3339
from feapi.testing.integration_tests.common import get_collection_id_for, reconfigure
from feapi.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_1_date_1_instant_with,
    insert_table_pnt_4326_1_date_with,
    insert_table_pnt_4326_1_instant_local_with,
    insert_table_pnt_4326_1_instant_utc_with,
    insert_table_pnt_4326_2_dates_with,
    insert_table_pnt_4326_2_instants_local_with,
    insert_table_pnt_4326_2_instants_mixed_with,
    insert_table_pnt_4326_2_instants_utc_with,
    table_pnt_4326_1_date,
    table_pnt_4326_1_date_1_instant,
    table_pnt_4326_1_instant_local,
    table_pnt_4326_1_instant_utc,
    table_pnt_4326_2_dates,
    table_pnt_4326_2_instants_local,
    table_pnt_4326_2_instants_mixed,
    table_pnt_4326_2_instants_utc,
    truncate_common,
    update_db_timezone,
)

SOURCE_NAME: Final = "stac"
COLLECTIONS_URL: Final = "/collections?format=json"
COLLECTION_URL: Final = "/collections/{collection_id}?format=json"
ALTERNATE_TZ: Final = "Australia/Darwin"


def setup_module():
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)
    update_db_timezone(SOURCE_NAME, None)


def test_interval_null_instant(test_app):
    insert_table_pnt_4326_1_instant_utc_with(SOURCE_NAME, None)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_instant_utc)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [None, None]


def test_interval_null_instants(test_app):
    insert_table_pnt_4326_2_instants_utc_with(SOURCE_NAME, None, None)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_instants_utc)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [None, None]


def test_interval_valid_instant_utc(test_app):
    instant_utc = timezone("UTC").localize(datetime(2020, 6, 30, 11, 15, 30))
    insert_table_pnt_4326_1_instant_utc_with(SOURCE_NAME, instant_utc)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_instant_utc)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    instant_str = datetime_as_rfc3339(instant_utc)
    assert collection["extent"]["temporal"]["interval"][0] == [
        instant_str,
        instant_str,
    ]


def test_interval_valid_instant_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    instant = timezone(ALTERNATE_TZ).localize(datetime(2020, 6, 30, 11, 15, 30, 0))
    instant_utc = instant.astimezone(timezone("UTC"))
    insert_table_pnt_4326_1_instant_local_with(SOURCE_NAME, instant)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_instant_local)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    instant_utc_str = datetime_as_rfc3339(instant_utc)
    assert collection["extent"]["temporal"]["interval"][0] == [
        instant_utc_str,
        instant_utc_str,
    ]


def test_interval_valid_instants_utc(test_app):
    start_instant_utc = timezone("UTC").localize(datetime(2020, 6, 30, 11, 15, 30, 0))
    mid_instant_utc = timezone("UTC").localize(datetime(2020, 11, 21, 16, 3, 0))
    end_instant_utc = timezone("UTC").localize(datetime(2021, 9, 3, 14, 45, 30, 0))
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, start_instant_utc, mid_instant_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, mid_instant_utc, end_instant_utc
    )
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_instants_utc)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(start_instant_utc),
        datetime_as_rfc3339(end_instant_utc),
    ]


def test_interval_valid_instants_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    start_instant = timezone(ALTERNATE_TZ).localize(datetime(2020, 6, 30, 11, 15, 30, 0))
    start_instant_utc = start_instant.astimezone(timezone("UTC"))
    end_instant = timezone(ALTERNATE_TZ).localize(datetime(2021, 9, 3, 14, 45, 30, 0))
    end_instant_utc = end_instant.astimezone(timezone("UTC"))
    insert_table_pnt_4326_2_instants_local_with(SOURCE_NAME, start_instant, end_instant)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_instants_local)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(start_instant_utc),
        datetime_as_rfc3339(end_instant_utc),
    ]


def test_interval_valid_instants_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    start_instant_utc = timezone("UTC").localize(datetime(2020, 6, 30, 11, 15, 30, 0))
    end_instant = timezone(ALTERNATE_TZ).localize(datetime(2021, 9, 3, 14, 45, 30, 0))
    end_instant_utc = end_instant.astimezone(timezone("UTC"))
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, start_instant_utc, end_instant
    )
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_instants_mixed)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(start_instant_utc),
        datetime_as_rfc3339(end_instant_utc),
    ]


def test_interval_null_date(test_app):
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, None)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_date)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [None, None]


def test_interval_null_dates(test_app):
    insert_table_pnt_4326_2_dates_with(SOURCE_NAME, None, None)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_dates)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [None, None]


def test_interval_valid_date(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    date = timezone(ALTERNATE_TZ).localize(datetime(2020, 6, 30))
    date_utc = date.astimezone(timezone("UTC"))
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_date)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    date_utc_str = datetime_as_rfc3339(date_utc)
    assert collection["extent"]["temporal"]["interval"][0] == [
        date_utc_str,
        date_utc_str,
    ]


def test_interval_valid_dates(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    start_date = timezone(ALTERNATE_TZ).localize(datetime(2020, 6, 30))
    start_date_utc = start_date.astimezone(timezone("UTC"))
    end_date = timezone(ALTERNATE_TZ).localize(datetime(2021, 9, 3))
    end_date_utc = end_date.astimezone(timezone("UTC"))
    insert_table_pnt_4326_2_dates_with(SOURCE_NAME, start_date, end_date)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_2_dates)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(start_date_utc),
        datetime_as_rfc3339(end_date_utc),
    ]


def test_interval_mix_instant_date(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    start_date_utc = timezone("UTC").localize(datetime(2020, 6, 30, 11, 15, 30, 0))
    end_date = timezone(ALTERNATE_TZ).localize(datetime(2021, 9, 3))
    end_date_utc = end_date.astimezone(timezone("UTC"))
    insert_table_pnt_4326_1_date_1_instant_with(SOURCE_NAME, start_date_utc, end_date)
    reconfigure(test_app)
    collection = _get_collection_by_title(test_app, table_pnt_4326_1_date_1_instant)
    assert len(collection["extent"]["temporal"]["interval"]) == 1
    assert collection["extent"]["temporal"]["interval"][0] == [
        datetime_as_rfc3339(start_date_utc),
        datetime_as_rfc3339(end_date_utc),
    ]


def _get_collection_by_title(test_app, collection_title: str) -> Dict[str, Any]:
    collection_id = get_collection_id_for(test_app, collection_title)
    return test_app.get(COLLECTION_URL.format(collection_id=collection_id)).json()
