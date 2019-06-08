from collections import OrderedDict
from threading import Lock


class SafeOrderedDict:
    def __init__(self):
        self._mutex = Lock()
        self._map = OrderedDict() 
    
    def __setitem__(self, key, value):
        with self._mutex:
            self._map[key] = value
    
    def __getitem__(self, key):
        with self._mutex:
            return self._map[key]

    def __contains__(self, key):
        with self._mutex:
            return key in self._map
    
    def __len__(self):
        with self._mutex:
            return len(self._map)

    def __str__(self):
        with self._mutex:
            return str(self._map)
