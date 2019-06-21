# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void sigmoid(int *n, float *input, float *output)
{
    /*
    s(x) = 1 / (1 + exp(-x))
    */
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = __fdividef(1, 1 + __expf(-input[idx]));
    }
}

__global__ void sigmoid_grad(int *n, float *top_grad, float *top_data,
                             float *bottom_grad) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float top_data_ = top_data[idx];
        bottom_grad[idx] += top_grad[idx] * top_data_ * (1.f - top_data_);
    }
}
""")

sigmoid_kernel = kernel.get_function('sigmoid')
sigmoid_grad_kernel = kernel.get_function('sigmoid_grad')


class SigmoidOp(OpKernel):
    def __init__(self, input_shape):
        self.res_shape = input_shape

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()
    

    def sigmoid(self, input, output):
        sigmoid_kernel(self.n, input, output,
                       grid=(self.cuda_num_blocks, 1, 1),
                       block=(self.cuda_num_threads, 1, 1))


    def sigmoid_grad(self, top_grad, top_data, bottom_grad):
        sigmoid_grad_kernel(self.n, top_grad, top_data, bottom_grad,
                            grid=(self.cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))
