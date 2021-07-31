import os
from typing import Set

from oaff.app.settings import ENV_VAR_PREFIX


def source_names() -> Set[str]:
    return set(os.environ.get(f"{ENV_VAR_PREFIX}POSTGRESQL_SOURCE_NAMES", "").split(","))


def profile(name: str) -> str:
    return os.environ[f"{ENV_VAR_PREFIX}POSTGRESQL_PROFILE{name_to_suffix(name)}"]


def host(name: str) -> str:
    return os.environ.get(
        f"{ENV_VAR_PREFIX}POSTGRESQL_HOST{name_to_suffix(name)}", "localhost"
    )


def port(name: str) -> int:
    return int(
        os.environ.get(f"{ENV_VAR_PREFIX}POSTGRESQL_PORT{name_to_suffix(name)}", 5432)
    )


def user(name: str) -> str:
    return os.environ.get(
        f"{ENV_VAR_PREFIX}POSTGRESQL_USER{name_to_suffix(name)}", "postgres"
    )


def password(name: str) -> str:
    return os.environ.get(
        f"{ENV_VAR_PREFIX}POSTGRESQL_PASSWORD{name_to_suffix(name)}", "postgres"
    )


def dbname(name: str) -> str:
    return os.environ.get(
        f"{ENV_VAR_PREFIX}POSTGRESQL_DBNAME{name_to_suffix(name)}", "postgres"
    )


def connect_retries(name: str) -> int:
    return int(
        os.environ.get(
            f"{ENV_VAR_PREFIX}POSTGRESQL_CONNECT_RETRIES{name_to_suffix(name)}", 30
        )
    )


def url(name: str) -> str:
    return "".join(
        [
            "postgresql://",
            f"{user(name)}:",
            f"{password(name)}@",
            f"{host(name)}:",
            f"{port(name)}/",
            f"{dbname(name)}",
        ]
    )


def default_tz_code(name: str) -> str:
    return os.environ.get(
        f"{ENV_VAR_PREFIX}POSTGRESQL_DEFAULT_TZ{name_to_suffix(name)}", "UTC"
    )


def name_to_suffix(name: str) -> str:
    if name is None:
        return ""
    else:
        return f"_{name}"
