from collections import OrderedDict

from .hash import MD5
from .base import Base


class Basic(MD5, Base):

    def __init__(self, size):
        super().__init__()
        self.cache = OrderedDict()
        self.size = size

    def filter(self):
        if len(self.cache) > self.size:
            diff = len(self.cache) - self.size
            for (i, key) in enumerate([x for x in self.cache.keys()]):
                if i < diff:
                    del self.cache[key]
        return None
