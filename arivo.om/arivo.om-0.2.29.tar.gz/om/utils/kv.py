import json

from redis import Redis


class RedisKV(object):
    def __init__(self, config):
        self.db = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB,
                        socket_timeout=5, socket_connect_timeout=5, decode_responses=True)

    def get(self, k):
        res = self.db.hget("kv", k)
        if not res:
            return dict()
        try:
            return json.loads(res)
        except:
            return dict()

    def set(self, k, v):
        v = json.dumps(v)
        self.db.hset("kv", k, v)

    def ls(self):
        return self.db.hkeys("kv")

    def delete(self, k):
        self.db.hdel("kv", k)
