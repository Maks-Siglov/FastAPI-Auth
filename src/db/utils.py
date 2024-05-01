from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from models import Base


async def create_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as connection:
        query = f"CREATE DATABASE {db_name};"
        await connection.execute(text(query))


async def drop_db(postgres_url: str, db_name: str) -> None:
    engine = create_async_engine(
        url=postgres_url, isolation_level="AUTOCOMMIT"
    )
    async with engine.begin() as connect:
        query = f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE);"
        await connect.execute(text(query))


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
