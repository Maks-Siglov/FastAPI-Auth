import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

import uvloop
from uvicorn import Config, Server

from admin.views import admin_router
from auth.views import router as auth_router
from balance.views import balance_router
from core.settings import settings
from db.session import close_dbs, set_session_pool
from error_handler import http_exception_handler
from logger import logger_config


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    await set_session_pool()
    yield
    await close_dbs()


def create_app() -> FastAPI:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    logger_config()

    app = FastAPI(lifespan=lifespan)

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(balance_router)

    app.add_exception_handler(HTTPException, http_exception_handler)

    return app


def create_server(app: FastAPI) -> Server:
    config = Config(
        app=app,
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload,
    )
    return Server(config=config)


if __name__ == "__main__":
    app = create_app()
    server = create_server(app)
    server.run()
