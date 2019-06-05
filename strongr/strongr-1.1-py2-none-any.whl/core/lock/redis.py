import time
import strongr.core.gateways
import logging

class RedisLock(object):
    def __init__(self, name, namespace, timeout):
        self._timeout = timeout
        self._name = name
        self._redis_namespace = namespace
        self._redis = strongr.core.gateways.Gateways.redis()
        self._logger = logging.getLogger('redislock')

    def exists(self):
        return self._redis.exists(self._redis_namespace + self._name)

    def __enter__(self):
        timeout_after = int(time.time()) + self._timeout
        self._logger.debug('Attempting to acquire lock {}'.format(self._name))
        while not self._redis.setnx(self._redis_namespace + self._name, True) and int(time.time()) > timeout_after:
            time.sleep(.1)
        else:
            self._logger.debug('Lock acquired on {}'.format(self._name))
            return self

        self._logger.debug('Failed to acquire lock on {}'.format(self._name))
        raise IOError('Could not aquire lock for {}'.format(self._name))

    def __exit__(self, type, value, traceback):
        self._logger.debug('Releasing lock on {}'.format(self._name))
        self._redis.delete(self._redis_namespace + self._name)
