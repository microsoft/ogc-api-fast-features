import os
from http import HTTPStatus
from typing import Final
from uuid import uuid4

from bs4 import BeautifulSoup

from oaff.testing.data.load.db import query, update_db
from oaff.testing.integration_tests.common import get_collection_id_for, reconfigure
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    insert_table_pnt_4326_float_id_with,
    insert_table_pnt_4326_str_id_with,
    table_mply_4326,
    table_pnt_4326_float_id,
    table_pnt_4326_str_id,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
ITEM_1_NAME: Final = str(uuid4())
ITEM_2_NAME: Final = str(uuid4())
BASE_URL: Final = "/collections/{collection_id}/items/{feature_id}"
JSON_URL: Final = f"{BASE_URL}?format=json"
HTML_URL: Final = f"{BASE_URL}?format=html"


def setup_module():
    drop_common(SOURCE_NAME)
    os.environ["APP_DATA_SOURCE_TYPES"] = "postgresql"
    os.environ["APP_POSTGRESQL_SOURCE_NAMES"] = SOURCE_NAME
    os.environ[f"APP_POSTGRESQL_MAC_{SOURCE_NAME}"] = "0"
    create_common(SOURCE_NAME)


def teardown_module():
    drop_common(SOURCE_NAME)


def teardown_function():
    truncate_common(SOURCE_NAME)


def test_feature_int_id_json(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            feature_id=_get_feature_id_by_name(ITEM_2_NAME),
        )
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["properties"]["name"] == ITEM_2_NAME
    assert response.json()["geometry"]["coordinates"] == [
        [[[0, 0], [0, 2], [2, 2], [2, 0], [0, 0]]]
    ]


def test_missing_feature_int_id_json(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            feature_id=2147483647,
        )
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_missing_collection_json(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=str(uuid4()),
            feature_id=_get_feature_id_by_name(ITEM_1_NAME),
        )
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_feature_int_id_html(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        HTML_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            feature_id=_get_feature_id_by_name(ITEM_1_NAME),
        )
    )
    assert response.status_code == HTTPStatus.OK
    soup = BeautifulSoup(str(response.content), "html.parser")
    feature_id = soup.find_all("h2", attrs={"class": "feature-id-title"})
    assert len(feature_id) == 1
    assert feature_id[0].text == str(_get_feature_id_by_name(ITEM_1_NAME))


def test_missing_feature_int_id_html(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        HTML_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            feature_id=2147483647,
        )
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_missing_collection_html(test_app):
    _item_setup_int_id(test_app)
    response = test_app.get(
        HTML_URL.format(
            collection_id=str(uuid4()),
            feature_id=_get_feature_id_by_name(ITEM_1_NAME),
        )
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_feature_float_id_json(test_app):
    reconfigure(test_app)
    id = 1.1
    insert_table_pnt_4326_float_id_with(SOURCE_NAME, id)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_4326_float_id),
            feature_id=id,
        )
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == id


def test_feature_str_id_json(test_app):
    reconfigure(test_app)
    id = str(uuid4())
    insert_table_pnt_4326_str_id_with(SOURCE_NAME, id)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_4326_str_id),
            feature_id=id,
        )
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == id


def _item_setup_int_id(test_app):
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('{ITEM_1_NAME}', ST_GeomFromText('MULTIPOLYGON (((
            0 0, 0 1, 1 1, 1 0, 0 0
        )))', 4326))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('{ITEM_2_NAME}', ST_GeomFromText('MULTIPOLYGON (((
            0 0, 0 2, 2 2, 2 0, 0 0
        )))', 4326))
        """,
        SOURCE_NAME,
    )
    reconfigure(test_app)


def _get_feature_id_by_name(name: str):
    return query(f"SELECT id FROM {table_mply_4326} WHERE name = '{name}'", SOURCE_NAME)[
        0
    ][0]
