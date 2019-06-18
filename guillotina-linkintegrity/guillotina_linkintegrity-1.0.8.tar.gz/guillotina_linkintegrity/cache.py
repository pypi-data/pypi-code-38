import asyncio
import json
import logging

import aioredis
from guillotina import app_settings
from guillotina_rediscache import cache
from lru import LRU


logger = logging.getLogger(__name__)

_cache = None


class LinkIntegrityCache:

    _redis = _pool = None

    def __init__(self):
        self.settings = app_settings.get('linkintegrity', {
            'cache_size': 1500,
            'updates_channel': 'liinvalidate'
        })
        self.size = self.settings.get('cache_size', 1500)
        self.cache = LRU(self.size)

    async def initialize(self):
        if 'redis' not in app_settings:
            # redis not configured, we're not doing invalidations
            return
        while True:
            try:
                self._pool = await cache.get_redis_pool()
                self._redis = aioredis.Redis(self._pool)
                res = await self._redis.subscribe(
                    self.settings.get('updates_channel', 'liinvalidate'))
                ch = res[0]
                while (await ch.wait_message()):
                    keys = json.loads(await ch.get())
                    self.invalidate(*keys)
            except (asyncio.CancelledError, RuntimeError):
                # task cancelled, let it die
                return
            except Exception:
                logger.warn(
                    'Error subscribing to redis changes. Waiting before trying again',  # noqa
                    exc_info=True)
            await asyncio.sleep(5)

    def invalidate(self, *keys):
        for key in keys:
            if key in self.cache:
                del self.cache[key]

    async def publish_invalidation(self, *keys):
        self.invalidate(*keys)
        if self._redis is None:
            return
        try:
            await self._redis.publish(
                self.settings.get('updates_channel', 'liinvalidate'),
                json.dumps(keys))
        except RuntimeError:  # loop closing
            pass

    def get(self, key):
        try:
            return self.cache[key]
        except KeyError:
            pass

    def put(self, key, val):
        self.cache[key] = val


def get_cache():
    global _cache
    if _cache is None:
        _cache = LinkIntegrityCache()
        asyncio.ensure_future(_cache.initialize())
    return _cache


class cached_wrapper:

    def __init__(self, *keys, ob_key=True):
        self.keys = keys
        self.ob_key = ob_key

    def __call__(self, func):
        this = self

        async def _func(ob, *args, **kwargs):
            start_key = ob
            if this.ob_key:
                start_key = ob._p_oid
            key = '{}-{}'.format(
                start_key,
                '-'.join(this.keys))
            cache = get_cache()
            val = cache.get(key)
            if val is not None:
                return val
            val = await func(ob, *args, **kwargs)
            cache.put(key, val)
            return val

        return _func


class invalidate_wrapper:

    def __init__(self, *keysets):
        self.keysets = keysets

    def __call__(self, func):
        this = self

        async def _func(ob, *args, **kwargs):
            val = await func(ob, *args, **kwargs)
            cache = get_cache()
            keys = []
            for keyset in this.keysets:
                key = '{}-{}'.format(
                    ob._p_oid,
                    '-'.join(keyset))
                keys.append(key)
            await cache.publish_invalidation(*keys)
            return val

        return _func
