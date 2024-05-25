import logging

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db.models import Base

log = logging.getLogger(__name__)


async def create_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        query = f"CREATE DATABASE {db_name};"
        try:
            log.info("Created database %s", db_name)
            await connection.execute(text(query))
        except ProgrammingError:
            log.error("Database %s already exists", db_name)


async def drop_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(
        url=postgres_url, isolation_level="AUTOCOMMIT"
    )
    async with engine.begin() as connect:
        query = f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE);"
        await connect.execute(text(query))
        log.info("Dropped database %s", db_name)


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        log.info("Created tables for %s", engine.name)


async def drop_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        log.info("Dropped tables for %s", engine.name)


def upgrade_database(db_url: str) -> None:
    import alembic.command
    import alembic.config

    alembic_config = alembic.config.Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", db_url)
    alembic.command.upgrade(alembic_config, "head")
    log.info("Database %s upgrade with alembic complete", db_url)
