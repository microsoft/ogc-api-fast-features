from http import HTTPStatus

from pydantic import BaseModel


class Response(BaseModel):
    status_code: HTTPStatus = HTTPStatus.OK
