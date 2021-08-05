import os
from http import HTTPStatus
from typing import Final
from uuid import uuid4

from bs4 import BeautifulSoup

from oaff.testing.data.load.db import update_db
from oaff.testing.integration_tests.common import (
    get_collection_id_for,
    get_item_id_for,
    reconfigure,
)
from oaff.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    table_mply_4326,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
ITEM_1_NAME: Final = str(uuid4())
ITEM_2_NAME: Final = str(uuid4())
BASE_URL: Final = "/collections/{collection_id}/items?limit={limit}&offset={offset}"
JSON_URL: Final = f"{BASE_URL}&format=json"
HTML_URL: Final = f"{BASE_URL}&format=html"


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


def test_all_items_json(test_app):
    _item_setup(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            limit=2,
            offset=0,
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["type"] == "FeatureCollection"
    assert response_content["numberMatched"] == 2
    assert response_content["numberReturned"] == 2
    assert (
        len(
            list(
                filter(
                    lambda link: link["rel"] in ["next", "prev"],
                    response_content["links"],
                )
            )
        )
        == 0
    )
    assert len(response_content["features"]) == 2
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_1_NAME,
                    response_content["features"],
                )
            )
        )
        == 1
    )
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_2_NAME,
                    response_content["features"],
                )
            )
        )
        == 1
    )


def test_first_item_json(test_app):
    _item_setup(test_app)
    collection_id = get_collection_id_for(test_app, table_mply_4326)
    response = test_app.get(
        JSON_URL.format(collection_id=collection_id, limit=1, offset=0)
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["type"] == "FeatureCollection"
    assert response_content["numberMatched"] == 2
    assert response_content["numberReturned"] == 1
    assert (
        len(list(filter(lambda link: link["rel"] == "prev", response_content["links"])))
        == 0
    )
    assert list(filter(lambda link: link["rel"] == "next", response_content["links"]))[0][
        "href"
    ].endswith(JSON_URL.format(collection_id=collection_id, limit=1, offset=1))
    assert len(response_content["features"]) == 1
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_1_NAME,
                    response_content["features"],
                )
            )
        )
        == 1
    )
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_2_NAME,
                    response_content["features"],
                )
            )
        )
        == 0
    )


def test_second_item_json(test_app):
    _item_setup(test_app)
    collection_id = get_collection_id_for(test_app, table_mply_4326)
    response = test_app.get(
        JSON_URL.format(collection_id=collection_id, limit=1, offset=1)
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["type"] == "FeatureCollection"
    assert response_content["numberMatched"] == 2
    assert response_content["numberReturned"] == 1
    assert (
        len(list(filter(lambda link: link["rel"] == "next", response_content["links"])))
        == 0
    )
    assert list(filter(lambda link: link["rel"] == "prev", response_content["links"]))[0][
        "href"
    ].endswith(JSON_URL.format(collection_id=collection_id, limit=1, offset=0))
    assert len(response_content["features"]) == 1
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_1_NAME,
                    response_content["features"],
                )
            )
        )
        == 0
    )
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_2_NAME,
                    response_content["features"],
                )
            )
        )
        == 1
    )


def test_all_items_html(test_app):
    _item_setup(test_app)
    collection_id = get_collection_id_for(test_app, table_mply_4326)
    response = test_app.get(
        HTML_URL.format(collection_id=collection_id, limit=2, offset=0)
    )
    assert response.status_code == HTTPStatus.OK
    response_content = str(response.content)
    soup = BeautifulSoup(response_content, "html.parser")
    id_links = soup.find_all("a", attrs={"class": "feature-id-link"})
    item_1_id = get_item_id_for(test_app, collection_id, ITEM_1_NAME)
    item_2_id = get_item_id_for(test_app, collection_id, ITEM_2_NAME)
    assert len(id_links) == 2
    assert (
        len(
            list(
                filter(
                    lambda id_link: id_link.attrs["href"]
                    == "".join(
                        [
                            f"/collections/{collection_id}/items/",
                            f"{item_1_id}",
                        ]
                    ),
                    id_links,
                )
            )
        )
        == 1
    )
    assert (
        len(
            list(
                filter(
                    lambda id_link: id_link.attrs["href"]
                    == "".join(
                        [
                            f"/collections/{collection_id}/items/",
                            f"{item_2_id}",
                        ]
                    ),
                    id_links,
                )
            )
        )
        == 1
    )


def _item_setup(test_app):
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
