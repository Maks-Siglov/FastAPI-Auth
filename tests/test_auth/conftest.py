from asyncio import current_task

from sqlalchemy.ext.asyncio import async_scoped_session

import pytest_asyncio

from src.api.v1.auth.utils.password import hash_password
from src.db.models import User
from src.db.session import get_async_pool, s
from src.settings import DbSettings


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
