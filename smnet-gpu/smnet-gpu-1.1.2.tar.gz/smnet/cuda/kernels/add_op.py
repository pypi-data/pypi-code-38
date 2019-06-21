# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *
from . import multiply_op


kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__global__ void add(int *n, float *a, float *b, float *c,
                    int *pad_shape_a, int *pad_shape_b, int *broadcast_shape,
                    int *shape_size_)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
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
        c[tmp_idx] = a[a_ind] + b[b_ind];
    }
}

__global__ void add_grad(float *a_grad, float *grad, 
                         int *grad_shape, int *a_pad_shape, int *shape_size,
                         int *size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *size) {
        int tmp_idx = idx;

        int a_shape[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            if (a_pad_shape[i] == 1) {
                a_shape[i] = 0;
            }
            else {
                a_shape[i] = idx % grad_shape[i];
            }
            idx /= grad_shape[i];
        }
        int a_ind = 0, factor = 1;
        for (int i = *shape_size - 1; i >= 0; i--) {
            a_ind += factor * a_shape[i];
            factor *= a_pad_shape[i];
        }
        a_grad[a_ind] += grad[tmp_idx];
    }
}

__global__ void bias_add(int *n, float *a, float *b, float *output,
                         int *b_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = a[idx] + b[idx % *b_size];
    }
}

__global__ void identity_add(int *n, float *a, float *b, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = a[idx] + b[idx];
    }
}
""")

add_kernel = kernel.get_function('add')
add_grad_kernel = kernel.get_function('add_grad')
bias_add_kernel = kernel.get_function('bias_add')
identity_add_kernel = kernel.get_function('identity_add')


class AddOp(multiply_op.MultiplyOp):
    def __init__(self, shape_a, shape_b):
        super(AddOp, self).__init__(shape_a, shape_b)
        self._gpu_broadcast_shape = to_gpu(
            np.array(self.res_shape, dtype=np.int32))
        self._gpu_pad_shape_a = to_gpu(
            np.array(self.pad_shape_a, dtype=np.int32))
        self._gpu_pad_shape_b = to_gpu(
            np.array(self.pad_shape_b, dtype=np.int32))
        self._gpu_shape_size = to_gpu(
            np.array([len(self.res_shape)], dtype=np.int32))
        self.grid = int(np.prod(self.res_shape))
        self._gpu_size = to_gpu(
            np.array([self.grid], dtype=np.int32))
        self.block, self.thread = grid_alloc(self.grid)
        return

        self._shape_a = shape_a
        self._shape_b = shape_b
        self._res_shape, self._pad_shape_a, self._pad_shape_b = broadcast(
            shape_a, shape_b)

        self._gpu_pad_shape_a = to_gpu(
            np.array(self._pad_shape_a, dtype=np.int32))
        self._gpu_pad_shape_b = to_gpu(
            np.array(self._pad_shape_b, dtype=np.int32))
        self._gpu_broadcast_shape = to_gpu(
            np.array(self._res_shape, dtype=np.int32))
        self._gpu_shape_size = to_gpu(
            np.array([len(self._res_shape)], dtype=np.int32))
        self.grid = int(np.prod(self._res_shape))

        self._gpu_size = to_gpu(
            np.array([self.grid], dtype=np.int32))
        self.block, self.thread = grid_alloc(self.grid)

    
    def add(self, a, b, output):
        if self.type == 'identity':
            identity_add_kernel(self.n, a, b, output,
                                grid=(self.cuda_num_blocks, 1, 1),
                                block=(self.cuda_num_threads, 1, 1))
        elif self.type == 'bias':
            if self.mainly == 'left':
                bias_add_kernel(self.n, a, b, output, self.gpu_b_size,
                                grid=(self.cuda_num_blocks, 1, 1),
                                block=(self.cuda_num_threads, 1, 1))
            elif self.mainly == 'right':
                bias_add_kernel(self.n, b, a, output, self.gpu_b_size,
                                grid=(self.cuda_num_blocks, 1, 1),
                                block=(self.cuda_num_threads, 1, 1))
            else:
                raise ValueError('shapetype return an error value.'
                                 'it is internal frame error, please submit to us: '
                                 'smarsu@foxmail.com')
        elif self.type == 'common':
            add_kernel(self.n, a, b, output,
                       self.gpu_pad_shape_a, self.gpu_pad_shape_b, self.gpu_broadcast_shape,
                       self.gpu_shape_size,
                       grid=(self.cuda_num_blocks, 1, 1),
                       block=(self.cuda_num_threads, 1, 1))
        else:
            raise ValueError('shapetype return an error value.'
                                'it is internal frame error, please submit to us: '
                                'smarsu@foxmail.com')

    
    def add_identity(self, a, b, output):
        identity_add_kernel(self.n, a, b, output,
                            grid=(self.cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))


    def add_old(self, a, b, output):
        add_kernel(a, b, output,
                   self._gpu_pad_shape_a, self._gpu_pad_shape_b,
                   self._gpu_broadcast_shape, self._gpu_shape_size,
                   self._gpu_size,
                   grid=self.block, 
                   block=self.thread)


    def add_grad_left(self, a_grad, grad):
        add_grad_kernel(a_grad, grad, 
                        self._gpu_broadcast_shape, 
                        self._gpu_pad_shape_a, 
                        self._gpu_shape_size,
                        self._gpu_size,
                        grid=self.block, 
                        block=self.thread)


    def add_grad_right(self, b_grad, grad):
        add_grad_kernel(b_grad, grad, 
                        self._gpu_broadcast_shape, 
                        self._gpu_pad_shape_b, 
                        self._gpu_shape_size,
                        self._gpu_size,
                        grid=self.block, 
                        block=self.thread)
