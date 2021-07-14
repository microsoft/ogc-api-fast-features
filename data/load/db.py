import os
from logging import getLogger
from typing import Final, List, Tuple

import psycopg2  # type: ignore

LOGGER: Final = getLogger(__file__)
SOURCE_NAME: Final = "TEST"


def query(sql: str) -> List[Tuple]:
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    _release_connection(connection)

    return result


def update_db(statement: str) -> None:
    connection = _get_connection()
    cursor = connection.cursor()
    cursor.execute(statement)
    connection.commit()
    cursor.close()
    _release_connection(connection)


def check_connection() -> None:
    _release_connection(_get_connection())


def _get_connection() -> psycopg2.extensions.connection:
    try:
        return psycopg2.connect(
            host=os.environ["APP_POSTGRESQL_HOST"],
            port=os.environ["APP_POSTGRESQL_PORT"],
            dbname=os.environ["APP_POSTGRESQL_DBNAME"],
            user=os.environ["APP_POSTGRESQL_USER"],
            password=os.environ["APP_POSTGRESQL_PASSWORD"],
        )
    except Exception as e:
        LOGGER.error(f"Error establishing DB connection: {e}")
        raise e


def _release_connection(connection: psycopg2.extensions.connection) -> None:
    try:
        connection.close()
    except Exception as e:
        LOGGER.warning(f"Problem encountered when closing database connection: {e}")
