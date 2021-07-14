import os
from typing import Final, Set

from sqlalchemy import MetaData

from feapi.app.data.sources.postgresql.settings import ENV_VAR_PREFIX, name_to_suffix

FEAPI_SCHEMA_NAME: Final = "feapi"
FEAPI_METADATA: Final = MetaData(schema=FEAPI_SCHEMA_NAME)


def manage_as_collections(name: str) -> bool:
    return (
        int(os.environ.get(f"{ENV_VAR_PREFIX}POSTGRESQL_MAC{name_to_suffix(name)}", "1"))
        == 1
    )


def blacklist(name: str) -> Set[str]:
    return {
        entry
        for entry in os.environ.get(
            f"{ENV_VAR_PREFIX}POSTGRESQL_LAYER_BLACKLIST{name_to_suffix(name)}",
            "",
        ).split(",")
        if len(entry) > 0
    }


def whitelist(name: str) -> Set[str]:
    return {
        entry
        for entry in os.environ.get(
            f"{ENV_VAR_PREFIX}POSTGRESQL_LAYER_WHITELIST{name_to_suffix(name)}",
            "",
        ).split(",")
        if len(entry) > 0
    }
