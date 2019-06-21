# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void __cuda_exp(int *n, float *input, float *output) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = __expf(input[idx]);
    }
}

__global__ void exp_grad(int *n, float *output_grad, float *output, float *input_grad) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        input_grad[idx] += output_grad[idx] * output[idx];
    }
}
""")

softmax_kernel = kernel.get_function('__cuda_exp')
softmax_grad_kernel = kernel.get_function('exp_grad')


class ExpOp(OpKernel):
    def __init__(self, input_shape):
        # 1. Generate output shape
        self.res_shape = input_shape

        # 2. Generate attrs
        n = int(np.prod(input_shape))

        # 3. Generate gpu attrs
        self.gpu_n = to_gpu(np.prod(input_shape).astype(np.int32))

        # 4. Generate nums of blocks
        self.cuda_num_blocks = self.get_cuda_num_blocks(n)

    
    def exp(self, input, output):
        softmax_kernel(self.gpu_n, input, output,
                       grid=(self.cuda_num_blocks, 1, 1),
                       block=(self.cuda_num_threads, 1, 1))


    def exp_grad(self, output_grad, output, input_grad):
        softmax_grad_kernel(self.gpu_n, output_grad, output, input_grad,
                            grid=(self.cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))
