# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void hse(int *n, float *labels, float *logits, float *output) 
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float sub = labels[idx] - logits[idx];
        output[idx] = 0.5f * sub * sub;
    }
}

__global__ void hse_grad(int *n, float *grad, float *labels, float *logits,
                         float *labels_grad, float *logits_grad)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        labels_grad[idx] += grad[idx] * (labels[idx] - logits[idx]);
        logits_grad[idx] += grad[idx] * (logits[idx] - labels[idx]);
    }
}
""")

hse_kernel = kernel.get_function('hse')
hse_grad_kernel = kernel.get_function('hse_grad')


class HseOp(OpKernel):
    def __init__(self, labels_shape):
        self.res_shape = labels_shape

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def hse(self, labels, logits, output):
        hse_kernel(self.n, labels, logits, output,
                   grid=(self.cuda_num_blocks, 1, 1),
                   block=(self.cuda_num_threads, 1, 1))

    
    def hse_grad(self, grad, labels, logits, labels_grad, logits_grad):
        hse_grad_kernel(self.n, grad, labels, logits, labels_grad, logits_grad,
                        grid=(self.cuda_num_blocks, 1, 1),
                        block=(self.cuda_num_threads, 1, 1))
