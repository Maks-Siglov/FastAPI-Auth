import asyncio
from asyncio import current_task

from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest

from src.api.v1.auth.utils.password import hash_password
from src.app import app
from src.db.models import User
from src.db.session import (
    close_dbs,
    get_async_pool,
    s
)
from src.db.utils import (
    create_db,
    create_tables,
    drop_db,
    drop_tables
)
from src.settings import DbSettings


@pytest.fixture(scope="session", autouse=True)
def loop():
    loop = asyncio.new_event_loop()
    yield
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connect_db(loop):
    await create_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)
    current_pool = await get_async_pool(DbSettings.get_async_db_url())
    await create_tables(current_pool.engine)

    yield

    await drop_tables(current_pool.engine)
    await close_dbs()
    await drop_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
async def test_user() -> None:
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
