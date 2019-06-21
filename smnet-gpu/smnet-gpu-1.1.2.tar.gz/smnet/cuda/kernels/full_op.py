# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void full(int *n, float *x, float *value)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        x[idx] = *value;
    }
}
""")

full_kernel = kernel.get_function('full')


class FullOp(OpKernel):
    def __init__(self, input_shape, value=None):
        self.res_shape = input_shape

        if value is not None:
            self.gpu_value = to_gpu(np.array(value, dtype=np.float32))

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def full(self, input, value=None):
        if value is None:
            value = self.gpu_value
        full_kernel(self.n, input, value,
                    grid=(self.cuda_num_blocks, 1, 1),
                    block=(self.cuda_num_threads, 1, 1))
