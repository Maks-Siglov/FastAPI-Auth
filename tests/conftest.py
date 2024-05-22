import asyncio

from fastapi.testclient import TestClient

import pytest

from app import app
from auth.utils.password import hash_password
from db.utils import (
    create_db,
    create_tables,
    drop_db,
    drop_tables
)
from src.core.settings import db_settings
from src.db.session import (
    close_dbs,
    get_engine,
    pop_session,
    s,
    set_session_pool
)
from src.models import User


@pytest.fixture(scope="session", autouse=True)
def loop():
    loop = asyncio.new_event_loop()
    yield
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connect_db(loop):
    await create_db(db_settings.get_postgres_db_url(), db_settings.db_name)
    bind = await get_engine()
    await create_tables(bind)

    yield

    await drop_tables(bind)
    await close_dbs()
    await drop_db(db_settings.get_postgres_db_url(), db_settings.db_name)


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
