import asyncio

from fastapi.testclient import TestClient

import pytest

from api.v1.auth.utils.password import hash_password
from src.app import app
from src.settings import DbSettings
from src.db.models import User
from src.db.session import (
    close_dbs,
    get_engine,
    pop_session,
    s,
    set_session_pool,
)
from src.db.utils import create_db, create_tables, drop_db, drop_tables


@pytest.fixture(scope="session", autouse=True)
def loop():
    loop = asyncio.new_event_loop()
    yield
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connect_db(loop):
    await create_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)
    bind = await get_engine()
    await create_tables(bind)

    yield

    await drop_tables(bind)
    await close_dbs()
    await drop_db(DbSettings.get_postgres_db_url(), DbSettings.db_name)


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def test_user() -> None:
    await set_session_pool()

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

    await pop_session()
