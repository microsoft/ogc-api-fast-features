from typing import Final

from oaff.app.requests.collection_items import CollectionItems
from oaff.fastapi.api.routes.collections import PATH as ROOT_PATH
from oaff.fastapi.api.settings import ITEMS_LIMIT_DEFAULT, ITEMS_OFFSET_DEFAULT
from oaff.fastapi.tests import common_delegation as common

handler_calls, collection_id, _ = common.make_params_common()
endpoint_path: Final = f"{ROOT_PATH}/{collection_id}/items"


def setup_module():
    common.setup_module(handler_calls)


def setup_function():
    common.setup_function(handler_calls)


def teardown_module():
    common.teardown_module()


def test_basic_defaults(test_app):
    common.test_basic_defaults(
        test_app,
        endpoint_path,
        CollectionItems,
        handler_calls,
    )
    assert handler_calls[0].collection_id == collection_id
    assert handler_calls[0].limit == ITEMS_LIMIT_DEFAULT
    assert handler_calls[0].offset == ITEMS_OFFSET_DEFAULT


def test_format_html(test_app):
    common.test_format_html(test_app, endpoint_path, handler_calls)


def test_format_json(test_app):
    common.test_format_json(test_app, endpoint_path, handler_calls)


def test_language_en_US(test_app):
    common.test_language_en_US(test_app, endpoint_path, handler_calls)


def test_language_unknown_with_known_fallback(test_app):
    common.test_language_unknown_with_known_fallback(
        test_app,
        endpoint_path,
        handler_calls,
    )


def test_language_unknown_without_known_fallback(test_app):
    common.test_language_unknown_without_known_fallback(
        test_app,
        endpoint_path,
        handler_calls,
    )


def test_non_default_limit(test_app):
    limit: Final = 123
    common.request(test_app, endpoint_path, f"?limit={limit}")
    assert handler_calls[0].limit == limit


def test_non_default_offset(test_app):
    offset: Final = 321
    common.request(test_app, endpoint_path, f"?offset={offset}")
    assert handler_calls[0].offset == offset


def test_non_default_limit_offset(test_app):
    limit: Final = 123
    offset: Final = 321
    common.request(test_app, endpoint_path, f"?limit={limit}&offset={offset}")
    assert handler_calls[0].limit == limit
    assert handler_calls[0].offset == offset


def test_format_header_html(test_app):
    common.test_format_header_html(test_app, endpoint_path, handler_calls)


def test_format_header_json(test_app):
    common.test_format_header_json(test_app, endpoint_path, handler_calls)


def test_format_header_override(test_app):
    common.test_format_header_override(test_app, endpoint_path, handler_calls)


def test_unknown_param(test_app):
    common.test_unknown_param(test_app, endpoint_path)
