# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void to_zero(int *n, float *x)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        x[idx] = 0.f;
    }
}
""")

to_zero_kernel = kernel.get_function('to_zero')


class ToZeroOp(OpKernel):
    def __init__(self, size):
        self.size = size
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def to_zero(self, x):
        to_zero_kernel(self.n, x,
                       grid=(self.cuda_num_blocks, 1, 1),
                       block=(self.cuda_num_threads, 1, 1))
