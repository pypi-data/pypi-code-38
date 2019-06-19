#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import tensorflow as tf

from . import common
from .. import conf
from .. import init


class Embedding(common.Widget):

    def __init__(self,
                 name,
                 voc_size,
                 emb_size,
                 trainable=True,
                 w_init=init.GlorotUniform()):
        """Embedding.

        Args:
            name (str): The widget name.
            voc_size (int): The vocabulary size.
            emb_size (int): The embedding size.
            trainable (bool): Is the embedding matrix trainable?
            w_init (init.Initializer): The matrix initializer.

        """
        self._voc_size = voc_size
        self._emb_size = emb_size
        self._trainable = trainable
        self._w_init = w_init
        super(Embedding, self).__init__(name)

    @property
    def emb_size(self):
        return self._emb_size

    @property
    def output_size(self):
        return self._emb_size

    @property
    def trainable(self):
        return self._trainable

    def _build(self):
        self._w = self._variable(
            name='w',
            initializer=self._w_init,
            shape=(self._voc_size, self._emb_size),
            dtype=conf.dtype,
            trainable=self._trainable
        )

    def _setup(self, indexes, name='out'):
        return tf.nn.embedding_lookup(self._w, indexes, name=name)

    def load_embedding(self, emb_matrix):
        self._w.load(emb_matrix, common.get_session())

    def dump_embedding(self):
        return common.get_session().run(self._w)
