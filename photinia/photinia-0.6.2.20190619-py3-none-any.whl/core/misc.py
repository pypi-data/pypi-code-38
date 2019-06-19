#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import tensorflow as tf

from . import basic
from . import common
from .. import conf
from .. import init
from .. import ops


class BatchNorm(common.Widget):

    def __init__(self,
                 name,
                 size,
                 is_training=True,
                 beta_init=init.Zeros(),
                 gamma_init=init.Ones(),
                 epsilon=1e-5):
        self._size = size
        self._is_training = is_training
        self._beta_init = beta_init
        self._gamma_init = gamma_init
        self._epsilon = epsilon
        super(BatchNorm, self).__init__(name)

    @property
    def size(self):
        return self._size

    @property
    def input_size(self):
        return self._size

    @property
    def output_size(self):
        return self._size

    @property
    def epsilon(self):
        return self._epsilon

    def _build(self):
        self._beta = self._variable(
            name='beta',
            initializer=self._beta_init,
            shape=(self._size,),
            dtype=conf.dtype
        )
        self._gamma = self._variable(
            name='gamma',
            initializer=self._gamma_init,
            shape=(self._size,),
            dtype=conf.dtype
        )
        self._mean = self._variable(
            'mean',
            initializer=init.Zeros(),
            shape=(self._size,),
            dtype=conf.float
        )
        self._variance = self._variable(
            'variance',
            initializer=init.Zeros(),
            shape=(self._size,),
            dtype=conf.float
        )

    def _setup(self,
               x,
               is_training=None,  # TODO: deprecated
               axis=-1,
               name='out'):
        if is_training is not None:
            self._is_training = is_training
            print('Deprecated argument "is_training". Use it in the constructor.')

        if isinstance(self._is_training, bool):
            if self._is_training:
                return self._setup_for_train(x, axis, name)
            else:
                return self._setup_for_predict(x, name)
        else:
            return tf.cond(
                self._is_training,
                lambda: self._setup_for_train(x, axis, None),
                lambda: self._setup_for_predict(x, None),
                name=name
            )

    def _setup_for_train(self, x, axis, name):
        if axis == -1:
            axes = tuple(range(len(x.shape) - 1))
        else:
            axes = tuple(i for i in range(len(x.shape)) if i != axis)
        mean, variance = tf.nn.moments(x=x, axes=axes)
        update_mean = tf.assign(self._mean, (self._mean + mean) * 0.5)
        update_variance = tf.assign(self._variance, (self._variance + variance) * 0.5)
        with tf.control_dependencies([update_mean, update_variance]):
            mean = tf.identity(mean)
            variance = tf.identity(variance)
        y = tf.nn.batch_normalization(
            x=x,
            mean=mean,
            variance=variance,
            offset=self._beta,
            scale=self._gamma,
            variance_epsilon=self._epsilon,
            name=name
        )
        return y

    def _setup_for_predict(self, x, name):
        y = tf.nn.batch_normalization(
            x=x,
            mean=tf.stop_gradient(self._mean),
            variance=tf.stop_gradient(self._variance),
            offset=self._beta,
            scale=self._gamma,
            variance_epsilon=self._epsilon,
            name=name
        )
        return y

    @property
    def beta(self):
        return self._beta

    @property
    def gamma(self):
        return self._gamma


class SoftAttention(common.Widget):
    """Soft attention.

    The algorithm is described below:

        Sequence: S = {s_1, s_2, ..., s_n'}, in which s_i in R^n.
        Vector: v in R^m.
        Sequence weight: W, a k by n matrix.
        Vector weight: U, a k by m matrix.
        Omega, a k dimension vector.

        Attention sequence: A = {a_1, a_2, ..., a_n'}, in which a_i in R. A is computed as follow:
            a'_i = tanh(W @ c_i + U @ S)
            A = softmax(omega @ A')
        Attention context: AC = sum(A * C)
    """

    def __init__(self,
                 name,
                 seq_elem_size,
                 vec_size,
                 common_size,
                 w_seq_init=init.GlorotUniform(),
                 w_context_init=init.GlorotUniform(),
                 omega_init=init.GlorotUniform()):
        self._seq_elem_size = seq_elem_size
        self._vec_size = vec_size
        self._common_size = common_size
        self._w_seq_init = w_seq_init
        self._w_context_init = w_context_init
        self._omega_init = omega_init
        super(SoftAttention, self).__init__(name)

    @property
    def seq_elem_size(self):
        return self._seq_elem_size

    @property
    def vec_size(self):
        return self._vec_size

    @property
    def common_size(self):
        return self._common_size

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_seq_init,
            shape=(self._seq_elem_size, self._common_size),
            dtype=conf.dtype
        )
        self._u = self._variable(
            name='u',
            initializer=self._w_context_init,
            shape=(self._vec_size, self._common_size),
            dtype=conf.dtype
        )
        self._omega = self._variable(
            name='omega',
            initializer=self._omega_init,
            shape=(self._common_size, 1),
            dtype=conf.dtype
        )

    @property
    def w(self):
        return self._w

    @property
    def u(self):
        return self._u

    @property
    def omega(self):
        return self._omega

    def _setup(self, seq, vec, seq_length=None, activation=tf.nn.tanh, name='out'):
        """Setup a soft attention mechanism for the given context sequence and state.
        The result is an attention context for the state.

        Args:
            seq: The sequence tensor with shape (seq_length, batch_size, seq_elem_size).
            vec: The vector tensor with shape (batch_size, vec_size).
            seq_length: Sequence length tensor with shape (batch_size,)
            activation: The activation function.
                Default is tf.nn.tanh.
            name (str): Output name.

        Returns:
            tf.Tensor: An attention context with shape (batch_size, seq_elem_size).

        """
        #
        # (batch_size, seq_length, seq_elem_size) -> (seq_length, batch_size, seq_elem_size)
        # seq = ops.transpose_sequence(seq)
        #
        # (seq_length, batch_size, seq_elem_size) @ (seq_elem_size, common_size)
        # -> (seq_length, batch_size, common_size)
        a = tf.tensordot(seq, self._w, ((2,), (0,)))
        #
        # (batch_size, vec_size) @ (vec_size, common_size)
        # -> (batch_size, common_size)
        # -> (1, batch_size, common_size)
        b = tf.matmul(vec, self._u)
        b = tf.reshape(b, (1, -1, self._common_size))
        #
        # -> (seq_length, batch_size, common_size)
        # (seq_length, batch_size, common_size) @ (common_size, 1)
        # -> (seq_length, batch_size, 1)
        a = activation(a + b) if activation is not None else a + b
        a = tf.tensordot(a, self._omega, ((2,), (0,)))
        if seq_length is None:
            a = tf.nn.softmax(a, dim=0, name='a')
        else:
            m = tf.sequence_mask(seq_length, dtype=conf.dtype)  # (batch_size, seq_length)
            m_shape = tf.shape(m)
            m = tf.reshape(tf.transpose(m), (m_shape[1], m_shape[0], 1))
            s = tf.exp(a)
            a = tf.div(s, tf.reduce_sum(s * m, axis=0, keep_dims=True), name='a')
        #
        # (seq_length, batch_size, 1) * (seq_length, batch_size, seq_elem_size)
        # -> (seq_length, batch_size, seq_elem_size)
        # -> (batch_size, seq_elem_size)
        att_context = tf.reduce_sum(a * seq, 0, name=name)
        return att_context


class Gate(common.Widget):

    def __init__(self,
                 name,
                 input_sizes,
                 output_size,
                 w_init=init.TruncatedNormal(0.0, 1e-3),
                 b_init=init.Zeros()):
        if not isinstance(input_sizes, (tuple, list)):
            input_sizes = (input_sizes,)
        self._input_sizes = input_sizes
        self._output_size = output_size
        self._w_init = w_init
        self._b_init = b_init
        super(Gate, self).__init__(name)

    def _build(self):
        self._w_list = list()
        for i, input_size in enumerate(self._input_sizes):
            w = self._variable(
                name='w_%d' % i,
                initializer=self._w_init,
                shape=(input_size, self._output_size),
                dtype=conf.dtype
            )
            self._w_list.append(w)
        self._b = self._variable(
            name='b',
            initializer=self._b_init,
            shape=(self._output_size,),
            dtype=conf.dtype
        )

    def _setup(self, *x_list, name='out'):
        if len(x_list) != len(self._w_list):
            raise ValueError()
        y = None
        for i, x in enumerate(x_list):
            if y is None:
                y = tf.matmul(x, self._w_list[i])
            else:
                y += tf.matmul(x, self._w_list[i])
        y += self._b
        y = tf.nn.sigmoid(y, name=name)
        return y


class ResidualLayer(common.Widget):
    """Residual network cell for DNN.

    The original version is contributed by zhkun~(Kun Zhang) in his testing code.
    """

    def __init__(self,
                 name,
                 size,
                 num_layers=1,
                 w_init=init.GlorotUniform(),
                 b_init=init.Zeros()):
        """Residual network cell for DNN.

        Args:
            name (str): Widget name.
            size (int): Input and output size.
            num_layers (int): Number of layers.
            w_init (init.Initializer): Initializer for weight.
            b_init (initializers.Initializer): Initializer for bias.

        """
        if num_layers < 1:
            raise ValueError(
                'Invalid number of layers. Number that larger than 1 expected, got %d.' % num_layers
            )
        self._size = size
        self._num_layers = num_layers
        self._w_init = w_init
        self._b_init = b_init
        self._layers = list()
        super(ResidualLayer, self).__init__(name)

    @property
    def size(self):
        return self._size

    @property
    def num_layers(self):
        return self._num_layers

    def _build(self):
        for i in range(self._num_layers):
            layer = basic.Linear(
                'lin_' + str(i),
                input_size=self._size,
                output_size=self._size,
                w_init=self._w_init,
                b_init=self._b_init
            )
            self._layers.append(layer)

    def _setup(self,
               x,
               axis=-1,
               activation=ops.lrelu,
               name='out',
               axes=None):
        """Setup.

        Args:
            x: Input tensor.
            activation: Activation function.
            name (str): Output name.

        Returns:
            tf.Tensor: Output Tensor.

        """
        h = x
        for layer in self._layers[:-1]:
            h = layer.setup(h, axis=axis, axes=axes)
            if activation is not None:
                h = activation(h)

        h = self._layers[-1].setup(h, axis=axis, axes=axes)
        if activation is not None:
            h = tf.add(h, x)
            h = activation(h, name=name)
        else:
            h = tf.add(h, x, name=name)
        return h


class HighwayLayer(common.Widget):
    """Highway network cell for DNN.

    The original version is contributed by zhkun~(Kun Zhang) in his testing code.
    """

    def __init__(self,
                 name,
                 size,
                 w_init=init.GlorotUniform(),
                 b_init=init.Zeros()):
        """Highway network cell for DNN.

        Args:
            name (str): Widget name.
            size (int): Input and output size.
            w_init (init.Initializer): Initializer for weight.
            b_init (initializers.Initializer): Initializer for bias.

        """
        self._size = size
        self._w_init = w_init
        self._b_init = b_init
        super(HighwayLayer, self).__init__(name)

    def _build(self):
        self._linear = basic.Linear(
            'lin',
            input_size=self._size,
            output_size=self._size,
            w_init=self._w_init,
            b_init=self._b_init
        )
        self._gate = basic.Linear(
            'gate',
            input_size=self._size,
            output_size=self._size,
            w_init=self._w_init,
            b_init=self._b_init
        )

    def _setup(self,
               x,
               axis=-1,
               activation=ops.lrelu,
               name='out',
               axes=None):
        """Setup.

        Args:
            x (tf.Tensor): Input tensor.
            activation ((tf.Tensor) -> tf.Tensor): Activation function.
            name (str): Output name.

        Returns:
            tf.Tensor: Output Tensor.

        """
        h = self._linear.setup(x, axis=axis, axes=axes)
        if activation is not None:
            h = activation(h)

        g = self._gate.setup(x, axis=axis, axes=axes)
        g = tf.nn.sigmoid(g)

        y = tf.add(
            tf.multiply(g, h),
            tf.multiply((1.0 - g), x),
            name=name
        )
        return y


class LayerNorm(common.Widget):

    def __init__(self, name, size, eps=1e-6):
        self._name = name
        self._size = size
        self._eps = eps
        super(LayerNorm, self).__init__(name)

    @property
    def size(self):
        return self._size

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=init.Zeros(),
            shape=(self._size,),
            dtype=conf.float
        )
        self._b = self._variable(
            name='b',
            initializer=init.Zeros(),
            shape=(self._size,),
            dtype=conf.float
        )

    def _setup(self, x, name='out'):
        """Setup for a tensor.

        Args:
            x: A tensor whose last dimension should be equal to "size".
            name (str): The output name.

        Returns:
            A tensor which has the same shape as "x".

        """
        mean, var = tf.nn.moments(x, axes=-1, keep_dims=True)
        normalized = (x - mean) / tf.sqrt(var + self._eps)
        result = tf.add(self._w * normalized, self._b, name=name)
        return result
