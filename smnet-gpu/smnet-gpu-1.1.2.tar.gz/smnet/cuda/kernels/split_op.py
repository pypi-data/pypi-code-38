# --------------------------------------------------------
# SMNet cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8

__global__ void split(int *n, float *input, float *output, 
                      int *input_shape, int *output_shape,
                      int *axis, int *begin, int *shape_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int idx_tmp = idx;
        int cur_dims[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            cur_dims[i] = idx % output_shape[i];
            idx /= output_shape[i];
        }
        cur_dims[*axis] += *begin;
        int input_idx = 0, factor = 1;
        for (int i = *shape_size - 1; i >= 0; i--) {
            input_idx += cur_dims[i] * factor;
            factor *= input_shape[i];
        }
        output[idx_tmp] = input[input_idx];
    }
}


__global__ void split_grad(int *n, float *top_grad, float *bottom_grad, 
                          int *input_shape, int *output_shape,
                          int *axis, int *begin, int *shape_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int idx_tmp = idx;
        int cur_dims[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            cur_dims[i] = idx % output_shape[i];
            idx /= output_shape[i];
        }
        cur_dims[*axis] += *begin;
        int input_idx = 0, factor = 1;
        for (int i = *shape_size - 1; i >= 0; i--) {
            input_idx += cur_dims[i] * factor;
            factor *= input_shape[i];
        }
        bottom_grad[input_idx] += top_grad[idx_tmp];
    }
}
""")

split_kernel = kernel.get_function('split')
split_grad_kernel = kernel.get_function('split_grad')


class SplitOp(OpKernel):
    def __init__(self, input_shape, size_splits, axis):
        """size_splits: [1, 2, 2, 1]"""
        begins = [sum(size_splits[:i]) for i in range(len(size_splits))]  # sum([]) == 0
        if axis < 0:
            axis += len(input_shape)

        self.res_shapes = [tuple(dim if index != axis else size_split for index, dim in enumerate(input_shape))
                           for size_split in size_splits]
        self.gpu_input_shape = to_gpu(np.array(input_shape, dtype=np.int32))
        self.gpu_output_shapes = [to_gpu(np.array(output_shape, dtype=np.int32))
                                  for output_shape in self.res_shapes]
        self.gpu_axis = to_gpu(np.array(axis, dtype=np.int32))
        self.gpu_begins = [to_gpu(np.array(begin, dtype=np.int32))
                           for begin in begins]
        self.gpu_shape_size = to_gpu(np.array(len(input_shape), dtype=np.int32))
        
        self.sizes = [int(np.prod(shape)) for shape in self.res_shapes]
        self.ns = [to_gpu(np.array(size, dtype=np.int32)) for size in self.sizes]
        self.cuda_num_blocks_arr = self.get_cuda_num_blocks_arr()


    def split(self, input, outputs):
        for output, n, gpu_output_shape, gpu_begin, cuda_num_blocks in zip(
            outputs, self.ns, self.gpu_output_shapes, self.gpu_begins,
            self.cuda_num_blocks_arr):
            split_kernel(n, input, output, 
                         self.gpu_input_shape, gpu_output_shape,
                         self.gpu_axis, gpu_begin, self.gpu_shape_size,
                         grid=(cuda_num_blocks, 1, 1),
                         block=(self.cuda_num_threads, 1, 1))

    
    def split_grad(self, top_grads, bottom_grad):
        for top_grad, n, gpu_output_shape, gpu_begin, cuda_num_blocks in zip(
            top_grads, self.ns, self.gpu_output_shapes, self.gpu_begins,
            self.cuda_num_blocks_arr):
            split_grad_kernel(n, top_grad, bottom_grad, 
                            self.gpu_input_shape, gpu_output_shape,
                            self.gpu_axis, gpu_begin, self.gpu_shape_size,
                            grid=(cuda_num_blocks, 1, 1),
                            block=(self.cuda_num_threads, 1, 1))
