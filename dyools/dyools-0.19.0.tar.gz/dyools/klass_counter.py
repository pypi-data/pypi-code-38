from __future__ import (absolute_import, division, print_function, unicode_literals)

import time

from .klass_print import Print


class Counter(object):

    def __init__(self, name=''):
        self.__stop = False
        self.__start = time.time()
        self.__name = name

    def restart(self):
        self.start()

    def start(self):
        self.__start = time.time()

    def stop(self):
        if not self.__stop:
            self.__stop = time.time()

    def resume(self):
        total = self._get_elapsed_time()['total']
        self.__start = time.time() - total
        self.__stop = False

    def _get_elapsed_time(self, r=True):
        if self.__stop:
            elapsed_time = self.__stop - self.__start
        else:
            elapsed_time = time.time() - self.__start
        res = dict(total=int(elapsed_time) if r else elapsed_time)
        h = int(elapsed_time / 3600)
        if h:
            elapsed_time -= h * 3600
        m = int(elapsed_time / 60)
        if m:
            elapsed_time -= m * 60
        res.update(dict(
            hours=h, minutes=m, seconds=int(elapsed_time) if r else elapsed_time
        ))
        return res

    def print(self, r=True, title=''):
        Print.info(self.to_str(r=r, title=title))

    def to_str(self, r=True, title=''):
        name = self.__name
        if title:
            title = '{}: '.format(title)
        if name:
            name = 'Counter {}: '.format(self.__name)
        fmt = '{name}{title}{hours:0>2}:{minutes:0>2}:{seconds:0>2}'
        return fmt.format(name=name, title=title, **self._get_elapsed_time(r=r))

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return self.to_str()
