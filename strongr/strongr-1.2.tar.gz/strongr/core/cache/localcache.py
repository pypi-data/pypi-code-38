import time

class LocalCache:
    _cache = {}
    _timeout = {}

    def _checkKey(self, key):
        if key in self._timeout and int(time.time()) > self._timeout[key]:
            del self._cache[key]
            del self._timeout[key]


    def set(self, key, value, timeout):
        self._cache[key] = value
        self._timeout[key] = int(time.time()) + timeout

    def get(self, key):
        self._checkKey(key)
        if key in self._cache:
            return self._cache[key]
        return None

    def delete(self, key):
        if self.exists(key):
            del self._timeout[key]
            del self._cache[key]

    def exists(self, key):
        self._checkKey(key)
        if key in self._cache:
            return True
        return False

