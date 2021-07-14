from logging import getLogger
from os import path
from typing import Final

from feapi.app.configuration.frontend_configuration import FrontendConfiguration

LOGGER: Final = getLogger(__file__)
_frontend_configuration: FrontendConfiguration = None


def set_frontend_configuration(frontend_configuration: FrontendConfiguration) -> None:
    global _frontend_configuration
    _frontend_configuration = frontend_configuration


def get_frontend_configuration() -> FrontendConfiguration:
    return _frontend_configuration


def get_assets_path() -> str:
    return path.join(path.dirname(__file__), "..", "assets")
