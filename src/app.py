import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException

import uvloop
from uvicorn import Config, Server

from admin.views import admin_router
from auth.views import auth_router
from balance.views import balance_router
from core.settings import settings
from db.session import close_dbs, set_session_pool
from error_handler import http_exception_handler
from logger import logger_config
from routes import api_router_v1


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    await set_session_pool()
    yield
    await close_dbs()


def create_app() -> FastAPI:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    logger_config()

    app = FastAPI(lifespan=lifespan)

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    app.include_router(main_api_router)

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
