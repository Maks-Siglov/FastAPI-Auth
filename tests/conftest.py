from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.db.session import close_dbs, get_async_pool
from src.db.utils import (
    create_db,
    create_tables,
    drop_db,
    drop_tables
)
from src.settings import DbSettings


@pytest_asyncio.fixture()
async def connect_db():
    await create_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    await create_tables(current_pool.engine)

    yield

    await drop_tables(current_pool.engine)
    await close_dbs()
    await drop_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)


@pytest_asyncio.fixture()
async def async_test_client(connect_db) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client
