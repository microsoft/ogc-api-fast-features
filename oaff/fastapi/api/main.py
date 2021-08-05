from logging import getLogger
from typing import Final

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles

from oaff.app.configuration.frontend_configuration import FrontendConfiguration
from oaff.app.configuration.frontend_interface import get_assets_path
from oaff.app.gateway import cleanup, configure
from oaff.fastapi.api import settings
from oaff.fastapi.api.middleware.request_context_log_middleware import (
    RequestContextLogMiddleware,
)
from oaff.fastapi.api.openapi.openapi import get_openapi_handler
from oaff.fastapi.api.routes import router
from oaff.fastapi.api.util import alternate_format_for_url, next_page, prev_page

LOGGER: Final = getLogger(__file__)
ASSETS_PATH: Final = f"{settings.ROOT_PATH}/assets"


app = FastAPI(
    title=settings.NAME,
    docs_url=settings.SWAGGER_PATH,
    openapi_url=settings.OPENAPI_PATH,
    redoc_url=settings.REDOC_PATH,
)
# OGC requires a specific response header
# Duplicate OpenAPI docs with this content-type
app.add_route(
    settings.OPENAPI_OGC_PATH, get_openapi_handler(app), include_in_schema=False
)

app.include_router(router)

# CORS configuration, select appropriate CORS regex from settings
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=settings.CORS_ANY_LOCALHOST_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Log messages with unique request IDs
app.add_middleware(RequestContextLogMiddleware)

# expose assets provided by business logic package
app.mount(ASSETS_PATH, StaticFiles(directory=get_assets_path()), name="assets")


# override FastAPI's default 422 bad request error to match OGC spec
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.on_event("startup")
async def startup():
    await configure(
        FrontendConfiguration(
            asset_url_base=ASSETS_PATH,
            api_url_base=settings.ROOT_PATH,
            endpoint_format_switcher=alternate_format_for_url,
            next_page_link_generator=next_page,
            prev_page_link_generator=prev_page,
            openapi_path_html=settings.SWAGGER_PATH,
            openapi_path_json=settings.OPENAPI_OGC_PATH,
        )
    )


@app.on_event("shutdown")
async def shutdown():
    await cleanup()


# Development / debug support, not executed when running in container
# Start a local server on port 8008 by default,
# or whichever port was provided by the caller, when script / module executed directly
if __name__ == "__main__":
    import sys

    import uvicorn  # type: ignore

    port = 8008 if len(sys.argv) == 1 else int(sys.argv[1])
    LOGGER.info("Available on port %d", port)
    LOGGER.debug("Debug logging enabled if visible")
    uvicorn.run(app, host="0.0.0.0", port=port)
