from feapi.app.responses.response import Response


class ErrorResponse(Response):
    detail: str = ""
