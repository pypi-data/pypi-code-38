#!/usr/bin/env python3


"""
@author: xi
@since: 2019-05-14
"""

import tensorflow as tf

import photinia as ph


class Gen(ph.Widget):

    def __init__(self,
                 name,
                 input_channels,
                 num_channels,
                 filter_size,
                 dropout,
                 is_training,
                 activation):
        self._num_channels = num_channels
        self._filter_size = filter_size
        self._input_channels = input_channels
        self._dropout = dropout
        self._is_training = is_training
        self._activation = activation
        super(Gen, self).__init__(name)

    def _build(self):
        ic, nc = self._input_channels, self._num_channels

        ################################################################################
        # encoder
        ################################################################################
        self._conv('conv_1', ic, nc * 1)

        self._conv('conv_2', nc * 1, nc * 2)
        self._cobn('cobn_2', nc * 2)

        self._conv('conv_3', nc * 2, nc * 4)
        self._cobn('cobn_3', nc * 4)

        self._conv('conv_4', nc * 4, nc * 8)
        self._cobn('cobn_4', nc * 8)

        self._conv('conv_5', nc * 8, nc * 8)
        self._cobn('cobn_5', nc * 8)

        self._conv('conv_6', nc * 8, nc * 8)
        self._cobn('cobn_6', nc * 8)

        self._conv('conv_7', nc * 8, nc * 8)
        self._cobn('cobn_7', nc * 8)

        self._conv('conv_8', nc * 8, nc * 8)
        self._cobn('cobn_8', nc * 8)

        ################################################################################
        # decoder
        ################################################################################
        self._deconv('deconv_8', nc * 8, nc * 8)
        self._decobn('decobn_8', nc * 8)

        self._deconv('deconv_7', nc * 8 * 2, nc * 8)
        self._decobn('decobn_7', nc * 8)

        self._deconv('deconv_6', nc * 8 * 2, nc * 8)
        self._decobn('decobn_6', nc * 8)

        self._deconv('deconv_5', nc * 8 * 2, nc * 8)
        self._decobn('decobn_5', nc * 8)

        self._deconv('deconv_4', nc * 8 * 2, nc * 4)
        self._decobn('decobn_4', nc * 4)

        self._deconv('deconv_3', nc * 4 * 2, nc * 2)
        self._decobn('decobn_3', nc * 2)

        self._deconv('deconv_2', nc * 2 * 2, nc * 1)
        self._decobn('decobn_2', nc * 1)

        self._deconv('deconv_1', nc * 1 * 2, ic)

    def _conv(self, name, input_channels, output_channels):
        return ph.Conv2D(
            name,
            input_channels=input_channels,
            output_channels=output_channels,
            filter_size=self._filter_size,
            stride_size=2
        )

    def _cobn(self, name, size):
        return ph.BatchNorm(name, size=size, is_training=self._is_training)

    def _deconv(self, name, input_channels, output_channels):
        return ph.Deconv2D(
            name,
            input_channels=input_channels,
            output_channels=output_channels,
            filter_size=self._filter_size,
            stride_size=2
        )

    def _decobn(self, name, size):
        return ph.BatchNorm(name, size=size, is_training=self._is_training)

    def _setup(self, x):
        ################################################################################
        # encoder
        ################################################################################
        h = ph.setup(
            x, [
                self['conv_1'], self._activation, 'map_1',
                self['conv_2'], self['cobn_2'], self._activation, 'map_2',
                self['conv_3'], self['cobn_3'], self._activation, 'map_3',
                self['conv_4'], self['cobn_4'], self._activation, 'map_4',
                self['conv_5'], self['cobn_5'], self._activation, 'map_5',
                self['conv_6'], self['cobn_6'], self._activation, 'map_6',
                self['conv_7'], self['cobn_7'], self._activation, 'map_7',
                self['conv_8'], self['cobn_8'], self._activation, 'map_8',
            ]
        )

        ################################################################################
        # decoder
        ################################################################################
        def concat(a, b):
            return tf.concat([a, b], axis=-1)

        h = ph.setup(
            h, [
                self['deconv_8'], self['decobn_8'], self._activation,
                (concat, {'b': self['map_7']}), self['deconv_7'], self['decobn_7'], self._activation,
                (concat, {'b': self['map_6']}), self['deconv_6'], self['decobn_6'], self._activation,
                (concat, {'b': self['map_5']}), self['deconv_5'], self['decobn_5'], self._activation,
                (concat, {'b': self['map_4']}), self['deconv_4'], self['decobn_4'], self._activation,
                (concat, {'b': self['map_3']}), self['deconv_3'], self['decobn_3'], self._activation, self._dropout,
                (concat, {'b': self['map_2']}), self['deconv_2'], self['decobn_2'], self._activation, self._dropout,
                (concat, {'b': self['map_1']}), self['deconv_1'], tf.nn.tanh
            ]
        )
        return h


class Dis(ph.Widget):

    def __init__(self,
                 name,
                 input_channels,
                 num_channels,
                 filter_size,
                 is_training,
                 activation):
        self._input_channels = input_channels
        self._num_channels = num_channels
        self._filter_size = filter_size
        self._is_training = is_training
        self._activation = activation
        super(Dis, self).__init__(name)

    def _build(self):
        ic, nc = self._input_channels, self._num_channels

        self._conv('conv_1', ic * 2, nc * 1)

        self._conv('conv_2', nc * 1, nc * 2)
        self._cobn('cobn_2', nc * 2)

        self._conv('conv_3', nc * 2, nc * 4)
        self._cobn('cobn_3', nc * 4)

        self._conv('conv_4', nc * 4, nc * 8)
        self._cobn('cobn_4', nc * 8)

        ph.Conv2D(
            'conv_5',
            input_channels=nc * 8,
            output_channels=1,
            filter_size=self._filter_size,
            stride_size=1
        )

    def _conv(self, name, input_channels, output_channels):
        return ph.Conv2D(
            name,
            input_channels=input_channels,
            output_channels=output_channels,
            filter_size=self._filter_size,
            stride_size=2
        )

    def _cobn(self, name, size):
        return ph.BatchNorm(name, size=size, is_training=self._is_training)

    def _setup(self, x, y):
        h = ph.setup(
            tf.concat([x, y], axis=-1), [
                self['conv_1'], self._activation,
                self['conv_2'], self['cobn_2'], self._activation,
                self['conv_3'], self['cobn_3'], self._activation,
                self['conv_4'], self['cobn_4'], self._activation,
                self['conv_5']
            ]
        )
        h = tf.reduce_mean(h, axis=[1, 2, 3])
        h = tf.nn.sigmoid(h)
        return h


class UNet(ph.Model):

    def __init__(self,
                 name,
                 height,
                 width,
                 input_channels,
                 num_channels,
                 filter_size,
                 gan_weight,
                 l1_weight,
                 is_training,
                 activation=ph.ops.swish):
        self._height = height
        self._width = width
        self._input_channels = input_channels
        self._num_channels = num_channels
        self._filter_size = filter_size
        self._gan_weight = gan_weight
        self._l1_weight = l1_weight
        self._is_training = is_training
        self._activation = activation
        super(UNet, self).__init__(name)

    def _build(self):
        image_input = ph.placeholder('image_input', (None, self._height, self._width, self._input_channels), ph.float)
        image_target = ph.placeholder('image_target', (None, self._height, self._width, self._input_channels), ph.float)

        dropout = ph.Dropout('dropout')
        gen = Gen(
            'gen',
            input_channels=self._input_channels,
            num_channels=self._num_channels,
            filter_size=self._filter_size,
            dropout=dropout,
            is_training=self._is_training,
            activation=self._activation
        )
        dis = Dis(
            'dis',
            input_channels=self._input_channels,
            num_channels=self._num_channels,
            filter_size=self._filter_size,
            is_training=self._is_training,
            activation=self._activation
        )

        image_output = gen.setup(image_input)
        predict_real = dis.setup(image_input, image_target)
        predict_fake = dis.setup(image_input, image_output)

        ################################################################################
        # train discriminator
        ################################################################################
        loss_dis = tf.reduce_mean(-(tf.log(predict_real + 1e-8) + tf.log(1 - predict_fake + 1e-8)))
        vars_dis = dis.get_trainable_variables()
        grads_dis = tf.gradients(loss_dis, vars_dis)
        lr = ph.train.ExponentialDecayedValue(
            'lr',
            init_value=1e-3,
            min_value=1e-5,
            num_loops=5e4
        )
        update_dis = tf.train.AdamOptimizer(lr.value, 0.5).apply_gradients(zip(grads_dis, vars_dis))
        self.train_dis = ph.Step(
            inputs=(image_input, image_target),
            outputs=loss_dis,
            updates=update_dis,
            givens={dropout.keep_prob: 1.0}
        )

        ################################################################################
        # train generator
        ################################################################################
        l1_weight = ph.train.ExponentialDecayedValue(
            'l1_weight',
            init_value=1e3,
            min_value=1e2,
            num_loops=5e4
        )
        loss_gen = tf.reduce_mean(-tf.log(predict_fake + 1e-8))
        loss_l1 = tf.reduce_mean(tf.abs(image_target - image_output))
        loss = self._gan_weight * loss_gen + l1_weight.value * loss_l1
        vars_gen = gen.get_trainable_variables()
        grads_gen = tf.gradients(loss, vars_gen)
        update_gen = tf.train.AdamOptimizer(1e-4, 0.5).apply_gradients(zip(grads_gen, vars_gen))
        self.train = ph.Step(
            inputs=(image_input, image_target),
            outputs=(loss_gen, loss_l1, l1_weight.variable, image_output),
            updates=update_gen,
            givens={dropout.keep_prob: 1.0}
        )
