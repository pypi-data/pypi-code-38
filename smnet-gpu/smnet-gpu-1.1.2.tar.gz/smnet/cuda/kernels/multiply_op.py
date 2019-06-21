# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__global__ void multiply(int *n, float *a, float *b, float *c,
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
        c[tmp_idx] = a[a_ind] * b[b_ind];
    }
}

__global__ void bias_multiply(int *n, float *a, float *b, float *output,
                              int *b_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = a[idx] * b[idx % *b_size];
    }
}

__global__ void identity_multiply(int *n, float *a, float *b, float *output)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        output[idx] = a[idx] * b[idx];
    }
}


__global__ void identity_grad(int *n, float *grad, float *input, 
                                  float *grad_output) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        grad_output[idx] += grad[idx] * input[idx];
    }
}

__global__ void bias_grad(int *n, float *grad, float *input, 
                          float *grad_output, int *size_broadcast) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        float grad_tmp = 0.f;
        int start_index_of_grad = *size_broadcast * idx;
        for (int i = 0; i < *size_broadcast; i++) 
            grad_tmp += grad[start_index_of_grad + i];
        grad_output[idx] += grad_tmp;
    }
}
""")

multiply_kernel = kernel.get_function('multiply')
bias_multiply_kernel = kernel.get_function('bias_multiply')
identity_multiply_kernel = kernel.get_function('identity_multiply')
bias_multiply_grad_kernel = kernel.get_function('bias_grad')
identity_multiply_grad_kernel = kernel.get_function('identity_grad')


class MultiplyOp(OpKernel):
    def __init__(self, shape_a, shape_b):
        res_shape, pad_shape_a, pad_shape_b = broadcast(shape_a, shape_b)
        self.pad_shape_a = pad_shape_a
        self.pad_shape_b = pad_shape_b

        self.res_shape = res_shape
        self.type, self.mainly = shapetype(shape_a, shape_b, res_shape)

        if self.type == 'identity':
            pass
        elif self.type == 'bias':
            if self.mainly == 'left':
                self.gpu_b_size = to_gpu(np.prod(shape_b).astype(np.int32))

                size_broadcast = np.prod(res_shape) / np.prod(shape_b)
                self.gpu_size_broadcast = to_gpu(size_broadcast.astype(np.int32))
                assert int(size_broadcast) != 1
            elif self.mainly == 'right':
                self.gpu_b_size = to_gpu(np.prod(shape_a).astype(np.int32))

                size_broadcast = np.prod(res_shape) / np.prod(shape_a)
                self.gpu_size_broadcast = to_gpu(size_broadcast.astype(np.int32))
                assert int(size_broadcast) != 1
            else:
                raise ValueError('shapetype return an error value.'
                                 'it is internal frame error, please submit to us: '
                                 'smarsu@foxmail.com')
        elif self.type == 'common':
            self.gpu_pad_shape_a = to_gpu(np.array(pad_shape_a, dtype=np.int32))
            self.gpu_pad_shape_b = to_gpu(np.array(pad_shape_b, dtype=np.int32))
            self.gpu_broadcast_shape = to_gpu(np.array(res_shape, dtype=np.int32))
            self.gpu_shape_size = to_gpu(np.array(len(res_shape), dtype=np.int32))
        else:
            raise ValueError('shapetype return an error value.'
                             'it is internal frame error, please submit to us: '
                             'smarsu@foxmail.com')

        self.size = int(np.prod(res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

    
    def multiply(self, a, b, output):
        if self.type == 'identity':
            identity_multiply_kernel(self.n, a, b, output,
                                     grid=(self.cuda_num_blocks, 1, 1),
                                     block=(self.cuda_num_threads, 1, 1))
        elif self.type == 'bias':
            if self.mainly == 'left':
                bias_multiply_kernel(self.n, a, b, output, self.gpu_b_size,
                                     grid=(self.cuda_num_blocks, 1, 1),
                                     block=(self.cuda_num_threads, 1, 1))
            elif self.mainly == 'right':
                bias_multiply_kernel(self.n, b, a, output, self.gpu_b_size,
                                     grid=(self.cuda_num_blocks, 1, 1),
                                     block=(self.cuda_num_threads, 1, 1))
            else:
                raise ValueError('shapetype return an error value.'
                                 'it is internal frame error, please submit to us: '
                                 'smarsu@foxmail.com')
        elif self.type == 'common':
            multiply_kernel(self.n, a, b, output,
                            self.gpu_pad_shape_a, self.gpu_pad_shape_b, self.gpu_broadcast_shape,
                            self.gpu_shape_size,
                            grid=(self.cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))
        else:
            raise ValueError('shapetype return an error value.'
                                'it is internal frame error, please submit to us: '
                                'smarsu@foxmail.com')
    

    def multiply_grad(self, grad, a, b, grad_a, grad_b):
        if self.type == 'identity':
            identity_multiply_grad_kernel(self.n, grad, b, grad_a,
                                          grid=(self.cuda_num_blocks, 1, 1),
                                          block=(self.cuda_num_threads, 1, 1))
            identity_multiply_grad_kernel(self.n, grad, a, grad_b,
                                          grid=(self.cuda_num_blocks, 1, 1),
                                          block=(self.cuda_num_threads, 1, 1))
        elif self.type == 'bias':
            if self.mainly == 'left':
                identity_multiply_grad_kernel(self.n, grad, b, grad_a,
                                              grid=(self.cuda_num_blocks, 1, 1),
                                              block=(self.cuda_num_threads, 1, 1))
                bias_multiply_grad_kernel(self.gpu_b_size, grad, a, 
                                          grad_b, self.gpu_size_broadcast)
            elif self.mainly == 'right':
                identity_multiply_grad_kernel(self.n, grad, a, grad_b,
                                              grid=(self.cuda_num_blocks, 1, 1),
                                              block=(self.cuda_num_threads, 1, 1))
                bias_multiply_grad_kernel(self.gpu_b_size, grad, b, 
                                          grad_a, self.gpu_size_broadcast)
            else:
                raise ValueError('shapetype return an error value.'
                                 'it is internal frame error, please submit to us: '
                                 'smarsu@foxmail.com')
        elif self.type == 'common':
            raise NotImplementedError
        else:
            raise ValueError('shapetype return an error value.'
                             'it is internal frame error, please submit to us: '
                             'smarsu@foxmail.com')
