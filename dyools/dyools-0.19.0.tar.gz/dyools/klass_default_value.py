from __future__ import (absolute_import, division, print_function, unicode_literals)


class DefaultValue(object):

    def __init__(self, obj, defaults={False: '', None: ''}, types=()):
        self.__obj = obj
        self.__defaults = defaults
        self.__types = tuple(types)

    def __getitem__(self, item):
        res = self.__obj[item]
        for v, dv in self.__defaults.items():
            if res is v:
                return dv
        if self.__types:
            if isinstance(res, self.__types):
                return DefaultValue(res)
        return res

    def __getattr__(self, item):
        res = getattr(self.__obj, item)
        for v, dv in self.__defaults.items():
            if res is v:
                return dv
        if self.__types:
            if isinstance(res, self.__types):
                return DefaultValue(res)
        return res
