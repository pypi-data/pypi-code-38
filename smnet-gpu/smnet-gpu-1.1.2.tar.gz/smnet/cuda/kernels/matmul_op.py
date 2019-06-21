# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__global__ void matmul(int *n, float *a, float *b, float *output,
                       int *k, int *m)
{
    /*
    Args:
        a: shape [n, k]
        b: shape [k, m]    
    */
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int row = idx / *m;
        int col = idx % *m;

        int row_ind = row * *k;
        float tmp = 0.f;
        for (int i = 0; i < *k; i++) {
            tmp += a[row_ind + i] * b[*m * i + col];
        }
        output[idx] = tmp;
    }
}

__global__ void matmul_left_grad(int *n, float *a_grad, float *b,
                                 float *grad,
                                 int *k, int *m)
{
    // Use tmp for accelerate.
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int inds[2] = {__fdividef(idx, *k), idx % *k};
        float tmp = 0.f;
        for (int i = 0; i < *m; i++) {
            tmp += grad[inds[0] * *m + i] * b[inds[1] * *m + i];
        }
        a_grad[idx] += tmp;
    }
}

__global__ void matmul_right_grad(int *n, float *b_grad, float *a,
                                  float *grad,
                                  int *dim1, int *m, int *k) 
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int inds[2] = {__fdividef(idx, *m), idx % *m};
        float tmp = 0.f;
        for (int i = 0; i < *dim1; i++) {
            tmp += grad[i * *m + inds[1]] * a[i * *k + inds[0]];
        }
        b_grad[idx] += tmp;
    }
}

__global__ void matmul_grad(int *n, float *a_grad, float *b_grad,
                            float *grad,
                            float *a, float *b,
                            int *k, int *m)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int row = idx / *m;
        int col = idx % *m;

        int row_ind = row * *k;
        for (int i = 0; i < *k; i++) {
            a_grad[row_ind + i] += b[*m * i + col] * grad[idx];
            b_grad[*m * i + col] += a[row_ind + i] * grad[idx];
        }
    }
}


__global__ void matmul_left_grad_set(int *n, float *a_grad, float *b,
                                     float *grad,
                                     int *k, int *m)
{
    // Use tmp for accelerate.
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int inds[2] = {__fdividef(idx, *k), idx % *k};
        float tmp = 0.f;
        for (int i = 0; i < *m; i++) {
            tmp += grad[inds[0] * *m + i] * b[inds[1] * *m + i];
        }
        a_grad[idx] = tmp;
    }
}
""")

matmul_kernel = kernel.get_function('matmul')
matmul_grad_kernel = kernel.get_function('matmul_grad')
matmul_left_grad_kernel = kernel.get_function('matmul_left_grad')
matmul_right_grad_kernel = kernel.get_function('matmul_right_grad')
matmul_left_grad_set_kernel = kernel.get_function('matmul_left_grad_set')


class MatmulOp(OpKernel):
    def __init__(self, shape_a, shape_b):
        """c = cuda.matmul(a, b)

        Args:
            shape_a:
            shape_b:
        """
        self._n, self._k = shape_a
        _, self._m = shape_b
        self._output_size = self._n * self._m
        self.res_shape = (self._n, self._m)

        self.gpu_dim1 = to_gpu(np.array(self._n, dtype=np.int32))
        self.gpu_k = to_gpu(np.array(self._k, dtype=np.int32))
        self.gpu_m = to_gpu(np.array(self._m, dtype=np.int32))

        self.n_left = to_gpu(np.prod(shape_a).astype(np.int32))
        self.n_right = to_gpu(np.prod(shape_b).astype(np.int32))

        self.size = int(np.prod(self.res_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

        self.left_cuda_num_blocks = self.get_cuda_num_blocks(int(np.prod(shape_a)))
        self.right_cuda_num_blocks = self.get_cuda_num_blocks(int(np.prod(shape_b)))


    def matmul(self, a, b, output):
        matmul_kernel(self.n, a, b, output,
                      self.gpu_k, self.gpu_m,
                      grid=(self.cuda_num_blocks, 1, 1),
                      block=(self.cuda_num_threads, 1, 1))


    def matmul_left_grad(self, a_grad, b, grad):
        matmul_left_grad_kernel(self.n_left, a_grad, b,
                                grad,
                                self.gpu_k, self.gpu_m,
                                grid=(self.left_cuda_num_blocks, 1, 1),
                                block=(self.cuda_num_threads, 1, 1))

    
    def matmul_right_grad(self, b_grad, a, grad):
        matmul_right_grad_kernel(self.n_right, b_grad, a,
                                  grad,
                                  self.gpu_dim1, self.gpu_m, self.gpu_k,
                                  grid=(self.right_cuda_num_blocks, 1, 1),
                                  block=(self.cuda_num_threads, 1, 1))

    
    def matmul_grad(self, a_grad, b_grad, grad, a, b):
        matmul_grad_kernel(self.n, a_grad, b_grad, grad,
                           a, b,
                           self.gpu_k, self.gpu_m,
                           grid=(self.cuda_num_blocks, 1, 1),
                           block=(self.cuda_num_threads, 1, 1))
