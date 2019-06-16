import time
import collections

from .hash import MD5
from .base import Base


class Timed(MD5, Base):

    def __init__(self, timeout):
        super().__init__()
        self.cache = collections.OrderedDict()
        self.timeout = timeout

    def filter(self):
        now = time.time()
        for key, (value, updated) in self.cache.copy().items():
            if updated + self.timeout < now:
                del self.cache[key]
        return None

    def get(self, *args, **kwargs):
        now = time.time()
        key, (value, last) = super().get(*args, **kwargs)
        if last + self.timeout < now:
            raise KeyError('Key timed out.')
        return key, value

    def set(self, value, *args, **kwargs):
        now = time.time()
        key = super().set((value, now), *args, **kwargs)
        return key
