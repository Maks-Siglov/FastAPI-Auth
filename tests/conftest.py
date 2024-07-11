import pytest_asyncio

from src.db.session import close_dbs, get_async_pool
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
