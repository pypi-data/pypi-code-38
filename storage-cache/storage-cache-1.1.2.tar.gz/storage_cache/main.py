"""
:author: Henley Kuang
:since: 06/13/2019
"""
from storage_cache.cache.redis_cache import StorageRedisCache
from storage_cache.types import REDIS_STORAGE_CACHE
from storage_cache.excepts import CacheClassDoesNotExistException

CACHE_TYPE_CLASS = {
    REDIS_STORAGE_CACHE: StorageRedisCache,
}


class StorageCacheFactory(object):
    @staticmethod
    def factory(cache_type):
        try:
            return CACHE_TYPE_CLASS[cache_type]
        except KeyError as e:
            raise CacheClassDoesNotExistException(
                "Invalid value passed into StorageCacheFactory: %s" % cache_type)
