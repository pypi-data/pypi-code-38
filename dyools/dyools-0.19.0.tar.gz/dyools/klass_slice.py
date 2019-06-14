from __future__ import (absolute_import, division, print_function, unicode_literals)


class Slice(object):

    def __init__(self, data, step, with_percent=False):
        assert step > 0, "Step should be up to 0"
        self.data = data
        self.step = step
        self.index = 0
        self.with_percent = with_percent
        self.length = len(data)

    def get(self):
        while True:
            res = self.data[self.index: self.index + self.step]
            if hasattr(res, 'size') and res.size == 0:
                break
            elif not hasattr(res, 'size') and not res:
                break
            yield res
            self.index += self.step


    @property
    def percent(self):
        if not self.length:
            res = 1
        else:
            res = self.index / self.length
        return 1 if res > 1 else res

    def __iter__(self):
        while True:
            res = self.data[self.index: self.index + self.step]
            if hasattr(res, 'size') and res.size == 0:
                break
            elif not hasattr(res, 'size') and not res:
                break
            self.index += self.step
            if self.with_percent:
                yield res, self.percent
            else:
                yield res

