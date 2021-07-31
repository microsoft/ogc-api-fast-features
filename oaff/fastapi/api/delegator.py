from typing import Awaitable, Callable, Type

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from oaff.app.gateway import handle as gateway_handler
from oaff.app.request_handlers.common.request_handler import RequestHandler
from oaff.app.requests.common.request_type import RequestType
from oaff.app.responses.error_response import ErrorResponse
from oaff.app.responses.response import Response as AppResponse


def get_default_handler() -> Callable[[Type[RequestHandler]], Awaitable[AppResponse]]:
    return gateway_handler


# expect handler as argument so that it is overridable in testing
async def delegate(
    request: Type[RequestType],
    handler: Callable[
        [Type[RequestHandler]], Awaitable[Type[AppResponse]]
    ] = get_default_handler(),
) -> Response:
    try:
        app_response = await handler(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    if isinstance(app_response, ErrorResponse):
        raise HTTPException(
            status_code=app_response.status_code, detail=app_response.detail
        )
    else:
        return Response(
            content=app_response.encoded_response,
            status_code=app_response.status_code,
            headers=app_response.additional_headers,
            media_type=app_response.mime_type,
        )
