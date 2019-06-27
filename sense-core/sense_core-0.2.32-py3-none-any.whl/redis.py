import redis
from .config import config

__client_map = {}


def get_redis_client(db=0, label='redis'):
    global __client_map
    label1 = label + str(db)
    if label1 not in __client_map:
        redis_host = config(label, 'host')
        redis_port = config(label, 'port')
        redis_pass = config(label, 'pass', '')
        if redis_pass == '':
            redis_pass = config(label, 'password', '')
        if len(redis_pass) == 0:
            redis_pass = None
        redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, password=redis_pass, db=db)
        __client_map[label1] = redis_pool
    clients = redis.Redis(connection_pool=__client_map[label1])
    return clients
