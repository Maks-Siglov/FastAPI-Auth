from asyncio import current_task
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.auth.dependencies import (
    get_current_user,
    get_redis_client,
    get_user_from_refresh_token,
)
from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings
from tests.test_auth.mock import get_mock_redis_client

TEST_USER_EMAIL = "test_email@gmail.com"
TEST_IN_ACTIVE_USER_EMAIL = "test_in_active_user@gmail.com"
MOCK_USER_EMAIL = "mock_user@gmail.com"
TEST_USER_PASSWORD = "Test_password22"

AUTH_API_V1 = "/api/v1/auth"


@pytest_asyncio.fixture()
async def test_mock_user(connect_db) -> User:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    mock_user = User(
        email=MOCK_USER_EMAIL, password=hash_password(TEST_USER_PASSWORD)
    )

    s.user_db.add(mock_user)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()

    yield mock_user


@pytest_asyncio.fixture()
async def async_test_client(
    connect_db, test_mock_user: User
) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    def override_get_current_user():
        """Overridden get_current_user dependency which return test user"""
        mock_user = test_mock_user
        s.user_db.add(mock_user)
        return mock_user

    my_app.dependency_overrides[get_redis_client] = get_mock_redis_client
    my_app.dependency_overrides[get_user_from_refresh_token] = (
        override_get_current_user
    )
    my_app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client


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
async def test_access_token(
    async_test_client: AsyncClient, test_users: None
) -> str | None:
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    response = await async_test_client.post(
        f"{AUTH_API_V1}/login/", json=login_data
    )

    return response.json().get("access_token")
