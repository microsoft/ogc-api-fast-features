from logging import getLogger
from threading import Lock
from typing import Dict, Final, List

from feapi.app import settings
from feapi.app.data.sources.common.data_source import DataSource
from feapi.app.data.sources.common.layer import Layer

LOGGER: Final = getLogger(__file__)
_data_sources: Final[Dict[str, DataSource]] = dict()
_data_sources_lock: Final = Lock()
_layers: Final[Dict[str, Layer]] = dict()
_layers_lock: Final = Lock()


async def discover() -> None:  # noqa: C901
    with _data_sources_lock:
        for data_source in _data_sources.values():
            await data_source.disconnect()
        _data_sources.clear()
        for data_source_type in settings.DATA_SOURCE_TYPES():
            manager = None
            if data_source_type == "postgresql":
                try:
                    from feapi.app.data.sources.postgresql.postgresql_manager import (
                        PostgresqlManager,
                    )

                    manager = PostgresqlManager()
                except Exception as e:
                    LOGGER.error(f"error creating data source manager: {e}")
                    continue
            else:
                LOGGER.warning(f"Unknown data source type {data_source_type}")
                continue

            try:
                for data_source in manager.get_data_sources():
                    _data_sources[data_source.id] = data_source
            except Exception as e:
                LOGGER.error(f"error retrieving data sources from manager: {e}")

    with _layers_lock:
        _layers.clear()
        for data_source in _data_sources.values():
            LOGGER.info(f"initializing data source {data_source.name}")
            try:
                await data_source.initialize()
            except Exception as e:
                LOGGER.error(f"error initializing {data_source.name}: {e}")
                continue
            LOGGER.info(f"configuring layers in {data_source.name}")
            try:
                layers = await data_source.get_layers()
            except Exception as e:
                LOGGER.error(f"error configuring layers for {data_source.name}: {e}")
                continue
            for layer in layers:
                if layer.id in _layers:
                    LOGGER.warning(
                        f"layer ID clash on {layer.id}, latest wins ({data_source.name})"
                    )
                _layers[layer.id] = layer


async def cleanup() -> None:
    for data_source in _data_sources.values():
        await data_source.disconnect()
    _data_sources.clear()


def get_data_source(data_source_id: str) -> DataSource:
    return _data_sources[data_source_id]


def get_layers() -> List[Layer]:
    with _layers_lock:
        return list(_layers.values())


def get_layer(layer_id: str) -> Layer:
    with _layers_lock:
        return _layers[layer_id] if layer_id in _layers else None
