from re import compile, search, sub
from typing import Final, Optional, Set

from fastapi import Header, Query
from fastapi.requests import Request
from pydantic import BaseModel

from feapi.app.i18n.locales import Locales
from feapi.app.i18n.translations import DEFAULT_LOCALE
from feapi.app.responses.response_format import ResponseFormat
from feapi.app.responses.response_type import ResponseType

RESPONSE_FORMAT_BY_MIME: Final = {
    mime_type: format_name
    for format_name, mime_types in {
        item.name: set(item.value.values()) for item in ResponseFormat
    }.items()
    for mime_type in mime_types
}
RESPONSE_FORMAT_BY_NAME: Final = {format.name: format for format in ResponseFormat}
COMMON_QUERY_PARAMS: Final = ["format"]


class CommonParameters(BaseModel):
    format: ResponseFormat
    locale: Locales
    root: str

    @classmethod
    async def populate(
        cls,
        request: Request,
        format_qs: Optional[str] = Query(
            alias="format",
            default=None,
        ),
        format_header: Optional[str] = Header(
            alias="Accept",
            default=ResponseFormat.json[ResponseType.METADATA],
        ),
        language_header: Optional[str] = Header(
            alias="Accept-Language",
            default=None,
        ),
    ):
        locale = None
        if language_header is not None:
            for option in cls._header_options_by_preference(language_header):
                if option in Locales._value2member_map_:
                    locale = Locales._value2member_map_[option]
                    break

        format = None
        if format_header is not None:
            for option in cls._header_options_by_preference(format_header):
                if option in RESPONSE_FORMAT_BY_MIME:
                    format = ResponseFormat[RESPONSE_FORMAT_BY_MIME[option]]

        if format_qs in RESPONSE_FORMAT_BY_NAME:
            format = RESPONSE_FORMAT_BY_NAME[format_qs]

        return cls(
            format=format or ResponseFormat.json,
            locale=locale or DEFAULT_LOCALE,
            root=sub("/$", "", str(request.base_url)),
        )

    @classmethod
    def _header_options_by_preference(cls, header_value: str) -> Set[str]:
        options = list(
            filter(
                lambda option: len(option) > 0,
                [option.strip() for option in header_value.split(",")],
            )
        )
        weight_pattern = compile(r";q=")
        unweighted = [
            option for option in options if search(weight_pattern, option) is None
        ]
        weighted = [
            option for option in options if search(weight_pattern, option) is not None
        ]
        options_with_weight = {
            option_and_weight[0].strip(): option_and_weight[1].strip()
            for option_and_weight in [option.split(";q=") for option in weighted]
        }
        return unweighted + sorted(options_with_weight, key=options_with_weight.get)[::-1]
