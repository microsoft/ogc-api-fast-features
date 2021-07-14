import os
from http import HTTPStatus
from typing import Final
from uuid import uuid4

from bs4 import BeautifulSoup

from feapi.testing.data.load.db import update_db
from feapi.testing.integration_tests.common import (
    get_collection_id_for,
    get_item_id_for,
    reconfigure,
)
from feapi.testing.integration_tests.common_pg import (
    create_common,
    drop_common,
    table_mply_4326,
    table_pnt_3857,
    table_pnt_geog,
    truncate_common,
)

SOURCE_NAME: Final = "stac"
ITEM_NAMES: Final = [str(uuid4()) for i in range(7)]
BASE_URL: Final = "/collections/{collection_id}/items?bbox={bbox}"
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


def setup_function():
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('{ITEM_NAMES[0]}', ST_GeomFromText('MULTIPOLYGON (((
            -180 -90,180 -90,180 90,-180 90,-180 -90
        )))', 4326))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('{ITEM_NAMES[1]}', ST_GeomFromText('MULTIPOLYGON (
            ((-5 -5,5 -5,5 5,-5 5,-5 -5)),
            ((80 80,85 80,85 85,80 85,80 80))
        )', 4326))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_mply_4326} (name, boundary) VALUES
        ('{ITEM_NAMES[2]}', ST_GeomFromText('MULTIPOLYGON (((
            -50 -50,-45 -50,-45 -45,-50 -45,-50 -50
        )))', 4326))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_pnt_3857} (name, location) VALUES
        ('{ITEM_NAMES[3]}', ST_GeomFromText('POINT (-13692297.37 7170156.29)', 3857))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_pnt_3857} (name, location) VALUES
        ('{ITEM_NAMES[4]}', ST_GeomFromText('POINT (13692297.37 -7170156.29)', 3857))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_pnt_geog} (id, location) VALUES
        ('{ITEM_NAMES[5]}', ST_GeogFromText('SRID=4326;POINT (-45 -45)'))
        """,
        SOURCE_NAME,
    )
    update_db(
        f"""
        INSERT INTO {table_pnt_geog} (id, location) VALUES
        ('{ITEM_NAMES[6]}', ST_GeogFromText('SRID=4326;POINT (45 45)'))
        """,
        SOURCE_NAME,
    )


def teardown_function():
    truncate_common(SOURCE_NAME)


def test_bbox_json_data4326(test_app):
    reconfigure(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            bbox="-10,-10,0,0",
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["numberMatched"] == 2
    assert response_content["numberReturned"] == 2
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_NAMES[0],
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
                    lambda feature: feature["properties"]["name"] == ITEM_NAMES[1],
                    response_content["features"],
                )
            )
        )
        == 1
    )


def test_bbox_html_data4326(test_app):
    reconfigure(test_app)
    collection_id = get_collection_id_for(test_app, table_mply_4326)
    response = test_app.get(
        HTML_URL.format(
            collection_id=get_collection_id_for(test_app, table_mply_4326),
            bbox="-10,-10,0,0",
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = str(response.content)
    soup = BeautifulSoup(response_content, "html.parser")
    id_links = soup.find_all("a", attrs={"class": "feature-id-link"})
    assert len(id_links) == 2
    assert (
        len(
            list(
                filter(
                    lambda id_link: id_link.attrs["href"]
                    == "".join(
                        [
                            f"/collections/{collection_id}/items/",
                            f"{get_item_id_for(test_app, collection_id, ITEM_NAMES[0])}",
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
                            f"{get_item_id_for(test_app, collection_id, ITEM_NAMES[1])}",
                        ]
                    ),
                    id_links,
                )
            )
        )
        == 1
    )


def test_bbox_json_data3857(test_app):
    reconfigure(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_3857),
            bbox="-130,50,-120,60",
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["numberMatched"] == 1
    assert response_content["numberReturned"] == 1
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["properties"]["name"] == ITEM_NAMES[3],
                    response_content["features"],
                )
            )
        )
        == 1
    )


def test_bbox_html_data3857(test_app):
    reconfigure(test_app)
    collection_id = get_collection_id_for(test_app, table_pnt_3857)
    response = test_app.get(
        HTML_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_3857),
            bbox="-130,50,-120,60",
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = str(response.content)
    soup = BeautifulSoup(response_content, "html.parser")
    id_links = soup.find_all("a", attrs={"class": "feature-id-link"})
    assert len(id_links) == 1
    assert (
        len(
            list(
                filter(
                    lambda id_link: id_link.attrs["href"]
                    == "".join(
                        [
                            f"/collections/{collection_id}/items/",
                            f"{get_item_id_for(test_app, collection_id, ITEM_NAMES[3])}",
                        ]
                    ),
                    id_links,
                )
            )
        )
        == 1
    )


def test_bbox_json_geog(test_app):
    reconfigure(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_geog),
            bbox="0,0,179.9,89.9",
        )
    )
    assert response.status_code == HTTPStatus.OK
    response_content = response.json()
    assert response_content["numberReturned"] == 1
    assert (
        len(
            list(
                filter(
                    lambda feature: feature["id"] == ITEM_NAMES[6],
                    response_content["features"],
                )
            )
        )
        == 1
    )


def test_bbox_error(test_app):
    reconfigure(test_app)
    response = test_app.get(
        JSON_URL.format(
            collection_id=get_collection_id_for(test_app, table_pnt_geog),
            bbox="0,0,180,90",
        )
    )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
