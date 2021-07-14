from typing import List, Optional

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from feapi.fastapi.api.routes.common.common_parameters import COMMON_QUERY_PARAMS


def strict(request: Request, permitted: Optional[List[str]] = []) -> None:
    excessive = set(request.query_params.keys()).difference(
        set(permitted + COMMON_QUERY_PARAMS)
    )
    if len(excessive) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown query parameters: {', '.join(excessive)}",
        )
