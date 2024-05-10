from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from core.settings import settings

user_db = ContextVar[AsyncSession]("user_db")


@dataclass
class EnginePool:
    engine: AsyncEngine
    maker: async_sessionmaker


session_pools: dict[str, EnginePool] = {}


class SessionException(Exception):
    pass


async def set_session_pool() -> None:
    current_pool = await get_async_pool(settings.db.db_url)
    s.user_db = current_pool.maker()
    await s.user_db.connection(
        execution_options={"isolation_level": "AUTOCOMMIT"}
    )


async def get_engine(db_url: str = settings.db.db_url) -> AsyncEngine:
    current_pool = await get_async_pool(db_url)
    return current_pool.engine


async def get_async_pool(
    db_url: str, db_settings: dict[str, Any] | None = None
) -> EnginePool:
    current = session_pools.get(db_url)
    if current is None:
        db_settings = {} if db_settings is None else db_settings
        engine = create_async_engine(url=db_url, **db_settings)
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


class Session:
    @property
    def user_db(self) -> AsyncSession:
        return user_db.get()

    @user_db.setter
    def user_db(self, value: AsyncSession) -> None:
        user_db.set(value)


s = Session()
