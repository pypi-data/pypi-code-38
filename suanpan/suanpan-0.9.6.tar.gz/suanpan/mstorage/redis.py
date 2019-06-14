# coding=utf-8
from __future__ import absolute_import, print_function

import redis


class RedisMStorage(object):
    def __init__(
        self,  # pylint: disable=unused-argument
        redisHost="localhost",
        redisPort=6379,
        redisKeepalive=False,
        # redisKeepaliveIDLE=120,
        # redisKeepaliveCNT=2,
        # redisKeepaliveINTVL=30,
        redisDefaultExpire=30,
        options=None,
        client=None,
        **kwargs
    ):
        self.options = options or {}
        self.options.update(
            host=redisHost,
            port=redisPort,
            keepalive=redisKeepalive,
            # keepidle=redisKeepaliveIDLE,
            # keepcnt=redisKeepaliveCNT,
            # keepintvl=redisKeepaliveINTVL,
        )
        if client and not isinstance(client, redis.Redis):
            raise Exception("Invalid client: {}".format(client))
        self.client = client or redis.Redis(
            host=self.options["host"],
            port=self.options["port"],
            socket_keepalive=self.options["keepalive"],
            # socket_keepalive_options={
            #     socket.TCP_KEEPIDLE: self.options["keepidle"],
            #     socket.TCP_KEEPCNT: self.options["keepcnt"],
            #     socket.TCP_KEEPINTVL: self.options["keepintvl"],
            # },
        )
        self.defaultExpire = redisDefaultExpire

    def type(self, name):
        return self.client.type(name)

    def exists(self, *names):
        return self.client.exists(*names)

    def expire(self, name, expire):
        return self.client.expire(name, expire)

    def delete(self, *names):
        return self.client.delete(*names)

    def get(self, name):
        return self._kget(name)

    def set(self, name, value, *args, **kwargs):
        kwargs.setdefault("expire", self.defaultExpire)
        return self._kset(name, value, *args, **kwargs)

    def mget(self, name):
        return self._hmgetall(name)

    def mset(self, name, mapping, expire=None):
        result = self._hmset(name, mapping)
        expire = expire or self.defaultExpire
        self.expire(name, expire)
        return result

    def lpush(self, name, *values, **kwargs):
        first = kwargs.pop("first", False)
        _push = self._lpush if first else self._rpush
        return _push(name, *values)

    def lpop(self, name, count=1, first=True):
        return (
            self._lpopmore(name, count, first=first)
            if count > 1
            else self._lpopone(name, first=first)
        )

    def llen(self, name):
        return self._llen(name)

    def lrange(self, name, start, end):
        return self._lrange(name, start, end)

    def ltrim(self, name, start, end):
        return self._ltrim(name, start, end)

    def _lpopone(self, name, first=True):
        _pop = self._lpop if first else self._rpop
        return _pop(name)

    def _lpopmore(self, name, count, first=True):
        length = self._llen(name)
        if not length:
            return []

        count = min(count, length)
        poprange, trimrange = (
            ((0, count - 1), (count, -1))
            if first
            else ((-count, -1), (0, length - count - 1))
        )
        values = self._lrange(name, *poprange)
        self._ltrim(name, *trimrange)
        return values

    def _kget(self, name):
        return self.client.get(name)

    def _kset(self, name, value, expire=None):
        return self.client.set(name, value, ex=expire)

    def _hmget(self, name, keys=None):
        return self._hmgetfields(name, keys) if keys else self._hmgetall(name)

    def _hmgetall(self, name):
        return self._decode_keys(self.client.hgetall(name))

    def _hmgetfields(self, name, keys):
        return self._decode_keys(dict(zip(keys, self.client.hmget(name, keys))))

    def _hmset(self, name, mapping):
        return self.client.hmset(name, mapping)

    def _lset(self, name, index, value):
        return self.client.lset(name, index, value)

    def _llen(self, name):
        return self.client.llen(name)

    def _lpop(self, name):
        return self.client.lpop(name)

    def _rpop(self, name):
        return self.client.rpop(name)

    def _lpush(self, name, *values):
        return self.client.lpush(name, *values)

    def _rpush(self, name, *values):
        return self.client.rpush(name, *values)

    def _lrange(self, name, start, end):
        return self.client.lrange(name, start, end)

    def _ltrim(self, name, start, end):
        return self.client.ltrim(name, start, end)

    def _decode_keys(self, mapping):
        return {k.decode(): v for k, v in mapping.items()}
