#!/usr/bin/env python3

"""
@author: xi
@since: 2018-03-17
"""

import tensorflow as tf

import photinia as ph


class Encoder(ph.Widget):
    """Encoder
    """

    def __init__(self,
                 name,
                 height,
                 width,
                 channels,
                 output_size,
                 num_layers=5,
                 kernel_size=5,
                 output_channels1=32,
                 w_init=ph.init.TruncatedNormal(),
                 b_init=ph.init.Zeros()):
        self._height = height
        self._width = width
        self._channels = channels
        self._output_size = output_size
        self._num_layers = num_layers
        self._kernel_size = kernel_size
        self._output_channels1 = output_channels1
        self._w_init = w_init
        self._b_init = b_init
        super(Encoder, self).__init__(name)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def channels(self):
        return self._channels

    @property
    def output_size(self):
        return self._output_size

    def _build(self):
        self._layers = list()
        input_size = (self._height, self._width, self._channels)
        output_channels = self._output_channels1
        for i in range(self._num_layers):
            layer = ph.Conv2D(
                'conv%d' % (i + 1),
                input_size, output_channels,
                self._kernel_size, self._kernel_size,
                2, 2,
                w_init=self._w_init,
                b_init=self._b_init
            )
            self._layers.append(layer)
            input_size = layer.output_size
            output_channels *= 2
        self._fc = ph.Linear('fc', self._layers[-1].flat_size, self._output_size)

    def _setup(self, x, activation=ph.ops.lrelu):
        widget_list = list()
        for layer in self._layers:
            widget_list.append(layer)
            widget_list.append(activation)
        widget_list += [ph.ops.flatten, self._fc, tf.nn.tanh]
        y = ph.setup(x, widget_list)
        return y


class Decoder(ph.Widget):
    """Decoder

    [fc1] -->
    [tconv5] --(h/16, w/16, 256)-->
    [tconv4] --(h/8, w/8, 128)-->
    [tconv3] --(h/4, w/4, 64)-->
    [tconv2] --(h/2, w/2, 32)-->
    [tconv1] --(h, w, c)-->
    """

    def __init__(self,
                 name,
                 height,
                 width,
                 channels,
                 input_size,
                 num_layers=5,
                 kernel_size=5,
                 input_channels1=32,
                 w_init=ph.init.TruncatedNormal(),
                 b_init=ph.init.Zeros()):
        self._height = height
        self._width = width
        self._channels = channels
        self._input_size = input_size
        self._num_layers = num_layers
        self._kernel_size = kernel_size
        self._input_channels1 = input_channels1
        self._w_init = w_init
        self._b_init = b_init
        super(Decoder, self).__init__(name)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def channels(self):
        return self._channels

    @property
    def input_size(self):
        return self._input_size

    def _build(self):
        self._layers = list()
        output_size = (self._height, self._width, self._channels)
        input_channels = self._input_channels1
        for i in range(self._num_layers):
            layer = ph.Conv2DTrans(
                'tconv%d' % (self._num_layers - i),
                output_size, input_channels,
                self._kernel_size, self._kernel_size,
                2, 2,
                w_init=self._w_init,
                b_init=self._b_init
            )
            self._layers.append(layer)
            output_size = layer.input_size
            input_channels *= 2
        self._fc = ph.Linear('fc', self._input_size, self._layers[-1].flat_size)

    def _setup(self, x, activation=ph.ops.lrelu, dropout=None):
        widget_list = [
            dropout,
            self._fc, activation,
            (tf.reshape, {'shape': (-1, *self._layers[-1].input_size)})
        ]
        for layer in reversed(self._layers):
            widget_list.append(layer)
            widget_list.append(activation)
        widget_list[-1] = tf.nn.tanh
        y = ph.setup(x, widget_list)
        return y


class Model(ph.Model):

    def __init__(self,
                 name,
                 height,
                 width,
                 channels,
                 emb_size,
                 num_layers=5,
                 kernel_size=5,
                 channels1=32,
                 optimizer=tf.train.RMSPropOptimizer(1e-4, 0.9, 0.9),
                 reg=1e-6):
        """DC-AE trainer.

        h = enc(x),
        y = dec(h),
        loss = mean((y - x) ** 2),
        where h is the embedding of x, and y is the reconstruction.

        :param name: Trainer name.
        :param height: Rows.
        :param width: Columns.
        :param channels: Channels.
        :param emb_size: Embedding size. (Dimension of h.)
        :param optimizer: Optimizer.
        :param reg: Regularize coefficient.
        """
        self._height = height
        self._width = width
        self._channels = channels
        self._emb_size = emb_size
        self._num_layers = num_layers
        self._kernel_size = kernel_size
        self._channels1 = channels1
        self._optimizer = optimizer
        self._reg = reg
        super(Model, self).__init__(name)

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def channels(self):
        return self._channels

    @property
    def emb_size(self):
        return self._emb_size

    def _build(self):
        encoder = Encoder(
            'dc_encoder',
            self._height, self._width, self._channels,
            self._emb_size,
            self._num_layers, self._kernel_size, self._channels1
        )
        decoder = Decoder(
            'dc_decoder',
            self._height, self._width, self._channels,
            self._emb_size,
            self._num_layers, self._kernel_size, self._channels1
        )
        self._encoder = encoder
        self._decoder = decoder

        x = ph.placeholder('x', (None, self._height, self._width, self._channels))
        h = encoder.setup(x, activation=ph.ops.lrelu)
        x_ = decoder.setup(h, activation=ph.ops.lrelu)
        self._x = x
        self._h = h
        self._x_ = x_

        loss = tf.reduce_mean((x_ - x) ** 2)
        self._loss = loss

        reg = ph.reg.Regularizer()
        reg.add_l1_l2(self.get_trainable_variables())

        update = self._optimizer.minimize(loss + reg.get_loss(self._reg) if self._reg > 0 else loss)
        self._add_slot(
            'train',
            inputs=x,
            outputs={'y': x_, 'loss': loss},
            updates=update
        )
        self._add_slot(
            'predict',
            inputs=x,
            outputs={'h': h, 'y': x_, 'loss': loss}
        )

    @property
    def encoder(self):
        return self._encoder

    @property
    def decoder(self):
        return self._decoder

    @property
    def x(self):
        return self._x

    @property
    def h(self):
        return self._h

    @property
    def x_(self):
        return self._x_

    @property
    def loss(self):
        return self._loss
