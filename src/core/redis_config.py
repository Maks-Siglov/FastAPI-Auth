import redis

from core.settings import settings

redis_client = redis.Redis(host=settings.redis.host, port=settings.redis.port)


async def get_redis() -> redis.Redis:
    yield redis_client
