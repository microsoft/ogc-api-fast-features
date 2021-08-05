from logging import getLogger
from time import sleep
from typing import Final, List, Type

from databases import Database

from oaff.app.data.sources.common.data_source import DataSource
from oaff.app.data.sources.common.data_source_manager import DataSourceManager
from oaff.app.data.sources.postgresql import settings
from oaff.app.data.sources.postgresql.profile import PostgresqlProfile
from oaff.app.data.sources.postgresql.stac_hybrid.postgresql_data_source import (
    PostgresqlDataSource as HybridDataSource,
)

LOGGER: Final = getLogger(__file__)
PROFILES: Final = {
    PostgresqlProfile.STAC_HYBRID: HybridDataSource,
}


class PostgresqlManager(DataSourceManager):
    def get_data_sources(self) -> List[Type[DataSource]]:
        data_sources = list()
        source_names = settings.source_names()

        async def connection_tester(database: Database, source_name: str) -> None:
            if not database.is_connected:
                iteration = 0
                while iteration < settings.connect_retries(source_name):
                    try:
                        await database.connect()
                        LOGGER.info(f"connection tester succeeded iteration {iteration}")
                        return
                    except Exception as e:
                        LOGGER.info(
                            f"connection tester iteration {iteration} failed: {e}"
                        )
                        iteration += 1
                        sleep(1)

        for source_name in source_names if len("".join(source_names)) > 1 else [None]:
            data_sources.append(
                PROFILES[settings.profile(source_name)](
                    source_name,
                    connection_tester,
                )
            )

        return data_sources
