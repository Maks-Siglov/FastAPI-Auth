from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from core.settings import settings


@dataclass
class EnginePool:
    engine: AsyncEngine
    maker: async_sessionmaker


session_pools: dict[str, EnginePool] = {}


class SessionException(Exception):
    pass


async def set_session_pool(db_url: str = settings.db.postgres_url) -> None:
    await get_async_pool(db_url)


async def get_session(db_url: str = settings.db.postgres_url) -> AsyncSession:
    current_pool = await get_async_pool(db_url)
    return current_pool.maker()


async def get_async_pool(db_url: str) -> EnginePool:
    current = session_pools.get(db_url)
    if current is None:
        engine = create_async_engine(url=db_url)
        await _check_connection(engine)
        maker = await _create_async_sessionmaker(engine)
        current = EnginePool(engine=engine, maker=maker)
        session_pools[db_url] = current

    return current


async def _check_connection(engine: AsyncEngine) -> None:
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as e:
        raise SessionException(e)


async def _create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False, future=True)


async def close_dbs() -> None:
    for ses_pool in session_pools.values():
        await ses_pool.engine.dispose()
