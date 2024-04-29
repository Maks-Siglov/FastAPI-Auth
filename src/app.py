import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

import uvicorn
import uvloop

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

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
