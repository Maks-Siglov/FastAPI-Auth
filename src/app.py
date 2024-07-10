import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import (
    APIRouter,
    FastAPI,
    HTTPException
)

from uvicorn import Config, Server

from src.api.routers import api_router_v1
from src.db.session import close_dbs
from src.error_handler import http_exception_handler
from src.logger import logger_config
from src.settings import AppSettings

logger_config()

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(my_app: FastAPI) -> AsyncGenerator[None, None]:
    log.warning("Start application")
    yield
    log.warning("Application shutdown")
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
            host=AppSettings.host,
            port=AppSettings.port,
            reload=AppSettings.reload,
        )
    )
    server.run()
