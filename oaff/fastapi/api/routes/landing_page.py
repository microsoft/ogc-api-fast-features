from logging import getLogger
from typing import Final

from fastapi import APIRouter, Depends
from fastapi.requests import Request

from oaff.app.requests.landing_page import LandingPage as LandingPageRequestType
from oaff.app.responses.response_type import ResponseType
from oaff.fastapi.api import settings
from oaff.fastapi.api.delegator import delegate, get_default_handler
from oaff.fastapi.api.routes.common.common_parameters import CommonParameters
from oaff.fastapi.api.routes.common.parameter_control import strict as enforce_strict

PATH: Final = f"{settings.ROOT_PATH}"
ROUTER: Final = APIRouter()
LOGGER: Final = getLogger(__file__)


@ROUTER.get("/")
async def root(
    request: Request,
    common_parameters: CommonParameters = Depends(CommonParameters.populate),
    handler=Depends(get_default_handler),
):
    enforce_strict(request)
    return await delegate(
        LandingPageRequestType(
            type=ResponseType.METADATA,
            format=common_parameters.format,
            url=str(request.url),
            locale=common_parameters.locale,
            root=common_parameters.root,
        ),
        handler,
    )
