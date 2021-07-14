from typing import Awaitable, Callable, Type

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from feapi.app.gateway import handle as gateway_handler
from feapi.app.request_handlers.common.request_handler import RequestHandler
from feapi.app.requests.common.request_type import RequestType
from feapi.app.responses.error_response import ErrorResponse
from feapi.app.responses.response import Response as AppResponse


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
