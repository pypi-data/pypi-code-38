#!/usr/bin/env python
import datetime

class InfiniteObject(object):
    """This mixin can be used to create "infinite" subclasses of numeric objects (eg datetime).
       Currently, this is only useful for comparison and does not support arithmetic operations like additon, subtraction etc.
       InfiniteObject can only be used with classes which are descended from "object" or classes which DO NOT implement the
       "rich comparison" operators (<,>,== etc) as these are the only cases in which comparisons behave symmetrically. That is
       these are the only cases in which the infinite subclass can be placed either side of the comparison operator and still
       evaluate as infinite.

       This is the class to use for normal numeric comparisons. Inheriting from int will result in incorrect results when
       comparing with floats."""

    def __init__(self, positive=True):
        self.__positive = positive

    def positive(self):
        return self.__positive

    def negative(self):
        return not self.__positive

    def __str__(self):
        return "Infinity" if self.__positive else "-Infinity"

    def __cmp__(self, other):
        if isinstance(other, InfiniteObject):
            if self.__positive == other.__positive:
                return 0
        if other == float("inf"):
            if self.__positive:
                return 0
        if other == float("-inf"):
            if not self.__positive:
                return 0
        if other is None and not self.__positive:
            return 0
        if self.__positive:
            return 1
        return -1

    def __lt__(self, other):
        return self.__cmp__(other) == -1

    def __le__(self, other):
        return self.__cmp__(other) < 1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __ge__(self, other):
        return self.__cmp__(other) > -1

    def __gt__(self, other):
        return self.__cmp__(other) == 1

class InfiniteDate(InfiniteObject, datetime.datetime):
    def __new__(cls, positive=True):
        if positive:
            return super(InfiniteDate,cls).__new__(cls,datetime.MAXYEAR,12,31,23,59,59,999999)
        return super(InfiniteDate,cls).__new__(cls,datetime.MINYEAR,1,1)

    year = property(fget = lambda self:InfiniteObject(self.positive()))

    def __str__(self):
        return "Infinite Date" if self.__positive else "-Infinite Date"