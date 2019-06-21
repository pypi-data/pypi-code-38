# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *
from .matmul_op import matmul_left_grad_set_kernel

kernel = SourceModule("""
__global__ void power(int n, float *x, float *y, float *powed) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        powed[idx] = powf(x[idx], *y);
    }
}

/*
*  The n of `power_grad` equal to the n of `power`.
*/
__global__ void power_grad(int n, float *grad, float *x, float *y, 
                           float *x_grad) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        powed[idx] += *y * powf(x[idx], *y - 1);
    }
}
""")

power_kernel = kernel.get_function('power')
power_grad_kernel = kernel.get_function('power_grad')


class PowOp(OpKernel):
    def __init__(self, x_shape, y):
        self.res_shape = x_shape

        self.gpu_y = to_gpu(np.float32(y))

        self.size = int(np.prod(self.res_shape))
        self.gpu_n = to_gpu(np.prod(self.res_shape).astype(np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def pow(self, x, powed):
        power_kernel(self.gpu_n, x, self.gpu_y, powed,
                     grid=(self.cuda_num_blocks, 1, 1),
                     block=(self.cuda_num_threads, 1, 1))


    def pow_grad(self, grad, x, x_grad):
        power_kernel(self.gpu_n, grad, x, self.gpu_y, x_grad,
                     grid=(self.cuda_num_blocks, 1, 1),
                     block=(self.cuda_num_threads, 1, 1))

