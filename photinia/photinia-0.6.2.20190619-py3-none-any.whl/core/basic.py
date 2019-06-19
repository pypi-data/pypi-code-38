#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import tensorflow as tf

from . import common
from .. import conf
from .. import init


class Linear(common.Widget):
    """Linear layer.
    y = wx + b
    """

    def __init__(self,
                 name,
                 input_size,
                 output_size,
                 with_bias=True,
                 w_init=init.GlorotUniform(),
                 b_init=init.Zeros()):
        """Linear layer.

        y = Wx + b

        Args:
            name (str): Widget name.
            input_size (int): Input size.
            output_size (int): Output size.
            with_bias (bool): If the layer contains bias.
            w_init (init.Initializer): Weight initializer.
            b_init (initializers.Initializer): Bias initializer.

        """
        self._input_size = input_size
        self._output_size = output_size
        self._with_bias = with_bias
        self._w_init = w_init
        self._b_init = b_init
        super(Linear, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def output_size(self):
        return self._output_size

    @property
    def with_bias(self):
        return self._with_bias

    def _build(self):
        """Build the linear layer.
        Two parameters: weight and bias.

        """
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(self._input_size, self._output_size),
            dtype=conf.dtype,
        )
        if self._with_bias:
            self._b = self._variable(
                name='b',
                initializer=self._b_init,
                shape=(self._output_size,),
                dtype=conf.dtype
            )
        else:
            self._b = None

    @property
    def w(self):
        return self._w

    @property
    def b(self):
        return self._b

    def _setup(self, x, axis=-1, name='out', axes=None):
        """Setup the layer.

        Args:
            x (tf.Tensor): Input tensor.
            axis (int): If the order of "x" is larger than 2, the layer will perform tensor dot.
            name (str): Output name.

        Returns:
            tf.Tensor: Output tensor.

        """
        if self._with_bias:
            if len(x.shape) == 2:
                y = tf.matmul(x, self._w)
            else:
                if axes is None:
                    axes = [(axis,), (0,)]
                y = tf.tensordot(x, self._w, axes=axes)
            y = tf.add(y, self._b, name=name)
        else:
            if len(x.shape) == 2:
                y = tf.matmul(x, self._w, name=name)
            else:
                if axes is None:
                    axes = [(axis,), (0,)]
                y = tf.tensordot(x, self._w, axes=axes, name=name)
        return y



class Dropout(common.Widget):

    def __init__(self, name, keep_prob=None):
        """Dropout

        Args:
            name (str): Widget name.
            keep_prob (float|tf.Tensor): Keep probability.

        """
        self._keep_prob = keep_prob
        super(Dropout, self).__init__(name)

    @property
    def keep_prob(self):
        return self._keep_prob

    def _build(self):
        if self._keep_prob is None:
            self._keep_prob = tf.placeholder(
                shape=(),
                dtype=conf.dtype
            )

    def _setup(self, x, name='out'):
        """Setup dropout.

        Args:
            x (tf.Tensor): Input tensor.
            name (str): Output name.

        Returns:
            tf.Tensor: Output tensor.

        """
        return tf.nn.dropout(x, self._keep_prob, name=name)


