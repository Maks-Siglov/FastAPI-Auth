from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI, HTTPException

from uvicorn import Config, Server

from src.db.session import close_dbs
from src.error_handler import http_exception_handler
from src.logger import logger_config
from src.routes import api_router_v1
from src.settings import app_settings

logger_config()


@asynccontextmanager
async def lifespan(my_app: FastAPI) -> AsyncGenerator[None, None]:
    yield
    await close_dbs()


app = FastAPI(lifespan=lifespan)

main_api_router = APIRouter(prefix="/api")
main_api_router.include_router(api_router_v1)

app.include_router(main_api_router)

app.add_exception_handler(HTTPException, http_exception_handler)


if __name__ == "__main__":
    server = Server(
        Config(
            app=app,
            host=app_settings.host,
            port=app_settings.port,
            reload=app_settings.reload,
        )
    )
    server.run()
