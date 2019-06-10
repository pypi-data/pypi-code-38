# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan.arguments import Bool, Int, String
from suanpan.mq.redis import RedisMQ
from suanpan.proxy import Proxy


class MQProxy(Proxy):
    MAPPING = {"redis": RedisMQ}
    DEFAULT_ARGUMENTS = [String("mq-type")]
    REDIS_ARGUMENTS = [
        String("mq-redis-host", default="localhost"),
        Int("mq-redis-port", default=6379),
        Bool("mq-redis-realtime", default=False),
        Bool("mq-redis-keepalive", default=True),
        # Int("mq-redis-keepalive-idle", default=120),
        # Int("mq-redis-keepalive-cnt", default=2),
        # Int("mq-redis-keepalive-intvl", default=30),
    ]
    ARGUMENTS = list(itertools.chain(DEFAULT_ARGUMENTS, REDIS_ARGUMENTS))


mq = MQProxy()
