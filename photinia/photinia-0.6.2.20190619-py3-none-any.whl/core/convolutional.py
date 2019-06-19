#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import math

import tensorflow as tf

from . import common
from .. import conf
from .. import init


class Conv2D(common.Widget):

    def __init__(self,
                 name,
                 input_channels=None,
                 output_channels=None,
                 filter_size=None,
                 stride_size=None,
                 input_size=None,
                 filter_height=None, filter_width=None,
                 stride_height=None, stride_width=None,
                 padding='SAME',
                 use_bias=True,
                 w_init=init.TruncatedNormal(),
                 b_init=init.Zeros()):
        ################################################################################
        # filter and stride
        ################################################################################
        self._filter_height, self._filter_width = filter_height, filter_width
        if filter_size is not None:
            if isinstance(filter_size, (tuple, list)):
                assert len(filter_size) == 2
                self._filter_height, self._filter_width = filter_size
            else:
                self._filter_height = self._filter_width = filter_size
        if self._filter_height is None or self._filter_width is None:
            raise ValueError(f'Invalid filter: height={self._filter_height}, width={self._filter_width}.')

        self._stride_height, self._stride_width = stride_height, stride_width
        if stride_size is not None:
            if isinstance(stride_size, (tuple, list)):
                assert len(stride_size) == 2
                self._stride_height, self._stride_width = stride_size
            else:
                self._stride_height = self._stride_width = stride_size
        if self._stride_height is None or self._stride_width is None:
            raise ValueError(f'Invalid stride: height={self._stride_height}, width={self._stride_width}.')

        ################################################################################
        # misc
        ################################################################################
        padding = padding.upper()
        assert padding in {'SAME', 'VALID'}
        self._padding = padding

        self._use_bias = use_bias
        self._w_init = w_init
        self._b_init = b_init

        ################################################################################
        # input_size and output_size
        ################################################################################
        self._input_channels = input_channels
        self._output_channels = output_channels
        if input_size is None:
            self._input_size = None
            self._input_height = None
            self._input_width = None
            self._flat_size = None
        else:
            self._input_size = input_size
            if isinstance(input_size, (tuple, list)):
                if len(input_size) == 2:
                    self._input_height, self._input_width = input_size
                elif len(input_size) == 3:
                    self._input_height, self._input_width, self._input_channels = input_size
                else:
                    raise ValueError(f'Invalid input_size {input_size}.')
            else:
                self._input_height = input_size
                self._input_width = input_size
            if self._padding == 'SAME':
                self._output_height = math.ceil(self._input_height / self._stride_height)
                self._output_width = math.ceil(self._input_width / self._stride_width)
            else:
                self._output_height = math.ceil((self._input_height - self._filter_height + 1) / self._stride_height)
                self._output_width = math.ceil((self._input_width - self._filter_width + 1) / self._stride_width)
            self._flat_size = self._output_height * self._output_width * output_channels

        super(Conv2D, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def output_size(self):
        return self._output_height, self._output_width

    @property
    def output_height(self):
        return self._output_height

    @property
    def output_width(self):
        return self._output_width

    @property
    def output_channels(self):
        return self._output_channels

    @property
    def filter_height(self):
        return self._filter_height

    @property
    def filter_width(self):
        return self._filter_width

    @property
    def stride_height(self):
        return self._stride_height

    @property
    def stride_width(self):
        return self._stride_width

    @property
    def flat_size(self):
        return self._flat_size

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(
                self._filter_height,
                self._filter_width,
                self._input_channels,
                self._output_channels
            ),
            dtype=conf.dtype
        )
        if self._use_bias:
            self._b = self._variable(
                name='b',
                initializer=self._b_init,
                shape=(self._output_channels,),
                dtype=conf.dtype
            )

    @property
    def w(self):
        return self._w

    @property
    def b(self):
        return self._b

    def _setup(self, x, name='out'):
        if self._use_bias:
            y = tf.nn.conv2d(
                input=x,
                filter=self._w,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding=self._padding,
                data_format='NHWC'
            )
            y = tf.add(y, self._b, name=name)
        else:
            y = tf.nn.conv2d(
                input=x,
                filter=self._w,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding=self._padding,
                data_format='NHWC',
                name=name
            )
        return y


class Deconv2D(common.Widget):

    def __init__(self,
                 name,
                 input_channels=None,
                 output_channels=None,
                 filter_size=None,
                 stride_size=None,
                 input_size=None,
                 filter_height=None, filter_width=None,
                 stride_height=None, stride_width=None,
                 use_bias=True,
                 w_init=init.TruncatedNormal(),
                 b_init=init.Zeros()):
        ################################################################################
        # filter and stride
        ################################################################################
        self._filter_height, self._filter_width = filter_height, filter_width
        if filter_size is not None:
            if isinstance(filter_size, (tuple, list)):
                assert len(filter_size) == 2
                self._filter_height, self._filter_width = filter_size
            else:
                self._filter_height = self._filter_width = filter_size
        if self._filter_height is None or self._filter_width is None:
            raise ValueError(f'Invalid filter: height={self._filter_height}, width={self._filter_width}.')

        self._stride_height, self._stride_width = stride_height, stride_width
        if stride_size is not None:
            if isinstance(stride_size, (tuple, list)):
                assert len(stride_size) == 2
                self._stride_height, self._stride_width = stride_size
            else:
                self._stride_height = self._stride_width = stride_size
        if self._stride_height is None or self._stride_width is None:
            raise ValueError(f'Invalid stride: height={self._stride_height}, width={self._stride_width}.')

        ################################################################################
        # misc
        ################################################################################
        # TODO: now it only support the "SAME" padding method
        self._use_bias = use_bias
        self._w_init = w_init
        self._b_init = b_init

        ################################################################################
        # input_size and output_size
        ################################################################################
        self._input_channels = input_channels
        self._output_channels = output_channels
        if input_size is None:
            self._input_size = None
            self._input_height = None
            self._input_width = None
            self._flat_size = None
        else:
            self._input_size = input_size
            if isinstance(input_size, (tuple, list)):
                assert len(input_size) == 2
                self._input_height, self._input_width = input_size
            else:
                self._input_height = input_size
                self._input_width = input_size
                self._output_height = self._input_height * self._stride_height
                self._output_width = self._input_width * self._stride_width

        super(Deconv2D, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def output_size(self):
        return self._output_height, self._output_width

    @property
    def output_height(self):
        return self._output_height

    @property
    def output_width(self):
        return self._output_width

    @property
    def output_channels(self):
        return self._output_channels

    @property
    def filter_height(self):
        return self._filter_height

    @property
    def filter_width(self):
        return self._filter_width

    @property
    def stride_height(self):
        return self._stride_height

    @property
    def stride_width(self):
        return self._stride_width

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(
                self._filter_height,
                self._filter_width,
                self._output_channels,
                self._input_channels
            ),
            dtype=conf.dtype
        )
        if self._use_bias:
            self._b = self._variable(
                name='b',
                initializer=self._b_init,
                shape=(self._output_channels,),
                dtype=conf.dtype
            )

    @property
    def w(self):
        return self._w

    @property
    def b(self):
        return self._b

    def _setup(self, x, name='out'):
        input_shape = tf.shape(x)
        batch_size, input_height, input_width = input_shape[0], input_shape[1], input_shape[2]
        output_shape = (
            batch_size,
            input_height * self._stride_height,
            input_width * self._stride_width,
            self._output_channels
        )
        if self._use_bias:
            y = tf.nn.conv2d_transpose(
                value=x,
                filter=self._w,
                output_shape=output_shape,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding='SAME',
                data_format='NHWC'
            )
            y = tf.add(y, self._b, name=name)
        else:
            y = tf.nn.conv2d_transpose(
                value=x,
                filter=self._w,
                output_shape=output_shape,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding='SAME',
                data_format='NHWC',
                name=name
            )
        return y


class Pool2D(common.Widget):

    def __init__(self,
                 name,
                 input_size,
                 filter_height=3,
                 filter_width=3,
                 stride_height=2,
                 stride_width=2,
                 padding='SAME',
                 pool_type='max'):
        """Pooling layer for 2D.

        Args:
            name (str): Widget name.
            input_size (tuple[int]|list[int]): Input size.
            filter_height (int): Filter height.
            filter_width (int): Filter width.
            stride_height (int): Stride height.
            stride_width (int): Stride width.
            padding (str): Padding type. Should be one of {"SAME", "VALID"}. Default is "SAME".
            pool_type (str): Pooling type. Should be one of {"max", "mean"}. Default is "max".

        """
        self._input_size = input_size
        self._filter_height = filter_height
        self._filter_width = filter_width
        self._stride_height = stride_height
        self._stride_width = stride_width
        self._padding = padding
        pool_type = pool_type.lower()
        if pool_type not in {'max', 'avg'}:
            raise ValueError('pool_type should be one of {"max", "avg"}, '
                             'but got %s' % pool_type)
        self._pool_type = pool_type
        #
        self._input_height = input_size[0]
        self._input_width = input_size[1]
        self._input_channels = input_size[2]
        if self._padding == 'SAME':
            self._output_height = math.ceil(self._input_height / stride_height) \
                if self._input_height is not None else None
            self._output_width = math.ceil(self._input_width / stride_width) \
                if self._input_width is not None else None
        else:
            self._output_height = math.ceil((self._input_height - filter_height + 1) / stride_height) \
                if self._input_height is not None else None
            self._output_width = math.ceil((self._input_width - filter_width + 1) / stride_width) \
                if self._input_width is not None else None
        if self._output_height is not None and self._output_width is not None:
            self._flat_size = self._output_height * self._output_width * self._input_channels
        else:
            self._flat_size = None
        super(Pool2D, self).__init__(name)

    @property
    def input_size(self):
        return self._input_size

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def output_size(self):
        return self._output_height, self._output_width, self._input_channels

    @property
    def output_height(self):
        return self._output_height

    @property
    def output_width(self):
        return self._output_width

    @property
    def flat_size(self):
        return self._flat_size

    def _build(self):
        pass

    def _setup(self, x, name='out'):
        """Setup pooling layer for 2D.

        Args:
            x (tf.Tensor): Input tensor.
            name (str): Output name.

        Returns:
            tf.Tensor: Output tensor.

        """
        if self._pool_type == 'max':
            y = tf.nn.max_pool(
                value=x,
                ksize=[1, self._filter_height, self._filter_width, 1],
                strides=[1, self._stride_height, self._stride_width, 1],
                padding=self._padding,
                data_format='NHWC',
                name=name
            )
        elif self._pool_type == 'avg':
            y = tf.nn.avg_pool(
                value=x,
                ksize=[1, self._filter_height, self._filter_width, 1],
                strides=[1, self._stride_height, self._stride_width, 1],
                padding=self._padding,
                data_format='NHWC',
                name=name
            )
        else:
            raise ValueError('pool_type should be one of {"max", "avg"}')
        return y


class MaxPool2D(Pool2D):

    def __init__(self,
                 name,
                 input_size,
                 filter_height=3,
                 filter_width=3,
                 stride_height=2,
                 stride_width=2,
                 padding='SAME'):
        super(MaxPool2D, self).__init__(
            name,
            input_size=input_size,
            filter_height=filter_height,
            filter_width=filter_width,
            stride_height=stride_height,
            stride_width=stride_width,
            padding=padding
        )


class GroupConv2D(common.Widget):
    """Group 2D convolutional layer.
    """

    def __init__(self,
                 name,
                 input_size,
                 output_channels,
                 num_groups,
                 filter_height=3,
                 filter_width=3,
                 stride_height=1,
                 stride_width=1,
                 padding='SAME',
                 use_bias=True,
                 w_init=init.TruncatedNormal(),
                 b_init=init.Zeros()):
        if not (isinstance(input_size, (tuple, list)) and len(input_size) == 3):
            raise ValueError('input_size should be tuple or list with 3 elements.')
        self._input_height = input_size[0]
        self._input_width = input_size[1]
        self._input_channels = input_size[2]
        self._output_channels = output_channels
        self._num_groups = num_groups
        self._filter_height = filter_height
        self._filter_width = filter_width
        self._stride_height = stride_height
        self._stride_width = stride_width
        self._padding = padding
        self._use_bias = use_bias
        self._w_init = w_init
        self._b_init = b_init
        #
        if self._padding == 'SAME':
            self._output_height = math.ceil(self._input_height / stride_height) \
                if self._input_height is not None else None
            self._output_width = math.ceil(self._input_width / stride_width) \
                if self._input_width is not None else None
        else:
            self._output_height = math.ceil((self._input_height - filter_height + 1) / stride_height) \
                if self._input_height is not None else None
            self._output_width = math.ceil((self._input_width - filter_width + 1) / stride_width) \
                if self._input_width is not None else None
        if self._output_height is not None and self._output_width is not None:
            self._flat_size = self._output_height * self._output_width * output_channels
        else:
            self._flat_size = None
        super(GroupConv2D, self).__init__(name)

    @property
    def input_size(self):
        return self._input_height, self._input_width

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def output_height(self):
        return self._output_height

    @property
    def output_width(self):
        return self._output_width

    @property
    def output_size(self):
        return self._output_height, self._output_width, self._output_channels

    @property
    def output_channels(self):
        return self._output_channels

    @property
    def num_groups(self):
        return self._num_groups

    @property
    def filter_height(self):
        return self._filter_height

    @property
    def filter_width(self):
        return self._filter_width

    @property
    def stride_height(self):
        return self._stride_height

    @property
    def stride_width(self):
        return self._stride_width

    @property
    def flat_size(self):
        return self._flat_size

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(
                self._filter_height,
                self._filter_width,
                math.floor(self._input_channels / self._num_groups),
                self._output_channels
            ),
            dtype=conf.dtype
        )
        if self._use_bias:
            self._b = self._variable(
                name='b',
                initializer=self._b_init,
                shape=(self._output_channels,),
                dtype=conf.dtype
            )

    @property
    def w(self):
        return self._w

    @property
    def b(self):
        return self._b

    def _setup(self, x, name='out'):
        x_list = tf.split(value=x, num_or_size_splits=self._num_groups, axis=3)
        w_list = tf.split(value=self._w, num_or_size_splits=self._num_groups, axis=3)
        if self._use_bias:
            y_list = [
                tf.nn.conv2d(
                    input=x,
                    filter=w,
                    strides=[1, self._stride_height, self._stride_width, 1],
                    padding=self._padding,
                    data_format='NHWC'
                )
                for x, w in zip(x_list, w_list)
            ]
            y = tf.concat(values=y_list, axis=3)
            y = tf.add(y, self._b, name=name)
        else:
            y_list = [
                tf.nn.conv2d(
                    input=x,
                    filter=w,
                    strides=[1, self._stride_height, self._stride_width, 1],
                    padding=self._padding,
                    data_format='NHWC'
                )
                for x, w in zip(x_list, w_list)
            ]
            y = tf.concat(values=y_list, axis=3, name=name)
        return y


class Conv2DTrans(common.Widget):

    def __init__(self,
                 name,
                 output_size,
                 input_channels,
                 filter_height=3,
                 filter_width=3,
                 stride_height=2,
                 stride_width=2,
                 use_bias=True,
                 w_init=init.TruncatedNormal(),
                 b_init=init.Zeros(),
                 flat_input=False):
        """Transpose convolutional layer for 2D.

        Args:
            name (str): Widget name.
            output_size (tuple[int]|list[int]): Output size.
            input_channels (int): Input size.
            filter_height (int): Filter height.
            filter_width (int): Filter width.
            stride_height (int): Stride height.
            stride_width (int): Stride width.
            w_init (init.Initializer): Weight(Kernel) initializer.
            b_init (initializers.Initializer): Bias initializer.
            flat_input (bool): If True, the output will be converted into flat vector(with shape batch_size * dim).

        """
        if not (isinstance(output_size, (tuple, list)) and len(output_size) == 3):
            raise ValueError('output_size should be tuple or list with 3 elements.')
        self._output_height = output_size[0]
        self._output_width = output_size[1]
        self._output_channels = output_size[2]
        self._input_channels = input_channels
        self._filter_height = filter_height
        self._filter_width = filter_width
        self._stride_height = stride_height
        self._stride_width = stride_width
        self._use_bias = use_bias
        self._w_init = w_init
        self._b_init = b_init
        self._flat_input = flat_input
        #
        self._input_height = math.ceil(self._output_height / stride_height)
        self._input_width = math.ceil(self._output_width / stride_width)
        self._flat_size = self._input_height * self._input_width * input_channels
        super(Conv2DTrans, self).__init__(name)

    @property
    def input_size(self):
        return self._input_height, self._input_width, self._input_channels

    @property
    def input_height(self):
        return self._input_height

    @property
    def input_width(self):
        return self._input_width

    @property
    def input_channels(self):
        return self._input_channels

    @property
    def flat_size(self):
        return self._flat_size

    @property
    def output_size(self):
        return self._output_height, self._output_width, self._output_channels

    @property
    def output_height(self):
        return self._output_height

    @property
    def output_width(self):
        return self._output_width

    @property
    def output_channels(self):
        return self._output_channels

    @property
    def filter_height(self):
        return self._filter_height

    @property
    def filter_width(self):
        return self._filter_width

    @property
    def stride_height(self):
        return self._stride_height

    @property
    def stride_width(self):
        return self._stride_width

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(
                self._filter_height,
                self._filter_width,
                self._output_channels,
                self._input_channels
            ),
            dtype=conf.dtype
        )
        if self._use_bias:
            self._b = self._variable(
                name='b',
                initializer=self._b_init,
                shape=(self._output_channels,),
                dtype=conf.dtype
            )

    @property
    def w(self):
        return self._w

    @property
    def b(self):
        return self._b

    def _setup(self, x, name='out'):
        input_shape = tf.shape(x)
        batch_size, input_height, input_width = input_shape[0], input_shape[1], input_shape[2]
        output_shape = (
            batch_size,
            input_height * self._stride_height,
            input_width * self._stride_width,
            self._output_channels
        )
        if self._use_bias:
            y = tf.nn.conv2d_transpose(
                value=x,
                filter=self._w,
                output_shape=output_shape,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding='SAME',
                data_format='NHWC'
            )
            y = tf.add(y, self._b, name=name)
        else:
            y = tf.nn.conv2d_transpose(
                value=x,
                filter=self._w,
                output_shape=output_shape,
                strides=[1, self._stride_height, self._stride_width, 1],
                padding='SAME',
                data_format='NHWC',
                name=name
            )
        return y
