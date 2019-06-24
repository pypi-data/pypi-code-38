""" Stop watch """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
from tfmodelserver.utils import dict_map


class _StopWatch:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def interval(self):
        return self._interval

    def __enter__(self):
        self._t1 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._t2 = time.time()
        self._interval = self._t2 - self._t1

        return False


class Timer:
    def __init__(self):
        self._stop_watches = {}

    def start(self, name: str) -> _StopWatch:
        stop_watch = _StopWatch(name)
        self._stop_watches.update({name: stop_watch})

        return stop_watch

    @property
    def __dict__(self):
        return dict_map(lambda k, v: (k, v.interval), self._stop_watches)
