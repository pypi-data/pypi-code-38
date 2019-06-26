import os
import os.path
import struct

try:
    import numpy as np

    has_numpy = True
except ImportError:
    has_numpy = False


def get_importers():
    if has_numpy:
        return {'labview': labview}
    else:
        return {}


def labview(filename, N):
    assert (N > 0)
    readDouble64 = lambda f: struct.unpack('<d', f.read(8))[0]
    size = os.path.getsize(filename)
    columns = size / 8 / N
    f = open(filename, 'rb')
    data = np.zeros((N, columns))
    for jj in xrange(columns):
        for ii in xrange(N):
            data[ii, jj] = readDouble64(f)
    f.close()
    return data
