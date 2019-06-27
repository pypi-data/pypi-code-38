# -*- coding: utf-8 -*-

import abc


class TriggerException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Trigger(object):
    __metaclass__ = abc.ABCMeta

    @staticmethod
    def help():
        return ''

    @abc.abstractmethod
    def run(self, event):
        return '', True
