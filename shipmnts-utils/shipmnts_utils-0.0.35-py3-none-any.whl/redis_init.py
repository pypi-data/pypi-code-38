import os

from redis import Redis


class RedisConfig:
    def __init__(self):
        self.client = Redis.from_url(os.getenv("REDIS_HOST", "redis://localhost"))
