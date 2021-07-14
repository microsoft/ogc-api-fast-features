from logging import getLogger
from typing import Final

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from feapi.app.requests.conformance import Conformance as ConformanceRequestType
from feapi.app.responses.response_type import ResponseType
from feapi.fastapi.api import settings
from feapi.fastapi.api.delegator import delegate, get_default_handler
from feapi.fastapi.api.routes.common.common_parameters import CommonParameters
from feapi.fastapi.api.routes.common.parameter_control import strict as enforce_strict

PATH: Final = f"{settings.ROOT_PATH}/conformance"
ROUTER: Final = APIRouter()
LOGGER: Final = getLogger(__file__)


@ROUTER.get("")
async def root(
    request: Request,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
):
    enforce_strict(request)
    return await delegate(
        ConformanceRequestType(
            type=ResponseType.METADATA,
            format=common_parameters.format,
            url=str(request.url),
            locale=common_parameters.locale,
            root=common_parameters.root,
        ),
        handler,
    )
