

class FileCache:
    def __init__(self, source, cache_dir):
        self.source = source
        self.cache_dir = cache_dir

    def __getattr__(self, item):
        return getattr(self.source, item)
