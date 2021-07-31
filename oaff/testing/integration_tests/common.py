from datetime import datetime
from http import HTTPStatus

from pytz import timezone


def reconfigure(test_app):
    reconfigure_response = test_app.post("/control/reconfigure")
    assert reconfigure_response.status_code == HTTPStatus.OK


def get_collection_id_for(test_app, collection_title: str) -> str:
    response = test_app.get("/collections?format=json").json()
    return list(
        filter(
            lambda collection: collection["title"] == collection_title,
            response["collections"],
        )
    )[0]["id"]


def get_item_id_for(test_app, collection_id: str, feature_name: str) -> str:
    return list(
        filter(
            lambda feature: feature["properties"]["name"] == feature_name,
            test_app.get(f"/collections/{collection_id}/items?format=json").json()[
                "features"
            ],
        )
    )[0]["id"]


def utc_datetime(*args, **kwargs) -> datetime:
    return tz_datetime("UTC", *args, **kwargs)


def tz_datetime(tz: str, *args, **kwargs) -> datetime:
    return timezone(tz).localize(datetime(*args, **kwargs))
