from http import HTTPStatus
from typing import List, Type
from uuid import uuid4

from oaff.app.i18n.locales import Locales
from oaff.app.requests.common.request_type import RequestType
from oaff.app.responses.response_format import ResponseFormat
from oaff.fastapi.api.delegator import get_default_handler
from oaff.fastapi.api.main import app
from oaff.fastapi.tests.common import get_mock_handler_provider


def make_params_common():
    return (list(), str(uuid4()), str(uuid4()))


def setup_module(handler_calls):
    app.dependency_overrides[get_default_handler] = get_mock_handler_provider(
        handler_calls
    )


def setup_function(handler_calls):
    handler_calls.clear()


def teardown_module():
    app.dependency_overrides = {}


def test_basic_defaults(
    test_app,
    endpoint_path: str,
    type: Type[RequestType],
    handler_calls: List[Type[RequestType]],
):
    request(test_app, endpoint_path)
    assert handler_calls[0].__class__ == type
    assert handler_calls[0].format == ResponseFormat.json
    assert handler_calls[0].locale == Locales.en_US
    assert str(handler_calls[0].url).endswith(endpoint_path)


def test_format_html(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(test_app, endpoint_path, url_suffix="?format=html")
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.html


def test_format_json(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(test_app, endpoint_path, url_suffix="?format=json")
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.json


def test_language_en_US(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(test_app, endpoint_path)
    assert len(handler_calls) == 1
    assert handler_calls[0].locale == Locales.en_US


def test_language_unknown_with_known_fallback(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app,
        endpoint_path,
        headers={"Accept-Language": "unknown_language, en_US:0.9"},
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].locale == Locales.en_US


def test_language_unknown_without_known_fallback(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app,
        endpoint_path,
        headers={"Accept-Language": "unknown_language, another_unknown_language:0.9"},
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].locale == Locales.en_US


def test_accept_ordering_multiple_ordered(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app,
        endpoint_path,
        headers={"Accept": "text/html, application/json"},
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.html


def test_accept_ordering_weighted(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app,
        endpoint_path,
        headers={"Accept": "text/html;q=0.7, application/json;q=0.9"},
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.json


def test_format_header_html(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(test_app, endpoint_path, url_suffix="", headers={"Accept": "text/html"})
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.html


def test_format_header_json(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app, endpoint_path, url_suffix="", headers={"Accept": "application/json"}
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.json


def test_format_header_override(
    test_app,
    endpoint_path: str,
    handler_calls: List[Type[RequestType]],
):
    request(
        test_app,
        endpoint_path,
        url_suffix="?format=json",
        headers={"Accept": "text/html"},
    )
    assert len(handler_calls) == 1
    assert handler_calls[0].format == ResponseFormat.json


def test_unknown_param(test_app, endpoint_path: str):
    assert (
        request(test_app, endpoint_path, f"?{str(uuid4())}={str(uuid4())}").status_code
        == HTTPStatus.BAD_REQUEST
    )


def request(test_app, endpoint_path: str, url_suffix="", headers=dict()):
    return test_app.get(f"{endpoint_path}{url_suffix}", headers=headers)
