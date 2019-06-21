# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__global__ void reshape(int *n, float *a, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = a[idx];
    }
}

__global__ void reshape_grad(int *n, float *grad, float *input_grad) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        input_grad[idx] += grad[idx];
    }
}
""")

reshape_kernel = kernel.get_function('reshape')
reshape_grad_kernel = kernel.get_function('reshape_grad')


class ReshapeOp(OpKernel):
    def __init__(self, shape):
        self.size = int(np.prod(shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def reshape(self, input, output):
        reshape_kernel(self.n, input, output,
                       grid=(self.cuda_num_blocks, 1, 1),
                       block=(self.cuda_num_threads, 1, 1))


    def reshape_grad(self, grad, input_grad):
        reshape_grad_kernel(self.n, grad, input_grad,
                            grid=(self.cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))
