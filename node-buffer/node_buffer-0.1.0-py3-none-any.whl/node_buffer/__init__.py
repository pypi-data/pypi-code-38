# -*- coding: utf-8 -*-

"""
                                node_buffer:
A minor rewrite of the NodeJS Buffer Library for efficient memory management
"""

__author__ = "Miraculous Owonubi"
__copyright__ = "Copyright 2019"
__credits__ = ["Miraculous Owonubi"]
__license__ = "Apache-2.0"
__version__ = "0.1.0"
__maintainer__ = "Miraculous Owonubi"
__email__ = "omiraculous@gmail.com"
__status__ = "Development"


class Buffer():
    def __repr__(self):
        tflow = 35
        return '<Buffer %s%s>' % (' '.join(self.hexList(tflow)), '' if len(self) <= tflow else ' ... %s more bytes' % (len(self) - tflow))

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.__bytearray)

    def __getitem__(self, index):
        return self.__bytearray[index]

    def size(self):
        return len(self) - self.__bytearray.count(0)

    def tolist(self):
        return list(self.__bytearray)

    def hexList(self, n):
        return [hex(v).split('x')[1].zfill(2) for v in self.tolist()[:n]]

    def toString(self, encoding='utf8', start=0, end=None):
        block = self.__bytearray[start:end]
        return block.hex() if encoding == "hex" else block.decode(encoding)

    def includes(self, value, offset=0, encoding='utf8'):
        try:
            return bool(self.indexOf(value, offset, encoding))
        except:
            return False

    def indexOf(self, value, offset=0, encoding='utf8'):
        block = self.__bytearray[offset:]
        return block.index(bytes(value, encoding))

    def fill(self, value, offset=0, end=None, encoding=None):
        import math
        total = end or len(self)
        content = Buffer.__settle(value)
        count = total - offset
        remainsOne = bool(count % len(content))
        return self.write((content*math.ceil(count / len(content)))[:-1 if remainsOne else None], offset, total)

    def copy(self, target, targetStart=0, sourceStart=0, sourceEnd=None):
        return target.write(self[sourceStart:sourceEnd or len(self)], targetStart)

    def write(self, val, offset=0, length=None, encoding='utf8'):
        stack = Buffer.__settle(val)
        index = offset
        total = length or min(len(self), len(stack))
        while index < total:
            self.__bytearray[index] = stack[index - offset]
            index += 1
        return self

    def clear(self, start=0, end=None):
        return self.fill(0, start, end)

    @classmethod
    def alloc(cls, n, fill=None, encoding='utf8'):
        res = cls()
        res.__bytearray = bytearray(n)
        if fill:
            res.fill(fill, encoding=encoding)
        return res

    @classmethod
    def new(cls, val, encoding='utf8', length=0):
        if type(encoding) is int:
            [encoding, length] = [length if type(
                length) == str else 'utf8', encoding]
        content = cls.__settle(val, encoding)
        length = length or len(content)
        buf = cls.alloc(length)
        return buf.write(content, 0, length, encoding)

    @classmethod
    def __settle(cls, val, encoding='utf8'):
        if isinstance(val, cls):
            return val.tolist()
        elif isinstance(val, int):
            return [val]
        elif isinstance(val, str):
            return bytes.fromhex(val) if encoding == 'hex' else bytes(val, encoding)
        elif isinstance(val, (list, tuple, bytes, bytearray)):
            return val
        else:
            er = "Expected value input to be within the following: 'Buffer' or 'int' or 'str' or 'list' or 'bytes' or 'bytearray'"
            raise TypeError(er)
