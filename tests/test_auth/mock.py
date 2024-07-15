class MockRedisClient:
    def __init__(self):
        self.store = {}

    async def set(self, name, value, ex=None):
        self.store[name] = value

    async def get(self, name):
        return self.store.get(name)


mock_redis_client = MockRedisClient()


async def get_mock_redis_client():
    return mock_redis_client
