# -*- coding: utf-8 -*-
"""
Used to space/separate choices group
"""


class Separator(object):
    line = '-' * 15

    def __init__(self, line=None):
        if line:
            self.line = line

    def __str__(self):
        return self.line

    def __eq__(self, other):
        if isinstance(other, Separator):
            return self.line == other.line

        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result

        return not result
