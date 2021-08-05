from typing import Final

from oaff.app.requests.landing_page import LandingPage
from oaff.fastapi.api.routes.landing_page import PATH as ROOT_PATH
from oaff.fastapi.tests import common_delegation as common

handler_calls, collection_id, _ = common.make_params_common()
endpoint_path: Final = f"{ROOT_PATH}/"


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
        LandingPage,
        handler_calls,
    )


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


def test_format_header_html(test_app):
    common.test_format_header_html(test_app, endpoint_path, handler_calls)


def test_format_header_json(test_app):
    common.test_format_header_json(test_app, endpoint_path, handler_calls)


def test_format_header_override(test_app):
    common.test_format_header_override(test_app, endpoint_path, handler_calls)


def test_unknown_param(test_app):
    common.test_unknown_param(test_app, endpoint_path)
