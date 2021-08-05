from pydantic import BaseModel

from oaff.app.i18n.locales import Locales
from oaff.app.responses.response_format import ResponseFormat
from oaff.app.responses.response_type import ResponseType


class RequestType(BaseModel):
    url: str
    root: str
    format: ResponseFormat
    type: ResponseType
    locale: Locales
