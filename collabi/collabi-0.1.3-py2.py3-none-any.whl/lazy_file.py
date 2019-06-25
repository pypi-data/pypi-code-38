"""Provides R/W access to a file, but dealys the open call until the first operation (to help avoid
having too many file descriptors open at a time.
"""
import os

class LazyFile(object):
    def __init__(self, name, mode='r'):
        self.name = name
        self.mode = mode
        self.raw_file = None
        self.len = os.path.getsize(self.name)

    def __iter__(self):
        return self._ensure_open().iter()

    def next(self):
        return self._ensure_open().next()

    def read(self, *args):
        return self._ensure_open().read(*args)

    def write(self, *args):
        return self._ensure_open().write(*args)

    def close(self):
        if self.raw_file:
            self.raw_file.close()
            self.raw_file = None

    def _ensure_open(self):
        if not self.raw_file:
            self.raw_file = open(self.name, self.mode)
        return self.raw_file
