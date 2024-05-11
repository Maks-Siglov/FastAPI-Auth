import logging
from asyncio import current_task
from contextvars import ContextVar
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine
)

from core.settings import settings

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
    current_pool = await get_async_pool(settings.db.db_url)
    s.user_db = current_pool.maker()
    await s.user_db.connection(
        execution_options={"isolation_level": "AUTOCOMMIT"}
    )


async def _create_connection() -> async_scoped_session[AsyncSession]:
    current_pool = await get_async_pool(settings.db.db_url)
    ses = async_scoped_session(current_pool.maker, scopefunc=current_task)
    return ses


async def get_engine(db_url: str = settings.db.db_url) -> AsyncEngine:
    current_pool = await get_async_pool(db_url)
    return current_pool.engine


async def get_async_pool(db_url: str) -> EnginePool:
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
        echo=settings.db.echo,
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


async def handle_session():
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
    except Exception as e:
        await s.user_db.rollback()
        log.error(f"During session error occurred {str(e)}.Session ROLLBACK ")
    finally:
        await s.user_db.close()


class Session:
    @property
    def user_db(self) -> AsyncSession:
        return user_db.get()

    @user_db.setter
    def user_db(self, value: AsyncSession) -> None:
        user_db.set(value)


s = Session()
