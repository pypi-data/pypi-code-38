# --------------------------------------------------------
# SMNet net
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Stack layers to a graph(network). 

Inference: compute result by method `forward`.
Train: optimize weight by method `optimize`.

For `forward` and `optimize`, we need high performance calculations, 
so we don't do error check.
"""

import os
import time
import logging

import numpy as np
from .ops import math_ops

if ('CUDA_VISIBLE_DEVICES' in os.environ and 
    os.environ['CUDA_VISIBLE_DEVICES'] == ''):
    use_cuda = False
else:
    use_cuda = True

if ('sm_profiling' in os.environ and
    os.environ['sm_profiling'] == 'true'):
    profiling = True
else:
    profiling = False

# The default graph, layers will be added to it.
graph = None


def set_default_graph(cls):
    """Decorators for set default graph
    
    Every time you create a new graph, set it as the default graph.
    """
    def set_graph(*args, **kargs):
        global graph
        graph = cls(*args, **kargs)
        return graph

    return set_graph


@set_default_graph
class Net(object):
    """Class Net.

    Stack layers to build graph. Collection blobs to inference the graph's output
    or optimize the graph's parameters.
    """
    def __init__(self):
        """A new graph should be constructed by empty layers and blobs.
        
        layers: Every time you call a layer, the layer will be added to 
            the default graph orderly. During inference, layers' 
            `forward` method will be called in the same order.
        backlayers: The reverse of layers. During optimization, The gradient
            will flow in the opposite direction of the forward direction.
        variables: Every time you create a variable, it will be added to
            the graph.
        tensors: Every time you create a tensor, it will be added to
            the graph.
        variable_momentum: The momentum of last grad.
        dtype_checked: A boolean to indicate whether the dtype has been checked.
        reshape_tag: reshape should be called at the first forward or shape
            changed.
        """
        self._layers = []
        self._backlayers = []

        self._variables = set()
        self._tensors = set()

        self._variable_momentum = {}

        self._dtype_checked = False
        self._reshape_tag = True


    def add_layer(self, layer):
        """Stack layer to graph.
        
        Every time create a layer, it will be stacked orderly.

        Args:
            layer: sm.Layer
        Raise:
            ValueError: If layer is not a sm.Layer
        """
        from .layer import Layer
        if not isinstance(layer, Layer):
            raise ValueError('layer is expected to be a sm.Layer, '
                'it is internal frame error, please submit to us: '
                'smarsu@foxmail.com')
        self._layers.append(layer)
        self._backlayers.insert(0, layer)


    def add_tensor(self, tensor):
        """Add tensor to graph.
        
        Args:
            tensor: sm.Tensor
        Raise:
            ValueError: If tensor is not a sm.Tensor
        """
        from .blob import Tensor
        if not isinstance(tensor, Tensor):
            raise ValueError('tensor is expected to be a sm.Tensor, '
                'it is internal frame error, please submit to us: '
                'smarsu@foxmail.com')
        self._tensors.add(tensor)


    def add_variable(self, variable):
        """Add variable to graph.
        
        Args:
            variable: sm.Variable
        Raise:
            ValueError: If variable is not a sm.Variable
        """
        from .blob import Variable
        if not isinstance(variable, Variable):
            raise ValueError('variable is expected to be a sm.Variable, '
                'it is internal frame error, please submit to us: '
                'smarsu@foxmail.com')
        self._variables.add(variable)


    @property
    def _name_to_variable(self, name_to_variable={}):
        """Map name to variable.

        Returns:
            name_to_variable: dict, get variable by name."""
        if not name_to_variable:
            name_to_variable = {variable.name: variable 
                                for variable in self._variables}
        return name_to_variable

    
    def reshape(self):
        """Reshape blob and malloc gpu memory for data.

        This is useful to propagate changes to layer sizes without running
        a forward pass, e.g. to compute output feature size.

        Reference: 
            Caffe Net::Reshape
                https://github.com/BVLC/caffe/blob/master/src/caffe/net.cpp
        """
        for layer in self._layers:
            layer.reshape()


    def forward(self, fetches=None, feed_dict=None):
        if use_cuda:
            values = self._gpu_forward(fetches, feed_dict)
        else:
            values = self._cpu_forward(fetches, feed_dict)
        return values


    def _cpu_forward(self, fetches, feed_dict):
        """Compute top tensor results based on bottom layer results 
            layer by layer.

        First, feed the numpy value to placeholder blob.
        Second, compute the layers' output orderly.

        TODO(smarsu): Partial graph comput.
        
        Args:
            feed_dict: dict, 
                key: blobs;
                values: blobs' numpy value.
        """
        if feed_dict is not None:
            # Feed input/label data to graph
            # Use init feed to check and correct shape and dtype.
            for blob, value in feed_dict.items():
                blob.init_feed(value)

        if profiling is True:
            for layer in self._layers:
                start_time = time.time()
                layer.forward()
                end_time = time.time()
                gap = end_time - start_time
                print('Profiling: use cuda - {}, {} layer forward time {} ms'.format(
                    use_cuda, layer.name, gap * 1000))
        else:
            for layer in self._layers:
                layer.forward()

        if fetches is None:
            return
        else:
            return [blob.data for blob in fetches]


    def _gpu_forward(self, fetches, feed_dict):
        """
        Raise:
            ValueError: If fetches is None
        """
        if fetches is None:
            raise ValueError('sm.forward: fetches cannot be None.')

        if feed_dict is not None:
            for blob, value in feed_dict.items():
                if blob.shape != np.array(value).shape:
                    self._reshape_tag = True
                blob.init_feed_gpu(value)
        if self._reshape_tag is True:
            self.reshape()
            self._reshape_tag = False

        if profiling is True:
            for layer in self._layers:
                start_time = time.time()
                layer.forward()
                end_time = time.time()
                gap = end_time - start_time
                print('Profiling: use cuda - {}, {} layer forward time {} ms'.format(
                    use_cuda, layer.name, gap * 1000))
        else:
            for layer in self._layers:
                layer.forward()

        if profiling is True:
            for blob in fetches:
                start_time = time.time()
                blob.to_cpu()
                end_time = time.time()
                gap = end_time - start_time
                print('Profiling: use cuda - {}, blob {} MemcpyDtoH time {} ms'.format(
                    use_cuda, blob.name, gap * 1000))
        else:
            for blob in fetches:
                blob.to_cpu()

        return [blob.data for blob in fetches]

    
    def backward(self, blobs, lr, momentum, weight_decay):
        if use_cuda:
            values = self._gpu_backward(blobs, lr, momentum, weight_decay)
        else:
            values = self._cpu_backward(blobs, lr, momentum, weight_decay)
        return values


    def _gpu_backward(self, blobs, lr, momentum, weight_decay):
        for blob in blobs:
            blob.set_gpu_grad(lr)

        if profiling is True:
            for layer in self._backlayers:
                if not layer.stop_grad:
                    start_time = time.time()
                    layer.backward()
                    end_time = time.time()
                    gap = end_time - start_time
                    print('Profiling: use cuda - {}, {} layer backward time {} ms'.format(
                        use_cuda, layer.name, gap * 1000))
        else:
            for layer in self._backlayers:
                if not layer.stop_grad:
                    layer.backward()


    def _cpu_backward(self, blobs, lr, momentum, weight_decay):
        """Flow grad from top layer to bottom layer.

        TODO(smarsu): Check out why momentum affect the converge. 

        Args:
            blobs: The blobs which store loss values should be set 
                initial grad.
            lr: Learning rate.
            momentum: Param for MomentumOptimizer
            weight_decay: Param for weights' l2 normalize.
        """
        for blob in blobs:
            blob.set_grad(np.full(blob.shape, lr, dtype=blob.dtype))

        if profiling is True:
            for layer in self._backlayers:
                if not layer.stop_grad:
                    start_time = time.time()
                    layer.backward()
                    end_time = time.time()
                    gap = end_time - start_time
                    print('Profiling: use cuda - {}, {} layer backward time {} ms'.format(
                        use_cuda, layer.name, gap * 1000))
        else:
            for layer in self._backlayers:
                if not layer.stop_grad:
                    layer.backward()

        if momentum > 0.:
            self._momentum_update(momentum)
        if weight_decay > 0.:
            self._weight_norm(weight_decay)


    def _momentum_update(self, momentum):
        """Add momentum to grad.
        
        "Ut+1 = m * Ut + grad"
        "Wt+1 = Wt - lr * Ut+1"
        Reference: https://arxiv.org/abs/1706.02677v1

        Args:
            momentum: The extent of the last gradient.
        """
        for variable in self._variables:
            self._variable_momentum[variable] = variable.add_grad(
                momentum * self._variable_momentum.get(variable, 0.))


    def _weight_norm(self, weight_decay):
        """L2 normalize for the weights of graph.

        Args:
            weight_decay: The attenuation coefficient of weight.
        """
        for variable in self._variables:
            variable.add_grad(
                weight_decay * math_ops.l2_loss(variable.data))


    def update(self):
        if use_cuda:
            values = self._gpu_update()
        else:
            values = self._cpu_update()
        return values


    def _cpu_update(self):
        """Apply grad to data, then clear grad.

        Just apply grad to variable, no need for tensor.
        """
        for variable in self._variables:
            variable.update()
        
        for variable in self._variables:
            variable.clear_grad()

        for tensor in self._tensors:
            tensor.clear_grad()


    def _gpu_update(self):
        for variable in self._variables:
            variable.gpu_update()

        for variable in self._variables:
            variable.clear_gpu_grad()

        for tensor in self._tensors:
            tensor.clear_gpu_grad()


    def optimize(self, blobs, lr=1., momentum=0., weight_decay=0.):
        """Exposed interface for optimizing weights.
        
        Args:
            blobs: The blobs which store loss values should be set 
                initial grad.
            lr: Learning rate.
            momentum: Param for MomentumOptimizer
            weight_decay: Param for weights' l2 normalize.
        """
        self.backward(blobs, lr, momentum, weight_decay)
        self._check_dtype()
        self.update()


    def save(self, path):
        """Dump the variables' data to file.
        
        Args:
            path: The .npz file stores the variables.
                The realpath name is `path + '.npz'`
        """
        variable_dict = {variable.name: variable.data 
                         for variable in self._variables}
        np.savez(path, **variable_dict)


    def restore(self, path):
        """Load the variables' data from the .npz file.
        
        Args:
            path: The .npz file stores the variables.
        Raise:
            NameError: path not endwith .npz
        """
        if not path.endswith('.npz'):
            raise NameError('path is expected to be endwith .npz, '
                            'but {}'.format(path))

        variable_dict = np.load(path)
        if len(variable_dict) != len(self._variables):
            logging.warning('Stored variables and graph variables '
                            'not completely match.')
        for name, data in variable_dict.items():
            if name not in self._name_to_variable:
                logging.warning('Variable {} not found in graph.'.format(name))
            else:
                self._name_to_variable[name].restore(data)


    def _check_dtype(self):
        """Check the data/grad type of all tensors and variables in the graph.

        After forwark and backward, blob's data and grad will be calculated,
        check the dtype at this time.
        """
        if use_cuda:
            return

        if self._dtype_checked:
            return
        else:
            self._dtype_checked = True

        blobs = self._variables.union(self._tensors)
        for blob in blobs:
            if blob._data.dtype != blob.dtype:
                logging.warning('{}: dtype of data unmatch, '
                                'expected {} but {}. '
                                'it is internal frame error, please submit to us: '
                                'smarsu@foxmail.com'.format(
                                    blob.name, blob.dtype, blob._data.dtype))
            if not isinstance(blob._grad, int) and blob._grad.dtype != blob.dtype:
                logging.warning('{}: dtype of grad unmatch, '
                                'expected {} but {}. '
                                'it is internal frame error, please submit to us: '
                                'smarsu@foxmail.com'.format(
                                    blob.name, blob.dtype, blob._data.dtype))


sm = Net()
