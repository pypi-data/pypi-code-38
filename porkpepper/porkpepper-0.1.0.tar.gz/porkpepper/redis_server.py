from typing import *
from .result import *
from .redis_server_base import RedisServerBase


class RedisServer(RedisServerBase):
    async def get(self, key) -> Result[bytes]:
        return Result(NotImplementedError())

    async def getset(self, key, value) -> Result:
        return Result(NotImplementedError())

    async def set(self, key, value) -> Result:
        return Result(NotImplementedError())

    def hmget(self, key, *fields):
        return Result(NotImplementedError())

    def hmset(self, key, **fields):
        return Result(NotImplementedError())

    async def key_type(self, key):
        return Result(NotImplementedError())

    async def ping(self):
        return Result(NotImplementedError())

    async def info(self):
        return Result(NotImplementedError())

    def subscribe(self, channle):
        return Result(NotImplementedError())

    async def auth(self, password) -> Result[bool]:
        """
        如果是连接状态问题或者非密码对错的情况下，这里应返回 Result[Exception]
        判断密码正确时，应返回 Result[bool]
        :param password:
        :return:
        """
        return Result(NotImplementedError())

    async def ttl(self, key):
        return Result(NotImplementedError())

    async def scan(self, pattern):
        return Result(NotImplementedError())

    async def dbsize(self):
        return Result(NotImplementedError())

    async def select(self, db):
        return Result(NotImplementedError())

    async def config(self, get_set, field, value=None):
        return Result(NotImplementedError())


__all__ = ["RedisServer", ]
