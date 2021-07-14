from pydantic import BaseModel

from feapi.app.i18n.locales import Locales
from feapi.app.responses.response_format import ResponseFormat
from feapi.app.responses.response_type import ResponseType


class RequestType(BaseModel):
    url: str
    root: str
    format: ResponseFormat
    type: ResponseType
    locale: Locales
