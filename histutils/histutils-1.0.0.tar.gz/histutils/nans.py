from numpy import empty, nan


def nans(shape=1, dtype=float, order='F'):
    a = empty(shape, dtype, order)
    a.fill(nan)
    return a


def nans_like(arr):
    return nans(arr.shape, arr.dtype)
