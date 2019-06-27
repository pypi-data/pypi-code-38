from django.http import HttpResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from typing import Optional, Union, NewType, NamedTuple, Any
import redis
import pickle
import hashlib
from functools import wraps
from CTUtil.types import HTTPResponseStates
from django.conf import settings
from typing import NamedTuple
import time
import json
from datetime import datetime

MD5Str = NewType('MD5Str', str)
expire: int = 60 * 60 * 24


class RedisObject(NamedTuple):
    expire: float
    value: Any

    @property
    def is_expire(self):
        return time.time() > self.expire

    def __str__(self):
        return json.dumps({
            'expire': datetime.fromtimestamp(self.expire).isoformat(),
            'is_expire': self.is_expire,
        }, ensure_ascii=False)


try:
    config: dict = settings.Redis.setdefault('default', {})
except:
    config = {}

RedisPool: redis.ConnectionPool = redis.ConnectionPool(
    host=config.setdefault('host', 'localhost'), port=config.setdefault('port', 6379))

_using: redis.Redis = redis.Redis(connection_pool=RedisPool)
_table: str = 'default'


def get_using_config(key: str) -> redis.Redis:
    try:
        config: dict = settings.Redis.setdefault(key, {})
        return redis.Redis(
            host=config.setdefault('host', 'localhost'),
            port=config.setdefault('port', 6379)
        )
    except:
        raise TypeError(f'{key} not exists')


class Cache:
    def __init__(self, using: Optional[str]=None, table: Optional[str]=_table):
        self.using = _using if not using else get_using_config(using)
        self.table: str = table

    def add(self, key: str, value: Any, expire: Optional[int]=None):
        key: MD5Str = self.get_md5_key(key)
        if not expire:
            expire: int = int(config.setdefault('expire', 60 * 60 * 24))
        o: RedisObject = RedisObject(expire=time.time() + expire, value=value)
        v: bytes = pickle.dumps(o)
        self.using.hset(self.table, key, v)

    def delete(self, key: str):
        key: MD5Str = self.get_md5_key(key)
        self.using.hdel(self.table, key)

    def update(self, key: str, value: Any, expire: Optional[int]=None):
        return self.add(key, value, expire)

    def clear(self):
            self.using.delete(self.table)

    def get(self, key: str) -> Any:
        key: MD5Str = self.get_md5_key(key)
        v: bytes = self.using.hget(self.table, key)
        if not v:
            return None
        o: RedisObject = pickle.loads(v)
        if o.is_expire:
            self.using.hdel(self.table, key)
            return None
        else:
            return o.value

    @classmethod
    def get_md5_key(cls, key: str) -> MD5Str:
        return hashlib.md5(key.encode()).hexdigest()


class DjangoHttpMixin:

    @classmethod
    def make_request_key(cls, request: HttpRequest) -> str:
        base: str = request.path + json.dumps(request.POST.copy())
        try:
            d: str = json.dumps(json.loads(request.body), ensure_ascii=False)
            return base + d
        except:
            return base

    @classmethod
    def cache_response(cls, cache: Optional[Cache]=None, expire: Optional[int]=None):
        def _cached_response(func):
            @wraps(func)
            def _set_caches(*args, **kwargs):
                request: HttpRequest = args[-1]
                resp: HttpResponse = func(*args, **kwargs)
                try:
                    if resp.status_code == HTTPResponseStates.SUCCESS:
                        c = cache if cache else Cache()
                        key: str = cls.make_request_key(request)
                        c.add(key, pickle.dumps(resp), expire=expire)
                except:
                    pass
                return resp
            return _set_caches
        return _cached_response


class CachesMiddleware(MiddlewareMixin):

    Cache: Cache = Cache()

    def process_request(self, request):
        try:
            key: str = DjangoHttpMixin.make_request_key(request)
            value = self.Cache.get(key)
            if value:
                return pickle.loads(value)
        except:
            return
