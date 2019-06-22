import logging

from guillotina.component import get_utility
from guillotina.interfaces import ICacheUtility


logger = logging.getLogger(__name__)


class cached_wrapper:

    def __init__(self, *keys, ob_key=True):
        self.keys = keys
        self.ob_key = ob_key

    def __call__(self, func):
        this = self

        async def _func(ob, *args, **kwargs):
            start_key = ob
            if this.ob_key:
                start_key = ob.__uuid__
            key = '{}-{}'.format(
                start_key,
                '-'.join(this.keys))
            cache = get_utility(ICacheUtility)
            val = await cache.get(key)
            if val is not None:
                return val
            val = await func(ob, *args, **kwargs)
            await cache.set(key, val)
            return val

        return _func


class invalidate_wrapper:

    def __init__(self, *keysets):
        self.keysets = keysets

    def __call__(self, func):
        this = self

        async def _func(ob, *args, **kwargs):
            val = await func(ob, *args, **kwargs)
            cache = get_utility(ICacheUtility)
            keys = []
            for keyset in this.keysets:
                key = '{}-{}'.format(
                    ob.__uuid__,
                    '-'.join(keyset))
                keys.append(key)
            await cache.invalidate(data={
                'tid': None,
                'keys': keys
            })
            await cache.send_invalidation(keys)
            return val

        return _func
