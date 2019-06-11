from tornado.options import options, define
from .json_utils import dumps
import asyncio, aioredis
import logging
import redis


async def connect(redis_url: str = None):
    """
        Create a single connection to redis using
        option.redis_url if none is supplied
    """
    redis_url = options.redis_url if redis_url is None else redis_url
    loop = asyncio.get_event_loop()
    redis = await aioredis.create_redis(redis_url, loop=loop)
    logging.info("connect to redis: %s", redis_url)
    return redis


async def pool(redis_url: str = None):
    """
        Create a pool connection to redis using
        option.redis_url if none is supplied
    """
    redis_url = options.redis_url if redis_url is None else redis_url
    loop = asyncio.get_event_loop()
    pool = await aioredis.create_pool(redis_url, minsize=5, maxsize=10, loop=loop)
    logging.info("pool to redis: %s", redis_url)
    return pool
