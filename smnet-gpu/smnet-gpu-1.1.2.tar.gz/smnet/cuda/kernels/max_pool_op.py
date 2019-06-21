# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8
//#define INT_MAX 2147483647
#define INT_MIN (-INT_MAX - 1)

__device__ int dim4Index(int n, int h, int w, int c,
                         int N, int H, int W, int C)
{
    return c + w * C + h * C * W + n * C * W * H;
}

__device__ float max_element(float *elements, const int *size)
{
    float largest = elements[0];
    for (int i = 1; i < *size; i++) {
        if (largest < elements[i]) {
            largest = elements[i];
        }
    }
    return largest;
}


__global__ void max_pool(int *n, const float *input, float *output, 
                         int *arg_max_pool,
                         const int *ksize, const int *strides, 
                         const int *input_shape, const int *output_shape)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int tmp_idx = idx;
    if (idx < *n) {
        int C = idx % output_shape[3];
        idx /= output_shape[3];
        int W = idx % output_shape[2];
        idx /= output_shape[2];
        int H = idx % output_shape[1];
        idx /= output_shape[1];
        int N = idx;

        float largest = INT_MIN;
        int max_index;
        for (int h = 0; h < ksize[1]; h++) {
            for (int w = 0; w < ksize[2]; w++) {
                int current_index = dim4Index(N, h + H * strides[1], w + W * strides[2], C, input_shape[0], input_shape[1], input_shape[2], input_shape[3]);
                float inter_mem =  input[current_index];
                if (largest < inter_mem) {
                    largest = inter_mem; 
                    max_index = current_index;
                }
            }
        }
        output[tmp_idx] = largest;
        arg_max_pool[tmp_idx] = max_index;
    }
}


__global__ void max_pool_grad(int *n, float *grad, float *input_grad, 
                              int *arg_index, int *arg_index_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float tmp_grad = 0.f;
        for (int i = 0; i < *arg_index_size; i++) {
            if (arg_index[i] == idx)
                tmp_grad += grad[i];
        }
        input_grad[idx] += tmp_grad;
    }
}
""")

max_pool_kernel = kernel.get_function('max_pool')
max_pool_grad_kernel = kernel.get_function('max_pool_grad')


class MaxPoolOp(OpKernel):
    def __init__(self, input_shape, ksize, strides):
        # 1. Compute self.res_shape
        ni, hi, wi, ci = input_shape
        nf, hf, wf, cf = ksize
        ns, hs, ws, cs = strides
        ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1
        self.res_shape = (ni, ho, wo, ci)

        # 2. Prepare gpu_data
        self.gpu_ksize = to_gpu(np.array(ksize, dtype=np.int32))
        self.gpu_strides = to_gpu(np.array(strides, dtype=np.int32))
        self.gpu_input_shape = to_gpu(np.array(input_shape, dtype=np.int32))
        self.gpu_output_shape = to_gpu(np.array(self.res_shape, dtype=np.int32))
        self.gpu_arg_index = gpu_empty(int(np.prod(self.res_shape)))

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

        self.gpu_arg_index_size = to_gpu(np.array(self.size, dtype=np.int32))

        self.input_n = to_gpu(np.prod(input_shape).astype(np.int32))
        self.input_cuda_num_blocks = self.get_cuda_num_blocks(int(np.prod(input_shape)))


    def max_pool(self, input, output):
        max_pool_kernel(self.n, input, output, self.gpu_arg_index,
                        self.gpu_ksize, self.gpu_strides, 
                        self.gpu_input_shape, self.gpu_output_shape,
                        grid=(self.cuda_num_blocks, 1, 1),
                        block=(self.cuda_num_threads, 1, 1))

    
    def max_pool_grad(self, grad, input_grad):
        max_pool_grad_kernel(self.input_n, grad, input_grad, 
                             self.gpu_arg_index, self.gpu_arg_index_size,
                             grid=(self.input_cuda_num_blocks, 1, 1),
                             block=(self.cuda_num_threads, 1, 1))
