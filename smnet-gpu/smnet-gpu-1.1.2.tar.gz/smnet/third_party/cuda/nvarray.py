# --------------------------------------------------------
# SMNet Cuda
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

import os.path as osp
import ctypes
import numpy as np


def get_lib_path():
    rlpt = osp.realpath(__file__)
    rldir = osp.split(rlpt)[0]
    lbpt = osp.join(rldir, 'lib', 'libsmnv.so')
    return lbpt


libnv = ctypes.cdll.LoadLibrary(get_lib_path())
libnv.nvEmpty.restype = ctypes.c_void_p


def c_data(data):
    """
    Args:
        data: numpy data.
    """
    if data.dtype != np.float32 and data.dtype != np.int32:
        raise ValueError('Nvarray only support dtype of float32 and int32, '
                         'but the dtype is {}'.format(data.dtype))
    
    host_ptr = data.ctypes.data_as(ctypes.c_void_p)
    return host_ptr


def empty(shape, dtype=np.float32):
    """Malloc a cuda memory.

    By default, the dtype is float32/int32
    """
    size = int(np.prod(shape))
    # 4 means 4 bytes of float or int
    dev_ptr = ctypes.c_void_p(libnv.nvEmpty(4 * size))
    print(dev_ptr.value)
    return NvArray(dev_ptr, shape, dtype)


def array(data, dtype=np.float32):
    """Malloc device memory and memcpy host data to device.
    
    By default, the dtype is float32/int32
    """
    data = np.asarray(data, dtype=dtype)
    # data of NvArray
    na_data = empty(data.shape, dtype)
    # 4 means 4 bytes of float or int
    libnv.nvArray(na_data.data, c_data(data), 4 * data.size)
    return na_data


class NvArray(object):
    def __init__(self, dev_ptr, shape, dtype):
        self._data = dev_ptr
        print(self._data)
        self._shape = shape
        self._size = int(np.prod(shape))

        if dtype == np.float32:
            self._host_ptr = (ctypes.c_float * self._size)()
        elif dtype == np.int32:
            self._host_ptr = (ctypes.c_int * self._size)()
        else:
            raise ValueError('Nvarray only support dtype of float32 and int32, '
                            'but the dtype is {}'.format(data.dtype))

    
    def __del__(self):
        # 4 means 4 bytes of float or int
        libnv.nvFree(self._data, self._size * 4)


    def to_array(self):
        # 4 means 4 bytes of float or int
        libnv.hostArray(self._host_ptr, self._data, 4 * self._size)
        return np.ctypeslib.as_array(self._host_ptr).reshape(self._shape)

    
    @property
    def data(self):
        return self._data

    
    @property
    def shape(self):
        return self._shape

    
    @property
    def size(self):
        return self._size
