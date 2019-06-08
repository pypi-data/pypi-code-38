from threading import Lock

class SafeList:
    def __init__(self):
        self._list = list()
        self._mutex = Lock()
    
    def __setitem__(self, idx, value):
        with self._mutex:
            self._list[idx] = value
    
    def __getitem__(self, idx):
        with self._mutex:
            return self._list[idx]
    
    def __len__(self):
        with self._mutex:
            return len(self._list)

    def __contains__(self, value):
        with self._mutex:
            return value in self._list
    
    def append(self, value):
        with self._mutex:
            self._list.append(value)

    def extend(self, value):
        with self._mutex:
            self._list.extend(value)
    
    def remove(self, value):
        with self._mutex:
            self._list.remove(value)
    
    def pop(self, idx):
        with self._mutex:
            self._list.pop(idx)
    
    def clear(self):
        with self._mutex:
            self._list.clear()
    
    def index(self, value, start, end):
        with self._mutex:
            return self._list.index(value, start=start, end=end)
    
    def count(self, value):
        with self._mutex:
            return self._list.count(value)
    
    def sort(self, key=None, reverse=False):
        with self._mutex:
            self._list.sort(key=key, reverse=reverse)
        
    def reverse(self):
        with self._mutex:
            self._list.reverse()
    
    def copy(self):
        with self._mutex:
            return self._list.copy() 
    

