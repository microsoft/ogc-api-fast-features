import os
from typing import Final, List

ENV_VAR_PREFIX: Final = os.environ.get("APP_ENV_VAR_PREFIX", "APP_")
SPATIAL_FILTER_GEOMETRY_FIELD_ALIAS: Final = "geometry"
OPENAPI_OGC_TYPE: Final = "application/vnd.oai.openapi+json;version=3.0"


def DATA_SOURCE_TYPES() -> List[str]:
    return [
        type.lower()
        for type in os.environ.get(f"{ENV_VAR_PREFIX}DATA_SOURCE_TYPES", "").split(",")
    ]
