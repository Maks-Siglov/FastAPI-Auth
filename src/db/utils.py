from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from models import Base


async def create_db(db_url: str, db_name: str) -> None:
    async with create_async_engine(url=db_url).begin() as connect:
        await connect.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")


async def drop_db(db_url: str, db_name: str) -> None:
    async with create_async_engine(url=db_url).begin() as connect:
        await connect.execute(
            f"DROP DATABASE IF EXISTS {db_name} WITH(FORCE) ;"
        )


async def create_tables(db_url: str) -> None:
    async with create_async_engine(url=db_url) as engine:
        Base.metadata.create_all(engine)


async def drop_tables(db_url: str) -> None:
    async with create_async_engine(url=db_url) as engine:
        Base.metadata.drop_all(engine)

