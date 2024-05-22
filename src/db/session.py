import logging
from asyncio import current_task
from contextvars import ContextVar
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.core.settings import db_settings

log = logging.getLogger(__name__)


user_db = ContextVar[AsyncSession]("user_db")


@dataclass
class EnginePool:
    engine: AsyncEngine
    maker: async_sessionmaker


session_pools: dict[str, EnginePool] = {}


class SessionException(Exception):
    pass


async def set_session_pool() -> None:
    current_pool = await get_async_pool(db_settings.get_async_db_url())
    s.user_db = current_pool.maker()
    await s.user_db.connection(
        execution_options={"isolation_level": "AUTOCOMMIT"}
    )


async def get_async_pool(
    db_url: str = db_settings.get_async_db_url(),
) -> EnginePool:
    current = session_pools.get(db_url)
    if current is None:
        engine = _create_async_engine(db_url)
        await _check_connection(engine)
        maker = _create_async_sessionmaker(engine)
        current = EnginePool(engine=engine, maker=maker)
        session_pools[db_url] = current

    return current


def _create_async_engine(
    url: str, isolation_level: str = "AUTOCOMMIT"
) -> AsyncEngine:
    return create_async_engine(
        url=url,
        isolation_level=isolation_level,
        echo=db_settings.echo,
        future=True,
    )


async def _check_connection(engine: AsyncEngine) -> None:
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
            log.info("Connection success")
    except Exception as e:
        log.error("During check connection error occurred")
        raise SessionException(e)


def _create_async_sessionmaker(
    engine: AsyncEngine,
) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False, future=True)


async def _create_connection() -> async_scoped_session[AsyncSession]:
    current_pool = await get_async_pool(db_settings.get_async_db_url())
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    return ses


async def handle_session() -> AsyncGenerator[None, None]:
    AsyncScopedSession = await _create_connection()
    s.user_db = AsyncScopedSession()
    try:
        yield
        await AsyncScopedSession.commit()
    finally:
        await s.user_db.close()
        await AsyncScopedSession.remove()


async def close_dbs() -> None:
    for ses_pool in session_pools.values():
        await ses_pool.engine.dispose()
    log.info("Session pools closed")


async def pop_session() -> None:
    try:
        await s.user_db.commit()
    except Exception as exc:
        log.error("During session error occurred %s.Session ROLLBACK", exc)
        await s.user_db.rollback()
    finally:
        await s.user_db.close()


async def get_engine(
    db_url: str = db_settings.get_async_db_url(),
) -> AsyncEngine:
    current_pool = await get_async_pool(db_url)
    return current_pool.engine


class Session:
    @property
    def user_db(self) -> AsyncSession:
        return user_db.get()

    @user_db.setter
    def user_db(self, value: AsyncSession) -> None:
        user_db.set(value)


s = Session()
