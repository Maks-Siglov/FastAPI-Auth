from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)


@dataclass
class EnginePool:
    engine: AsyncEngine
    maker: async_sessionmaker


session_pool: dict[str, EnginePool] = {}


class SessionException(Exception):
    pass


async def get_async_pool(db_url: str) -> EnginePool:
    current = session_pool.get(db_url)
    if current is None:
        engine = create_async_engine(url=db_url)
        await _check_connection(engine)
        maker = await _create_async_sessionmaker(engine)
        current = EnginePool(engine=engine, maker=maker)
        session_pool[db_url] = current

    return current


async def _check_connection(engine: AsyncEngine) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(select(1))
    except Exception as e:
        raise SessionException(e)


async def _create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False, future=True)
