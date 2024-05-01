import asyncio

import uvloop
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

import pytest

from db.utils import create_db, create_tables, drop_db, drop_tables
from src.core.settings import settings
from src.app import app
from src.db.main import close_dbs, get_session, set_session_pool, get_engine
from src.models import User


@pytest.fixture(scope="session")
def loop():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def connect_db(loop):
    await set_session_pool(
        settings.db.postgres_url, {"isolation_level": "AUTOCOMMIT"}
    )
    bind: AsyncEngine = await get_engine(settings.db.postgres_url,)
    await create_db(bind, settings.db.db_name)
    await create_tables(bind)

    yield

    await drop_tables(bind)
    await close_dbs()


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture
async def get_db_session() -> AsyncSession:
    session = await get_session()
    yield session
    await session.close()


@pytest.fixture(scope="session")
async def test_user(get_db_session: AsyncSession):
    test_user = User(email="test_email@gmail.com", password="Test_password22")
    get_db_session.add(test_user)
    await get_db_session.commit()
