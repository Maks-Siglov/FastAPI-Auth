from redis.asyncio import Redis

from core.settings import redis_settings


async def get_redis_client():
    redis_client = Redis(host=redis_settings.host, port=redis_settings.port)
    yield redis_client
    await redis_client.aclose()
