CACHE_TYPE_EMPTY = 1
CACHE_TYPE_SIMPLE = 2

class EmptyCache():

    def __init__(self):
        self.type = CACHE_TYPE_EMPTY

    def has(self, key):
        return False

    def set(self, key, value, expire = 600):
        pass

    def get(self, key):
        return False

    def delete(self, key):
        pass

class SimpleCache():

    def __init__(self):
        self.type = CACHE_TYPE_SIMPLE
        self.cache_data = {}

    def has(self, key):
        return key in self.cache_data

    def set(self, key, value, expire = 600):
        self.cache_data[key] = value

    def get(self, key):
        if key in cache_data:
            return cache_data[key]
        return False

    def delete(self, key):
        if key in cache_data:
            del cache_data[key]

empty_cache = EmptyCache()
simple_cache = SimpleCache()

cache_proxy = empty_cache
def set_cach_proxy(proxy):
    cache_proxy = proxy

def has(key):
    return cache_proxy.has(key)

def set(key, value, expire = 600):
    return cache_proxy.set(key, value, expire)

def get(key):
    return cache_proxy.get(key)

def delete(key):
    return cache_proxy.delete(key)
