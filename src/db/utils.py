import logging

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.models import Base

log = logging.getLogger(__name__)


async def create_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        query = f"CREATE DATABASE {db_name};"
        try:
            await connection.execute(text(query))
            log.info(f"Created database {db_name}")
        except ProgrammingError:
            log.error(f"Database {db_name} already exists")


async def drop_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(
        url=postgres_url, isolation_level="AUTOCOMMIT"
    )
    async with engine.begin() as connect:
        query = f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE);"
        await connect.execute(text(query))
        log.info(f"Dropped database {db_name}")


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        log.info(f"Created tables for {engine.name}")


async def drop_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        log.info(f"Dropped tables for {engine.name}")
