from . import AbstractKeyValueStore

import time

class InMemoryStore(AbstractKeyValueStore):
    _store = {}
    _lastAccesed = {}

    def _logAccess(self, key):
        self._lastAccesed[key] = int(time.time())

    def _logRemove(self, key):
        self._lastAccesed.pop(key, None)

    def get(self, key):
        if key in self._store:
            self._logAccess(key)
            return self._store[key]
        return None

    def set(self, key, value):
        self._logAccess(key)
        self._store[key] = value

    def getAll(self):
        for key in self._store.keys():
            self._logAccess(key)
        return self._store.keys()

    def rem(self, key):
        self._logRemove(key)
        self._store.pop(key, None)

    def clear(self):
        self._logAccess = {}
        self._store = {}

    def append(self, key, value):
        if key in self._store:
            self._logAccess(key)
            self._store = self._store + value

    def exists(self, key):
        if key in self._store:
            return True
        return False
