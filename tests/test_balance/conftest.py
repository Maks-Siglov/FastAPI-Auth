from asyncio import current_task
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings


@pytest_asyncio.fixture()
async def test_user_with_balance(connect_db) -> AsyncGenerator[User, None]:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    user_with_balance = User(
        email="user_with_balance@gmail.com",
        password=hash_password("Test_password22"),
        balance=200,
    )

    s.user_db.add(user_with_balance)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()

    yield user_with_balance


@pytest_asyncio.fixture()
async def async_test_balance_client(
    connect_db, test_user_with_balance: User
) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    def override_get_current_user():
        """Overridden get_current_user dependency which return test user"""
        return test_user_with_balance

    my_app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client
