import os
from http import HTTPStatus
from typing import Final

import pytest
from bs4 import BeautifulSoup

from oaff.testing.data.load.db import update_db
from oaff.testing.integration_tests.common import reconfigure
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_mply_4326_basic,
    table_mply_4326,
    table_pnt_3857,
    table_pnt_4326,
    table_pnt_geog,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
JSON_URL: Final = "/collections?format=json"
HTML_URL: Final = "/collections?format=html"


def setup_module():
    drop_common(SOURCE_NAME)
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(
        SOURCE_NAME,
        [
            table_mply_4326,
            table_pnt_4326,
            table_pnt_3857,
            table_pnt_geog,
        ],
    )


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(
        SOURCE_NAME,
        [
            table_mply_4326,
            table_pnt_4326,
            table_pnt_3857,
            table_pnt_geog,
        ],
    )
    if f"APP_POSTGRESQL_LAYER_WHITELIST_{SOURCE_NAME}" in os.environ:
        del os.environ[f"APP_POSTGRESQL_LAYER_WHITELIST_{SOURCE_NAME}"]
    if f"APP_POSTGRESQL_LAYER_BLACKLIST_{SOURCE_NAME}" in os.environ:
        del os.environ[f"APP_POSTGRESQL_LAYER_BLACKLIST_{SOURCE_NAME}"]


def test_default(test_app):
    reconfigure(test_app)
    response = test_app.get(JSON_URL)
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert len(response_content["collections"]) == 4
    for collection in response_content["collections"]:
        collection_bbox = collection["extent"]["spatial"]["bbox"][0]
        assert collection_bbox[0] == -180
        assert collection_bbox[1] == -90
        assert collection_bbox[2] == 180
        assert collection_bbox[3] == 90


def test_bbox(test_app):
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('boundary 01', ST_GeomFromText('MULTIPOLYGON (((
            0 0, 0 1, 1 1, 1 0, 0 0
        )))', 4326)),
        ('boundary 02', ST_GeomFromText('MULTIPOLYGON (((
            0.5 0.5, 0.5 1.5, 1.5 1.5, 1.5 0.5, 0.5 0.5
        )))', 4326))
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    collection = list(
        filter(
            lambda collection: collection["title"] == table_mply_4326,
            response_content["collections"],
        )
    )[0]
    collection_bbox = collection["extent"]["spatial"]["bbox"][0]
    assert collection_bbox[0] == pytest.approx(0, 0.000001)
    assert collection_bbox[1] == pytest.approx(0, 0.000001)
    assert collection_bbox[2] == pytest.approx(1.5, 0.000001)
    assert collection_bbox[3] == pytest.approx(1.5, 0.000001)


def test_whitelist(test_app):
    os.environ[
        f"APP_POSTGRESQL_LAYER_WHITELIST_{SOURCE_NAME}"
    ] = f"public.{table_mply_4326}"
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    assert len(response_content["collections"]) == 1
    assert response_content["collections"][0]["title"] == table_mply_4326


def test_blacklist(test_app):
    os.environ[
        f"APP_POSTGRESQL_LAYER_BLACKLIST_{SOURCE_NAME}"
    ] = f"public.{table_mply_4326},public.{table_pnt_3857},public.{table_pnt_geog}"
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    assert len(response_content["collections"]) == 1
    assert response_content["collections"][0]["title"] == table_pnt_4326


def test_whitelist_blacklist(test_app):
    os.environ[
        f"APP_POSTGRESQL_LAYER_WHITELIST_{SOURCE_NAME}"
    ] = f"public.{table_mply_4326}"
    os.environ[
        f"APP_POSTGRESQL_LAYER_BLACKLIST_{SOURCE_NAME}"
    ] = f"public.{table_mply_4326}"
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    assert len(response_content["collections"]) == 4


def test_crs_conversion(test_app):
    update_db(
        f"""
        INSERT INTO {table_pnt_3857} (location) VALUES
        (ST_GeomFromText('POINT (-13692297.37 5621521.49)', 3857)),
        (ST_GeomFromText('POINT (13692297.37 -5621521.49)', 3857))
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)
    response_content = test_app.get(JSON_URL).json()
    collection = list(
        filter(
            lambda collection: collection["title"] == table_pnt_3857,
            response_content["collections"],
        )
    )[0]
    collection_bbox = collection["extent"]["spatial"]["bbox"][0]
    assert collection_bbox[0] == pytest.approx(-123, 0.000001)
    assert collection_bbox[1] == pytest.approx(-45, 0.000001)
    assert collection_bbox[2] == pytest.approx(123, 0.000001)
    assert collection_bbox[3] == pytest.approx(45, 0.000001)


def test_self_links_json(test_app):
    insert_table_mply_4326_basic(SOURCE_NAME)
    reconfigure(test_app)
    links = test_app.get(JSON_URL).json()["links"]
    assert (
        len(
            list(
                filter(
                    lambda link: link["rel"] == "alternate"
                    and link["type"] == "text/html"
                    and link["href"].endswith(HTML_URL),
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
                    and link["href"].endswith(JSON_URL),
                    links,
                )
            )
        )
        == 1
    )


def test_self_links_html(test_app):
    insert_table_mply_4326_basic(SOURCE_NAME)
    reconfigure(test_app)
    soup = BeautifulSoup(str(test_app.get(HTML_URL).content), "html.parser")
    self_link = soup.find_all("a", attrs={"class": "link-self"})
    assert len(self_link) == 1
    assert self_link[0].attrs["href"].endswith(HTML_URL)
    alt_link = soup.find_all("a", attrs={"class": "link-alternate"})
    assert len(alt_link) == 1
    assert alt_link[0].attrs["href"].endswith(JSON_URL)
