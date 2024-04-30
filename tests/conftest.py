from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.core.settings import settings
from src.app import app
from src.db.main import close_dbs, get_session, set_session_pool, session_pools
from src.models import User


@pytest.fixture(scope="session")
def test_client():
    return TestClient(app)


@pytest.fixture(scope="session")
async def db_connection():
    await set_session_pool(settings.db.test_postgres_url)
    yield
    await close_dbs()


@pytest.fixture
async def get_db_session() -> AsyncSession:
    session = await get_session(settings.db.test_postgres_url)
    yield session
    await session.close()


@pytest.fixture(scope="session")
async def test_user(get_db_session: AsyncSession):
    test_user = User(email="test_email@gmail.com", password="Test_password22")
    get_db_session.add(test_user)
    await get_db_session.commit()
