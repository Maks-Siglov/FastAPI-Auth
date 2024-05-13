from redis.asyncio import Redis

from core.settings import settings


async def get_redis_client():
    redis_client = Redis(host=settings.redis.host, port=settings.redis.port)
    yield redis_client
    await redis_client.aclose()
