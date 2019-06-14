from __future__ import (absolute_import, division, print_function, unicode_literals)


class Convert(object):
    def __init__(self, arg={}):
        self.data = arg

    @classmethod
    def data(self, amount, origin, to, r=None):
        units = ["B", "K", "M", "G", "T", "P", "E", "Z", "Y"]
        origin, to = origin.strip().upper()[0], to.strip().upper()[0]
        assert origin in units and to in units, 'The units are not mapped'
        i = 0
        while origin != units[i]:
            amount *= 2 ** 10
            i += 1
        i = 0
        while to != units[i]:
            amount /= 2 ** 10
            i += 1
        if r is not None:
            amount = round(amount, r)
        return amount

    @classmethod
    def time(self, tt, origin='S', to='S', r=None):
        units = ["MS", "S", "M", "H"]
        origin, to = origin.strip().upper(), to.strip().upper()
        assert origin in units and to in units, 'The units are not mapped'
        i = 0
        while origin != units[i]:
            tt *= 60.0 if i != 0 else 1000.0
            i += 1
        i = 0
        while to != units[i]:
            tt /= 60.0 if i != 0.0 else 1000.0
            i += 1
        if r is not None:
            tt = round(tt, r)
        return tt
