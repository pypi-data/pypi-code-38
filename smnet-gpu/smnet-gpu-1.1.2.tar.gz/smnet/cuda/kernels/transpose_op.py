# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8


// Transpose
__global__ void transpose(float *a, float *output, 
                          int *perm, int *src_shape, int *shape_size_,
                          int *size)
{
    /* Transpose operate

    dst(i, j) = src(j, i)

    Input:
        a: shape ?
    Output:
        output: shape ?
    Attrs:
        perm: list of int
        src_shape: list of int
    */

    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *size) {
        int tmp_idx = idx;
        int old_idns[MAX_SHAPE_SIZE];

        int shape_size = shape_size_[0];
        for (int i = shape_size - 1; i >= 0; i--) {
            old_idns[i] = idx % src_shape[i];
            idx /= src_shape[i];
        }
        int tmp = 0, factor = 1;
        for (int i = shape_size - 1; i >= 0; i--) {
            tmp += factor * old_idns[perm[i]];
            factor *= src_shape[perm[i]];
        }
        output[tmp] = a[tmp_idx];
    }
}
""")

transpose_kernel = kernel.get_function('transpose')


class TransposeOp(OpKernel):
    def __init__(self, a_shape, perm, size):
        self._a_shape = a_shape
        self._perm = perm

        self._gpu_perm = to_gpu(
            np.array(self._perm, dtype=np.int32))
        self._gpu_src_shape = to_gpu(
            np.array(self._a_shape, dtype=np.int32))
        self._gpu_shape_size = to_gpu(
            np.array([len(self._a_shape)], dtype=np.int32))
        self._gpu_size = to_gpu(
            np.array([size], dtype=np.int32))
        self.grid = int(np.prod(a_shape))

        self.block, self.thread = grid_alloc(self.grid)


    def __call__(self, a, output):
        transpose_kernel(a, output, 
                         self._gpu_perm, self._gpu_src_shape, 
                         self._gpu_shape_size, self._gpu_size,
                         grid=self.block, 
                         block=self.thread)
