from asyncio import current_task

from sqlalchemy.ext.asyncio import async_scoped_session


from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.auth.dependencies import get_redis_client
from tests.test_auth.mock import get_mock_redis_client


@pytest_asyncio.fixture()
async def test_user(connect_db) -> None:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_user = User(
        email="test_email@gmail.com", password=hash_password("Test_password22")
    )
    test_in_active_user = User(
        email="test_in_active_user@gmail.com",
        password=hash_password("Test_password22"),
        is_active=False,
    )

    s.user_db.add_all([test_user, test_in_active_user])
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()


@pytest_asyncio.fixture()
async def async_test_client(connect_db) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    my_app.dependency_overrides[get_redis_client] = get_mock_redis_client

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client
