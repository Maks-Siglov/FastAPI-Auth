from asyncio import current_task
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.auth.dependencies import get_redis_client
from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings
from tests.test_auth.mock import get_mock_redis_client


TEST_USER_EMAIL = "test_email@gmail.com"
TEST_IN_ACTIVE_USER_EMAIL = "test_in_active_user@gmail.com"
TEST_USER_PASSWORD = "Test_password22"


@pytest_asyncio.fixture()
async def test_users(connect_db) -> None:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_user = User(
        email=TEST_USER_EMAIL, password=hash_password(TEST_USER_PASSWORD)
    )
    test_in_active_user = User(
        email=TEST_IN_ACTIVE_USER_EMAIL,
        password=hash_password(TEST_USER_PASSWORD),
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
