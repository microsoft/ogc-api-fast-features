from datetime import datetime
from logging import getLogger
from typing import Final, Optional, Tuple, Union, cast
from urllib.parse import quote

import iso8601
import pytz
from fastapi import APIRouter, HTTPException, Query
from fastapi.param_functions import Depends
from fastapi.requests import Request

from oaff.app.requests.collection import Collection as CollectionRequestType
from oaff.app.requests.collection_items import (
    CollectionItems as CollectionItemsRequestType,
)
from oaff.app.requests.collections_list import CollectionsList as CollectionsListRequest
from oaff.app.requests.feature import Feature as FeatureRequestType
from oaff.app.responses.response_type import ResponseType
from oaff.fastapi.api import settings
from oaff.fastapi.api.delegator import delegate, get_default_handler
from oaff.fastapi.api.routes.common.common_parameters import CommonParameters
from oaff.fastapi.api.routes.common.parameter_control import strict as enforce_strict

PATH: Final = f"{settings.ROOT_PATH}/collections"
ROUTER: Final = APIRouter()
LOGGER: Final = getLogger(__file__)
BBOX_MEMBER_REGEX: Final = r"(\-)?\d+(\.\d+)?"

PATH_GET_COLLECTION: Final = "/{collection_id}"
PATH_GET_COLLECTION_ITEMS: Final = "/{collection_id}/items"
PATH_GET_FEATURE: Final = "/{collection_id}/items/{feature_id}"


@ROUTER.get("")
async def get_collections_list(
    request: Request,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
):
    enforce_strict(request)
    return await delegate(
        CollectionsListRequest(
            type=ResponseType.METADATA,
            format=common_parameters.format,
            locale=common_parameters.locale,
            root=common_parameters.root,
            url=str(request.url),
        ),
        handler,
    )


@ROUTER.get(PATH_GET_COLLECTION)
async def get_collection(
    collection_id: str,
    request: Request,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
):
    enforce_strict(request)
    return await delegate(
        CollectionRequestType(
            type=ResponseType.METADATA,
            collection_id=collection_id,
            format=common_parameters.format,
            locale=common_parameters.locale,
            url=_get_safe_url(PATH_GET_COLLECTION, request, common_parameters.root),
            root=common_parameters.root,
        ),
        handler,
    )


@ROUTER.get(PATH_GET_COLLECTION_ITEMS)
async def get_collection_items(
    collection_id: str,
    request: Request,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
    limit_param: int = Query(
        alias="limit",
        default=settings.ITEMS_LIMIT_DEFAULT,
        ge=settings.ITEMS_LIMIT_MIN,
        le=settings.ITEMS_LIMIT_MAX,
    ),
    offset_param: int = Query(
        alias="offset",
        default=settings.ITEMS_OFFSET_DEFAULT,
        ge=settings.ITEMS_OFFSET_MIN,
    ),
    bbox_param: Optional[str] = Query(
        alias="bbox",
        default=settings.ITEMS_BBOX_DEFAULT,
        regex="".join(
            [
                r"^",
                rf"{BBOX_MEMBER_REGEX},",
                rf"{BBOX_MEMBER_REGEX},",
                rf"{BBOX_MEMBER_REGEX},",
                rf"{BBOX_MEMBER_REGEX}",
                r"(," rf"{BBOX_MEMBER_REGEX},",
                rf"{BBOX_MEMBER_REGEX},",
                r")?" r"$",
            ]
        ),
    ),
    bbox_crs_param: Optional[str] = Query(
        alias="bbox-crs",
        default=settings.ITEMS_BBOX_CRS_DEFAULT,
    ),
    datetime_param: Optional[str] = Query(
        alias="datetime",
        default=settings.ITEMS_DATETIME_DEFAULT,
        # OGC spec states RFC 3339 but lots of discussion / ambiguity about whether
        # that does or does not mandate "T" separator. Permit T or single whitespace
        regex="".join(
            [
                r"^(|\.\.|\d{4}\-\d{2}\-\d{2}(T|\s)\d{2}\:\d{2}\:\d{2}(\.\d{1,})?Z)",
                r"(\/(|\.\.|\d{4}\-\d{2}\-\d{2}(T|\s)\d{2}\:\d{2}\:\d{2}(\.\d{1,})?Z))?$",
            ]
        ),
    ),
    filter_param: Optional[str] = Query(
        alias="filter",
        default=None,
    ),
    filter_lang_param: Optional[str] = Query(
        alias="filter-lang",
        default=None,
    ),
    filter_crs_param: Optional[str] = Query(
        alias="filter-crs",
        default=None,
    ),
):
    enforce_strict(
        request,
        [
            "limit",
            "offset",
            "bbox",
            "bbox-crs",
            "datetime",
            "filter",
            "filter-lang",
            "filter-crs",
        ],
    )
    return await delegate(
        CollectionItemsRequestType(
            type=ResponseType.DATA,
            url=_get_safe_url(PATH_GET_COLLECTION_ITEMS, request, common_parameters.root),
            format=common_parameters.format,
            locale=common_parameters.locale,
            collection_id=collection_id,
            limit=limit_param,
            offset=offset_param,
            spatial_bounds=bbox_param.split(",") if bbox_param is not None else None,
            spatial_bounds_crs=bbox_crs_param,
            temporal_bounds=_process_datetime(datetime_param),
            filter_cql=filter_param,
            filter_lang=filter_lang_param,
            filter_crs=filter_crs_param,
            root=common_parameters.root,
        ),
        handler,
    )


@ROUTER.get(PATH_GET_FEATURE)
async def get_feature(
    collection_id: str,
    request: Request,
    feature_id: str,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
):
    enforce_strict(request)
    return await delegate(
        FeatureRequestType(
            type=ResponseType.DATA,
            collection_id=collection_id,
            feature_id=feature_id,
            format=common_parameters.format,
            locale=common_parameters.locale,
            url=_get_safe_url(PATH_GET_FEATURE, request, common_parameters.root),
            root=common_parameters.root,
        ),
        handler,
    )


def _process_datetime(
    parameter: Optional[str],
) -> Optional[Union[Tuple[datetime], Tuple[datetime, datetime]]]:
    if parameter is None:
        return None
    else:

        def parse_datetime(datetime_str: str) -> datetime:
            if len(datetime_str) == 0 or (datetime_str == ".."):
                return None
            parsed = iso8601.parse_date(datetime_str)
            parsed.astimezone(pytz.utc)
            return parsed

        result = [parse_datetime(part) for part in parameter.split("/")]
    result_not_none = list(filter(lambda result_part: result_part is not None, result))
    if len(result_not_none) == 0:
        return None
    if len(result_not_none) == 2:
        if result[0] > result[1]:
            raise HTTPException(
                status_code=400, detail="datetime start cannot be after end"
            )
    return cast(Union[Tuple[datetime], Tuple[datetime, datetime]], tuple(result))


def _get_safe_url(path_template: str, request: Request, root: str) -> str:
    """
    FastAPI request has URL-decoded URL rather than caller's URL-encoded URL.
    Application logic uses the caller's URL to build some links (e.g. alternate formats).
    Logic that builds links has inadequate context to reliably escape path parameters,
    so ensure the URL we pass to the business logic uses URL-encoded path parameters.
    """
    local_path = path_template.format(
        **{key: quote(value) for key, value in request.path_params.items()}
    )
    query_str = "&".join(
        [f"{key}={value}" for key, value in request.query_params.items()]
    )
    return f"{root}{PATH}{local_path}{f'?{query_str}' if len(query_str) > 0 else ''}"
