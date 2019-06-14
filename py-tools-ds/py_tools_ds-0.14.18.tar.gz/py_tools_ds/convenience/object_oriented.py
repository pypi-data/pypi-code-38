# -*- coding: utf-8 -*-
__author__ = 'Daniel Scheffler'


def alias_property(key):
    return property(
        lambda self: getattr(self, key),
        lambda self, val: setattr(self, key, val),
        lambda self: delattr(self, key))
