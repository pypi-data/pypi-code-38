#!/usr/bin/env python3

"""
@author: xi
@since: 2018-03-03
"""

import numpy as np
import tensorflow as tf

import photinia as ph

HEIGHT = 227
WIDTH = 227
SIZE = (HEIGHT, WIDTH)

MEAN = [103.939, 116.779, 123.68]


class AlexNet(ph.Widget):

    def __init__(self,
                 name,
                 activation=tf.nn.relu):
        """AlexNet (Krizhevsky, Alex, Ilya Sutskever, and Geoffrey E. Hinton. "Imagenet classification with deep
        convolutional neural networks." In Advances in neural information processing systems, pp. 1097-1105. 2012.)

        Args:
            name (str): The widget name.
            activation: The activation function.
                Note that the original activation function is ReLU. If you change the activation function when using
                the pre-trained parameters, the model cannot guarantee the original performance. Take your own risk!

        """
        self._height = HEIGHT
        self._width = WIDTH
        self._mean = np.reshape(MEAN, (1, 1, 1, 3))
        self._activation = activation
        super(AlexNet, self).__init__(name)

    def _build(self):
        ################################################################################
        # -> (55, 55, 96)
        # -> (27, 27, 96)
        ################################################################################
        self._conv_1 = ph.Conv2D(
            'conv_1',
            input_size=[self._height, self._width, 3],
            output_channels=96,
            filter_height=11, filter_width=11, stride_width=4, stride_height=4,
            padding='VALID'
        )
        self._pool_1 = ph.Pool2D(
            'pool_1',
            input_size=self._conv_1.output_size,
            filter_height=3, filter_width=3, stride_height=2, stride_width=2,
            padding='VALID',
            pool_type='max'
        )
        ################################################################################
        # -> (27, 27, 256)
        # -> (13, 13, 256)
        ################################################################################
        self._conv_2 = ph.GroupConv2D(
            'conv_2',
            input_size=self._pool_1.output_size,
            output_channels=256,
            num_groups=2,
            filter_height=5, filter_width=5, stride_height=1, stride_width=1,
            padding='SAME'
        )
        self._pool_2 = ph.Pool2D(
            'pool_2',
            input_size=self._conv_2.output_size,
            filter_height=3, filter_width=3, stride_height=2, stride_width=2,
            padding='VALID', pool_type='max'
        )
        ################################################################################
        # -> (13, 13, 384)
        ################################################################################
        self._conv_3 = ph.Conv2D(
            'conv_3',
            input_size=self._pool_2.output_size,
            output_channels=384,
            filter_width=3, filter_height=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        ################################################################################
        # -> (13, 13, 384)
        ################################################################################
        self._conv_4 = ph.GroupConv2D(
            'conv_4',
            input_size=self._conv_3.output_size,
            output_channels=384,
            num_groups=2,
            filter_width=3, filter_height=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        ################################################################################
        # -> (13, 13, 256)
        # -> (6, 6, 256)
        ################################################################################
        self._conv_5 = ph.GroupConv2D(
            'conv_5',
            input_size=self._conv_4.output_size,
            output_channels=256,
            num_groups=2,
            filter_width=3, filter_height=3, stride_width=1, stride_height=1,
            padding='SAME'
        )
        self._pool_5 = ph.Pool2D(
            'pool_5',
            input_size=self._conv_5.output_size,
            filter_height=3, filter_width=3, stride_height=2, stride_width=2,
            padding='VALID', pool_type='max'
        )
        #
        # fc layer
        self._dense_6 = ph.Linear('dense_6', input_size=self._pool_5.flat_size, output_size=4096)
        self._dense_7 = ph.Linear('dense_7', input_size=self._dense_6.output_size, output_size=4096)
        self._dense_8 = ph.Linear('dense_8', input_size=self._dense_7.output_size, output_size=1000)

    def _setup(self, x):
        return ph.setup(
            x - self._mean, [
                self._conv_1, self._activation, self._lrn, self._pool_1, 'map_1',
                self._conv_2, self._activation, self._lrn, self._pool_2, 'map_2',
                self._conv_3, self._activation, 'map_3',
                self._conv_4, self._activation, 'map_4',
                self._conv_5, self._activation, self._pool_5, 'map_5',
                ph.ops.flatten, 'feature_5',
                self._dense_6, self._activation, 'feature_6',
                self._dense_7, self._activation, 'feature_7',
                self._dense_8, tf.nn.softmax
            ]
        )

    @staticmethod
    def _lrn(x):
        return tf.nn.local_response_normalization(
            x,
            depth_radius=1,
            alpha=1e-5,
            beta=0.75,
            bias=1.0
        )
