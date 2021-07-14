import logging
import logging.config

from feapi.fastapi.api import settings
from feapi.fastapi.api.middleware.request_context_log_middleware import get_request_id


class LogContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


def configure_logging() -> None:
    logging_levels = {value: key for key, value in logging._levelToName.items()}
    logging_level_name = settings.LOG_LEVEL
    if logging_level_name not in logging_levels:
        raise ValueError(f"{logging_level_name} is not a valid log level")
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "request_context": {
                    "()": LogContextFilter,
                }
            },
            "formatters": {
                "default": {
                    "class": "logging.Formatter",
                    "datefmt": "%H:%M:%S%z",
                    "format": "".join(
                        [
                            "%(asctime)s %(filename)s:%(lineno)d %(levelname)s",
                            " - req:%(request_id)s %(message)s",
                        ]
                    ),
                },
            },
            "handlers": {
                "console": {
                    "level": logging_levels[logging_level_name],
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                    "filters": ["request_context"],
                },
            },
            "root": {
                "level": logging_levels[logging_level_name],
                "handlers": ["console"],
            },
        }
    )


configure_logging()
