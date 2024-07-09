from asyncio import current_task
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.routers import api_router_v1
from src.api.v1.admin.dependencies import check_admin_role
from src.api.v1.auth.utils.my_jwt import create_access_token
from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings
from tests.test_admin.mock import mock_check_admin_role


@pytest_asyncio.fixture()
async def async_test_admin_client(
    connect_db,
) -> AsyncGenerator[AsyncClient, None]:
    my_app = FastAPI()

    main_api_router = APIRouter(prefix="/api")
    main_api_router.include_router(api_router_v1)

    my_app.include_router(main_api_router)

    my_app.dependency_overrides[check_admin_role] = mock_check_admin_role

    async with AsyncClient(
        transport=ASGITransport(app=my_app), base_url="http://test"
    ) as a_client:
        yield a_client


@pytest_asyncio.fixture()
async def test_admin_user(connect_db) -> None:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_admin_user = User(
        email="test_admin_user@gmail.com",
        password=hash_password("Test_password22"),
        role="admin",
    )

    s.user_db.add(test_admin_user)
    await s.user_db.commit()

    await s.user_db.close()
    await ses.remove()


@pytest.fixture()
def test_admin_user_token(test_admin_user: User) -> str:
    access_token, _ = create_access_token(test_admin_user)
    return access_token
