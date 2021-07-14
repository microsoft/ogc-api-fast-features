import os
from typing import Final

ENV_VAR_PREFIX: Final = os.environ.get("API_ENV_VAR_PREFIX", "API_")
ROOT_PATH: Final = os.environ.get(f"{ENV_VAR_PREFIX}ROOT_PATH", "")
LOG_LEVEL: Final = os.environ.get(f"{ENV_VAR_PREFIX}LOG_LEVEL", "INFO").upper()
NAME: Final = os.environ.get(f"{ENV_VAR_PREFIX}NAME", "API")
SWAGGER_PATH: Final = os.environ.get(f"{ENV_VAR_PREFIX}SWAGGER_PATH", f"{ROOT_PATH}/docs")
OPENAPI_PATH: Final = os.environ.get(
    f"{ENV_VAR_PREFIX}OPENAPI_PATH", f"{ROOT_PATH}/openapi.json"
)
OPENAPI_OGC_PATH: Final = os.environ.get(
    f"{ENV_VAR_PREFIX}OPENAPI_OGC_PATH", f"{ROOT_PATH}/ogc/openapi.json"
)
REDOC_PATH: Final = os.environ.get(f"{ENV_VAR_PREFIX}REDOC_PATH", f"{ROOT_PATH}/redoc")
PERMITTED_CONTROL_IPS: Final = list(
    filter(
        lambda ip: len(ip) > 0,
        os.environ.get(f"{ENV_VAR_PREFIX}PERMITTED_CONTROL_IPS", "127.0.0.1").split(","),
    )
)

CORS_ANY_DOMAIN_REGEX: Final = ".*"
CORS_ANY_LOCALHOST_REGEX: Final = r"http(s)?://localhost(:\d{1,5})?/.*"

ITEMS_LIMIT_DEFAULT: Final = 10
ITEMS_LIMIT_MIN: Final = 1
ITEMS_LIMIT_MAX: Final = 10000
ITEMS_OFFSET_DEFAULT: Final = 0
ITEMS_OFFSET_MIN: Final = 0
ITEMS_BBOX_DEFAULT: Final = None
ITEMS_BBOX_CRS_DEFAULT: Final = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
ITEMS_DATETIME_DEFAULT: Final = None
