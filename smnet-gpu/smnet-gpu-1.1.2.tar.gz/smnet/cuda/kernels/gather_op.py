# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
__global__ void gather(int *n, float *params, int *indices, float *output,
                       int *feature_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int dims[2] = {__fdividef(idx, *feature_size), idx % *feature_size};
        output[idx] = params[indices[dims[0]] * *feature_size + dims[1]];
    }
}


__global__ void gather_grad(int *n, float *grad, float *params_grad, 
                            int *indices, int *indices_size, 
                            int *feature_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float tmp_grad = 0.f;
        int dims[2] = {__fdividef(idx, *feature_size), idx % *feature_size};
        for (int i = 0; i < *indices_size; i++) {
            if (indices[i] == dims[0]) {
                tmp_grad += grad[dims[1] + *feature_size * i];
            }
        }
        params_grad[idx] += tmp_grad;
    }
}
""")

gather_kernel = kernel.get_function('gather')
gather_grad_kernel = kernel.get_function('gather_grad')


class GatherOp(OpKernel):
    def __init__(self, params_shape, indices_shape):
        self.res_shape = tuple(list(indices_shape) + list(params_shape[1:]))

        self.gpu_feature_size = to_gpu(np.prod(params_shape[1:]).astype(np.int32))

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

        self.gpu_indices_size = to_gpu(np.prod(indices_shape).astype(np.int32))
        self.params_n = to_gpu(np.prod(params_shape).astype(np.int32))
        self.params_cuda_num_blocks = self.get_cuda_num_blocks(int(np.prod(params_shape)))

    
    def gather(self, params, indices, output):
        gather_kernel(self.n, params, indices, output, 
                      self.gpu_feature_size,
                      grid=(self.cuda_num_blocks, 1, 1),
                      block=(self.cuda_num_threads, 1, 1))

    
    def gather_grad(self, grad, params_grad, indices):
        gather_grad_kernel(self.params_n, grad, params_grad,
                           indices, self.gpu_indices_size, 
                           self.gpu_feature_size,
                           grid=(self.params_cuda_num_blocks, 1, 1),
                           block=(self.cuda_num_threads, 1, 1))
