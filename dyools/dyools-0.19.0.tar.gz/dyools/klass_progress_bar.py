from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
from threading import Thread


def clean_to_right(txt):
    if txt:
        txt = txt.rstrip()
        if txt:
            txt = ' ' + txt
    return txt


def clean_to_left(txt):
    if txt:
        txt = txt.lstrip()
        if txt:
            txt += ' '
    return txt


class ProgressBar(object):

    def __init__(self, percent=0.0, prefix='', suffix=''):
        self.__percent = percent
        self.__prefix = clean_to_left(prefix)
        self.__suffix = clean_to_right(suffix)
        self.__stop = False

    def update(self, percent=None, prefix=None, suffix=None):
        if percent is not None:
            self.__percent = percent
        if prefix is not None:
            self.__prefix = clean_to_left(prefix)
        if suffix is not None:
            self.__suffix = clean_to_right(suffix)

    @property
    def percent(self):
        return self.__percent

    @percent.setter
    def percent(self, value):
        self.__percent = value

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, value):
        self.__prefix = clean_to_left(value)

    @property
    def suffix(self):
        return self.__suffix

    @suffix.setter
    def suffix(self, value):
        self.__suffix = clean_to_right(value)

    def start(self):
        def __start():
            while True:
                print('\r{}[{} %]{}'.format(self.prefix, int(self.percent * 100), self.suffix), end='')
                if self.__stop:
                    break
                time.sleep(0.2)

        t = Thread(target=__start)
        t.start()

    def stop(self):
        self.__stop = True
