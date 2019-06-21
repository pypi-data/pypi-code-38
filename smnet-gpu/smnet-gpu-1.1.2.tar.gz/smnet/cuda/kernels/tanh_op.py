# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void __cuda_tanh(int *n, float *input, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = 1.f - __fdividef(2.f, __expf(2.f * input[idx]) + 1.f);
    }
}

__global__ void tanh_grad(int *n, float *grad, float *top_data, 
                          float *bottom_grad) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float top_data_ = top_data[idx];
        bottom_grad[idx] += grad[idx] * (1.f - top_data_ * top_data_);
    }
}
""")

tanh_kernel = kernel.get_function('__cuda_tanh')
tanh_grad_kernel = kernel.get_function('tanh_grad')


class TanhOp(OpKernel):
    def __init__(self, input_shape):
        self.res_shape = input_shape

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()


    def tanh(self, input, output):
        tanh_kernel(self.n, input, output,
                    grid=(self.cuda_num_blocks, 1, 1),
                    block=(self.cuda_num_threads, 1, 1))

    
    def tanh_grad(self, grad, top_data, bottom_grad):
        tanh_grad_kernel(self.n, grad, top_data, bottom_grad,
                         grid=(self.cuda_num_blocks, 1, 1),
                         block=(self.cuda_num_threads, 1, 1))
