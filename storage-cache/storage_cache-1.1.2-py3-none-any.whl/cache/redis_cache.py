"""
:author: Henley Kuang
:since: 06/13/2019
"""
import logging

from retry_redis import Redis

from storage_cache.util.config import (
    DEFAULT_LOG_FORMAT_STRING,
    DELIMITER,
)

LOGGER = logging.getLogger(__name__)


class StorageRedisCache(object):

    redis_db = None
    key_format = None

    def __init__(self, redis_host, redis_port, redis_password, redis_db, key_format):
        self.key_format = key_format
        self.redis_client = Redis(host=redis_host,
                                  port=redis_port,
                                  password=redis_password,
                                  db=redis_db,
                                  decode_responses=True)

    def get_key_name(self, primary_keys):
        primary_keys_str = DELIMITER.join(primary_keys)
        key_name = "%s%s%s" % (self.key_format, DELIMITER, primary_keys_str)
        return key_name

    def set_cache_hash(self, primary_keys, secondary_keys, meta_data, expiration_timeout):
        key_name = self.get_key_name(primary_keys)
        field_key = DELIMITER.join(secondary_keys)
        # Hash set and set expiration pipeline
        rp = self.redis_client.pipeline()
        rp.hset(key_name, field_key, meta_data)
        rp.expire(key_name, expiration_timeout)
        rp.execute()
        return ('hset', key_name, field_key, meta_data)

    def get_cache_hash(self, primary_keys, secondary_keys):
        key_name = self.get_key_name(primary_keys)
        field_key = DELIMITER.join(secondary_keys)
        meta_data = self.redis_client.hget(key_name, field_key)
        return meta_data

    def set_cache_str(self, primary_keys, meta_data, expiration_timeout):
        key_name = self.get_key_name(primary_keys)
        self.redis_client.setex(key_name, expiration_timeout, meta_data)
        return ('set', key_name, meta_data)

    def get_cache_str(self, primary_keys):
        key_name = self.get_key_name(primary_keys)
        meta_data = self.redis_client.get(key_name)
        return meta_data
