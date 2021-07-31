from typing import Any

from pydantic import BaseModel


class TemporalDeclaration(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class TemporalInstant(TemporalDeclaration):
    field_name: str
    field_tz_aware: bool
    tz: Any  # not actually Any but seemingly no common base class for pytz timezones


class TemporalRange(TemporalDeclaration):
    start_field_name: str
    start_tz_aware: bool
    end_field_name: str
    end_tz_aware: bool
    tz: Any
