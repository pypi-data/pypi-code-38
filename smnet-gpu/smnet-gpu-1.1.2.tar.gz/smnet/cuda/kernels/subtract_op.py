# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8


__global__ void subtract(float *a, float *b, float *c,
                       int *pad_shape_a, int *pad_shape_b, int *broadcast_shape,
                       int *shape_size_)
{
    int idx = blockIdx.x;
    int tmp_idx = idx;
    int shape_size = *shape_size_;

    int cur_a_shape[MAX_SHAPE_SIZE];
    int cur_b_shape[MAX_SHAPE_SIZE];
    for (int i = shape_size - 1; i >= 0; i--) {
        int remainder = idx % broadcast_shape[i];
        if (pad_shape_a[i] == 1) {
            cur_a_shape[i] = 0;
        }
        else {
            cur_a_shape[i] = remainder;
        }

        if (pad_shape_b[i] == 1) {
            cur_b_shape[i] = 0;
        }
        else {
            cur_b_shape[i] = remainder;
        }
        idx /= broadcast_shape[i];
    }
    int a_ind = 0, factor_a = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        a_ind += factor_a * cur_a_shape[i];
        factor_a *= pad_shape_a[i];
    }
    int b_ind = 0, factor_b = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        b_ind += factor_b * cur_b_shape[i];
        factor_b *= pad_shape_b[i];
    }
    c[tmp_idx] = a[a_ind] - b[b_ind];
}


__global__ void subtract_grad_left(float *grad, float *a_grad,
                                 int *pad_shape_a, int *pad_shape_b, 
                                 int *broadcast_shape, int *shape_size_)
{
    int idx = blockIdx.x;
    int tmp_idx = idx;
    int shape_size = *shape_size_;

    int cur_a_shape[MAX_SHAPE_SIZE];
    int cur_b_shape[MAX_SHAPE_SIZE];
    for (int i = shape_size - 1; i >= 0; i--) {
        int remainder = idx % broadcast_shape[i];
        if (pad_shape_a[i] == 1) {
            cur_a_shape[i] = 0;
        }
        else {
            cur_a_shape[i] = remainder;
        }

        if (pad_shape_b[i] == 1) {
            cur_b_shape[i] = 0;
        }
        else {
            cur_b_shape[i] = remainder;
        }
        idx /= broadcast_shape[i];
    }
    int a_ind = 0, factor_a = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        a_ind += factor_a * cur_a_shape[i];
        factor_a *= pad_shape_a[i];
    }
    int b_ind = 0, factor_b = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        b_ind += factor_b * cur_b_shape[i];
        factor_b *= pad_shape_b[i];
    }

    // get tmp_idx, a_ind, b_ind
    a_grad[a_ind] += grad[tmp_idx];
}


__global__ void subtract_grad_right(float *grad, float *b_grad,
                                  int *pad_shape_a, int *pad_shape_b, 
                                  int *broadcast_shape, int *shape_size_)
{
    int idx = blockIdx.x;
    int tmp_idx = idx;
    int shape_size = *shape_size_;

    int cur_a_shape[MAX_SHAPE_SIZE];
    int cur_b_shape[MAX_SHAPE_SIZE];
    for (int i = shape_size - 1; i >= 0; i--) {
        int remainder = idx % broadcast_shape[i];
        if (pad_shape_a[i] == 1) {
            cur_a_shape[i] = 0;
        }
        else {
            cur_a_shape[i] = remainder;
        }

        if (pad_shape_b[i] == 1) {
            cur_b_shape[i] = 0;
        }
        else {
            cur_b_shape[i] = remainder;
        }
        idx /= broadcast_shape[i];
    }
    int a_ind = 0, factor_a = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        a_ind += factor_a * cur_a_shape[i];
        factor_a *= pad_shape_a[i];
    }
    int b_ind = 0, factor_b = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        b_ind += factor_b * cur_b_shape[i];
        factor_b *= pad_shape_b[i];
    }

    // get tmp_idx, a_ind, b_ind
    b_grad[b_ind] += -grad[tmp_idx];
}


__global__ void identity_subtract(int *n, float *left, float *right, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = left[idx] - right[idx];
    }
}
""")

subtract_kernel = kernel.get_function('subtract')
subtract_grad_left_kernel = kernel.get_function('subtract_grad_left')
subtract_grad_right_kernel = kernel.get_function('subtract_grad_right')
identity_subtract_kernel = kernel.get_function('identity_subtract')


class SubtractOp(OpKernel):
    def __init__(self, shape_a, shape_b):
        self._shape_a = shape_a
        self._shape_b = shape_b
        self._res_shape, self._pad_shape_a, self._pad_shape_b = broadcast(
            shape_a, shape_b)

        self.res_shape = self._res_shape

        self._gpu_pad_shape_a = to_gpu(
            np.array(self._pad_shape_a, dtype=np.int32))
        self._gpu_pad_shape_b = to_gpu(
            np.array(self._pad_shape_b, dtype=np.int32))
        self._gpu_broadcast_shape = to_gpu(
            np.array(self._res_shape, dtype=np.int32))
        self._gpu_shape_size = to_gpu(
            np.array([len(self._res_shape)], dtype=np.int32))
        self.grid = int(np.prod(self._res_shape))

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()


    def subtract(self, a, b, output):
        subtract_kernel(a, b, output,
                      self._gpu_pad_shape_a, self._gpu_pad_shape_b, 
                      self._gpu_broadcast_shape, self._gpu_shape_size,
                      grid=(self.grid, 1, 1), block=(1, 1, 1))

    
    def identity_subtract(self, a, b, output):
        identity_subtract_kernel(self.n, a, b, output,
                                 grid=(self.cuda_num_blocks, 1, 1),
                                 block=(self.cuda_num_threads, 1, 1))


    def subtract_grad_left(self, grad, a_grad):
        subtract_grad_left_kernel(grad, a_grad,
                                self._gpu_pad_shape_a, self._gpu_pad_shape_b, 
                                self._gpu_broadcast_shape, self._gpu_shape_size,
                                grid=(self.grid, 1, 1), block=(1, 1, 1))


    def subtract_grad_right(self, grad, b_grad):
        subtract_grad_right_kernel(grad, b_grad,
                                 self._gpu_pad_shape_a, self._gpu_pad_shape_b, 
                                 self._gpu_broadcast_shape, self._gpu_shape_size,
                                 grid=(self.grid, 1, 1), block=(1, 1, 1))
