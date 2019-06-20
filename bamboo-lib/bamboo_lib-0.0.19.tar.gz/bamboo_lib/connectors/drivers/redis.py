import redis

from bamboo_lib.connectors.models import BaseDriver


class RedisDriver(BaseDriver):
    TYPE = 'Redis Connection Driver'

    def __init__(self, **kwargs):
        super(RedisDriver, self).__init__(**kwargs)
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 6379)
        self.redis_client = redis.StrictRedis(host=host, port=port, db=1)

    def get_client(self):
        return self.redis_client
