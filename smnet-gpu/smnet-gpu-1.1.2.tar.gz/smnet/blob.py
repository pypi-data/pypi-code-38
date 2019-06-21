# --------------------------------------------------------
# SMNet blob
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Blob stored datas and grads.

Variable stores the weights of the graph, which should be given at the beginning
of the inference/train, and the grad of Variable will be added to data during training;
Tensor stores the intermediate results and final results of the graph, some Tensor 
worked like placeholder should be given data at the beginning of the inference/train, 
and the intermediate and final results will be computed by call `forward`. And there is
no need to add the grad of Tensor to data. 

Because we need high performance calculations, we have not done memory copy
when you get the Blob's data and grad, you should be carefully to use them.

TODO(smarsu): Separate the mutable and no-mutable data/grad.
"""

import numpy as np

from . import net
if net.use_cuda:
    from .cuda import cuda
    from .cuda import cuda_ops
    from .cuda.kernels import *


class Blob(object):
    """Class Blob, store datas and grads.

    Every Blob should be name-unique, which can help restore.

    Attrs:
        name_id: The name id controls the auto name of Blobs, everytime you add
            a Blob, the name_id will be add 1. And if you are not specific the
            name of the Blob, a name will be automatically generated based on 
            the name_id.
    """
    _name_id = 0

    def __init__(self, data=None, dtype=np.float32, name=None, type='Blob'):
        """Construct a new Blob.
        
        Args:
            data: The initial data of the Blob. Variables must feed initial data, 
                and some Tensor can feed initial data to be a constant.
            dtype: The data type of the Blob, default is np.float32. It mainly 
                balance the calculation accuracy of floating point numbers and
                the calculation time.
            name: The name of Blob, if None, it will generated automatically.
            type: The class type, there are Blob, Variable and Tensor.
        Attrs:
            grad: Gradient corresponding to the data in Blob, it is initialized
                with 0. cause this can be quick, and we may don't know 
                the shape of data.
        Raise:
            ValueError: If ValueError be None.
            ValueError: If type be blob.
        """
        if dtype not in [np.float32, np.int32]:
            raise ValueError('You can not set the dtype to be {}, must be '
                             'one of the two numpy dtype:\n'
                             '    np.float32, np.int32, ...'.format(dtype))
        if type == 'Blob':
            raise ValueError('Type can not be, there are just variable and '
                             'tensor have exposed interface. '
                             'it is internal frame error, please submit to us: '
                             'smarsu@foxmail.com')
        self._data = None
        self._gpu_data = None
        self._shape = None
        self._size = None
        self._capacity = 0
        self._grad = 0
        self._dtype = dtype

        self._full_op = None
        self._subtract_op = None
        self._to_zero_op = None
        if data is not None:
            if not net.use_cuda:
                self.init_feed(data)
            else:
                self.init_feed_gpu(data)

        self._type = type
        self._name = self._get_name(name)


    def _get_name(self, name):
        """Generate blob's name.

        If name is None, we will generated a name automatically based on 
        type of blob.

        Args:
            name: None or str. 
        """
        Blob._name_id += 1
        if name is None:
            return '_'.join([self._type, str(Blob._name_id)])
        else:
            return name


    def init_feed(self, data):
        """Feed data to blob.
        
        The function will handle mismatched data types and shapes.
        Specifically, convert dtype of data to blob._dtype, reshape
        scalar data to shape [1].

        Args:
            data: It should be able to be converted to a numpy type.
        """
        data = np.array(data, dtype=self._dtype)
        # If the data is a scalar, then its shape needs to be set to [1].
        if not data.shape:
            data = np.reshape(data, [1])
        self.feed(data)


    def feed(self, data):
        """High-speed feed data.

        Attention: For high performance calculations, we have not done 
            memory copy here, you need carefully to handle these datas.
        
        Args:
            data: Which has been processed with the correct dtype and shape.
        """
        self._data = data


    def add_grad(self, grad):
        """Add top blob's grad to bottom blob after derivation.
        
        Attention: For high performance calculations, we have not done 
            memory copy here, you need carefully to handle these grads, 
            especially for self._grad is 0.

        Args:
            grad: Which computed by backpropagation, should be added to
                current blob.
        """
        if grad is 0:
            return self._grad

        if self._grad is 0:
            self._grad = grad
        else:
            self._grad += grad
        return self._grad


    def add_gpu_grad(self, grad):
        cuda_ops.left_add(self._gpu_grad, grad,
                          grid=(self.size, 1, 1), block=(1, 1, 1))


    def clear_grad(self):
        """Reset the blob's grad.
        
        The grad of each blobs should be reset after update.
        """
        self._grad = 0


    def clear_gpu_grad(self):
        self._to_zero_op.to_zero(self._gpu_grad)
        #self._gpu_grad = cuda.gpu_zeros(self.size, gpu_data=self._gpu_grad)


    def reshape(self, shape):
        """Change the dimensions of the blob, allocating new memory if
            necessary.
        
        This function can be called both to create an initial allocation
        of memory, and to adjust the dimensions of a top blob during Layer::Reshape
        or Layer::Forward. When changing the size of blob, memory will only be
        reallocated if sufficient memory does not already exist, and excess memory
        will never be freed.

        Reference:
            Caffe Blob::Reshape:
                https://github.com/BVLC/caffe/blob/master/include/caffe/blob.hpp
        """
        if self._shape == shape:
            return
        self._shape = shape

        size = int(np.prod(shape))
        if size != self._size:
            self._full_op = FullOp(self._shape, value=None)
            self._subtract_op = SubtractOp(self._shape, self._shape)
            self._to_zero_op = ToZeroOp(size)

        self._size = size
        if size > self._capacity:
            self._capacity = size
            self._gpu_data_malloc(size)
            self._gpu_grad_malloc(size)


    def _gpu_data_malloc(self, size):
        """Malloc gpu memory for data."""
        self._gpu_data = cuda.gpu_empty(size)


    def _gpu_grad_malloc(self, size):
        self._gpu_grad = cuda.gpu_zeros(size)


    def init_feed_gpu(self, data):
        self.init_feed(data)
        self.reshape(self._data.shape)
        self.feed_gpu(self._data)


    def feed_gpu(self, data):
        self._gpu_data = cuda.to_gpu(cpu_data=data,
                                     gpu_data=self._gpu_data,)


    def to_cpu(self):
        self._data = cuda.to_cpu(shape=self._shape,
                                 gpu_data=self._gpu_data, 
                                 dtype=self._dtype)


    # Properties
    @property
    def shape(self):
        if net.use_cuda:
            return self._shape #if self._data is None else self._data.shape
        else:
            return self._data.shape


    @property
    def size(self):
        if net.use_cuda:
            return self._size # if self._data is None else self._data.shape
        else:
            return self._data.size
        #return self._size if self._data is None else self._data.size

    
    @property
    def data(self):
        if self._data is None and self._gpu_data is not None:
            self.to_cpu() 
        return self._data

    
    @property
    def gpu_data(self):
        return self._gpu_data

    
    @property
    def grad(self):
        return self._grad


    @property
    def gpu_grad(self):
        return self._gpu_grad


    @property
    def dtype(self):
        return self._dtype

    
    @property
    def name(self):
        return self._name


    def __str__(self):
        """
        Show string to person (in print function).
        """
        return self._name

    
    def __repr__(self):
        """
        Show string to machine (in eval function).
        """
        return self.__str__()


    # Overloaded operators
    def __add__(self, other):
        from .layer import add
        return add(self, other)


    def __sub__(self, other):
        from .layer import subtract
        return subtract(self, other)

    
    def __mul__(self, other):
        from .layer import multiply
        return multiply(self, other)

    
    def __truediv__(self, other):
        from .layer import divide
        return divide(self, other)


    # Inv overloaded operators
    def __radd__(self, other):
        from .layer import add
        return add(other, self)
    

    def __rsub__(self, other):
        from .layer import subtract
        return subtract(other, self)

    
    def __rmul__(self, other):
        from .layer import multiply
        return multiply(other, self)

    
    def __rtruediv__(self, other):
        from .layer import divide
        return divide(other, self)

    # Unary operators
    def __pos__(self):
        return self


    def __neg__(self):
        from .layer import subtract
        return subtract(0., self)


class Variable(Blob):
    def __init__(self, data, name=None, dtype=np.float32):
        """Variable stores data and grad for the weights of graph.

        Our Variable must have initialized values, we will not provide 
        initialization at the network/graph level.

        Every time you create a Variable, it will be added to graph.

        Args:
            data: The initialized weights/bias.
            name: None or str.
            dtype: data type of data and grad.
        """
        super(Variable, self).__init__(data=data, dtype=dtype, 
                                       name=name, type='Variable')
        net.graph.add_variable(self)


    def restore(self, data):
        if not net.use_cuda:
            self.init_feed(data)
        else:
            self.init_feed_gpu(data)


    def update(self):
        """Adjustment weight's data by the computed grad."""
        if self._grad is not 0:
            self._data -= self._grad


    def gpu_update(self):
        self._subtract_op.identity_subtract(self._gpu_data, self._gpu_grad, self._gpu_data)
        #cuda_ops.left_subtract(self._gpu_data, self._gpu_grad,
        #                       grid=(self.size, 1, 1), block=(1, 1, 1))


class Tensor(Blob):
    def __init__(self, data=None, name=None, dtype=np.float32):
        """Tensor stores data and grad for the inter and final result.
        
        For some Tensors, you can initialized thier data with None. And 
        then feed values to them during inference/training. We call 
        these Tensors as placeholder. And some Tensors are feeded with
        initialized values, they are called as constant Tensor. Most 
        Tensors are generated by layers, the data of them will be computed
        by call function `forward`. 
        """
        super(Tensor, self).__init__(data=data, dtype=dtype, 
                                     name=name, type='Tensor')
        net.graph.add_tensor(self)


    def set_grad(self, grad):
        """Set grad.
        
        Set initialized grad for loss Tensor.
        
        Args:
            grad: The initialized grad of loss should be manually set.
                The shape and dtype of grad should be same with the data.
        """
        self._grad = grad


    def set_gpu_grad(self, grad):
        """
        Args:
            grad: float
        """
        self._full_op.full(self._gpu_grad, cuda.to_gpu(np.array(grad, dtype=self.dtype)))
        #self._gpu_grad = cuda.gpu_full(grad, self.size, gpu_data=self._gpu_grad)
