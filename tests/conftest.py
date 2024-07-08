from asyncio import current_task
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.v1.auth.utils.my_jwt import create_access_token
from src.api.v1.auth.utils.password import hash_password
from src.app import app
from src.db.models import User
from src.db.session import close_dbs, get_async_pool, s
from src.db.utils import create_db, create_tables, drop_db, drop_tables
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
async def a_test_client(connect_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as a_client:
        yield a_client


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
async def test_admin_user(connect_db) -> AsyncGenerator[User, None]:
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    s.user_db = ses()

    test_admin_user = User(
        email="test_admin_user@gmail.com",
        password=hash_password("Test_password22"),
        role="admin"
    )

    s.user_db.add(test_admin_user)
    await s.user_db.commit()

    yield test_admin_user

    await s.user_db.close()
    await ses.remove()


@pytest.fixture()
def test_admin_user_token(test_admin_user: User) -> str:
    access_token, _ = create_access_token(test_admin_user)
    return access_token
