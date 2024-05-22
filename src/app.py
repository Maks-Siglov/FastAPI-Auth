from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, HTTPException

from uvicorn import Config, Server

from src.core.settings import app_settings
from src.db.session import close_dbs, set_session_pool
from src.error_handler import http_exception_handler
from src.logger import logger_config
from src.routes import api_router_v1


@asynccontextmanager
async def lifespan(my_app: FastAPI):
    await set_session_pool()
    yield
    await close_dbs()


logger_config()

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
