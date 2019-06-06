# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan.arguments import Bool, Int, String
from suanpan.mstorage.redis import RedisMStorage
from suanpan.proxy import Proxy


class MStorageProxy(Proxy):
    MAPPING = {"redis": RedisMStorage}
    DEFAULT_ARGUMENTS = [String("mstorage-type")]
    REDIS_ARGUMENTS = [
        String("mstorage-redis-host", default="localhost"),
        Int("mstorage-redis-port", default=6379),
        Bool("mstorage-redis-keepalive", default=True),
        Int("mstorage-redis-keepalive-idle", default=120),
        Int("mstorage-redis-keepalive-cnt", default=2),
        Int("mstorage-redis-keepalive-intvl", default=30),
        Int("mstorage-redis-expire", default=30),
    ]
    ARGUMENTS = list(itertools.chain(DEFAULT_ARGUMENTS, REDIS_ARGUMENTS))


mstorage = MStorageProxy()
