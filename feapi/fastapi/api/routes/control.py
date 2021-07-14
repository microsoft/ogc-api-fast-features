import socket
from logging import getLogger
from typing import Final

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from feapi.app.gateway import discover
from feapi.fastapi.api import settings

PATH: Final = f"{settings.ROOT_PATH}/control"
ROUTER: Final = APIRouter()
LOGGER: Final = getLogger(__file__)


@ROUTER.post("/reconfigure", include_in_schema=False)
async def reconfigure(
    request: Request,
):
    if _permit(request):
        await discover()


# exercise basic control over who is allowed to update configuration
# may expand to more comprehensive authorisation logic in future
def _permit(request: Request) -> bool:
    if request.client.host in [
        *settings.PERMITTED_CONTROL_IPS,
        socket.gethostname(),
        "testclient",
    ]:
        return True
    else:
        LOGGER.warning(f"Attempt to access {PATH} by {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            headers={
                "x-client-host": request.client.host,
                "x-server-host": socket.gethostname(),
            },
        )
