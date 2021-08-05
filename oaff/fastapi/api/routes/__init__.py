from fastapi import APIRouter
from starlette.responses import RedirectResponse

from oaff.fastapi.api.routes.collections import (
    PATH as path_collections,
    ROUTER as router_collections,
)
from oaff.fastapi.api.routes.conformance import (
    PATH as path_conformance,
    ROUTER as router_conformance,
)
from oaff.fastapi.api.routes.control import PATH as path_control, ROUTER as router_control
from oaff.fastapi.api.routes.landing_page import (
    PATH as path_landing_page,
    ROUTER as router_landing_page,
)
from oaff.fastapi.api.settings import ROOT_PATH

router = APIRouter()
router.include_router(router_landing_page, prefix=path_landing_page)
router.include_router(router_collections, prefix=path_collections)
router.include_router(router_control, prefix=path_control)
router.include_router(router_conformance, prefix=path_conformance)

if len(ROOT_PATH) > 0 and ROOT_PATH != "/":

    @router.get("/")
    async def redirect():
        return RedirectResponse(url=ROOT_PATH)
