# --------------------------------------------------------
# SMNet cuda
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Wrapped pycuda gpu library."""

import pycuda.gpuarray as gpuarray
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import math

from . import cuda_ops

THREADS = [384, 256, 192, 128, 96]


def gpu_empty(size):
    """Allocate empty gpu memory.
    
    By default, size means float32/int32 data.

    Args:
        size: int
    """
    gpu_data = cuda.mem_alloc(size * 4)
    return gpu_data


def gpu_zeros(size, gpu_data=None):
    if gpu_data is None:
        gpu_data = cuda.mem_alloc(size * 4)
    cuda_ops.zeros(gpu_data,
                   grid=(size, 1, 1), block=(1, 1, 1))
    return gpu_data


def gpu_full(value, size, gpu_data=None):
    if gpu_data is None:
        gpu_data = cuda.mem_alloc(size * 4)
    cuda_ops.full(gpu_data,
                  to_gpu(np.array([value], dtype=np.float32)),
                  grid=(size, 1, 1), block=(1, 1, 1))
    return gpu_data


def to_cpu(shape, gpu_data, dtype=np.float32):
    """Memcpy gpu_data to cpu_data.
    
    The size of shape must be less equal to the size of gpu data.

    Args:
        shape: cpu data shape.
        gpu_data: gpu data.
    """
    cpu_data = np.empty(shape=shape, dtype=dtype)
    cuda.memcpy_dtoh(cpu_data, gpu_data)
    return cpu_data


def to_gpu(cpu_data, gpu_data=None):
    """Memcpy cpu_data to gpu_data.
    
    The size of cpu data must be less equal to the size of gpu data.

    Args:
        cpu_data: numpy data.
        gpu_data: If None, the function will allocate an empty gpu memory to
            accept the cpu data.
    """
    if gpu_data is None:
        gpu_data = cuda.mem_alloc(cpu_data.nbytes)
    cuda.memcpy_htod(gpu_data, cpu_data)
    return gpu_data


def broadcast(shape_a, shape_b):
    """numpy broadcast

    Reference:
        http://www.runoob.com/numpy/numpy-broadcast.html
    """
    # 1. pad 1
    max_len = max(len(shape_a), len(shape_b))
    pad_shape_a = [1] * (max_len - len(shape_a)) + list(shape_a)
    pad_shape_b = [1] * (max_len - len(shape_b)) + list(shape_b)

    # 2. check correctness and broadcast
    res_shape = []
    for size_a, size_b in zip(pad_shape_a, pad_shape_b):
        if size_a != size_b and size_a != 1 and size_b != 1:
            raise ValueError('Can not broadcast shape {}' 
                             'and shape {}'.format(shape_a, shape_b))
        res_shape.append(max(size_a, size_b))
    return res_shape, pad_shape_a, pad_shape_b


def shapetype(shape_a, shape_b, broadcast_shape):
    if list(shape_a) == list(shape_b):
        return 'identity', None
    
    if list(shape_a) == list(broadcast_shape):
        return 'bias', 'left'
    elif list(shape_b) == list(broadcast_shape):
        return 'bias', 'right'
    else:
        return 'common', None


def grid_alloc(size):
    thread_num = 192
    block_num = math.ceil(size / thread_num)
    return (block_num, 1, 1), (thread_num, 1, 1)
