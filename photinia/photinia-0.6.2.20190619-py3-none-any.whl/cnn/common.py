#!/usr/bin/env python3


"""
@author: xi
@since: 2019-05-13
"""

import tensorflow as tf

import photinia as ph


class CharLevelEmbedding(ph.Widget):

    def __init__(self,
                 name,
                 voc_size,
                 emb_size,
                 channels,
                 pooling='max',
                 kernel_height=3,
                 activation=ph.ops.lrelu):
        """利用一维卷积来生成字符级别的编码

        Args:
            name (str): The widget name.
            voc_size: Vocabulary size.
            emb_size: Embedding size.
            channels:
            pooling: Polling type.
            kernel_height: Convolutional kernel height.
                Note that the convolutional kernel size is (kernel_height, 1)

        """
        self._name = name
        self._voc_size = voc_size
        self._emb_size = emb_size
        self._channels = channels
        self._pooling = pooling
        self._kernel_height = kernel_height
        self._activation = activation
        super(CharLevelEmbedding, self).__init__(name)

    def _build(self):
        if not isinstance(self._channels, (tuple, list)):
            self._channels = [self._channels]

        self._char_emb = ph.Embedding(
            'char_emb',
            voc_size=self._voc_size,
            emb_size=self._emb_size
        )

        self._conv_layers = []
        current_size = self._emb_size
        for i, state_size in enumerate([*self._channels, self._emb_size]):
            layer = ph.Conv2D(
                f'conv2d_{i}',
                input_size=(None, None, current_size),
                output_channels=state_size,
                filter_height=self._kernel_height,
                filter_width=1,
                stride_height=1,
                stride_width=1,
            )
            self._conv_layers.append(layer)
            current_size = state_size

        self._norm = ph.LayerNorm('norm', size=self._emb_size)

    def _setup(self,
               seq,
               # dropout=None,
               name='out'):
        # (batch_size, seq_len, word_len)
        # => (batch_size, seq_len, word_len, emb_size)
        seq_emb = self._char_emb.setup(seq)

        # (batch_size, seq_len, word_len, emb_size)
        # => (batch_size, seq_len, word_len, kernel_size[-1])
        for layer in self._conv_layers:
            seq_emb = layer.setup(seq_emb)
            if self._activation is not None:
                seq_emb = self._activation(seq_emb)

        if self._pooling == 'max':
            seq_emb = tf.reduce_max(seq_emb, axis=2)
        else:
            seq_emb = tf.reduce_mean(seq_emb, axis=2)

        # if dropout is not None:
        #     seq_emb = dropout.setup(seq_emb)

        # seq_emb = self._norm(seq_emb, name=name)
        return seq_emb
