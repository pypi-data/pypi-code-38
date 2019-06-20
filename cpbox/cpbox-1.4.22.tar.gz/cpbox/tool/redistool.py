import json
import redis

class Proxy():

    def __init__(self):
        self.redis = None

    def init_redis(self, from_url):
        pool = redis.ConnectionPool.from_url(from_url)
        self.redis = redis.Redis(connection_pool=pool)

proxy = Proxy()

def set_proxy(redis):
    proxy.redis = redis

def init_proxy(from_url):
    proxy.init_redis(from_url)

def flushall():
    # not use in prod
    proxy.redis.flushall()

def set(kv, value, ttl = 600):
    value = json.dumps(value)
    proxy.redis.set(kv, value, ttl)

def set_list(kv_list, ttl = 600):
    pipe = proxy.redis.pipeline()
    for (k, value) in kv_list.items():
        value = json.dumps(value)
        pipe.set(k, value, ttl)
    pipe.execute()

def delete_keys(keys):
    pipe = proxy.redis.pipeline()
    for key in keys:
        pipe.delete(key)
    pipe.execute()

def delete(k):
    proxy.redis.delete(k)

def get(key, fallback=None):
    value = proxy.redis.get(key)
    if value is None:
        return fallback
    return json.loads(value)

def incr(key, value = 1, ttl = 600):
    proxy.redis.incr(key, value)
    proxy.redis.expire(key, ttl)

def get_list(key_list):
    redis_value_list = proxy.redis.mget(key_list)
    return_value_list = {}
    for index, key in enumerate(key_list):
        if redis_value_list[index] is None:
            continue
        else:
            return_value_list[key] = json.loads(redis_value_list[index])
    return return_value_list

def delete_list(k_list):
    pipe = proxy.redis.pipeline()
    for k in k_list:
        pipe.delete(k)
    pipe.execute()
