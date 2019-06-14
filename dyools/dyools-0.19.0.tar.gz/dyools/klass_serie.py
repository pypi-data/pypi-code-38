from __future__ import (absolute_import, division, print_function, unicode_literals)


class Serie(object):

    def __init__(self, arg):
        assert isinstance(arg, (list, Serie)), "The argument should be a list"
        if isinstance(arg, Serie):
            self.data = arg.data
        else:
            self.data = arg

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.data[item.start: item.stop: item.step]
        assert isinstance(item, int), "the index should be an integer"
        return self.data[item]

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x + other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k + v for k, v in zip(self.data, other.data)])
        return self

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x - other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k - v for k, v in zip(self.data, other.data)])
        return self

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return Serie([other - x for x in self.data])
        elif isinstance(other, Serie):
            return Serie([v - k for k, v in zip(self.data, other.data)])
        return self

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x * other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k * v for k, v in zip(self.data, other.data)])
        return self

    def __rmul__(self, other):
        return self.__mul__(other)

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x / other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k / v for k, v in zip(self.data, other.data)])
        return self

    def __rfloordiv__(self, other):
        if isinstance(other, (int, float)):
            return Serie([other / x for x in self.data])
        elif isinstance(other, Serie):
            return Serie([v / k for k, v in zip(self.data, other.data)])
        return self

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x / other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k / v for k, v in zip(self.data, other.data)])
        return self

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return Serie([other / x for x in self.data])
        elif isinstance(other, Serie):
            return Serie([v / k for k, v in zip(self.data, other.data)])
        return self

    def __div__(self, other):
        if isinstance(other, (int, float)):
            return Serie([x / other for x in self.data])
        elif isinstance(other, Serie):
            return Serie([k / v for k, v in zip(self.data, other.data)])
        return self

    def __rdiv__(self, other):
        if isinstance(other, (int, float)):
            return Serie([other / x for x in self.data])
        elif isinstance(other, Serie):
            return Serie([v / k for k, v in zip(self.data, other.data)])
        return self

    def __pow__(self, power, modulo=None):
        return Serie([pow(x, power) for x in self.data])

    def __str__(self):
        return "<Serie %s>" % self.data

    def __repr__(self):
        return "<Serie %s>" % self.data
