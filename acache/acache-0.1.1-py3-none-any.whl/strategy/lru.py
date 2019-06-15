import functools

from .basic import Basic


def lru(size):
    return functools.lru_cache(maxsize=size)


class LRU(Basic):

    def get(self, *args, **kwargs):
        key, value = super().get(*args, **kwargs)
        self.cache.move_to_end(key)
        return key, value
