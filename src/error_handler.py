from fastapi import HTTPException
from fastapi.responses import ORJSONResponse

from starlette.requests import Request


async def http_exception_handler(
    _: Request, exc: HTTPException
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )
