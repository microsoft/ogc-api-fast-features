import os
from http import HTTPStatus
from typing import Final
from uuid import uuid4

import pytest
from bs4 import BeautifulSoup

from oaff.testing.integration_tests.common import reconfigure
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_mply_4326_basic,
    table_mply_4326,
    truncate_common,
)

BASE_URL: Final = "/collections/{0}?format="
JSON_URL: Final = f"{BASE_URL}json"
HTML_URL: Final = f"{BASE_URL}html"
SOURCE_NAME: Final = "stac"


def setup_module():
    drop_common(SOURCE_NAME)
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def setup_function():
    insert_table_mply_4326_basic(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)


def test_basic(test_app):
    reconfigure(test_app)
    response = test_app.get(JSON_URL.format(_get_collection_id(test_app)))
    assert response.status_code == HTTPStatus.OK


def test_bbox(test_app):
    reconfigure(test_app)
    collection = test_app.get(JSON_URL.format(_get_collection_id(test_app))).json()
    collection_bbox = collection["extent"]["spatial"]["bbox"][0]
    assert collection_bbox[0] == pytest.approx(0, 0.000001)
    assert collection_bbox[1] == pytest.approx(0, 0.000001)
    assert collection_bbox[2] == pytest.approx(1, 0.000001)
    assert collection_bbox[3] == pytest.approx(1, 0.000001)


def test_self_links_json(test_app):
    reconfigure(test_app)
    collection_id = _get_collection_id(test_app)
    links = test_app.get(JSON_URL.format(collection_id)).json()["links"]
    assert (
        len(
            list(
                filter(
                    lambda link: link["rel"] == "alternate"
                    and link["type"] == "text/html"
                    and link["href"].endswith(HTML_URL.format(collection_id)),
                    links,
                )
            )
        )
        == 1
    )
    assert (
        len(
            list(
                filter(
                    lambda link: link["rel"] == "self"
                    and link["type"] == "application/json"
                    and link["href"].endswith(JSON_URL.format(collection_id)),
                    links,
                )
            )
        )
        == 1
    )


def test_self_links_html(test_app):
    reconfigure(test_app)
    collection_id = _get_collection_id(test_app)
    soup = BeautifulSoup(
        str(test_app.get(HTML_URL.format(collection_id)).content), "html.parser"
    )
    self_link = soup.find_all("a", attrs={"class": "link-self"})
    assert len(self_link) == 1
    assert self_link[0].attrs["href"].endswith(HTML_URL.format(collection_id))
    alt_link = soup.find_all("a", attrs={"class": "link-alternate"})
    assert len(alt_link) == 1
    assert alt_link[0].attrs["href"].endswith(JSON_URL.format(collection_id))


def test_missing_collection(test_app):
    response = test_app.get(JSON_URL.format(str(uuid4())))
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_html_present(test_app):
    # only purpose of this test is to verify that the
    # negative HTML tests that follow are valid
    reconfigure(test_app)
    soup = BeautifulSoup(
        str(test_app.get(HTML_URL.format(_get_collection_id(test_app))).content),
        "html.parser",
    )
    assert soup.find("div", attrs={"class": "title-container"}) is not None


def test_unconfigured_license_json(test_app):
    reconfigure(test_app)
    assert (
        test_app.get(JSON_URL.format(_get_collection_id(test_app))).json()["license"]
        is None
    )


def test_unconfigured_license_html(test_app):
    reconfigure(test_app)
    soup = BeautifulSoup(
        str(test_app.get(HTML_URL.format(_get_collection_id(test_app))).content),
        "html.parser",
    )
    assert soup.find("div", attrs={"class": "license-container"}) is None


def test_unconfigured_keywords_json(test_app):
    reconfigure(test_app)
    assert (
        test_app.get(JSON_URL.format(_get_collection_id(test_app))).json()["keywords"]
        is None
    )


def test_unconfigured_keywords_html(test_app):
    reconfigure(test_app)
    soup = BeautifulSoup(
        str(test_app.get(HTML_URL.format(_get_collection_id(test_app))).content),
        "html.parser",
    )
    assert soup.find("div", attrs={"class": "keywords-container"}) is None


def test_unconfigured_providers_json(test_app):
    reconfigure(test_app)
    assert (
        test_app.get(JSON_URL.format(_get_collection_id(test_app))).json()["providers"]
        is None
    )


def test_unconfigured_providers_html(test_app):
    reconfigure(test_app)
    soup = BeautifulSoup(
        str(test_app.get(HTML_URL.format(_get_collection_id(test_app))).content),
        "html.parser",
    )
    assert soup.find("div", attrs={"class": "providers-container"}) is None


def _get_collection_id(test_app):
    return list(
        filter(
            lambda collection: collection["title"] == table_mply_4326,
            test_app.get("/collections?format=json").json()["collections"],
        )
    )[0]["id"]
