import os
from logging import getLogger
from typing import Final, List, Tuple

import psycopg2  # type: ignore

LOGGER: Final = getLogger(__file__)


def query(sql: str, src_name: str = None) -> List[Tuple]:
    connection = _get_connection(src_name)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    _release_connection(connection)

    return result


def update_db(statement: str, src_name: str = None) -> None:
    connection = _get_connection(src_name)
    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()
    _release_connection(connection)


def check_connection(src_name: str = None) -> None:
    _release_connection(_get_connection(src_name))


def _get_connection(src_name: str = None) -> psycopg2.extensions.connection:
    suffix = f"_{src_name}" if src_name is not None else ""
    try:
        return psycopg2.connect(
            host=os.environ.get(f"APP_POSTGRESQL_HOST{suffix}", "localhost"),
            port=int(os.environ.get(f"APP_POSTGRESQL_PORT{suffix}", 5432)),
            dbname=os.environ.get(f"APP_POSTGRESQL_DBNAME{suffix}", "postgres"),
            user=os.environ.get(f"APP_POSTGRESQL_USER{suffix}", "postgres"),
            password=os.environ.get(f"APP_POSTGRESQL_PASSWORD{suffix}", "postgres"),
        )
    except Exception as e:
        LOGGER.error(f"Error establishing DB connection: {e}")
        raise e


def _release_connection(connection: psycopg2.extensions.connection) -> None:
    try:
        connection.close()
    except Exception as e:
        LOGGER.warning(f"Problem encountered when closing database connection: {e}")
