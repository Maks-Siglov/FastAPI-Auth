import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import uvicorn
import uvloop

from auth.views import router as auth_router
from core.settings import settings
from db.main import close_dbs, set_session_pool
from error_handler import http_exception_handler


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    await set_session_pool()
    yield
    await close_dbs()


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.add_exception_handler(HTTPException, http_exception_handler)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
