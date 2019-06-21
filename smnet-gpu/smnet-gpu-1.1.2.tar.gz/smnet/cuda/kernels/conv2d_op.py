# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *
from .matmul_op import matmul_left_grad_set_kernel

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__device__ int dim4Index(int n, int h, int w, int c,
                         int N, int H, int W, int C)
{
    return c + w * C + h * C * W + n * C * W * H;
}

__device__ int dim6Index(int x, int y, int n, int h, int w, int c,
                         int X, int Y, int N, int H, int W, int C)
{
    return c + w * C + h * C * W + n * C * W * H + y * C * W * H * N + x * C * W * H * N * Y;
}


__global__ void conv2d(const int *n, const float *input, const float *filter,
                       float *output, const int *input_shape,
                       const int *filter_shape, const int *strides,
                       const int *output_shape)
{
    /*
    Just implement the `VALID` type.
    Use pad to solve the `SAME` problem.
    */

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

        float tmp = 0.f;
        for (int h = 0; h < filter_shape[0]; h++) {
            for (int w = 0; w < filter_shape[1]; w++) {
                for (int c = 0; c < filter_shape[2]; c++) {
                    tmp += input[dim4Index(N, h + H * strides[1], w + W * strides[2], c, input_shape[0], input_shape[1], input_shape[2], input_shape[3])] * 
                        filter[dim4Index(h, w, c, C, filter_shape[0], filter_shape[1], filter_shape[2], filter_shape[3])];
                }
            }
        }
        output[tmp_idx] = tmp;
    }
}


__global__ void conv2d_grad(int *n, float *input_grad, float *filter_grad, float *grad,
                            float *input, float *filter,
                            int *input_shape, int *filter_shape, int *strides,
                            int *output_shape) 
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;

        int C = idx % output_shape[3];
        idx /= output_shape[3];
        int W = idx % output_shape[2];
        idx /= output_shape[2];
        int H = idx % output_shape[1];
        idx /= output_shape[1];
        int N = idx;

        for (int h = 0; h < filter_shape[0]; h++) {
            for (int w = 0; w < filter_shape[1]; w++) {
                for (int c = 0; c < filter_shape[2]; c++) {
                    int input_dim = dim4Index(N, h + H * strides[1], w + W * strides[2], c, input_shape[0], input_shape[1], input_shape[2], input_shape[3]);
                    int filter_dim = dim4Index(h, w, c, C, filter_shape[0], filter_shape[1], filter_shape[2], filter_shape[3]);

                    input_grad[input_dim] += filter[filter_dim] * grad[tmp_idx];
                    filter_grad[filter_dim] += input[input_dim] * grad[tmp_idx];
                    __syncthreads();
                }
            }
        }
    }
}


/* 
pass_mask:
    The pass position of the filter(0, 0).
 */
__global__ void conv2d_filter_grad(int *n, float *filter_grad, float *grad,
                                   float *input, int *pass_mask_x, 
                                   int *num_pass_mask_x, int *pass_mask_y, 
                                   int *num_pass_mask_y, int *filter_shape, 
                                   int *output_shape, int *input_shape, int *strides) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;

        int CO = idx % filter_shape[3];
        idx /= filter_shape[3];
        int CI = idx % filter_shape[2];
        idx /= filter_shape[2];
        int W = idx % filter_shape[1];
        idx /= filter_shape[1];
        int H = idx;

        float tmp_grad = 0.f;
        for (int n = 0; n < output_shape[0]; n++) {  /* n: batch */
            for (int h = 0; h < output_shape[1]; h++) {
                for (int w = 0; w < output_shape[2]; w++) {
                    /*tmp_grad += grad[dim4Index(n, h, w, CO,
                                               output_shape[0], 
                                               output_shape[1], 
                                               output_shape[2], 
                                               output_shape[3])] *
                                input[dim4Index(n, pass_mask_y[h] + H, pass_mask_x[w] + W, CI,
                                                input_shape[0], 
                                                input_shape[1], 
                                                input_shape[2], 
                                                input_shape[3])];*/

                    tmp_grad += grad[dim4Index(n, h, w, CO, 
                                               output_shape[0], 
                                               output_shape[1], 
                                               output_shape[2], 
                                               output_shape[3])] *
                                input[dim4Index(n, h * strides[1] + H, w * strides[2] + W, CI,
                                                input_shape[0], 
                                                input_shape[1], 
                                                input_shape[2], 
                                                input_shape[3])];
                }
            }
        }
        filter_grad[tmp_idx] += tmp_grad;
    }
}


/* Please copy from myself.

*/
__global__ void conv2d_input_grad(int *n, float *input_grad, float *grad,
                                  float *filter, int *input_shape, 
                                  int *output_shape, int *strides, 
                                  int *filter_shape) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;

        int C = idx % input_shape[3];
        idx /= input_shape[3];
        int W = idx % input_shape[2];
        idx /= input_shape[2];
        int H = idx % input_shape[1];
        idx /= input_shape[1];
        int N = idx;

        float tmp_grad = 0.f;
        for (int h = 0; h < output_shape[1]; h++) {
            for (int w = 0; w < output_shape[2]; w++) {
                int h_offset = H - h * strides[1];
                int w_offset = W - w * strides[2];
                if (h_offset >= 0 && 
                    h_offset < filter_shape[0] &&
                    w_offset >= 0 &&
                    w_offset < filter_shape[1]) {

                    /*tmp_grad += grad[dim6Index(N, h, w, h_offset, w_offset, C,
                                          output_shape[0], 
                                          output_shape[1], 
                                          output_shape[2], 
                                          filter_shape[0], 
                                          filter_shape[1], 
                                          filter_shape[2])];*/

                    for (int c = 0; c < output_shape[3]; c ++) {
                        tmp_grad += grad[dim4Index(N, h, w, c, 
                                          output_shape[0], 
                                          output_shape[1], 
                                          output_shape[2],
                                          output_shape[3] )] * 
                                    filter[dim4Index(h_offset, w_offset, C, c,
                                            filter_shape[0], 
                                          filter_shape[1], 
                                          filter_shape[2],
                                          filter_shape[3])];
                    }
                }
            }
        }

        input_grad[tmp_idx] += tmp_grad;
    }
}
""")

conv2d_kernel = kernel.get_function('conv2d')
conv2d_grad_kernel = kernel.get_function('conv2d_grad')
conv2d_filter_grad_kernel = kernel.get_function('conv2d_filter_grad')
conv2d_input_grad_kernel = kernel.get_function('conv2d_input_grad')


class Conv2dOp(OpKernel):
    def __init__(self, input_shape, filter_shape, strides, output_shape):
        self.gpu_input_shape = to_gpu(np.array(input_shape, dtype=np.int32))
        self.gpu_filter_shape = to_gpu(np.array(filter_shape, dtype=np.int32))
        self.gpu_strides = to_gpu(np.array(strides, dtype=np.int32))
        self.gpu_output_shape = to_gpu(np.array(output_shape, dtype=np.int32))

        self.size = int(np.prod(output_shape))
        self.n = to_gpu(np.array(self.size, dtype=np.int32))
        self.cuda_num_blocks = self.get_cuda_num_blocks()

        self.n_filter = to_gpu(np.prod(filter_shape).astype(np.int32))
        self.mask_x = np.array(range(0, input_shape[2], strides[2]), 
                               dtype=np.int32)
        self.gpu_mask_x = to_gpu(self.mask_x)
        self.gpu_num_mask_x = to_gpu(np.array(self.mask_x.size, dtype=np.int32))
        self.mask_y = np.array(range(0, input_shape[1], strides[1]),
                               dtype=np.int32)
        self.gpu_mask_y = to_gpu(self.mask_y)
        self.gpu_num_mask_y = to_gpu(np.array(self.mask_y.size, dtype=np.int32))

        input_tmp_size = int(np.prod(output_shape[:3]) * np.prod(filter_shape[:3]))
        self.gpu_tmp_input_grad = gpu_empty(input_tmp_size)
        self.n_input_tmp = to_gpu(np.array(input_tmp_size, dtype=np.int32))
        self.gpu_k = to_gpu(np.array(filter_shape[-1], dtype=np.int32))
        self.gpu_m = to_gpu(np.prod(filter_shape[:3]).astype(np.int32))

        input_size = int(np.prod(input_shape))
        self.n_input = to_gpu(np.array(input_size, dtype=np.int32))

        self.filter_cuda_num_blocks = self.get_cuda_num_blocks(int(np.prod(filter_shape)))
        self.input_tmp_cuda_num_blocks = self.get_cuda_num_blocks(input_tmp_size)
        self.input_cuda_num_blocks = self.get_cuda_num_blocks(input_size)

    
    def conv2d(self, input, filter, output):
        conv2d_kernel(self.n, input, filter, output, 
                      self.gpu_input_shape, self.gpu_filter_shape,
                      self.gpu_strides, self.gpu_output_shape,
                      grid=(self.cuda_num_blocks, 1, 1),
                      block=(self.cuda_num_threads, 1, 1))


    def conv2d_grad(self, input_grad, filter_grad, grad, input, filter):
        conv2d_grad_kernel(self.n, input_grad, filter_grad, grad,
                           input, filter, self.gpu_input_shape, 
                           self.gpu_filter_shape, self.gpu_strides,
                           self.gpu_output_shape,
                           grid=(self.cuda_num_blocks, 1, 1),
                           block=(self.cuda_num_threads, 1, 1))

    
    def conv2d_input_grad(self, filter, grad, input_grad):
        #matmul_left_grad_set_kernel(self.n_input_tmp, self.gpu_tmp_input_grad, filter,
        #                            grad,
        #                            self.gpu_k, self.gpu_m,
        #                            grid=(self.input_tmp_cuda_num_blocks, 1, 1),
        #                            block=(self.cuda_num_threads, 1, 1))
        conv2d_input_grad_kernel(self.n_input, input_grad, grad, #self.gpu_tmp_input_grad,
                                 filter, self.gpu_input_shape, 
                                 self.gpu_output_shape, self.gpu_strides, 
                                 self.gpu_filter_shape,
                                 grid=(self.input_cuda_num_blocks, 1, 1),
                                 block=(self.cuda_num_threads, 1, 1))

    
    def conv2d_filter_grad(self, input, grad, filter_grad):
        conv2d_filter_grad_kernel(self.n_filter, filter_grad, grad,
                                   input, self.gpu_mask_x, 
                                   self.gpu_num_mask_x, self.gpu_mask_y, 
                                   self.gpu_num_mask_y, self.gpu_filter_shape, 
                                   self.gpu_output_shape, self.gpu_input_shape, self.gpu_strides,
                                   grid=(self.filter_cuda_num_blocks, 1, 1),
                                   block=(self.cuda_num_threads, 1, 1))
