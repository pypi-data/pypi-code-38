from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

import tensorflow as tf


# TODO: Enum constants
class Padding:
    Constant = 'CONSTANT'
    Reflect = 'REFLECT'
    Symmetric = 'SYMMETRIC'
    NONE = 'NONE'


class Norm:
    Batch = 'Batch'
    Instance = 'Instance'
    Layer = 'Layer'
    Weight = 'Weight'
    NONE = None

    @classmethod
    def get(cls, name):
        if name == cls.Batch:
            return tf.layers.batch_normalization
        elif name == cls.Instance:
            return tf.contrib.layers.instance_norm
        elif name == cls.Layer:
            return tf.contrib.layers.layer_norm
        else:
            raise ValueError()


def prelu(inputs):
    with tf.variable_scope(None, default_name='PReLU', values=[inputs]):
        alpha = tf.get_variable('alpha', shape=(), dtype=tf.float32, initializer=tf.initializers.constant())
        inputs = tf.nn.leaky_relu(inputs, alpha=alpha)

        return inputs


class Nonlinear:
    ReLU = 'ReLU'
    LeakyReLU = 'LeakyReLU'
    PReLU = 'PReLU'
    Sigmoid = 'Sigmoid'
    Tanh = 'Tanh'
    NONE = None

    @classmethod
    def get(cls, name):
        if name == cls.ReLU:
            return tf.nn.relu
        elif name == cls.LeakyReLU:
            return tf.nn.leaky_relu
        elif name == cls.PReLU:
            return prelu
        elif name == cls.Sigmoid:
            return tf.nn.sigmoid
        elif name == cls.Tanh:
            return tf.nn.tanh
        else:
            raise ValueError()


class DeconvMethod:
    NNConv = 'NNConv'
    ConvTranspose = 'ConvTranspose'


class Conv2DWeightNorm(tf.layers.Conv2D):

    def build(self, input_shape):
        self.wn_g = self.add_weight(
            name='wn_g',
            shape=(self.filters,),
            dtype=self.dtype,
            initializer=tf.initializers.ones,
            trainable=True,
        )
        super(Conv2DWeightNorm, self).build(input_shape)
        square_sum = tf.reduce_sum(
            tf.square(self.kernel), [0, 1, 2], keepdims=False)
        inv_norm = tf.rsqrt(square_sum)
        self.kernel = self.kernel * (inv_norm * self.wn_g)


def conv2d_weight_norm(inputs,
                       filters,
                       kernel_size,
                       strides=(1, 1),
                       padding='valid',
                       data_format='channels_last',
                       dilation_rate=(1, 1),
                       activation=None,
                       use_bias=True,
                       kernel_initializer=None,
                       bias_initializer=tf.zeros_initializer(),
                       kernel_regularizer=None,
                       bias_regularizer=None,
                       activity_regularizer=None,
                       kernel_constraint=None,
                       bias_constraint=None,
                       trainable=True,
                       name=None,
                       reuse=None):
    layer = Conv2DWeightNorm(
        filters=filters,
        kernel_size=kernel_size,
        strides=strides,
        padding=padding,
        data_format=data_format,
        dilation_rate=dilation_rate,
        activation=activation,
        use_bias=use_bias,
        kernel_initializer=kernel_initializer,
        bias_initializer=bias_initializer,
        kernel_regularizer=kernel_regularizer,
        bias_regularizer=bias_regularizer,
        activity_regularizer=activity_regularizer,
        kernel_constraint=kernel_constraint,
        bias_constraint=bias_constraint,
        trainable=trainable,
        name=name,
        dtype=inputs.dtype.base_dtype,
        _reuse=reuse,
        _scope=name)
    return layer.apply(inputs)


def conv2d(inputs,
           num_filters,
           kernel_size,
           strides=1,
           dilation_rate=1,
           padding_mode=Padding.Constant,
           norm_fn=Norm.Instance,
           non_linear_fn=Nonlinear.ReLU,
           use_bias=True,
           scope=None,
           reuse=None):
    with tf.variable_scope(scope, 'Conv2d_{kernel_size}x{kernel_size}_{num_filters}'.format(kernel_size=kernel_size,
                                                                                            num_filters=num_filters),
                           values=[inputs], reuse=reuse):
        # Padding
        if padding_mode.upper() != Padding.NONE:
            padding = kernel_size + (kernel_size - 1) * (dilation_rate - 1) - strides
            padding = [padding // 2, padding - padding // 2]
            inputs = tf.pad(inputs, [[0] * 2, padding, padding, [0] * 2], mode=padding_mode)

        # Conv
        conv_fn = tf.layers.conv2d if norm_fn != Norm.Weight else conv2d_weight_norm

        inputs = conv_fn(inputs,
                         num_filters,
                         kernel_size,
                         strides=(strides, strides),
                         dilation_rate=(dilation_rate, dilation_rate),
                         padding='VALID',
                         use_bias=use_bias)

        # Normalization
        if norm_fn is not None and norm_fn != Norm.Weight:
            if not callable(norm_fn):
                norm_fn = Norm.get(norm_fn)
            inputs = norm_fn(inputs)

        # Non-linearity
        if non_linear_fn is not None:
            if not callable(non_linear_fn):
                non_linear_fn = Nonlinear.get(non_linear_fn)
            inputs = non_linear_fn(inputs)

        tf.add_to_collection(tf.GraphKeys.ACTIVATIONS, inputs)

        return inputs


def deconv2d(inputs,
             num_filters,
             kernel_size,
             strides=1,
             padding_mode=Padding.Constant,
             norm_fn=Norm.Layer,
             non_linear_fn=Nonlinear.ReLU,
             use_bias=True,
             method=DeconvMethod.NNConv,
             scope=None,
             reuse=None):
    with tf.variable_scope(scope, 'Deconv2d_{kernel_size}x{kernel_size}_{num_filters}'.format(kernel_size=kernel_size,
                                                                                              num_filters=num_filters),
                           values=[inputs], reuse=reuse):
        if method == DeconvMethod.NNConv:
            if strides > 1:
                shape = tf.shape(inputs)[1:3]
                inputs = tf.image.resize_nearest_neighbor(inputs, shape * strides)

            # Conv
            inputs = conv2d(inputs,
                            num_filters,
                            kernel_size,
                            strides=1,
                            padding_mode=padding_mode,
                            norm_fn=norm_fn,
                            non_linear_fn=non_linear_fn,
                            use_bias=use_bias)
        elif method == DeconvMethod.ConvTranspose:
            inputs = tf.layers.conv2d_transpose(inputs,
                                                num_filters,
                                                kernel_size,
                                                strides=(strides, strides),
                                                padding='SAME',
                                                use_bias=use_bias)

            # Normalization
            if norm_fn is not None:
                if not callable(norm_fn):
                    norm_fn = Norm.get(norm_fn)
                inputs = norm_fn(inputs)

            # Non-linearity
            if non_linear_fn is not None:
                if not callable(non_linear_fn):
                    non_linear_fn = Nonlinear.get(non_linear_fn)
                inputs = non_linear_fn(inputs)

        else:
            raise ValueError('`method` should be either {} or {}'.format(DeconvMethod.NNConv,
                                                                         DeconvMethod.ConvTranspose))

        tf.add_to_collection(tf.GraphKeys.ACTIVATIONS, inputs)

        return inputs


def residual_block(inputs,
                   num_filters,
                   padding_mode=Padding.Constant,
                   norm_fn=Norm.Instance,
                   non_linear_fn=Nonlinear.ReLU,
                   use_bias=True,
                   scale=1.0,
                   scope=None,
                   reuse=None):
    with tf.variable_scope(scope, 'Residual_Block', values=[inputs], reuse=reuse):
        shortcut = inputs
        inputs = conv2d(inputs, num_filters, 3,
                        padding_mode=padding_mode, norm_fn=norm_fn, non_linear_fn=non_linear_fn, use_bias=use_bias)
        inputs = conv2d(inputs, num_filters, 3,
                        padding_mode=padding_mode, norm_fn=norm_fn, non_linear_fn=Nonlinear.NONE, use_bias=use_bias)

        return scale * inputs + shortcut


def linear(inputs,
           num_units,
           norm_fn=Norm.Instance,
           non_linear_fn=Nonlinear.ReLU,
           use_bias=True,
           scope=None,
           reuse=None):
    with tf.variable_scope(scope, 'Linear_{num_units}'.format(num_units=num_units),
                           values=[inputs], reuse=reuse):
        # FC
        inputs = tf.layers.dense(inputs,
                                 num_units,
                                 use_bias=use_bias)

        # Normalization
        if norm_fn is not None:
            if not callable(norm_fn):
                norm_fn = Norm.get(norm_fn)
            inputs = norm_fn(inputs)

        # Non-linearity
        if non_linear_fn is not None:
            if not callable(non_linear_fn):
                non_linear_fn = Nonlinear.get(non_linear_fn)
            inputs = non_linear_fn(inputs)

        tf.add_to_collection(tf.GraphKeys.ACTIVATIONS, inputs)

        return inputs


def adaptive_instance_norm(inputs, gamma, beta, scope=None):
    with tf.variable_scope(scope, 'Adaptive_Instance_Norm', values=[inputs, gamma, beta]):
        inputs = tf.contrib.layers.instance_norm(inputs, center=False, scale=False)
        inputs = gamma * inputs + beta

        return inputs
