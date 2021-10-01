import re

from oaff.app.responses.response_format import ResponseFormat
from oaff.fastapi.api import settings


def alternate_format_for_url(url: str, format: ResponseFormat) -> str:
    format_pattern = re.compile(
        rf"(\?|&)format=({'|'.join([format.name for format in ResponseFormat])})"  # noqa: E501
    )
    query_string_pattern = re.compile(r"(\?|&).+=.*")
    if re.search(format_pattern, url) is not None:
        return re.sub(format_pattern, rf"\1format={format.name}", url)
    else:
        connector = "?"
        if re.search(query_string_pattern, url):
            connector = "&"
        return f"{url}{connector}format={format.name}"


def next_page(url: str) -> str:
    return _change_page(url, True)


def prev_page(url: str) -> str:
    return _change_page(url, False)


def _change_page(url: str, forward: bool) -> str:
    url_parts = url.split("?")
    parameters = {
        key: value
        for key, value in [
            part.split("=")
            for part in [
                part
                for part in (url_parts[1] if len(url_parts) == 2 else "").split("&")
                if len(part) > 0
            ]
        ]
    }
    limit = (
        int(parameters["limit"])
        if "limit" in parameters
        else settings.ITEMS_LIMIT_DEFAULT
    )
    offset = (
        int(parameters["offset"])
        if "offset" in parameters
        else settings.ITEMS_OFFSET_DEFAULT
    )
    return "{0}?{1}".format(
        url_parts[0],
        "&".join(
            [
                f"{key}={value}"
                for key, value in {
                    **parameters,
                    **{
                        "offset": str(max(offset + limit * (1 if forward else -1), 0)),
                        "limit": str(limit),
                    },
                }.items()
            ]
        ),
    )
