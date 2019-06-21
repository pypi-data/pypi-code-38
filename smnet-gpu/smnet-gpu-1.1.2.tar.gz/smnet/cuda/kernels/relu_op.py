# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

// Relu
__global__ void relu(int *n, float *input, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        if (input[idx] > 0) {
            output[idx] = input[idx];
        }
        else {
            output[idx] = 0;
        }
    }
}


// ReluGrad
__global__ void relu_grad(int *n, float *x_grad, float *grad, 
                          float *x)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        if (x[idx] > 0) {
            x_grad[idx] += grad[idx];
        }
    }
}
""")

relu_kernel = kernel.get_function('relu')
relu_grad_kernel = kernel.get_function('relu_grad')


class ReluOp(OpKernel):
    def __init__(self, x_shape, x_size):
        self.res_shape = x_shape

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()


    def relu(self, x, output):
        relu_kernel(self.n, x, output,
                    grid=(self.cuda_num_blocks, 1, 1),
                    block=(self.cuda_num_threads, 1, 1))

    
    def relu_grad(self, x_grad, grad, x):
        relu_grad_kernel(self.n, x_grad, grad, x, 
                         grid=(self.cuda_num_blocks, 1, 1),
                         block=(self.cuda_num_threads, 1, 1))
