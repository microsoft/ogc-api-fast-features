import os
from datetime import datetime
from typing import Any, Dict, Final, List, Optional
from uuid import uuid4

from pytz import timezone

from feapi.app.data.sources.postgresql.stac_hybrid.settings import FEAPI_SCHEMA_NAME
from feapi.app.util import datetime_as_rfc3339
from feapi.testing.data.load.db import update_db
from feapi.testing.integration_tests.common import reconfigure, tz_datetime, utc_datetime
from feapi.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_1_date_with,
    insert_table_pnt_4326_1_instant_utc_with,
    insert_table_pnt_4326_2_dates_with,
    insert_table_pnt_4326_2_instants_local_with,
    insert_table_pnt_4326_2_instants_mixed_with,
    insert_table_pnt_4326_2_instants_utc_with,
    insert_table_pnt_4326_4_instants_local_with,
    insert_table_pnt_4326_4_instants_mixed_with,
    insert_table_pnt_4326_4_instants_utc_with,
    table_pnt_4326_1_date,
    table_pnt_4326_1_instant_utc,
    table_pnt_4326_2_dates,
    table_pnt_4326_2_instants_local,
    table_pnt_4326_2_instants_mixed,
    table_pnt_4326_2_instants_utc,
    table_pnt_4326_4_instants_local,
    table_pnt_4326_4_instants_mixed,
    table_pnt_4326_4_instants_utc,
    temporal_config,
    truncate_common,
    update_db_timezone,
)

SOURCE_NAME: Final = "stac"
ITEMS_URL: Final = "".join(
    [
        "/collections/{collection_id}/items",
        "?format=json&limit=10000{datetime}{bbox}",
    ]
)
ALTERNATE_TZ: Final = "Australia/Darwin"


def setup_module():
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "1"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)
    update_db(f'TRUNCATE TABLE "{FEAPI_SCHEMA_NAME}".collections', SOURCE_NAME)
    update_db_timezone(SOURCE_NAME, None)


def test_empty_param_null_range(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    insert_table_pnt_4326_2_instants_utc_with(SOURCE_NAME, None, None)
    features = _get_collection_items(test_app, collection_id)
    assert len(features) == 1


def test_empty_param_null_ranges(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(SOURCE_NAME, None, None, None, None)
    features = _get_collection_items(test_app, collection_id)
    assert len(features) == 1


def test_instant_param_null_range(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    insert_table_pnt_4326_2_instants_utc_with(SOURCE_NAME, None, None)
    features = _get_collection_items(
        test_app, collection_id, datetime_as_rfc3339(datetime.utcnow())
    )
    assert len(features) == 0


def test_instant_param_null_ranges(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(SOURCE_NAME, None, None, None, None)
    features = _get_collection_items(
        test_app, collection_id, datetime_as_rfc3339(datetime.utcnow())
    )
    assert len(features) == 0


def test_instant_param_valid_range_utc(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(1990, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(1991, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(utc_datetime(2020, 10, 1)),
    )
    assert len(features) == 1


def test_instant_param_valid_range_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_local)
    reconfigure(test_app)
    range_1_start = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 57)
    range_1_end = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    range_2_start = tz_datetime(ALTERNATE_TZ, 1990, 8, 4, 15, 2, 59)
    range_2_end = tz_datetime(ALTERNATE_TZ, 1991, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_local_with(SOURCE_NAME, range_1_start, range_1_end)
    insert_table_pnt_4326_2_instants_local_with(SOURCE_NAME, range_2_start, range_2_end)
    features = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(
            timezone(ALTERNATE_TZ)
            .localize(datetime(2020, 8, 4, 15, 2, 58))
            .astimezone(timezone("UTC"))
        ),
    )
    assert len(features) == 1


def test_instant_param_valid_range_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_mixed)
    reconfigure(test_app)
    range_1_start_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2020, 8, 4, 15, 2, 57))
        .astimezone(timezone("UTC"))
    )
    range_1_end = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    range_2_start_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(1990, 8, 4, 15, 2, 59))
        .astimezone(timezone("UTC"))
    )
    range_2_end = tz_datetime(ALTERNATE_TZ, 1991, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, range_1_start_utc, range_1_end
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, range_2_start_utc, range_2_end
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(
            timezone(ALTERNATE_TZ)
            .localize(datetime(2020, 8, 4, 15, 2, 58))
            .astimezone(timezone("UTC"))
        ),
    )
    assert len(features) == 1


def test_instant_param_valid_ranges_utc_none(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(
        SOURCE_NAME,
        datetime.utcnow(),
        datetime.utcnow(),
        datetime.utcnow(),
        datetime.utcnow(),
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(utc_datetime(1999, 12, 31, 23, 59, 59)),
    )
    assert len(features) == 0


def test_instant_param_valid_ranges_utc(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    start_1_utc = utc_datetime(2005, 7, 4, 12, 39, 11)
    end_1_utc = utc_datetime(2006, 7, 4, 12, 39, 11)
    start_2_utc = utc_datetime(2007, 7, 4, 12, 39, 11)
    end_2_utc = utc_datetime(2008, 7, 4, 12, 39, 11)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(
        SOURCE_NAME, start_1_utc, end_1_utc, start_2_utc, end_2_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(utc_datetime(2005, 9, 4, 12, 39, 12)),
    )
    assert len(features) == 1


def test_instant_param_valid_ranges_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_4_instants_local)
    start_1 = tz_datetime(ALTERNATE_TZ, 2005, 7, 4, 12, 39, 11)
    end_1 = tz_datetime(ALTERNATE_TZ, 2006, 7, 4, 12, 39, 11)
    start_2 = tz_datetime(ALTERNATE_TZ, 2007, 7, 4, 12, 39, 11)
    end_2 = tz_datetime(ALTERNATE_TZ, 2008, 7, 4, 12, 39, 11)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_local_with(
        SOURCE_NAME, start_1, end_1, start_2, end_2
    )
    features = _get_collection_items(
        test_app, collection_id, datetime_as_rfc3339(start_2.astimezone(timezone("UTC")))
    )
    assert len(features) == 1


def test_instant_param_valid_ranges_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_4_instants_mixed)
    start_1_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2005, 7, 4, 12, 39, 11))
        .astimezone(timezone("UTC"))
    )
    end_1 = tz_datetime(ALTERNATE_TZ, 2006, 7, 4, 12, 39, 11)
    start_2_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2007, 7, 4, 12, 39, 11))
        .astimezone(timezone("UTC"))
    )
    end_2 = tz_datetime(ALTERNATE_TZ, 2008, 7, 4, 12, 39, 11)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_mixed_with(
        SOURCE_NAME, start_1_utc, end_1, start_2_utc, end_2
    )
    features = _get_collection_items(
        test_app, collection_id, datetime_as_rfc3339(start_2_utc)
    )
    assert len(features) == 1


def test_range_start_param_valid_range_utc(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        f"{datetime_as_rfc3339(utc_datetime(2020, 10, 1))}/",
    )
    assert len(features) == 1


def test_range_start_param_valid_range_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_local)
    reconfigure(test_app)
    range_1_start = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    range_1_end = tz_datetime(ALTERNATE_TZ, 2021, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_local_with(SOURCE_NAME, range_1_start, range_1_end)
    features = _get_collection_items(
        test_app,
        collection_id,
        f"{datetime_as_rfc3339(utc_datetime(2020, 10, 1))}/",
    )
    assert len(features) == 1


def test_range_start_param_valid_range_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_mixed)
    reconfigure(test_app)
    range_1_start_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2020, 8, 4, 15, 2, 58))
        .astimezone(timezone("UTC"))
    )
    range_1_end = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, range_1_start_utc, range_1_end
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        f"{datetime_as_rfc3339(range_1_start_utc)}/",
    )
    assert len(features) == 1


def test_range_end_param_valid_range_utc(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        f"/{datetime_as_rfc3339(utc_datetime(2020, 10, 1))}",
    )
    assert len(features) == 1


def test_range_end_param_valid_range_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_local)
    reconfigure(test_app)
    range_1_start = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    range_1_end = tz_datetime(ALTERNATE_TZ, 2021, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_local_with(SOURCE_NAME, range_1_start, range_1_end)
    features = _get_collection_items(
        test_app,
        collection_id,
        f"/{datetime_as_rfc3339(utc_datetime(2020, 10, 1))}",
    )
    assert len(features) == 1


def test_range_end_param_valid_range_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_instants_mixed)
    reconfigure(test_app)
    range_1_start_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2020, 8, 4, 15, 2, 58))
        .astimezone(timezone("UTC"))
    )
    range_1_end = tz_datetime(ALTERNATE_TZ, 2020, 8, 4, 15, 2, 59)
    range_2_start_utc = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2021, 8, 4, 15, 2, 58))
        .astimezone(timezone("UTC"))
    )
    range_2_end = tz_datetime(ALTERNATE_TZ, 2021, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, range_1_start_utc, range_1_end
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME, range_2_start_utc, range_2_end
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        f"/{datetime_as_rfc3339(range_1_end.astimezone(timezone(ALTERNATE_TZ)))}",
    )
    assert len(features) == 1


def test_range_param_valid_range_utc_span_multiple(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(2022, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(2023, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2021, 1, 1)),
                datetime_as_rfc3339(utc_datetime(2023, 1, 1)),
            ]
        ),
    )
    assert len(features) == 2


def test_range_param_valid_range_utc_contained(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(2022, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(2023, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2020, 9, 1)),
                datetime_as_rfc3339(utc_datetime(2020, 10, 1)),
            ]
        ),
    )
    assert len(features) == 1


def test_range_param_valid_range_utc_contains(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(2022, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(2023, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2020, 1, 1)),
                datetime_as_rfc3339(utc_datetime(2024, 1, 1)),
            ]
        ),
    )
    assert len(features) == 2


def test_range_param_valid_range_utc_intersect_start(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(2022, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(2023, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2019, 1, 1)),
                datetime_as_rfc3339(utc_datetime(2020, 9, 1)),
            ]
        ),
    )
    assert len(features) == 1


def test_range_param_valid_range_utc_intersect_end(test_app):
    collection_id = _configure_collection(table_pnt_4326_2_instants_utc)
    reconfigure(test_app)
    range_1_start_utc = utc_datetime(2020, 8, 4, 15, 2, 59)
    range_1_end_utc = utc_datetime(2021, 8, 4, 15, 2, 59)
    range_2_start_utc = utc_datetime(2022, 8, 4, 15, 2, 59)
    range_2_end_utc = utc_datetime(2023, 8, 4, 15, 2, 59)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_1_start_utc, range_1_end_utc
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME, range_2_start_utc, range_2_end_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2023, 1, 1)),
                datetime_as_rfc3339(utc_datetime(2025, 9, 1)),
            ]
        ),
    )
    assert len(features) == 1


def test_range_param_valid_ranges_utc_span(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    start_1_utc = utc_datetime(2005, 7, 4, 12, 39, 11)
    end_1_utc = utc_datetime(2006, 7, 4, 12, 39, 11)
    start_2_utc = utc_datetime(2007, 7, 4, 12, 39, 11)
    end_2_utc = utc_datetime(2008, 7, 4, 12, 39, 11)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(
        SOURCE_NAME, start_1_utc, end_1_utc, start_2_utc, end_2_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2005, 9, 4, 12, 39, 12)),
                datetime_as_rfc3339(utc_datetime(2007, 9, 4, 12, 39, 12)),
            ]
        ),
    )
    assert len(features) == 1


def test_range_param_valid_ranges_utc_none(test_app):
    collection_id = _configure_collection(table_pnt_4326_4_instants_utc)
    start_1_utc = utc_datetime(2005, 7, 4, 12, 39, 11)
    end_1_utc = utc_datetime(2006, 7, 4, 12, 39, 11)
    start_2_utc = utc_datetime(2007, 7, 4, 12, 39, 11)
    end_2_utc = utc_datetime(2008, 7, 4, 12, 39, 11)
    reconfigure(test_app)
    insert_table_pnt_4326_4_instants_utc_with(
        SOURCE_NAME, start_1_utc, end_1_utc, start_2_utc, end_2_utc
    )
    features = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2007, 1, 1)),
                datetime_as_rfc3339(utc_datetime(2007, 2, 1)),
            ]
        ),
    )
    assert len(features) == 0


def test_range_param_date(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_1_date)
    date_1 = tz_datetime(ALTERNATE_TZ, 2020, 6, 1)
    date_2 = tz_datetime(ALTERNATE_TZ, 2020, 6, 2)
    date_2 = tz_datetime(ALTERNATE_TZ, 2020, 6, 3)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_1)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_2)
    reconfigure(test_app)
    result = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(date_1.astimezone(timezone("UTC"))),
                datetime_as_rfc3339(date_2.astimezone(timezone("UTC"))),
            ]
        ),
    )
    assert len(result) == 2


def test_range_param_dates(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_2_dates)
    date_start_1 = tz_datetime(ALTERNATE_TZ, 2020, 6, 1)
    date_end_1 = tz_datetime(ALTERNATE_TZ, 2020, 6, 2)
    date_start_2 = tz_datetime(ALTERNATE_TZ, 2020, 6, 3)
    date_end_2 = tz_datetime(ALTERNATE_TZ, 2020, 6, 4)
    date_start_3 = tz_datetime(ALTERNATE_TZ, 2020, 6, 5)
    date_end_3 = tz_datetime(ALTERNATE_TZ, 2020, 6, 6)
    insert_table_pnt_4326_2_dates_with(SOURCE_NAME, date_start_1, date_end_1)
    insert_table_pnt_4326_2_dates_with(SOURCE_NAME, date_start_2, date_end_2)
    insert_table_pnt_4326_2_dates_with(SOURCE_NAME, date_start_3, date_end_3)
    reconfigure(test_app)
    result = _get_collection_items(
        test_app,
        collection_id,
        "/".join(
            [
                datetime_as_rfc3339(date_start_1.astimezone(timezone("UTC"))),
                datetime_as_rfc3339(date_end_2.astimezone(timezone("UTC"))),
            ]
        ),
    )
    assert len(result) == 2


def test_instant_param_instant(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    collection_id = _configure_collection(table_pnt_4326_1_instant_utc)
    instant_1_utc = utc_datetime(2010, 1, 1, 23, 42, 12)
    instant_2_utc = utc_datetime(2011, 1, 1, 23, 42, 12)
    insert_table_pnt_4326_1_instant_utc_with(SOURCE_NAME, instant_1_utc)
    insert_table_pnt_4326_1_instant_utc_with(SOURCE_NAME, instant_2_utc)
    reconfigure(test_app)
    result = _get_collection_items(
        test_app,
        collection_id,
        datetime_as_rfc3339(instant_2_utc),
    )
    assert len(result) == 1


def _configure_collection(table_name: str) -> str:
    range_declared_start = utc_datetime(2017, 1, 1)
    range_declared_end = timezone("UTC").localize(
        datetime(2017, 12, 31, 23, 59, 59, 999999)
    )
    collection_id = str(uuid4())
    extent = f'{{"spatial": {{"bbox": [[-76.711405, 39.197233, -76.529674, 39.372]]}}, "temporal": {{"interval": [["{datetime_as_rfc3339(range_declared_start)}", "{datetime_as_rfc3339(range_declared_end)}"]]}}}}'  # noqa: E501
    update_db(
        f"""
        INSERT INTO {FEAPI_SCHEMA_NAME}.collections (
            id, title, description, keywords, license,
            providers, extent, schema_name, table_name,
            temporal
        ) VALUES (
            '{collection_id}'
          , '{str(uuid4())}'
          , '{str(uuid4())}'
          , '{{"{str(uuid4())}"}}'
          , '{str(uuid4())}'
          , '{{"url": "{str(uuid4())}"}}'
          , '{extent}'
          , 'public'
          , '{table_name}'
          , '{temporal_config[table_name]}'
        )
        """,
        SOURCE_NAME,
    )
    return collection_id


def _get_collection_items(
    test_app,
    collection_id: str,
    datetime_param: Optional[str] = None,
    bbox_param: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return test_app.get(
        ITEMS_URL.format(
            collection_id=collection_id,
            datetime=f"&datetime={datetime_param}" if datetime_param is not None else "",
            bbox=f"&bbox={bbox_param}" if bbox_param is not None else "",
        )
    ).json()["features"]
