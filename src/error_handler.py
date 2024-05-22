from fastapi import HTTPException

from starlette.requests import Request
from starlette.responses import JSONResponse


async def http_exception_handler(
    _: Request, exc: HTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )
