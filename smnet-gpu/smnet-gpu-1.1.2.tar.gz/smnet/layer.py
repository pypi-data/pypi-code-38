# --------------------------------------------------------
# SMNet layer
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Layer is responsible for forward and backward calculations.

If you want to customize layers, you need to implement the following three functions:
def _setup(self, a, b, ...):
    setup configure parameters for layer.
def forward(self):
    forward computes the data of the top blob from the data of the bottom blob.
def backward(self):
    backward computes the grad of the bottom blob from the grad of the top blob.
"""

import logging
import numpy as np
from numba import jit

from .blob import Tensor, Variable
from . import net
from .ops import array_ops, math_ops


class Layer(object):
    """Network is stacked by layers.

    Layer can be name-duplicate.

    Attrs:
        name_id: The name id controls the auto name of Layers, everytime you add
            a Layer, the name_id will be add 1. And if you are not specific the
            name of the Layer, a name will be automatically generated based on 
            the name_id.
    """
    _name_id = 0

    def __init__(self, stop_grad=False, name='Layer'):
        """Construct a new layer.
        
        Every time you create a layer, it will be added to graph.

        Args:
            stop_grad: A boolean to indicate whether call the function `backward`
                in this layer.
            name: The name of current layer.
        """
        net.graph.add_layer(self)
        
        self.stop_grad = stop_grad
        self._name = self._get_name(name)


    def _get_name(self, name):
        """Generate layer's name.

        TODO(smarsu): Other form of name.

        Args:
            name: str.
        """
        Layer._name_id += 1
        return name


    def _to_tensor(self, value, dtype=np.float32):
        """Convert value to tensor.
        
        They tensor will be a constant tensor.

        Args:
            value: Tensor/Variable, numpy, int, float, list of int...
        """
        if isinstance(value, Tensor) or isinstance(value, Variable):
            return value
        else:
            return Tensor(value, dtype=dtype)


    def reshape(self):
        logging.warning('No need to reshape cpu layer {}.'
                        'this is internal frame error, please submit to us: '
                        'smarsu@foxmail.com'.format(self.name))


    @property
    def name(self):
        return self._name


class Matmul(Layer):
    """TODO(samrsu): Merge bias to FullConnect"""

    def __init__(self, a, b):
        super(Matmul, self).__init__()
        self._setup(a, b)


    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare input data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(np.matmul(a, b))


    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)


    def _compute_grad_a(self, grad):
        """
        a_grad = res_grad * b.T
        """
        # 1. Prepare data
        b = self.b.data

        # 2. Compute and add grad
        self.a.add_grad(np.matmul(grad, b.T))


    def _compute_grad_b(self, grad):
        """
        b_grad = a.T * grad
        TODO(smarsu): Understand it.
        """
        # 1. Prepare data
        a = self.a.data

        # 2. Compute and add grad
        self.b.add_grad(np.matmul(a.T, grad))


def matmul(a, b, stop_grad=False, name='Matmul'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuMatmul(a, b, stop_grad, name).res
    else:
        return Matmul(a, b).res


class Add(Layer):
    def __init__(self, a, b):
        super(Add, self).__init__()
        self._setup(a, b)
    

    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare input data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(a + b)

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)


    def _compute_grad_a(self, grad):
        """For the NHWC data format, bias should collect gradients in the same way."""
        # 1. Prepare grad
        if grad.shape != self.a.shape:
            grad = np.reshape(grad, [-1] + list(self.a.shape))
            grad = np.sum(grad, axis=0)
        else:
            grad = grad.copy()

        # 2. Add grad
        self.a.add_grad(grad)

    
    def _compute_grad_b(self, grad):
        # 1. Prepare grad
        if grad.shape != self.b.shape:
            grad = np.reshape(grad, [-1] + list(self.b.shape))
            grad = np.sum(grad, axis=0)
        else:
            grad = grad.copy()

        # 2. Add grad
        self.b.add_grad(grad)


def add(a, b, stop_grad=False, name='Add'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuAdd(a, b, stop_grad, name).res
    return Add(a, b).res


class Subtract(Layer):
    def __init__(self, a, b):
        super(Subtract, self).__init__()
        self._setup(a, b)
    

    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare input data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(a - b)

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)


    def _compute_grad_a(self, grad):
        """For the NHWC data format, bias should collect gradients in the same way."""
        # 1. Prepare grad
        if grad.shape != self.a.shape:
            grad = np.reshape(grad, [-1] + list(self.a.shape))
            grad = np.sum(grad, axis=0)
        else:
            grad = grad.copy()

        # 2. Add grad
        self.a.add_grad(grad)

    
    def _compute_grad_b(self, grad):
        # 1. Prepare grad
        grad = -grad
        if grad.shape != self.b.shape:
            grad = np.reshape(grad, [-1] + list(self.b.shape))
            grad = np.sum(grad, axis=0)

        # 2. Add grad
        self.b.add_grad(grad)

    
def subtract(a, b, stop_grad=False, name='Subtract'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuSubtract(a, b, stop_grad, name).res
    return Subtract(a, b).res


class Multiply(Layer):
    def __init__(self, a, b):
        super(Multiply, self).__init__()
        self._setup(a, b)

    
    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(a * b)
    

    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)


    def _compute_grad_a(self, grad):
        # 1. Prepare data
        b = self.b.data

        # 2. Compute grad
        grad = grad * b
        if grad.shape != self.a.shape:
            grad = np.reshape(grad, [-1] + list(self.a.shape))
            grad = np.sum(grad, axis=0)

        # 3. Add grad
        self.a.add_grad(grad)
    

    def _compute_grad_b(self, grad):
        # 1. Prepare data
        a = self.a.data

        # 2. Compute grad
        grad = grad * a
        if grad.shape != self.b.shape:
            grad = np.reshape(grad, [-1] + list(self.b.shape))
            grad = np.sum(grad, axis=0)

        # 3. Add grad
        self.b.add_grad(grad)


def multiply(a, b, stop_grad=False, name='Multiply'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuMultiply(a, b, stop_grad, name).res
    else:
        return Multiply(a, b).res


class Divide(Layer):
    def __init__(self, a, b):
        super(Divide, self).__init__()
        self._setup(a, b)

    
    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(a / b)
    

    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)

    
    def _compute_grad_a(self, grad):
        # 1. Prepare data
        b = self.b.data

        # 2. Compute grad
        grad = grad / b
        if grad.shape != self.a.shape:
            grad = np.reshape(grad, [-1] + list(self.a.shape))
            grad = np.sum(grad, axis=0)

        # 3. Add grad
        self.a.add_grad(grad)
    

    def _compute_grad_b(self, grad):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute grad
        grad = grad * a / (-b * b)
        if grad.shape != self.b.shape:
            grad = np.reshape(grad, [-1] + list(self.b.shape))
            grad = np.sum(grad, axis=0)

        # 3. Add grad
        self.b.add_grad(grad)


def divide(a, b, stop_grad=False, name='Divide'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuDivide(a, b, stop_grad, name).res
    return Divide(a, b).res


class Sigmoid(Layer):
    def __init__(self, a):
        super(Sigmoid, self).__init__()
        self._setup(a)

    
    def _setup(self, a):
        self.a = self._to_tensor(a)
        self.res = Tensor()

    
    def forward(self):
        """Shall we add limit here to avoid overflow?"""
        # 1. Prepare data
        a = self.a.data

        # 2. Compute and feed result
        self.res.feed(array_ops.sigmoid(a))
    

    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)


    def _compute_grad_a(self, grad):
        # 1. Prepare data
        res = self.res.data

        # 2. Compute grad
        grad = grad * res * (1 - res)

        # 3. Add grad
        self.a.add_grad(grad)


def sigmoid(a, stop_grad=False, name='Sigmoid'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuSigmoid(a, stop_grad, name).res
    else:
        return Sigmoid(a).res


class Relu(Layer):
    def __init__(self, a):
        super(Relu, self).__init__()
        self._setup(a)

    
    def _setup(self, a):
        self.a = a
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        a = self.a.data

        # 2. Compute and feed result
        self.res.feed(np.maximum(0, a))

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)

    
    def _compute_grad_a(self, grad):
        # 1. Prepare data
        a = self.a.data

        # 2. Compute grad
        grad = np.where(a > 0, grad, 0)
        
        # 3. Add grad
        self.a.add_grad(grad)


def relu(a, stop_grad=False, name='Relu'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuRelu(a, stop_grad, name).res
    return Relu(a).res


class Tanh(Layer):
    def __init__(self, a):
        super(Tanh, self).__init__()
        self._setup(a)

    
    def _setup(self, a):
        self.a = self._to_tensor(a)
        self.res = Tensor()


    def forward(self):
        # 1. Prepare data
        a = self.a.data

        # 2. Compute and feed result
        self.res.feed(array_ops.tanh(a))


    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)


    def _compute_grad_a(self, grad):
        # 1. Prepare data
        res = self.res.data

        # 2. Compute grad
        grad = (1 - np.square(res)) * grad

        # 3. Add grad
        self.a.add_grad(grad)


def tanh(a, stop_grad=False, name='Tanh'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuTanh(a, stop_grad, name).res
    else:
        return Tanh(a).res


class Dropout(Layer):
    def __init__(self, x, keep_prob, stop_grad, name):
        super(Dropout, self).__init__(stop_grad, name)
        self._setup(x, keep_prob)

    
    def _setup(self, x, keep_prob):
        """
        Raise:
            ValueError: If keep_prob larger than 1 or less equal to 0.
        """
        if keep_prob > 1 or keep_prob <= 0:
            raise ValueError('sm.nn.dropout keep_prob should be located '
                             'in (0, 1], not {}'.format(keep_prob))

        self.x = x
        self.keep_prob = keep_prob
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        x = self.x.data
        keep_prob = self.keep_prob

        # 2. Setup mask
        mask = np.arange(x.size)
        np.random.shuffle(mask)
        keep_num = int(x.size * keep_prob)
        self.mask = np.where(mask < keep_num, 1 / keep_prob, 0)

        # 3. Compute and feed result
        self.res.feed(self.mask * x)


    def backward(self):
        grad = self.res.grad
        self._compute_grad_x(grad)

    
    def _compute_grad_x(self, grad):
        # 1. Prepare data
        mask = self.mask
        x = self.x.data

        # 2. Compute and add grad
        self.x.add_grad(grad * mask)


def dropout(x, keep_prob, stop_grad=False, name='Dropout'):
    return Dropout(x, keep_prob, stop_grad, name).res


class Square(Layer):
    def __init__(self, x, stop_grad, name):
        super(Square, self).__init__(stop_grad=stop_grad, name=name)
        self._setup(x)

    
    def _setup(self, x):
        self.x = x
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        x = self.x.data

        # 2. Compute and feed result
        self.res.feed(np.square(x))

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_x(grad)

    
    def _compute_grad_x(self, grad):
        # 1. Prepare data
        x = self.x.data

        # 2. Compute and add grad
        self.x.add_grad(2 * x * grad)


def square(x, stop_grad=False, name='Square'):
    return Square(x, stop_grad, name).res


class Hse(Layer):
    """Half square error."""

    def __init__(self, a, b):
        super(Hse, self).__init__()
        self._setup(a, b)

    
    def _setup(self, a, b):
        self.a = self._to_tensor(a)
        self.b = self._to_tensor(b)
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute and feed result
        self.res.feed(0.5 * np.square(a - b))


    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)
        self._compute_grad_b(grad)

    
    def _compute_grad_a(self, grad):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute grad
        grad = (a - b) * grad

        # 3. Add grad
        self.a.add_grad(grad)

    
    def _compute_grad_b(self, grad):
        # 1. Prepare data
        a = self.a.data
        b = self.b.data

        # 2. Compute grad
        grad = (b - a) * grad

        # 3. Add grad
        self.b.add_grad(grad)


def hse(labels, logits, stop_grad=False, name='Hse'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuHse(labels, logits, stop_grad, name).res
    return Hse(labels, logits).res


class Concat(Layer):
    def __init__(self, values, axis):
        super(Concat, self).__init__()
        self._setup(values, axis)

    
    def _setup(self, values, axis):
        self.values = [self._to_tensor(v) for v in values]
        self.axis = axis
        self.res = Tensor()
    

    def forward(self):
        # 1. Prepare data
        values = [v.data for v in self.values]
        axis = self.axis

        # 2. Compute and feed result
        self.res.feed(np.concatenate(values, axis))


    def backward(self):
        grad = self.res.grad
        self._compute_grad_values(grad)
        

    def _compute_grad_values(self, grad):
        # 1. Prepare data
        axis = self.axis

        # 2. Compute grad
        split_idx = []
        cur_idx = 0
        for blob in self.values:
            cur_idx += blob.shape[axis]
            split_idx.append(cur_idx)
        grads = np.split(grad, split_idx, axis)
        grads.pop()

        # 3. Add grad
        for value, grad in zip(self.values, grads):
            value.add_grad(grad)


def concat(values, axis, stop_grad=False, name='Concat'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuConcat(values, axis, stop_grad, name).res
    else:
        return Concat(values, axis).res


class Stack(Layer):
    def __init__(self, values, axis, stop_grad, name):
        super(Stack, self).__init__(stop_grad=stop_grad, name=name)
        self._setup(values, axis)

    
    def _setup(self, values, axis):
        self.values = values
        self.axis = axis
        self.res = Tensor()


    def forward(self):
        # 1. Prepare data
        values = [blob.data for blob in self.values]
        axis = self.axis

        # 2. Compute and feed result
        self.res.feed(np.stack(values, axis))

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_values(grad)


    def _compute_grad_values(self, grad):
        # 1. Prepare data
        axis = self.axis

        # 2. Compute grad
        grads = np.split(grad, list(range(1, grad.shape[axis] + 1)), axis)
        grads.pop()
        grads = [np.squeeze(grad, axis=axis) for grad in grads]

        # 3. Add grad
        for blob, grad in zip(self.values, grads):
            blob.add_grad(grad)


def stack(values, axis, stop_grad=False, name='Stack'):
    return Stack(values, axis, stop_grad, name).res


class Split(Layer):
    def __init__(self, value, num_or_size_splits, axis):
        super(Split, self).__init__()
        self._setup(value, num_or_size_splits, axis)

    
    def _setup(self, value, num_or_size_splits, axis):
        if not isinstance(num_or_size_splits, int):
            num_or_size_splits = [sum(num_or_size_splits[:index+1]) for 
                                  index in range(len(num_or_size_splits))]

        self.value = value
        self.num_or_size_splits = num_or_size_splits
        self.axis = axis

        num = num_or_size_splits if isinstance(num_or_size_splits, int) else len(num_or_size_splits)
        self.res = [Tensor() for _ in range(num)]

    
    def forward(self):
        """Splits a tensor into sub tensors.

        ```py
        >>> x = sm.Tensor(range(9))
        >>> sm.nn.split(x, 3)
        [Tensor([ 0.,  1.,  2.]), Tensor([ 3.,  4.,  5.]), Tensor([ 6.,  7.,  8.])]

        >>> x = sm.Tensor(range(8))
        >>> sm.nn.split(x, [3, 5, 6, 10])
        [Tensor([ 0.,  1.,  2.]),
        Tensor([ 3.,  4.]),
        Tensor([ 5.]),
        Tensor([ 6.,  7.]),]
        ```
        
        """
        # 1. Prepare data
        value = self.value.data
        num_or_size_splits = self.num_or_size_splits
        axis = self.axis

        # 2. Compute result
        if isinstance(num_or_size_splits, list):
            sub_values = np.split(value, num_or_size_splits, axis)
            sub_values.pop()
        else:
            sub_values = np.split(value, num_or_size_splits, axis)

        # 3. Feed result
        for res, sub_value in zip(self.res, sub_values):
            res.feed(sub_value)

    
    def backward(self):
        grads = [blob.grad for blob in self.res]
        self._compute_grad_value(grads)


    def _compute_grad_value(self, grads):
        # 1. Prepare data
        axis = self.axis

        # 2. Compute and add grad
        self.value.add_grad(np.concatenate(grads, axis))


def split(value, num_or_size_splits, axis, stop_grad=False, name='Split'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuSplit(value, num_or_size_splits, axis, stop_grad, name).res
    else:
        return Split(value, num_or_size_splits, axis).res


class Pad(Layer):
    def __init__(self, tensor, paddings, constant_values=0, stop_grad=False, name='Pad'):
        super(Pad, self).__init__(stop_grad=stop_grad, name=name)
        self._setup(tensor, paddings, constant_values)

    
    def _setup(self, tensor, paddings, constant_values):
        """
        TODO(smarsu): Multi type of paddings
        """
        self.tensor = self._to_tensor(tensor)
        self.paddings = paddings
        self.constant_values = constant_values
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        tensor = self.tensor.data
        paddings = self.paddings
        constant_values = self.constant_values

        # 2. Compute and feed result
        self.res.feed(np.pad(tensor, paddings, 
                             'constant', constant_values=constant_values))

    
    def backward(self):
        """
        We will not compute the grad of `paddings`
        """
        grad = self.res.grad
        self._compute_grad_tensor(grad)


    def _compute_grad_tensor(self, grad):
        # 1. Prepare data
        paddings = self.paddings

        # 2. Compute grad
        grad_shape = grad.shape
        grad = eval(
            'grad[{}]'.format(
                ','.join(['{}:{}'.format(l, grad_shape[idx]-r) 
                         for idx, (l, r) in enumerate(paddings)])
            )
        )

        # 3. Add grad
        self.tensor.add_grad(grad)


def pad(tensor, paddings, constant_values=0, stop_grad=False, name='Pad'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuPad(tensor, paddings, constant_values, stop_grad, name).res
    else:
        return Pad(tensor, paddings, constant_values, stop_grad, name).res


class Reshape(Layer):
    def __init__(self, tensor, shape, stop_grad=False, name='Reshape'):
        super(Reshape, self).__init__(stop_grad=stop_grad, name=name)
        self._setup(tensor, shape)

    
    def _setup(self, tensor, shape):
        self.tensor = self._to_tensor(tensor)
        self.shape = shape
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        tensor = self.tensor.data
        shape = self.shape

        # 2. Compute and feed result
        self.res.feed(np.reshape(tensor, shape))

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_tensor(grad)


    def _compute_grad_tensor(self, grad):
        # 1. Prepare data
        tensor_shape = self.tensor.shape

        # 2. Compute and add grad
        self.tensor.add_grad(np.reshape(grad, tensor_shape))


def reshape(tensor, shape, stop_grad=False, name='Reshape'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuReshape(tensor, shape, stop_grad, name).res
    else:
        return Reshape(tensor, shape, stop_grad, name).res


class Embedding_lookup(Layer):
    def __init__(self, params, ids, stop_grad):
        super(Embedding_lookup, self).__init__(stop_grad=stop_grad)
        self._setup(params, ids)

    
    def _setup(self, params, ids):
        """
        sm.nn.embedding_lookup will automatically add a row(all zeros) 
        at the end of params, it represents the pad character.

        Args:
            params: Tensor(), shape like [num_voca, num_feature]
            ids: Tensor(), shape like [batch, time_step] or [batch]
        Returns:
            res: Tensor(), shape like [batch(, time_step), num_feature]
        """
        self.params = params
        self.ids = ids
        self.res = Tensor()

        # Prepare pad data
        """params = params.data
        num_voca, num_feature = params.shape
        self.params.init_feed(np.concatenate([params, np.zeros((1, num_feature))], 0))"""

    
    def forward(self):
        """Looks up `ids` in a list of embedding tensors.

        The params had been padded
        """
        # 1. Prepare data
        params = self.params.data
        ids = self.ids.data

        # 2. Compute and feed result
        self.res.feed(params[ids])

    
    def backward(self):
        grad = self.res.grad
        self._compute_grad_params(grad)


    def _compute_grad_params(self, grad):
        """TODO(smarsu): Remove loop
        
        grad have shape [batch(, time_step), num_feature]
        ids have shape [batch(, time_step)]
        """
        # 1. Prepare data
        ids = self.ids.data

        # 2. Compute and add grad
        if self.params._grad is 0:
            self.params._grad = np.zeros(self.params.shape, dtype=self.params.dtype)

        num_voca, num_feature = self.params.shape
        grad = np.reshape(grad, [-1, num_feature])
        ids = ids.flatten()

        _embedding_lookup_backpropagation(ids, grad, self.params._grad, num_voca)

        #for id, part_grad in zip(ids.flatten(), grad):
        #    if id >= num_voca: continue  # The weight of the pad will not be updated
        #    self.params._grad[id] += part_grad


@jit(nopython=True, parallel=True, fastmath=True)
def _embedding_lookup_backpropagation(ids, grad, params_grad, num_voca):
    for i in range(len(ids)):
        if ids[i] >= num_voca: continue  # The weight of the pad will not be updated
        params_grad[ids[i]] += grad[i]  # [id] is quicker than [id, :]


def embedding_lookup(params, ids, stop_grad=False, name='EmbeddingLookup'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuGather(params, ids, stop_grad, name).res
    else:
        return Embedding_lookup(params, ids, stop_grad=stop_grad).res


class Softmax(Layer):
    def __init__(self, a):
        super(Softmax, self).__init__()
        self._setup(a)
    

    def _setup(self, a):
        self.a = a
        self.res = Tensor()


    def forward(self):
        # 1. Prepare data
        a = self.a.data

        # 2. Compute and feed result
        self.res.feed(array_ops.softmax(a))
    

    def backward(self):
        grad = self.res.grad
        self._compute_grad_a(grad)


    def _compute_grad_a(self, grad):
        raise NotImplementedError


def softmax(a):
    return Softmax(a).res


class Softmax_log_cross_entropy(Layer):
    def __init__(self, labels, logits):
        super(Softmax_log_cross_entropy, self).__init__()
        self._clip_value = 1e-6
        self._setup(labels, logits)
    

    def _setup(self, labels, logits):
        """
        The dim always be -1
        """

        logging.warning('sm.nn.softmax_log_cross_entropy always '
                        'calculates the value of the -1 dimension')

        self.labels = labels
        self.logits = logits
        self.res = Tensor()

    
    def forward(self):
        # 1. Prepare data
        labels = self.labels.data
        logits = self.logits.data

        # 2. Compute result
        softmax_logits = array_ops.softmax(logits)
        neg_log_logits = -np.log(np.maximum(softmax_logits, self._clip_value))
        cross_entropy = np.sum(labels * neg_log_logits, -1)
        #cross_entropy = labels * neg_log_logits

        self.softmax_logits = softmax_logits
        self.neg_log_logits = neg_log_logits

        # 3. Feed result
        self.res.feed(cross_entropy)

    
    def backward(self):
        grad = self.res.grad
        grad = np.tile(grad[..., np.newaxis], self.logits.shape[-1])
        self._compute_grad_lables(grad)
        self._compute_grad_logits(grad)

    
    def _compute_grad_lables(self, grad):
        """Actually, we need not compute lables grad."""
        # 1. Prepare data
        neg_log_logits = self.neg_log_logits

        # 2. Compute and add grad
        self.labels.add_grad(neg_log_logits * grad)

    
    def _compute_grad_logits(self, grad):
        """
        For grad[..., i], it affect grad[..., :] by the way [a, ..., k - 1, ..., n]
        """
        # 1. Prepare data
        labels = self.labels.data
        softmax_logits = self.softmax_logits

        # 2. Compute and add grad
        for i in range(labels.shape[-1]):
            softmax_logits_i = np.where(
                softmax_logits>self._clip_value, softmax_logits, 0)
            #softmax_logits_i = np.copy(softmax_logits)
            softmax_logits_i[..., i] -= 1
            self.logits._grad += grad[..., i:i+1] * labels[..., i:i+1] * softmax_logits_i


    def _compute_grad_logits_v2(self, a, b, grad):
        """THIS FUNCTION IS DEPRECATED, use _compute_grad_logits instead"""
        b = b.data

        softmax_a = array_ops.softmax(a.data)

        diff = np.zeros(a.shape)

        for i in range(a.shape[-1]):
            _softmax_a = np.copy(softmax_a)
            _softmax_a[..., i:i+1] = _softmax_a[..., i:i+1] - 1
            diff += b[..., i:i+1] * _softmax_a

        # Here grad maybe 1
        diff = diff * grad

        diff = np.where(softmax_a > 1e-10, diff, 0)

        self._add_diff(a, diff)
        return diff


def softmax_log_cross_entropy(labels, logits):
    return Softmax_log_cross_entropy(labels, logits).res


def bias_add(value, bias, stop_grad=False, name='BiadAdd'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuBiasAdd(value, bias, stop_grad, name).res
    return Add(value, bias).res


def transpose(x, perm, stop_grad=False, name='Transpose'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuTranspose(x, perm, stop_grad, name).res
    else:
        raise NotImplementedError
    return Transpose(x, perm).res  


def gather(params, indices, stop_grad=False, name='Gather'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuGather(params, indices, stop_grad, name).res
    else:
        raise NotImplementedError


def exp(a, stop_grad=False, name='Exp'):
    if net.use_cuda:
        from .cuda import cuda_layer
        return cuda_layer.GpuExp(a, stop_grad, name).res
    else:
        raise NotImplementedError
