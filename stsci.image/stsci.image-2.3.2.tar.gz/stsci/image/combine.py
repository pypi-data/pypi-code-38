from __future__ import (absolute_import, division, unicode_literals,
                        print_function)

import numpy as np
from ._combine import combine as _combine


def _combine_f(funcstr, arrays, output=None, outtype=None, nlow=0, nhigh=0,
               badmasks=None):
    arrays = [ np.asarray(a) for a in arrays ]
    shape = arrays[0].shape
    if output is None:
        if outtype is not None:
            out = arrays[0].astype(outtype)
        else:
            out = arrays[0].copy()
    else:
        out = output
    for a in tuple(arrays[1:])+(out,):
        if a.shape != shape:
            raise ValueError("all arrays must have identical shapes")
    _combine(arrays, out, nlow, nhigh, badmasks, funcstr)
    if output is None:
        return out

def imedian(arrays, output=None, outtype=None, nlow=0, nhigh=0, badmasks=None):
    """median() nominally computes the median pixels for a stack of
    identically shaped images, filling pixels with no weight with the value from
    the first input array.

    Parameters
    -----------
    arrays : list of ndarray
        A sequence of inputs arrays, which are nominally a stack of identically shaped images.

    output : ndarray
         Used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype : dtype
        The type of the output array when no 'output' is specified.

    nlow : int
        The number of pixels to be excluded from median on the low end of the pixel stack.

    nhigh : int
        The number of pixels to be excluded from median on the high end of the pixel stack.

    badmasks : list of ndarrays
        Boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               median calculation.

    Examples
    ---------
    >>> a = np.arange(4)
    >>> a = a.reshape((2,2))
    >>> arrays = [a*16, a*4, a*2, a*8]
    >>> median(arrays)
    array([[ 0,  6],
           [12, 18]])

    >>> median(arrays, nhigh=1)
    array([[ 0,  4],
           [ 8, 12]])

    >>> median(arrays, nlow=1)
    array([[ 0,  8],
           [16, 24]])

    >>> median(arrays, outtype=np.float32)
    array([[  0.,   6.],
           [ 12.,  18.]], dtype=float32)

    >>> bm = np.zeros((4,2,2), dtype=np.bool8)
    >>> bm[2,...] = 1
    >>> median(arrays, badmasks=bm)
    array([[ 0,  8],
           [16, 24]])

    >>> median(arrays, badmasks=threshhold(arrays, high=25))
    array([[ 0,  6],
           [ 8, 12]])

    """
    return _combine_f("imedian", arrays, output, outtype, nlow, nhigh, badmasks)

def median(arrays, output=None, outtype=None, nlow=0, nhigh=0, badmasks=None):
    """median() nominally computes the median pixels for a stack of
    identically shaped images.

    arrays     specifies a sequence of inputs arrays, which are nominally a
               stack of identically shaped images.

    output     may be used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype    specifies the type of the output array when no 'output' is
               specified.

    nlow       specifies the number of pixels to be excluded from median
               on the low end of the pixel stack.

    nhigh      specifies the number of pixels to be excluded from median
               on the high end of the pixel stack.

    badmasks   specifies boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               median calculation.

    >>> a = np.arange(4)
    >>> a = a.reshape((2,2))
    >>> arrays = [a*16, a*4, a*2, a*8]
    >>> median(arrays)
    array([[ 0,  6],
           [12, 18]])
    >>> median(arrays, nhigh=1)
    array([[ 0,  4],
           [ 8, 12]])
    >>> median(arrays, nlow=1)
    array([[ 0,  8],
           [16, 24]])
    >>> median(arrays, outtype=np.float32)
    array([[  0.,   6.],
           [ 12.,  18.]], dtype=float32)
    >>> bm = np.zeros((4,2,2), dtype=np.bool8)
    >>> bm[2,...] = 1
    >>> median(arrays, badmasks=bm)
    array([[ 0,  8],
           [16, 24]])
    >>> median(arrays, badmasks=threshhold(arrays, high=25))
    array([[ 0,  6],
           [ 8, 12]])
    """

    return _combine_f("median", arrays, output, outtype, nlow, nhigh, badmasks)


def iaverage(arrays, output=None, outtype=None, nlow=0, nhigh=0, badmasks=None):
    """average() nominally computes the average pixel value for a stack of
    identically shaped images, filling pixels with no weight with the value from
    the first input array.

    arrays     specifies a sequence of inputs arrays, which are nominally a
               stack of identically shaped images.

    output     may be used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype    specifies the type of the output array when no 'output' is
               specified.

    nlow       specifies the number of pixels to be excluded from average
               on the low end of the pixel stack.

    nhigh      specifies the number of pixels to be excluded from average
               on the high end of the pixel stack.

    badmasks   specifies boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               average calculation.

    >>> a = np.arange(4)
    >>> a = a.reshape((2,2))
    >>> arrays = [a*16, a*4, a*2, a*8]
    >>> average(arrays)
    array([[ 0,  7],
           [15, 22]])
    >>> average(arrays, nhigh=1)
    array([[ 0,  4],
           [ 9, 14]])
    >>> average(arrays, nlow=1)
    array([[ 0,  9],
           [18, 28]])
    >>> average(arrays, outtype=np.float32)
    array([[  0. ,   7.5],
           [ 15. ,  22.5]], dtype=float32)
    >>> bm = np.zeros((4,2,2), dtype=np.bool8)
    >>> bm[2,...] = 1
    >>> average(arrays, badmasks=bm)
    array([[ 0,  9],
           [18, 28]])
    >>> average(arrays, badmasks=threshhold(arrays, high=25))
    array([[ 0,  7],
           [ 9, 14]])

    """
    return _combine_f("iaverage", arrays, output, outtype, nlow, nhigh, badmasks)


def average(arrays, output=None, outtype=None, nlow=0, nhigh=0, badmasks=None):
    """average() nominally computes the average pixel value for a stack of
    identically shaped images.

    arrays     specifies a sequence of inputs arrays, which are nominally a
               stack of identically shaped images.

    output     may be used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype    specifies the type of the output array when no 'output' is
               specified.

    nlow       specifies the number of pixels to be excluded from average
               on the low end of the pixel stack.

    nhigh      specifies the number of pixels to be excluded from average
               on the high end of the pixel stack.

    badmasks   specifies boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               average calculation.

    >>> a = np.arange(4)
    >>> a = a.reshape((2,2))
    >>> arrays = [a*16, a*4, a*2, a*8]
    >>> average(arrays)
    array([[ 0,  7],
           [15, 22]])
    >>> average(arrays, nhigh=1)
    array([[ 0,  4],
           [ 9, 14]])
    >>> average(arrays, nlow=1)
    array([[ 0,  9],
           [18, 28]])
    >>> average(arrays, outtype=np.float32)
    array([[  0. ,   7.5],
           [ 15. ,  22.5]], dtype=float32)
    >>> bm = np.zeros((4,2,2), dtype=np.bool8)
    >>> bm[2,...] = 1
    >>> average(arrays, badmasks=bm)
    array([[ 0,  9],
           [18, 28]])
    >>> average(arrays, badmasks=threshhold(arrays, high=25))
    array([[ 0,  7],
           [ 9, 14]])

    """

    return _combine_f("average", arrays, output, outtype, nlow, nhigh,
                      badmasks)


def minimum(arrays, output=None, outtype=None, nlow=0, nhigh=0, badmasks=None):
    """minimum() nominally computes the minimum pixel value for a stack of
    identically shaped images.

    arrays     specifies a sequence of inputs arrays, which are nominally a
               stack of identically shaped images.

    output     may be used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype    specifies the type of the output array when no 'output' is
               specified.

    nlow       specifies the number of pixels to be excluded from minimum
               on the low end of the pixel stack.

    nhigh      specifies the number of pixels to be excluded from minimum
               on the high end of the pixel stack.

    badmasks   specifies boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               minimum calculation.

    >>> a = np.arange(4)
    >>> a = a.reshape((2,2))
    >>> arrays = [a*16, a*4, a*2, a*8]
    >>> minimum(arrays)
    array([[0, 2],
           [4, 6]])
    >>> minimum(arrays, nhigh=1)
    array([[0, 2],
           [4, 6]])
    >>> minimum(arrays, nlow=1)
    array([[ 0,  4],
           [ 8, 12]])
    >>> minimum(arrays, outtype=np.float32)
    array([[ 0.,  2.],
           [ 4.,  6.]], dtype=float32)
    >>> bm = np.zeros((4,2,2), dtype=np.bool8)
    >>> bm[2,...] = 1
    >>> minimum(arrays, badmasks=bm)
    array([[ 0,  4],
           [ 8, 12]])
    >>> minimum(arrays, badmasks=threshhold(arrays, low=10))
    array([[ 0, 16],
           [16, 12]])

    """

    return _combine_f("minimum", arrays, output, outtype, nlow, nhigh,
                      badmasks)


def threshhold(arrays, low=None, high=None, outputs=None):
    """threshhold() computes a boolean array 'outputs' with
    corresponding elements for each element of arrays.  The
    boolean value is true where each of the arrays values
    is < the low or >= the high threshholds.

    >>> a=np.arange(100)
    >>> a=a.reshape((10,10))
    >>> (threshhold(a, 1, 50)).astype(np.int8)
    array([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=int8)
    >>> (threshhold([ range(10)]*10, 3, 7)).astype(np.int8)
    array([[1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
           [1, 1, 1, 0, 0, 0, 0, 1, 1, 1]], dtype=int8)
    >>> (threshhold(a, high=50)).astype(np.int8)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=int8)
    >>> (threshhold(a, low=50)).astype(np.int8)
    array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=int8)

    """
    arrays = np.asarray(arrays)

    if high is None and low is None:
        return np.zeros_like(arrays, dtype=np.bool)

    if outputs is None:
        outputs = np.empty_like(arrays, dtype=np.bool)

    if high is None:
        for k in range(arrays.shape[0]):
            np.less(arrays[k], low, outputs[k])
    else:
        if low is None:
            for k in range(arrays.shape[0]):
                np.greater_equal(arrays[k], high, outputs[k])
        else:
            for k in range(arrays.shape[0]):
                arr = arrays[k]
                out = outputs[k]
                np.greater_equal(arr, high, out)
                np.logical_or(out, arr < low, out)

    return outputs


def _bench():
    """time a 10**6 element median"""
    import time
    a = np.arange(10**6)
    a = a.reshape((1000, 1000))
    arrays = [a*2, a*64, a*16, a*8]
    t0 = time.clock()
    median(arrays)
    print("maskless:", time.clock()-t0)

    a = np.arange(10**6)
    a = a.reshape((1000, 1000))
    arrays = [a*2, a*64, a*16, a*8]
    t0 = time.clock()
    median(arrays, badmasks=np.zeros((1000,1000), dtype=np.bool8))
    print("masked:", time.clock()-t0)
