from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from models import Base


async def create_db(db_url: str, db_name: str) -> None:
    engine = create_async_engine(url=db_url, isolation_level='AUTOCOMMIT')
    try:
        async with engine.connect() as connection:
            query = f"CREATE DATABASE {db_name};"
            await connection.execute(text(query))
    except ProgrammingError:
        pass


async def drop_db(db_url: str, db_name: str) -> None:
    engine = create_async_engine(url=db_url, isolation_level='AUTOCOMMIT')
    async with engine.begin() as connect:
        query = f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE);"
        await connect.execute(text(query))


async def create_tables(db_url: str) -> None:
    engine = create_async_engine(url=db_url, isolation_level='AUTOCOMMIT')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(db_url: str) -> None:
    engine = create_async_engine(url=db_url, isolation_level='AUTOCOMMIT')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
