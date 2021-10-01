from enum import Enum

from oaff.app.responses.response_type import ResponseType


class ResponseFormat(dict, Enum):  # type: ignore[misc]
    html = {
        ResponseType.DATA: "text/html",
        ResponseType.METADATA: "text/html",
    }
    json = {
        ResponseType.DATA: "application/geo+json",
        ResponseType.METADATA: "application/json",
    }
