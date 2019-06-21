# --------------------------------------------------------
# SMNet pad cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__device__ int fallOut(const int *curidx, const int *shape, 
                        const int *pad_width, const int *shape_size)
{
    int target = 0;
    for (int i = 0; i < *shape_size; i++) {
        target += curidx[i] < pad_width[i * 2];
        target += curidx[i] >= shape[i] - pad_width[i * 2 + 1];
    }
    return target;
}


__global__ void pad(const int *n, const float *input, float *output,
                    const float *pad_value,
                    const int *pad_width, const int *output_shape,
                    const int *input_shape,
                    const int *out_shape_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int tmp_idx = idx;
    if (idx < *n) {
        int cur_idx[MAX_SHAPE_SIZE];
        for (int i = *out_shape_size - 1; i >= 0; i--) {
            cur_idx[i] = idx % output_shape[i];
            idx /= output_shape[i];
        }

        if (fallOut(cur_idx, output_shape, pad_width, out_shape_size)) {
            output[tmp_idx] = *pad_value;
        }
        else {
            int in_idx = 0, factor = 1;
            for (int i = *out_shape_size - 1; i >= 0; i--) {
                in_idx += factor * (cur_idx[i] - pad_width[2 * i]);
                factor *= input_shape[i];
            }
            output[tmp_idx] = input[in_idx];
        }
    }
}


__global__ void pad_grad(int *n, float *input_grad, float *grad,
                         int *pad_width, int *output_shape,
                         int *input_shape, int *shape_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;
        int cur_idx[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            cur_idx[i] = idx % output_shape[i];
            idx /= output_shape[i];
        }

        if (!fallOut(cur_idx, output_shape, pad_width, shape_size)) {
            int in_idx = 0, factor = 1;
            for (int i = *shape_size - 1; i >= 0; i--) {
                in_idx += factor * (cur_idx[i] - pad_width[2 * i]);
                factor *= input_shape[i];
            }
            input_grad[in_idx] += grad[tmp_idx];
        }
    }
}
""")

pad_kernel = kernel.get_function('pad')
pad_grad_kernel = kernel.get_function('pad_grad')


class PadOp(OpKernel):
    def __init__(self, pad_width, pad_value, input_shape):
        output_shape = (np.sum(pad_width, -1) + input_shape).astype(np.int32)
        self.res_shape = tuple(output_shape.tolist())

        self.gpu_pad_width = to_gpu(np.array(pad_width, dtype=np.int32))
        self.gpu_pad_value = to_gpu(np.array(pad_value, dtype=np.float32))
        self.gpu_output_shape = to_gpu(output_shape)
        self.gpu_input_shape = to_gpu(np.array(input_shape, dtype=np.int32))
        self.gpu_out_shape_size = to_gpu(np.array(len(output_shape), dtype=np.int32))

        self.size = int(np.prod(output_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def pad(self, input, output):
        pad_kernel(self.n, input, output,
                   self.gpu_pad_value,
                   self.gpu_pad_width, self.gpu_output_shape,
                   self.gpu_input_shape,
                   self.gpu_out_shape_size,
                   grid=(self.cuda_num_blocks, 1, 1),
                   block=(self.cuda_num_threads, 1, 1))

    
    def pad_grad(self, input_grad, grad):
        pad_grad_kernel(self.n, input_grad, grad,
                        self.gpu_pad_width, self.gpu_output_shape,
                        self.gpu_input_shape, self.gpu_out_shape_size,
                        grid=(self.cuda_num_blocks, 1, 1),
                        block=(self.cuda_num_threads, 1, 1))
