# coding=utf-8
from __future__ import absolute_import, print_function

import collections
import functools
import time


def merge(*dicts):
    def _merge(result, item):
        result.update(item)
        return result

    return functools.reduce(_merge, dicts, {})


def count(iterable):
    if hasattr(iterable, "__len__"):
        return len(iterable)

    d = collections.deque(enumerate(iterable, 1), maxlen=1)
    return d[0][0] if d else 0


def shorten(value, maxlen=80):
    string = str(value)
    return string[: maxlen - 3] + "..." if len(string) > maxlen else string


class FrequenceTimeLimiter(object):
    def __init__(self, seconds):
        self.frequence = seconds
        self.time = time.time()

    def ifEnable(self):
        newTime = time.time()
        enable = self.frequence < newTime - self.time
        self.time = newTime if enable else self.time
        return enable


def onlyonce(func):
    setattr(func, "__onlyonce_called__", False)
    setattr(func, "__onlyonce_return__", None)

    @functools.wraps(func)
    def _dec(*args, **kwargs):
        if not getattr(func, "__onlyonce_called__", False):
            setattr(func, "__onlyonce_called__", True)
            setattr(func, "__onlyonce_return__", func(*args, **kwargs))
        return getattr(func, "__onlyonce_return__")

    return _dec
