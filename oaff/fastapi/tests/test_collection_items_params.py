from http import HTTPStatus
from typing import Final

from oaff.fastapi.api.routes.collections import PATH as ROOT_PATH
from oaff.fastapi.api.settings import ITEMS_LIMIT_MAX, ITEMS_LIMIT_MIN, ITEMS_OFFSET_MIN
from oaff.fastapi.tests import common_delegation as common
from oaff.fastapi.tests.common import get_valid_datetime_parameter

handler_calls, collection_id, _ = common.make_params_common()
endpoint_path: Final = f"{ROOT_PATH}/{collection_id}/items"


def setup_module():
    common.setup_module(handler_calls)


def setup_function():
    common.setup_function(handler_calls)


def teardown_module():
    common.teardown_module()


def test_items_valid_min(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?limit={ITEMS_LIMIT_MIN}&offset={ITEMS_OFFSET_MIN}",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_max(test_app):
    assert (
        common.request(
            test_app, endpoint_path, url_suffix=f"?limit={ITEMS_LIMIT_MAX}"
        ).status_code
        == HTTPStatus.OK
    )


def test_items_invalid_min_limit(test_app):
    assert (
        common.request(
            test_app, endpoint_path, url_suffix=f"?limit={ITEMS_LIMIT_MIN - 1}"
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_invalid_max_limit(test_app):
    assert (
        common.request(
            test_app, endpoint_path, url_suffix=f"?limit={ITEMS_LIMIT_MAX + 1}"
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_invalid_max_offset(test_app):
    assert (
        common.request(
            test_app, endpoint_path, url_suffix=f"?offset={ITEMS_OFFSET_MIN - 1}"
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_valid_bbox_ints(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?bbox=0,0,1,1",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_bbox_mixed(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?bbox=-0.4321,0,41143.432143115,999.43214",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_invalid_bbox_too_few(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?bbox=-0,1,1",
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_invalid_bbox_too_many(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?bbox=-0,1,1,2,3,4,5,6",
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_invalid_bbox_non_numeric(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?bbox=-one,two",
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_valid_datetime_instant(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?datetime={get_valid_datetime_parameter()}",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"""?datetime={
                get_valid_datetime_parameter()
            }/{
                get_valid_datetime_parameter()
            }""",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range_start(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?datetime={get_valid_datetime_parameter()}/..",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range_start_no_dot(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?datetime={get_valid_datetime_parameter()}/",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range_end(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?datetime=../{get_valid_datetime_parameter()}",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range_end_no_dot(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix=f"?datetime=/{get_valid_datetime_parameter()}",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_range_neither(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?datetime=../..",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_null(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?datetime=..",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_valid_datetime_empty(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?datetime=",
        ).status_code
        == HTTPStatus.OK
    )


def test_items_invalid_datetime_format_1(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?datetime=2010:12:15 12:05:12",
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )


def test_items_invalid_datetime_format_2(test_app):
    assert (
        common.request(
            test_app,
            endpoint_path,
            url_suffix="?datetime=2010-123-15T12:05:12",
        ).status_code
        == HTTPStatus.BAD_REQUEST
    )
