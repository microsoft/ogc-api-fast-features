from fastapi.responses import JSONResponse

from oaff.app.settings import OPENAPI_OGC_TYPE


class VndResponse(JSONResponse):
    media_type = OPENAPI_OGC_TYPE
