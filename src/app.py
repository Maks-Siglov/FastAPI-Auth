import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import uvicorn
import uvloop
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth.views import router as auth_router
from core.settings import settings
from db.main import close_dbs, set_session_pool


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    await set_session_pool()
    yield
    await close_dbs()


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
