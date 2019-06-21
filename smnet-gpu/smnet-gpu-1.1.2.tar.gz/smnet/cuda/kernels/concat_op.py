# --------------------------------------------------------
# SMNet conv2d cuda kernel
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

from .op_kernel import *

kernel = SourceModule("""
#define MAX_SHAPE_SIZE 8


__global__ void concat(int *n, float *input, float *output,
                       int *input_shape, int *output_shape,
                       int *begin, int *axis,
                       int *shape_size)
{
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;
        int cur_dims[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            cur_dims[i] = idx % input_shape[i];
            idx /= input_shape[i];
        }
        cur_dims[*axis] += *begin;
        
        int output_index = 0, factor = 1;
        for (int i = *shape_size - 1; i >= 0; i--) {
            output_index += cur_dims[i] * factor;
            factor *= output_shape[i];
        }
        output[output_index] = input[tmp_idx];
    }
}


__global__ void concat_grad(int *n, float *top_grad, float *bottom_grad,
                            int *input_shape, int *output_shape,
                            int *begin, int *axis,
                            int *shape_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *n) {
        int tmp_idx = idx;
        int cur_dims[MAX_SHAPE_SIZE];
        for (int i = *shape_size - 1; i >= 0; i--) {
            cur_dims[i] = idx % input_shape[i];
            idx /= input_shape[i];
        }
        cur_dims[*axis] += *begin;
        
        int output_index = 0, factor = 1;
        for (int i = *shape_size - 1; i >= 0; i--) {
            output_index += cur_dims[i] * factor;
            factor *= output_shape[i];
        }
        bottom_grad[tmp_idx] += top_grad[output_index];
    }
}
""")

concat_kernel = kernel.get_function('concat')
concat_grad_kernel = kernel.get_function('concat_grad')


class ConcatOp(OpKernel):
    def __init__(self, input_shapes, axis):
        if axis < 0:
            axis += len(input_shapes[0])
        correspond_dims = [shape[axis] for shape in input_shapes]
        begins = [sum(correspond_dims[:i]) for i in range(len(correspond_dims))]

        self.res_shape = tuple(dims[0] if index != axis else sum(dims) 
                               for index, dims in enumerate(zip(*input_shapes)))

        self.gpu_input_shapes = [to_gpu(np.array(shape, dtype=np.int32))
                                 for shape in input_shapes]
        self.gpu_output_shape = to_gpu(np.array(self.res_shape, dtype=np.int32))
        self.gpu_begins = [to_gpu(np.array(begin, np.int32))
                           for begin in begins]
        self.gpu_axis = to_gpu(np.array(axis, np.int32))
        self.gpu_shape_size = to_gpu(np.array(len(self.res_shape), dtype=np.int32))

        self.size = int(np.prod(self.res_shape))
        self.sizes = [int(np.prod(shape)) for shape in input_shapes]
        self.ns = [to_gpu(np.array(size, dtype=np.int32)) for size in self.sizes]
        self.cuda_num_blocks_arr = self.get_cuda_num_blocks_arr()


    def concat(self, inputs, output):
        for n, input, gpu_input_shape, gpu_begin, cuda_num_blocks in zip(
          self.ns, inputs, self.gpu_input_shapes, self.gpu_begins,
          self.cuda_num_blocks_arr):
            concat_kernel(n, input, output,
                          gpu_input_shape, self.gpu_output_shape,
                          gpu_begin, self.gpu_axis,
                          self.gpu_shape_size,
                          grid=(cuda_num_blocks, 1, 1),
                          block=(self.cuda_num_threads, 1, 1))

    
    def concat_grad(self, top_grad, bottom_grads):
        for n, bottom_grad, gpu_input_shape, gpu_begin, cuda_num_blocks in zip(
          self.ns, bottom_grads, self.gpu_input_shapes, self.gpu_begins,
          self.cuda_num_blocks_arr):
            concat_grad_kernel(n, top_grad, bottom_grad,
                               gpu_input_shape, self.gpu_output_shape,
                               gpu_begin, self.gpu_axis,
                               self.gpu_shape_size,
                               grid=(cuda_num_blocks, 1, 1),
                               block=(self.cuda_num_threads, 1, 1))
