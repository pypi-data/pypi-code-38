# cache implementation that uses redis if configured
# redis would be required for some auth implementations
from guillotina_rediscache import cache
from guillotina import app_settings
import aioredis

CACHE_PREFIX = 'gauth-'


async def get(key):
    if 'redis' not in app_settings:
        store = cache.get_memory_cache()
        try:
            return store[CACHE_PREFIX + key]
        except KeyError:
            pass
    else:
        pool = await cache.get_redis_pool()
        redis = aioredis.Redis(pool)
        return await redis.get(CACHE_PREFIX + key)


async def put(key, value, expires=60 * 1):
    if 'redis' not in app_settings:
        store = cache.get_memory_cache()
        store[CACHE_PREFIX + key] = value
    else:
        pool = await cache.get_redis_pool()
        redis = aioredis.Redis(pool)
        await redis.set(CACHE_PREFIX + key, value, expire=expires)
