from datetime import datetime
from typing import Final

from pytz import timezone

LON_MIN: Final = -180
LON_MAX: Final = 180
LAT_MIN: Final = -90
LAT_MAX: Final = 90
ALT_MIN: Final = -500
ALT_MAX: Final = 9000


def is_valid_lat(value: float) -> bool:
    return _within_range(value, LAT_MIN, LAT_MAX)


def is_valid_lon(value: float) -> bool:
    return _within_range(value, LON_MIN, LON_MAX)


def is_valid_alt(value: float) -> bool:
    return _within_range(value, ALT_MIN, ALT_MAX)


def _within_range(value: float, min: int, max: int) -> bool:
    return value >= min and value <= max


def limit_precision(input: float, precision: int) -> float:
    multiplier = pow(10, precision)
    return round(input * multiplier) / multiplier


def now_as_rfc3339() -> str:
    return datetime_as_rfc3339(datetime.now())


def datetime_as_rfc3339(datetime: datetime) -> str:
    if datetime is None:
        return None
    return datetime.astimezone(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
