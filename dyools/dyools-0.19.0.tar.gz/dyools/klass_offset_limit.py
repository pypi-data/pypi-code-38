from __future__ import (absolute_import, division, print_function, unicode_literals)


class OffsetLimit(object):

    def __init__(self, offset, limit, length=None):
        self.offset = offset
        self.limit = limit
        self.has_length = length is not None
        self.length = length or 0

    def __iter__(self):
        while True:
            if self.has_length :
                if self.length <= 0:
                    break
                if self.length <= self.limit:
                    self.limit = self.length
            yield [self.offset, self.limit]
            self.length -= self.limit
            self.offset += self.limit

