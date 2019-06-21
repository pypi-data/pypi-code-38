# --------------------------------------------------------
# SMNet cuda layer
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Cuda layers, forward and backward are computed on the device gpu."""

import math
import numpy as np

from ..blob import Tensor, Variable
from ..layer import Layer
from . import cuda_ops as cuda
from .cuda import gpu_empty, to_cpu, to_gpu, broadcast, gpu_zeros
from .kernels import *


def convert_shape(src_shape, dst_shape):
    """Handle -1 in shape"""
    if -1 in dst_shape:
        convert_v = int(-np.prod(src_shape) // np.prod(dst_shape))
        return tuple(dim if dim != -1 else convert_v for dim in dst_shape)
    else:
        return dst_shape


class GpuLayer(Layer):
    """Basic gpu layer."""

    def __init__(self, stop_grad, name='GpuLayer'):
        super(GpuLayer, self).__init__(stop_grad=stop_grad, name=name)


    def reshape(self):
        """Adjust the shapes of top blobs and internal buffers to accommodate
            the shapes of the bottom blobs.

        This method should reshape top blobs as needed according to the shapes
        of the bottom (input) blobs, as well as reshaping any internal buffers
        and making any other necessary adjustments so that the layer can
        accommodate the bottom blobs.

        Reference:
            Caffe Layer::Reshape
                https://github.com/BVLC/caffe/blob/master/include/caffe/layer.hpp
        """
        raise NotImplementedError


class GpuMatmul(GpuLayer):
    """There are a very strange matmul bug."""
    def __init__(self, a, b, stop_grad, name):
        super(GpuMatmul, self).__init__(stop_grad=stop_grad, name=name)
        self._setup(a, b)


    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()


    def reshape(self):
        self.matmul_op = MatmulOp(self.a.shape, self.b.shape)
        self.res.reshape(shape=self.matmul_op.res_shape)

        self.trans_left_op = TransposeOp(self.a.shape, (1, 0), self.a.size)
        self.trans_right_op = TransposeOp(self.b.shape, (1, 0), self.b.size)
        self.trans_left = gpu_empty(self.a.size)
        self.trans_right = gpu_empty(self.b.size)

        self.matmul_left_op = MatmulOp(self.res.shape, self.b.shape[::-1])
        self.matmul_right_op = MatmulOp(self.a.shape[::-1], self.res.shape)
        self.left_grad = gpu_empty(self.a.size)
        self.right_grad = gpu_empty(self.b.size)

        self.left_grad_add_op = AddOp(self.a.shape, self.a.shape)
        self.right_grad_add_op = AddOp(self.b.shape, self.b.shape)


    def forward(self):
        self.matmul_op.matmul(self.a.gpu_data, 
                              self.b.gpu_data, 
                              self.res.gpu_data)


    def backward(self):
        self.trans_left_op(self.a.gpu_data, self.trans_left)
        self.trans_right_op(self.b.gpu_data, self.trans_right)
        self.matmul_left_op.matmul(self.res.gpu_grad, self.trans_right, self.left_grad)
        self.matmul_right_op.matmul(self.trans_left, self.res.gpu_grad, self.right_grad)
        self.left_grad_add_op.add_identity(self.a.gpu_grad, self.left_grad, self.a.gpu_grad)
        self.right_grad_add_op.add_identity(self.b.gpu_grad, self.right_grad, self.b.gpu_grad)
        #self.matmul_op.matmul_left_grad(self.a.gpu_grad, self.b.gpu_data, self.res.gpu_grad)
        #self.matmul_op.matmul_right_grad(self.b.gpu_grad, self.a.gpu_data, self.res.gpu_grad)


class GpuAdd(GpuLayer):
    def __init__(self, a, b, stop_grad, name):
        super(GpuAdd, self).__init__(stop_grad, name)
        self._setup(a, b)

    
    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def reshape(self):
        self.add_op = AddOp(self.a.shape, self.b.shape)
        self.res.reshape(self.add_op.res_shape)


    def forward(self):
        self.add_op.add(self.a.gpu_data, 
                        self.b.gpu_data, 
                        self.res.gpu_data)


    def backward(self):
        grad = self.res.gpu_grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)


    def _compute_grad_a(self, grad):
        self.add_op.add_grad_left(self.a.gpu_grad, grad)

    
    def _compute_grad_b(self, grad):
        self.add_op.add_grad_right(self.b.gpu_grad, grad)

    
class GpuMultiply(GpuLayer):
    def __init__(self, a, b, stop_grad, name):
        super(GpuMultiply, self).__init__(stop_grad, name)
        self._setup(a, b)
    

    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def reshape(self):
        self.multiply_op = MultiplyOp(self.a.shape, self.b.shape)
        self.res.reshape(self.multiply_op.res_shape)

    
    def forward(self):
        self.multiply_op.multiply(self.a.gpu_data, 
                                  self.b.gpu_data, 
                                  self.res.gpu_data)


    def backward(self):
        self.multiply_op.multiply_grad(self.res.gpu_grad, self.a.gpu_data,
                                       self.b.gpu_data, self.a.gpu_grad, 
                                       self.b.gpu_grad)


class GpuBiasAdd(GpuLayer):
    """Adds bias to value.
    
    This is (mostly) a special case of tf.add where bias is restricted to 1-D.
    Broadcasting is supported, so value may have any number of dimensions. 
    """
    def __init__(self, value, bias, stop_grad, name):
        super(GpuBiasAdd, self).__init__(stop_grad, name)
        self._setup(value, bias)


    def _setup(self, value, bias):
        self.value = value
        self.bias = bias
        self.res = Tensor()

    
    def reshape(self):
        # 1. Setup gpu data
        self.bias_size = self.bias.size
        self.gpu_bias_size = to_gpu(np.array([self.bias.size], dtype=np.int32))
        self.value_size = self.value.size
    
        # 2. reshape
        self.res.reshape(self.value.shape)


    def forward(self):
        # 1. Prepare data
        value = self.value
        bias = self.bias

        cuda.bias_add(value.gpu_data, bias.gpu_data, self.res.gpu_data,
                      self.gpu_bias_size,
                      grid=(self.value_size, 1, 1), block=(1, 1, 1))


    def backward(self):
        raise NotImplementedError


class GpuDivide(GpuLayer):
    def __init__(self, a, b, stop_grad, name):
        super(GpuDivide, self).__init__(stop_grad, name)
        self._setup(a, b)


    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def reshape(self):
        self.divide_op = DivideOp(self.a.shape, self.b.shape)
        self.res.reshape(self.divide_op.res_shape)


    def forward(self):
        self.divide_op.divide(self.a.gpu_data, self.b.gpu_data, self.res.gpu_data)


    def backward(self):
        self._compute_grad_a()
        self._compute_grad_b()

    
    def _compute_grad_a(self):
        self.divide_op.divide_grad_left(self.b.gpu_data, 
                                        self.res.gpu_grad, 
                                        self.a.gpu_grad)


    def _compute_grad_b(self):
        self.divide_op.divide_grad_right(self.a.gpu_data, 
                                         self.b.gpu_data, 
                                         self.res.gpu_grad, 
                                         self.b.gpu_grad)


class GpuExp(GpuLayer):
    def __init__(self, a, stop_grad, name):
        super(GpuExp, self).__init__(stop_grad, name)
        self._setup(a)

    
    def _setup(self, a):
        self.a = self._to_tensor(a)
        self.res = Tensor()

    
    def reshape(self):
        self.exp_op = ExpOp(self.a.shape)
        self.res.reshape(self.exp_op.res_shape)

    
    def forward(self):
        self.exp_op.exp(self.a.gpu_data, self.res.gpu_data)

    
    def backward(self):
        self.exp_op.exp_grad(self.res.gpu_grad, self.res.gpu_data, 
                             self.a.gpu_grad)


class GpuRelu(GpuLayer):
    def __init__(self, a, stop_grad, name):
        super(GpuRelu, self).__init__(stop_grad, name)
        self._setup(a)


    def _setup(self, a):
        self.a = a
        self.res = Tensor()


    def reshape(self):
        self.relu_op = ReluOp(self.a.shape, self.a.size)
        self.res.reshape(self.relu_op.res_shape)


    def forward(self):
        self.relu_op.relu(self.a.gpu_data, self.res.gpu_data)


    def backward(self):
        grad = self.res.gpu_grad
        self._compute_grad_a(grad)

    
    def _compute_grad_a(self, grad):
        self.relu_op.relu_grad(self.a.gpu_grad, grad, self.a.gpu_data)


class GpuTanh(GpuLayer):
    def __init__(self, a, stop_grad, name):
        super(GpuTanh, self).__init__(stop_grad, name)
        self._setup(a)

    
    def _setup(self, a):
        self.a = self._to_tensor(a)
        self.res = Tensor()


    def reshape(self):
        self.tanh_op = TanhOp(self.a.shape)
        self.res.reshape(self.tanh_op.res_shape)

    
    def forward(self):
        self.tanh_op.tanh(self.a.gpu_data, self.res.gpu_data)

    
    def backward(self):
        self.tanh_op.tanh_grad(self.res.gpu_grad, self.res.gpu_data,
                               self.a.gpu_grad)


class GpuSigmoid(GpuLayer):
    def __init__(self, a, stop_grad, name):
        super(GpuSigmoid, self).__init__(stop_grad, name)
        self._setup(a)

    
    def _setup(self, a):
        self.a = self._to_tensor(a)
        self.res = Tensor()

    
    def reshape(self):
        self.sigmoid_op = SigmoidOp(self.a.shape)
        self.res.reshape(self.sigmoid_op.res_shape)

    
    def forward(self):
        self.sigmoid_op.sigmoid(self.a.gpu_data, self.res.gpu_data)

    
    def backward(self):
        self.sigmoid_op.sigmoid_grad(self.res.gpu_grad, self.res.gpu_data,
                                     self.a.gpu_grad)


class GpuHse(GpuLayer):
    def __init__(self, labels, logits, stop_grad, name):
        super(GpuHse, self).__init__(stop_grad, name)
        self._setup(labels, logits)


    def _setup(self, labels, logits):
        self.labels = self._to_tensor(labels)
        self.logits = self._to_tensor(logits)
        self.res = Tensor()


    def reshape(self):
        self.hse_op = HseOp(self.labels.shape)
        self.res.reshape(self.hse_op.res_shape)


    def forward(self):
        self.hse_op.hse(self.labels.gpu_data, 
                        self.logits.gpu_data, 
                        self.res.gpu_data)


    def backward(self):
        self.hse_op.hse_grad(self.res.gpu_grad, self.labels.gpu_data, self.logits.gpu_data, 
                             self.labels.gpu_grad, self.logits.gpu_grad)


class GpuSubtract(GpuLayer):
    def __init__(self, a, b, stop_grad, name):
        super(GpuSubtract, self).__init__(stop_grad, name)
        self._setup(a, b)


    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def reshape(self):
        self.subtract_op = SubtractOp(self.a.shape, self.b.shape)
        self.res.reshape(self.subtract_op.res_shape)

    
    def forward(self):
        self.subtract_op.subtract(self.a.gpu_data, 
                                  self.b.gpu_data, 
                                  self.res.gpu_data)

    
    def backward(self):
        self._compute_grad_a()
        self._compute_grad_b()


    def _compute_grad_a(self):
        self.subtract_op.subtract_grad_left(self.res.gpu_grad, 
                                            self.a.gpu_grad)

            
    def _compute_grad_b(self):
        self.subtract_op.subtract_grad_right(self.res.gpu_grad, 
                                             self.b.gpu_grad)


class GpuTranspose(GpuLayer):
    def __init__(self, x, perm, stop_grad, name):
        super(GpuTranspose, self).__init__(stop_grad, name)
        self._setup(x, perm)

    
    def _setup(self, x, perm):
        self.x = x
        self.perm = perm
        self.res = Tensor()


    def reshape(self):
        src_shape = self.x.shape
        self.gpu_perm = to_gpu(np.array(self.perm, dtype=np.int32))
        self.gpu_src_shape = to_gpu(np.array(src_shape, dtype=np.int32))
        self.gpu_shape_size = to_gpu(np.array([len(src_shape)], dtype=np.int32))
        self.grid_size = self.x.size

        self.res.reshape([src_shape[ind] for ind in self.perm])


    def forward(self):
        # 1. Prepare data
        x = self.x

        # 2. Compute and feed result
        cuda.transpose(x.gpu_data, self.res.gpu_data,
                       self.gpu_perm, self.gpu_src_shape, self.gpu_shape_size,
                       grid=(self.grid_size, 1, 1), block=(1, 1, 1))

    
    def backward(self):
        raise NotImplementedError


class GpuReshape(GpuLayer):
    def __init__(self, tensor, shape, stop_grad, name):
        super(GpuReshape, self).__init__(stop_grad, name)
        self._setup(tensor, shape)

    
    def _setup(self, tensor, shape):
        self.tensor = self._to_tensor(tensor)
        self.shape = shape
        self.res = Tensor()

    
    def reshape(self):
        self.res_shape = convert_shape(self.tensor.shape, self.shape)
        self.res.reshape(self.res_shape)
        self.reshape_op = ReshapeOp(self.res_shape)


    def forward(self):
        self.reshape_op.reshape(self.tensor.gpu_data, self.res.gpu_data)


    def backward(self):
        self.reshape_op.reshape_grad(self.res.gpu_grad, self.tensor.gpu_grad)


class GpuPad(GpuLayer):
    def __init__(self, x, pad_width, pad_value, stop_grad, name):
        super(GpuPad, self).__init__(stop_grad, name)
        self._setup(x, pad_width, pad_value)

    
    def _setup(self, x, pad_width, pad_value):
        self.x = self._to_tensor(x)
        self.pad_width = pad_width
        self.pad_value = pad_value
        self.res = Tensor()


    def reshape(self):
        pad_width_arr = np.array(self.pad_width)
        self.pad_op = PadOp(self.pad_width, self.pad_value, self.x.shape)

        self.res.reshape(self.pad_op.res_shape)

    
    def forward(self):
        self.pad_op.pad(self.x.gpu_data, self.res.gpu_data)


    def backward(self):
        self.pad_op.pad_grad(self.x.gpu_grad, self.res.gpu_grad)


class GpuConcat(GpuLayer):
    def __init__(self, values, axis, stop_grad, name):
        super(GpuConcat, self).__init__(stop_grad, name)
        self._setup(values, axis)


    def _setup(self, values, axis):
        self.values = [self._to_tensor(value) for value in values]
        self.axis = axis
        self.res = Tensor()


    def reshape(self):
        self.concat_op = ConcatOp([blob.shape for blob in self.values], 
                                  self.axis)
        self.res.reshape(self.concat_op.res_shape)

    
    def forward(self):
        self.concat_op.concat([blob.gpu_data for blob in self.values],
                              self.res.gpu_data)


    def backward(self):
        self.concat_op.concat_grad(self.res.gpu_grad, 
                                   [blob.gpu_grad for blob in self.values])


class GpuSplit(GpuLayer):
    def __init__(self, value, num_or_size_splits, axis, stop_grad, name):
        super(GpuSplit, self).__init__(stop_grad, name)
        self._setup(value, num_or_size_splits, axis)

    
    def _setup(self, value, num_or_size_splits, axis):
        self.value = self._to_tensor(value)
        self.num_or_size_splits = num_or_size_splits
        self.axis = axis
        self.num = num_or_size_splits if isinstance(num_or_size_splits, int) else len(num_or_size_splits)
        self.res = [Tensor() for _ in range(self.num)]


    def reshape(self):
        axis_dim = self.value.shape[self.axis]
        size_splits = self.num_or_size_splits if not isinstance(self.num_or_size_splits, int) else [axis_dim // self.num_or_size_splits] * self.num_or_size_splits
        self.split_op = SplitOp(self.value.shape, size_splits, self.axis)
        
        for shape, tensor in zip(self.split_op.res_shapes, self.res):
            tensor.reshape(shape)

    
    def forward(self):
        self.split_op.split(self.value.gpu_data,
                            [tensor.gpu_data for tensor in self.res])


    def backward(self):
        self.split_op.split_grad([tensor.gpu_grad for tensor in self.res],
                                 self.value.gpu_grad)


class GpuGather(GpuLayer):
    """
        params: (n, f)
        indices: (a, b, c, ...)

        res: (a, b, c, ..., f)
    """

    def __init__(self, params, indices, stop_grad, name):
        super(GpuGather, self).__init__(stop_grad, name)
        self._setup(params, indices)

    
    def _setup(self, params, indices):
        self.params = self._to_tensor(params)
        self.indices = self._to_tensor(indices, dtype=np.int32)
        self.res = Tensor()

    
    def reshape(self):
        self.gather_op = GatherOp(self.params.shape, self.indices.shape)
        self.res.reshape(self.gather_op.res_shape)

    
    def forward(self):
        self.gather_op.gather(self.params.gpu_data, self.indices.gpu_data,
                              self.res.gpu_data)

    
    def backward(self):
        self.gather_op.gather_grad(self.res.gpu_grad, self.params.gpu_grad,
                                   self.indices.gpu_data)


class GpuConv2d(GpuLayer):
    def __init__(self, input, filter, strides, padding, stop_grad, name):
        super(GpuConv2d, self).__init__(stop_grad, name)
        self._setup(input, filter, strides, padding)

    
    def _setup(self, input, filter, strides, padding):
        self.input = self._to_tensor(input)
        self.filter = self._to_tensor(filter)
        self.strides = strides
        self.padding = padding
        self.res = Tensor()

    
    def reshape(self):
        ni, hi, wi, ci = self.input.shape
        hf, wf, ci, co = self.filter.shape
        ns, hs, ws, cs = self.strides
        
        if self.padding == 'VALID':
            conv2d_input_shape = self.input.shape
            ho, wo = (hi - hf) // hs + 1, (wi - wf) // ws + 1
        elif self.padding == 'SAME':
            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)

            hp = hs * (ho - 1) + (hf - 1) + 1 - hi
            wp = ws * (wo - 1) + (wf - 1) + 1 - wi
            pad_shape = ((0, 0), (hp // 2, hp - hp // 2), (wp // 2, wp - wp // 2), (0, 0))
            self.pad_shape = pad_shape
            self.pad_op = PadOp(pad_shape, 0, self.input.shape)
            conv2d_input_shape = self.pad_op.res_shape
            self.pad_tensor = gpu_empty(self.pad_op.size)
            self.pad_grad = gpu_zeros(self.pad_op.size)

            self.to_zero_op = ToZeroOp(self.pad_op.size)
        else:
            raise ValueError('Conv2d padding type: SAME or VALID')

        self.res.reshape((ni, ho, wo, co))

        self.conv2d_op = Conv2dOp(conv2d_input_shape, self.filter.shape, 
                                  self.strides, self.res.shape)

    
    def forward(self):
        if self.padding == 'VALID':
            conv2d_tensor = self.input.gpu_data
        elif self.padding == 'SAME':
            self.pad_op.pad(self.input.gpu_data, self.pad_tensor)
            conv2d_tensor = self.pad_tensor
        else:
            raise ValueError('Conv2d padding type: SAME or VALID')

        self.conv2d_op.conv2d(conv2d_tensor, self.filter.gpu_data,
                              self.res.gpu_data)


    def backward(self):
        if self.padding == 'SAME':
            conv2d_tensor = self.pad_tensor
            conv2d_grad = self.pad_grad
        elif self.padding == 'VALID':
            conv2d_tensor = self.input.gpu_data
            conv2d_grad = self.input.gpu_grad
        else:
            raise ValueError('Conv2d padding type: SAME or VALID')

        self.conv2d_op.conv2d_input_grad(self.filter.gpu_data, 
                                         self.res.gpu_grad, conv2d_grad)
        self.conv2d_op.conv2d_filter_grad(conv2d_tensor, 
                                          self.res.gpu_grad, 
                                          self.filter.gpu_grad)

        #self.conv2d_op.conv2d_grad(conv2d_grad, self.filter.gpu_grad, 
        #                           self.res.gpu_grad,
        #                           conv2d_tensor, self.filter.gpu_data)

        if self.padding == 'SAME':
            self.pad_op.pad_grad(self.input.gpu_grad, self.pad_grad)
            self.to_zero_op.to_zero(conv2d_grad)


class GpuMaxPool(GpuLayer):
    def __init__(self, value, ksize, strides, padding, stop_grad, name):
        super(GpuMaxPool, self).__init__(stop_grad, name)
        self._setup(value, ksize, strides, padding)

    
    def _setup(self, value, ksize, strides, padding):
        self.value = self._to_tensor(value)
        self.ksize = ksize
        self.strides = strides
        self.padding = padding
        self.res = Tensor()

    
    def reshape(self):
        if self.padding == 'SAME':
            ni, hi, wi, ci = self.value.shape
            _, hf, wf, _ = self.ksize
            ns, hs, ws, cs = self.strides

            ho, wo = math.ceil(hi / hs), math.ceil(wi / ws)
            hp = hs * (ho - 1) + (hf - 1) + 1 - hi
            wp = ws * (wo - 1) + (wf - 1) + 1 - wi
            pad_shape = ((0, 0), (hp // 2, hp - hp // 2), (wp // 2, wp - wp // 2), (0, 0))
            self.pad_op = PadOp(pad_shape, -np.inf, self.value.shape)
            max_pool_input_shape = self.pad_op.res_shape
            self.pad_tensor = gpu_empty(self.pad_op.size)
            self.pad_grad = gpu_zeros(self.pad_op.size)

            self.to_zero_op = ToZeroOp(self.pad_op.size)
        elif self.padding == 'VALID':
            max_pool_input_shape = self.value.shape
        else:
            raise ValueError('MaxPool padding type: SAME or VALID')

        self.max_pool_op = MaxPoolOp(max_pool_input_shape, self.ksize, self.strides)
        self.res.reshape(self.max_pool_op.res_shape)


    def forward(self):
        if self.padding == 'SAME':
            self.pad_op.pad(self.value.gpu_data, self.pad_tensor)
            max_pool_input_tensor = self.pad_tensor
        elif self.padding == 'VALID':
            max_pool_input_tensor = self.value.gpu_data
        else:
            raise ValueError('MaxPool padding type: SAME or VALID')

        self.max_pool_op.max_pool(max_pool_input_tensor, self.res.gpu_data)

    
    def backward(self):
        if self.padding == 'SAME':
            max_pool_input_tensor = self.pad_tensor
            max_pool_input_grad = self.pad_grad
        elif self.padding == 'VALID':
            max_pool_input_tensor = self.value.gpu_data
            max_pool_input_grad = self.value.gpu_grad
        else:
            raise ValueError('MaxPool padding type: SAME or VALID')

        self.max_pool_op.max_pool_grad(self.res.gpu_grad, max_pool_input_grad)

        if self.padding == 'SAME':
            self.pad_op.pad_grad(self.value.gpu_grad, max_pool_input_grad)
            self.to_zero_op.to_zero(max_pool_input_grad)
