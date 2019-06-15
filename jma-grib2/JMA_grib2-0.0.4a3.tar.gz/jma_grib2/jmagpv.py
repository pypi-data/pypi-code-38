from datetime import datetime
import numpy as np

class JMAGPV(object):
    def __init__(self, file):
        self.f = file
        self.read()

    def read(self):
        pass

    def r(self, start, end=-1):
        assert self.f != None
        if end == -1:
            end = start
        return self.f.read(end-start+1)

    def r_int(self, start, end=-1, byte=None):
        return int.from_bytes(self.r(start, end) if byte == None else byte, 'big')

    def r_str(self, start, end=-1):
        return self.r(start, end).decode()

    def r_dt(self, start):
        return datetime(self.r_int(start, start+1),
                        self.r_int(start+2),
                        self.r_int(start+3),
                        self.r_int(start+4),
                        self.r_int(start+5),
                        self.r_int(start+6))
    @staticmethod
    def rle_repeat(rle, lngu, maxv):
        return sum([(lngu**(m))*(n - (maxv+1)) for m, n in enumerate(rle)])+1 if rle != [] else 1

    @classmethod
    def decode_rle(cls,b, nbit, maxv, column=2560, row=3360):
        prev = None
        rle = []
        result = []
        lngu = 2**nbit - 1 - maxv
        for i in b:
            if i <= maxv:
                if prev != None:
                    result.extend([prev] * cls.rle_repeat(rle, lngu, maxv))
                    rle = []
                prev = i
            else:
                rle += [i]
        result.extend([prev] * cls.rle_repeat(rle, lngu, maxv))
        return np.array(result, dtype=np.uint8).reshape(row, column)
