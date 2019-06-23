import jsoncfg

import redis
from swissarmykit.lib.core import Singleton

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py


@Singleton
class RedisConnect():

    def __init__(self, other_config=None):
        config = jsoncfg.load_config(appConfig.ROOT_DIR + '/config.json')[other_config if other_config else 'redis']
        self.redis = redis.Redis(host=config['host'].value, port=config['port'].value, db=config['db'].value)

    def get_restrict(self, other_config=None):
        config = jsoncfg.load_config(appConfig.ROOT_DIR + '/config.json')[other_config if other_config else 'redis']
        return redis.StrictRedis(host=config['host'].value, port=config['port'].value, db=config['db'].value)

    def get(self, key):
        return self.redis.get(key)

    def set(self, key, value, ex=3600):
        self.redis.set(key, value, ex=ex)

    def delete(self, key):
        self.redis.delete(key)

    def delete_namespace(self, ns):
       prefix = '%s:*' % ns
       for key in self.redis.scan_iter(prefix):
           self.delete(key)

