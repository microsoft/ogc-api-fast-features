from contextvars import ContextVar
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

REQUEST_ID_CTX_KEY = "request_id"

_request_id_ctx_var: ContextVar[str] = ContextVar(
    REQUEST_ID_CTX_KEY, default=None  # type: ignore
)


def get_request_id() -> str:
    return _request_id_ctx_var.get()


class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request_id = _request_id_ctx_var.set(str(uuid4()))

        response = await call_next(request)
        response.headers["X-Request-ID"] = get_request_id()

        _request_id_ctx_var.reset(request_id)

        return response
