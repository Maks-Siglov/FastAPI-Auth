from asyncio import current_task
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.admin.dependencies import check_admin_role
from src.api.v1.users.dependencies import get_current_user
from src.api.v1.users.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings
from tests.test_admin.mock import mock_check_admin_role

TEST_USER_EMAIL = "test_email@gmail.com"
TEST_BLOCKED_USER_EMAIL = "test_blocked_user@gmail.com"
TEST_USER_PASSWORD = "Test_password22"


@pytest_asyncio.fixture()
async def test_admin_user(connect_db) -> User:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_admin_user = User(
        email="test_admin_user@gmail.com",
        password=hash_password("Test_password22"),
        role="admin",
        first_name="John",
        last_name="Doe",
    )

    s.user_db.add(test_admin_user)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()

    return test_admin_user


@pytest_asyncio.fixture()
async def async_test_admin_client(
    connect_db, test_admin_user: User
) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    def override_get_current_user():
        """Overridden get_current_user dependency which return test
        admin user"""
        test_admin = test_admin_user
        s.user_db.add(test_admin)
        return test_admin

    my_app.dependency_overrides[get_current_user] = override_get_current_user
    my_app.dependency_overrides[check_admin_role] = mock_check_admin_role

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client


@pytest_asyncio.fixture()
async def test_user(connect_db) -> AsyncGenerator[User, None]:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_user = User(
        email=TEST_USER_EMAIL,
        password=hash_password(TEST_USER_PASSWORD),
        first_name="Test_name",
        last_name="Test_last_name",
    )

    s.user_db.add(test_user)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()

    yield test_user


@pytest_asyncio.fixture()
async def test_blocked_user(connect_db) -> AsyncGenerator[User, None]:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_blocked_user = User(
        email=TEST_BLOCKED_USER_EMAIL,
        password=hash_password(TEST_USER_PASSWORD),
        first_name="Test_name",
        last_name="Test_last_name",
        is_blocked=True,
    )

    s.user_db.add(test_blocked_user)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()

    yield test_blocked_user
