from redis.asyncio import Redis

from src.settings import RedisSettings


async def get_redis_client():
    redis_client = Redis(host=RedisSettings.host, port=RedisSettings.port)
    yield redis_client
    await redis_client.aclose()
