#!/usr/bin/env python3


"""
@author: zhkun, xi
@since: 2018-07-13


The pre-trained parameters can be downloaded from:

https://pan.baidu.com/s/1tae2EtyDw3JMgcxUyFgJbg

Use "model.load_parameters(path)" to load.
"""

import numpy as np
import tensorflow as tf

import photinia as ph

HEIGHT = 224
WIDTH = 224
SIZE = (HEIGHT, WIDTH)

MEAN = [103.939, 116.779, 123.68]


class VGG16(ph.Widget):

    @ph.deprecated(message='ph.cnn.vgg.VGG16 will no longer used. Use ph.apps.imagenet.vgg.VGG16 instead.')
    def __init__(self, name='vgg16'):
        self._height = HEIGHT
        self._width = WIDTH
        self._mean = np.reshape(MEAN, (1, 1, 1, 3))
        super(VGG16, self).__init__(name)

    def _build(self):
        # conv1 padding=SAME
        self._conv1_1 = ph.Conv2D(
            'conv1_1',
            input_size=[self._height, self._width, 3],
            output_channels=64,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        # conv1_2 padding=SAME
        self._conv1_2 = ph.Conv2D(
            'conv1_2',
            input_size=self._conv1_1.output_size,
            output_channels=64,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool1 = ph.Pool2D(
            'pool1',
            input_size=self._conv1_2.output_size,
            filter_height=2, filter_width=2, stride_height=2, stride_width=2,
            padding='SAME',
            pool_type='max'
        )
        #
        # conv2 padding=SAME
        self._conv2_1 = ph.Conv2D(
            'conv2_1',
            input_size=self._pool1.output_size,
            output_channels=128,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv2_2 = ph.Conv2D(
            'conv2_2',
            input_size=self._conv2_1.output_size,
            output_channels=128,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool2 = ph.Pool2D(
            'pool2',
            input_size=self._conv2_2.output_size,
            filter_height=2, filter_width=2, stride_height=2, stride_width=2,
            padding='SAME',
            pool_type='max'
        )
        #
        # conv3 padding=SAME
        self._conv3_1 = ph.Conv2D(
            'conv3_1',
            input_size=self._pool2.output_size,
            output_channels=256,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv3_2 = ph.Conv2D(
            'conv3_2',
            input_size=self._conv3_1.output_size,
            output_channels=256,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv3_3 = ph.Conv2D(
            'conv3_3',
            input_size=self._conv3_2.output_size,
            output_channels=256,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool3 = ph.Pool2D(
            'pool3',
            input_size=self._conv3_3.output_size,
            filter_height=2, filter_width=2, stride_height=2, stride_width=2,
            padding='SAME',
            pool_type='max'
        )
        #
        # conv4 padding=SAME
        self._conv4_1 = ph.Conv2D(
            'conv4_1',
            input_size=self._pool3.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv4_2 = ph.Conv2D(
            'conv4_2',
            input_size=self._conv4_1.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv4_3 = ph.Conv2D(
            'conv4_3',
            input_size=self._conv4_2.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool4 = ph.Pool2D(
            'pool4',
            input_size=self._conv4_3.output_size,
            filter_height=2, filter_width=2, stride_height=2, stride_width=2,
            padding='SAME',
            pool_type='max'
        )
        #
        # conv5 padding=SAME
        self._conv5_1 = ph.Conv2D(
            'conv5_1',
            input_size=self._pool4.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv5_2 = ph.Conv2D(
            'conv5_2',
            input_size=self._conv5_1.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._conv5_3 = ph.Conv2D(
            'conv5_3',
            input_size=self._conv5_2.output_size,
            output_channels=512,
            filter_height=3, filter_width=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool5 = ph.Pool2D(
            'pool5',
            input_size=self._conv5_3.output_size,
            filter_height=2, filter_width=2, stride_height=2, stride_width=2,
            padding='SAME',
            pool_type='max'
        )
        #
        # fc layer
        self._fc6 = ph.Linear('fc6', input_size=self._pool5.flat_size, output_size=4096)
        self._fc7 = ph.Linear('fc7', input_size=self._fc6.output_size, output_size=4096)
        self._fc8 = ph.Linear(
            'fc8',
            input_size=self._fc7.output_size, output_size=1000,
            w_init=ph.init.RandomNormal(stddev=1e-4)
        )

    @property
    def encode_size(self):
        return 4096

    @property
    def output_size(self):
        return 1000

    @property
    def fc6(self):
        return self._fc6

    @property
    def fc7(self):
        return self._fc7

    @property
    def fc8(self):
        return self._fc8

    def _setup(self, x, name='out'):
        return ph.setup(
            x - self._mean,
            [self._conv1_1, (tf.nn.relu, 'map1_1'),  # 1
             self._conv1_2, (tf.nn.relu, 'map1_2'), self._pool1,  # 2
             self._conv2_1, (tf.nn.relu, 'map2_1'),  # 3
             self._conv2_2, (tf.nn.relu, 'map2_2'), self._pool2,  # 4
             self._conv3_1, (tf.nn.relu, 'map3_1'),  # 5
             self._conv3_2, (tf.nn.relu, 'map3_2'),  # 6
             self._conv3_3, (tf.nn.relu, 'map3_3'), self._pool3,  # 7
             self._conv4_1, (tf.nn.relu, 'map4_1'),  # 8
             self._conv4_2, (tf.nn.relu, 'map4_2'),  # 9
             self._conv4_3, (tf.nn.relu, 'map4_3'), self._pool4,  # 10
             self._conv5_1, (tf.nn.relu, 'map5_1'),  # 11
             self._conv5_2, (tf.nn.relu, 'map5_2'),  # 12
             self._conv5_3, (tf.nn.relu, 'map5_3'), self._pool5,  # 13
             ph.ops.flatten,
             self._fc6, (tf.nn.relu, 'h6'),  # 14
             self._fc7, (tf.nn.relu, 'h7'),  # 15
             self._fc8, (tf.nn.softmax, name)]  # 16
        )

    def load_parameters(self, model_file):
        ph.io.load_model_from_file(self, model_file, 'vgg16')
