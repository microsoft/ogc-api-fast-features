from logging import getLogger
from typing import Final

from .db import check_connection

LOGGER: Final = getLogger(__file__)
if __name__ == "__main__":
    try:
        LOGGER.info("testing connection")
        check_connection()
    except Exception:
        LOGGER.warning("errored connection, exiting")
        exit(1)
