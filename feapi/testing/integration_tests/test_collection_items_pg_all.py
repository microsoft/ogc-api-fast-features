import os
from typing import Any, Dict, Final, List

from feapi.app.util import datetime_as_rfc3339
from feapi.testing.integration_tests.common import (
    get_collection_id_for,
    reconfigure,
    utc_datetime,
)
from feapi.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_1_instant_utc_with,
    table_pnt_4326_1_instant_utc,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
ITEMS_URL: Final = "".join(
    [
        "/collections/{collection_id}/items",
        "?format=json",
        "&limit={limit}&offset={offset}&datetime={datetime}&bbox={bbox}",
    ]
)


def setup_module():
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)


def test_range_param_and_bbox_and_constraints_no_limit(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(1 1)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(10 10)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 2, 0, 0, 0),
        "POINT(2 2)",
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2019, 12, 31, 23, 59, 59)),
                datetime_as_rfc3339(utc_datetime(2021, 1, 1, 0, 0, 0)),
            ]
        ),
        "0,0,3,3",
        3,
        0,
    )
    assert len(result) == 2


def test_range_param_and_bbox_and_constraints_limit(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(1 1)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(10 10)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 2, 0, 0, 0),
        "POINT(2 2)",
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2019, 12, 31, 23, 59, 59)),
                datetime_as_rfc3339(utc_datetime(2021, 1, 1, 0, 0, 0)),
            ]
        ),
        "0,0,3,3",
        1,
        0,
    )
    assert len(result) == 1


def test_range_param_and_bbox_and_constraints_offset(test_app):
    reconfigure(test_app)
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(1 1)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 1, 0, 0, 0),
        "POINT(10 10)",
    )
    insert_table_pnt_4326_1_instant_utc_with(
        SOURCE_NAME,
        utc_datetime(2020, 1, 2, 0, 0, 0),
        "POINT(2 2)",
    )
    result = _get_collection_items(
        test_app,
        table_pnt_4326_1_instant_utc,
        "/".join(
            [
                datetime_as_rfc3339(utc_datetime(2019, 12, 31, 23, 59, 59)),
                datetime_as_rfc3339(utc_datetime(2021, 1, 1, 0, 0, 0)),
            ]
        ),
        "0,0,3,3",
        1,
        3,
    )
    assert len(result) == 0


def _get_collection_items(
    test_app,
    collection_title: str,
    datetime_param: str,
    bbox_param: str,
    limit_param: int,
    offset_param: int,
) -> List[Dict[str, Any]]:
    collection_id = get_collection_id_for(test_app, collection_title)
    return test_app.get(
        ITEMS_URL.format(
            collection_id=collection_id,
            datetime=datetime_param,
            bbox=bbox_param,
            limit=limit_param,
            offset=offset_param,
        )
    ).json()["features"]
