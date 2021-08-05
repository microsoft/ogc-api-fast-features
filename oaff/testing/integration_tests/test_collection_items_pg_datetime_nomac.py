import os
from datetime import datetime
from typing import Any, Dict, Final, List, Optional

from pytz import timezone

from oaff.app.util import datetime_as_rfc3339
from oaff.testing.integration_tests.common import (
    get_collection_id_for,
    reconfigure,
    tz_datetime,
    utc_datetime,
)
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_1_date_with,
    insert_table_pnt_4326_1_instant_local_with,
    insert_table_pnt_4326_1_instant_utc_with,
    insert_table_pnt_4326_2_instants_local_with,
    insert_table_pnt_4326_2_instants_mixed_with,
    insert_table_pnt_4326_2_instants_utc_with,
    insert_table_pnt_4326_basic,
    table_pnt_4326,
    table_pnt_4326_1_date,
    table_pnt_4326_1_instant_local,
    table_pnt_4326_1_instant_utc,
    table_pnt_4326_2_instants_local,
    table_pnt_4326_2_instants_mixed,
    table_pnt_4326_2_instants_utc,
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
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)
    update_db_timezone(SOURCE_NAME, None)


def test_empty_param_null_instant(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(test_app, table_pnt_4326_1_instant_utc)
    assert len(result) == 1


def test_empty_param_null_instants(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME,
        None,
        None,
    )
    result = _get_collection_items(test_app, table_pnt_4326_2_instants_utc)
    assert len(result) == 1


def test_instant_param_null_instant(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_utc, datetime_as_rfc3339(datetime.utcnow())
    )
    assert len(result) == 0


def test_instant_param_null_instants(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME,
        None,
        None,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_utc, datetime_as_rfc3339(datetime.utcnow())
    )
    assert len(result) == 0


def test_instant_param_valid_instant_utc(test_app):
    reconfigure(test_app)
    instant_utc = utc_datetime(2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_utc,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_utc, datetime_as_rfc3339(instant_utc)
    )
    assert len(result) == 1


def test_instant_param_valid_instant_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    instant = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    instant_utc = instant.astimezone(timezone("UTC"))
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_local, datetime_as_rfc3339(instant_utc)
    )
    assert len(result) == 1


def test_instant_param_valid_instants_utc(test_app):
    reconfigure(test_app)
    instant_1_utc = utc_datetime(2021, 7, 14, 7, 3, 1)
    instant_2_utc = utc_datetime(2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME,
        None,
        None,
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME,
        instant_1_utc,
        instant_2_utc,
    )
    insert_table_pnt_4326_2_instants_utc_with(
        SOURCE_NAME,
        None,
        instant_1_utc,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_2_instants_utc, datetime_as_rfc3339(instant_1_utc)
    )
    assert len(result) == 2


def test_instant_param_valid_instants_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    start_1 = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    end_2 = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_2_instants_local_with(
        SOURCE_NAME,
        start_1,
        None,
    )
    insert_table_pnt_4326_2_instants_local_with(
        SOURCE_NAME,
        None,
        end_2,
    )
    insert_table_pnt_4326_2_instants_local_with(
        SOURCE_NAME,
        None,
        None,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_2_instants_local,
        datetime_as_rfc3339(
            timezone(ALTERNATE_TZ)
            .localize(datetime(2021, 7, 14, 7, 3, 1))
            .astimezone(timezone("UTC"))
        ),
    )
    assert len(result) == 2


def test_instant_param_valid_instants_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    start_1 = (
        timezone(ALTERNATE_TZ)
        .localize(datetime(2021, 7, 14, 7, 3, 1))
        .astimezone(timezone("UTC"))
    )
    end_2 = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_1,
        None,
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        None,
        end_2,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_2_instants_mixed, datetime_as_rfc3339(start_1)
    )
    assert len(result) == 2


def test_range_start_param_null_instant(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        None,
    )
    range_start_utc = datetime_as_rfc3339(
        timezone(ALTERNATE_TZ)
        .localize(datetime(2021, 7, 14, 7, 3, 1))
        .astimezone(timezone("UTC"))
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        f"{range_start_utc}/",
    )
    assert len(result) == 0


def test_range_end_param_null_instant(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        None,
    )
    range_end_utc = datetime_as_rfc3339(
        timezone(ALTERNATE_TZ)
        .localize(datetime(2021, 7, 14, 7, 3, 1))
        .astimezone(timezone("UTC"))
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        f"/{range_end_utc}",
    )
    assert len(result) == 0


def test_range_param_null_instant(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        "/".join(
            [
                datetime_as_rfc3339(
                    timezone(ALTERNATE_TZ)
                    .localize(datetime(2021, 7, 14, 7, 3, 1))
                    .astimezone(timezone("UTC"))
                ),
                datetime_as_rfc3339(
                    timezone(ALTERNATE_TZ)
                    .localize(datetime(2021, 7, 14, 7, 3, 2))
                    .astimezone(timezone("UTC"))
                ),
            ]
        ),
    )
    assert len(result) == 0


def test_range_start_param_valid_instant_utc(test_app):
    reconfigure(test_app)
    instant_1_utc = utc_datetime(2021, 3, 18, 19, 7, 1)
    instant_2_utc = utc_datetime(2021, 3, 18, 19, 7, 0)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_1_utc,
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_2_utc,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_utc, f"{datetime_as_rfc3339(instant_1_utc)}/"
    )
    assert len(result) == 1


def test_range_end_param_valid_instant_utc(test_app):
    reconfigure(test_app)
    instant_1_utc = utc_datetime(2021, 3, 18, 19, 7, 1)
    instant_2_utc = utc_datetime(2021, 3, 18, 19, 7, 2)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_1_utc,
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_2_utc,
    )
    result = _get_collection_items(
        test_app, table_pnt_4326_1_instant_utc, f"/{datetime_as_rfc3339(instant_1_utc)}"
    )
    assert len(result) == 1


def test_range_param_valid_instant_utc(test_app):
    reconfigure(test_app)
    instant_1_utc = utc_datetime(2021, 3, 18, 19, 7, 1)
    instant_2_utc = utc_datetime(2021, 3, 18, 19, 7, 2)
    instant_3_utc = utc_datetime(2021, 3, 18, 19, 7, 3)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_1_utc,
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_2_utc,
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_3_utc,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        "/".join(
            [
                datetime_as_rfc3339(instant_1_utc),
                datetime_as_rfc3339(instant_2_utc),
            ]
        ),
    )
    assert len(result) == 2


def test_range_start_param_valid_instant_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    instant_1 = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    instant_2 = tz_datetime(ALTERNATE_TZ, 2020, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_1,
    )
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_2,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        f'{datetime_as_rfc3339(instant_1.astimezone(timezone("UTC")))}/',
    )
    assert len(result) == 1


def test_range_end_param_valid_instant_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    instant_1 = tz_datetime(ALTERNATE_TZ, 2021, 7, 14, 7, 3, 1)
    instant_2 = tz_datetime(ALTERNATE_TZ, 2020, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_1,
    )
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_2,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        f'/{datetime_as_rfc3339(instant_2.astimezone(timezone("UTC")))}',
    )
    assert len(result) == 1


def test_range_param_valid_instant_local(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    instant_1 = tz_datetime(ALTERNATE_TZ, 2021, 3, 18, 19, 7, 1)
    instant_2 = tz_datetime(ALTERNATE_TZ, 2021, 3, 18, 19, 7, 2)
    instant_3 = tz_datetime(ALTERNATE_TZ, 2021, 3, 18, 19, 7, 3)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_1,
    )
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_2,
    )
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        instant_3,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        "/".join(
            [
                datetime_as_rfc3339(instant_1.astimezone(timezone("UTC"))),
                datetime_as_rfc3339(instant_3.astimezone(timezone("UTC"))),
            ]
        ),
    )
    assert len(result) == 3


def test_range_start_param_null_instants(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        f"{datetime_as_rfc3339(datetime.utcnow())}/",
    )
    assert len(result) == 0


def test_range_end_param_null_instants(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        f"/{datetime_as_rfc3339(datetime.utcnow())}",
    )
    assert len(result) == 0


def test_range_param_null_instants(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_local_with(
        SOURCE_NAME,
        None,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_local,
        "/".join(
            [
                datetime_as_rfc3339(datetime.utcnow()),
                datetime_as_rfc3339(datetime.utcnow()),
            ]
        ),
    )
    assert len(result) == 0


def test_range_start_param_valid_instants_mixed(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    start_1_utc = utc_datetime(2021, 3, 18, 19, 7, 1)
    end_1 = start_1_utc.astimezone(timezone(ALTERNATE_TZ))
    start_2_utc = utc_datetime(2021, 3, 18, 19, 7, 0)
    end_2 = start_1_utc.astimezone(timezone(ALTERNATE_TZ))
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_1_utc,
        end_1,
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_2_utc,
        end_2,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_2_instants_mixed,
        f"{datetime_as_rfc3339(start_1_utc)}/",
    )
    assert len(result) == 2


def test_range_end_param_valid_instants(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    start_1_utc = utc_datetime(2021, 3, 18, 19, 7, 1)
    end_1 = start_1_utc.astimezone(timezone(ALTERNATE_TZ))
    start_2_utc = utc_datetime(2021, 3, 18, 19, 7, 0)
    end_2 = start_1_utc.astimezone(timezone(ALTERNATE_TZ))
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_1_utc,
        end_1,
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_2_utc,
        end_2,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_2_instants_mixed,
        f"/{datetime_as_rfc3339(start_2_utc)}",
    )
    assert len(result) == 1


def test_range_param_valid_instants(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    reconfigure(test_app)
    start_1_utc = utc_datetime(2021, 3, 18, 19, 7, 0)
    end_1 = start_1_utc.astimezone(timezone(ALTERNATE_TZ))
    start_2_utc = utc_datetime(2021, 3, 18, 19, 7, 30)
    end_2 = start_2_utc.astimezone(timezone(ALTERNATE_TZ))
    start_3_utc = utc_datetime(2021, 3, 18, 19, 7, 59)
    end_3 = start_3_utc.astimezone(timezone(ALTERNATE_TZ))
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_1_utc,
        end_1,
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_2_utc,
        end_2,
    )
    insert_table_pnt_4326_2_instants_mixed_with(
        SOURCE_NAME,
        start_3_utc,
        end_3,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_2_instants_mixed,
        f"{datetime_as_rfc3339(start_1_utc)}/{datetime_as_rfc3339(start_3_utc)}",
    )
    assert len(result) == 3


def test_instant_param_date(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    date_1 = tz_datetime(ALTERNATE_TZ, 2020, 6, 30)
    date_2 = tz_datetime(ALTERNATE_TZ, 2020, 7, 30)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_1)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_2)
    reconfigure(test_app)
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_date,
        datetime_as_rfc3339(date_1.astimezone(timezone("UTC"))),
    )
    assert len(result) == 1


def test_range_param_date(test_app):
    update_db_timezone(SOURCE_NAME, ALTERNATE_TZ)
    date_1 = tz_datetime(ALTERNATE_TZ, 2020, 6, 30)
    date_2 = tz_datetime(ALTERNATE_TZ, 2020, 7, 30)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_1)
    insert_table_pnt_4326_1_date_with(SOURCE_NAME, date_2)
    reconfigure(test_app)
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_date,
        "/".join(
            [
                datetime_as_rfc3339(date_1.astimezone(timezone("UTC"))),
                datetime_as_rfc3339(date_2.astimezone(timezone("UTC"))),
            ]
        ),
    )
    assert len(result) == 2


def test_range_start_no_temporal(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_basic(SOURCE_NAME)
    result = _get_collection_items(
        test_app,
        table_pnt_4326,
        f"{datetime_as_rfc3339(datetime.utcnow())}/",
    )
    assert len(result) == 1


def test_range_end_no_temporal(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_basic(SOURCE_NAME)
    result = _get_collection_items(
        test_app,
        table_pnt_4326,
        f"/{datetime_as_rfc3339(datetime.utcnow())}",
    )
    assert len(result) == 1


def test_range_param_no_temporal(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_basic(SOURCE_NAME)
    result = _get_collection_items(
        test_app,
        table_pnt_4326,
        "/".join(
            [
                datetime_as_rfc3339(datetime.utcnow()),
                datetime_as_rfc3339(datetime.utcnow()),
            ]
        ),
    )
    assert len(result) == 1


def test_instant_and_bbox_in(test_app):
    reconfigure(test_app)
    instant_utc = utc_datetime(2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_utc,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        datetime_as_rfc3339(instant_utc),
        "-1,0,1,2",
    )
    assert len(result) == 1


def test_instant_and_bbox_out(test_app):
    reconfigure(test_app)
    instant_utc = utc_datetime(2021, 7, 14, 7, 3, 1)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        instant_utc,
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        datetime_as_rfc3339(instant_utc),
        "5,5,6,6",
    )
    assert len(result) == 0


def _get_collection_items(
    test_app,
    collection_title: str,
    datetime_param: Optional[str] = None,
    bbox_param: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return test_app.get(
        ITEMS_URL.format(
            collection_id=get_collection_id_for(test_app, collection_title),
            datetime=f"&datetime={datetime_param}" if datetime_param is not None else "",
            bbox=f"&bbox={bbox_param}" if bbox_param is not None else "",
        )
    ).json()["features"]
