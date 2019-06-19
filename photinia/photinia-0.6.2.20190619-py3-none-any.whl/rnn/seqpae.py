#!/usr/bin/env python3

"""
@author: xi
@since: 2018-08-24
"""

import tensorflow as tf

import photinia as ph
from . import seqae


class SeqPAE(ph.Model):

    def __init__(self,
                 name,
                 voc_size,
                 emb_size,
                 state_size,
                 semantic_weight=1.0,
                 optimizer=tf.train.RMSPropOptimizer(1e-4, 0.9, 0.9),
                 reg_weight=1e-5):
        """Pair-wise auto-encoder for sequence

        Args:
            name (str): Model name.
            voc_size (int): Vocabulary size.
            emb_size (int): Embedding size.
            state_size (int): State size.
            semantic_weight (float): Weight of the semantic loss.
            optimizer: Optimizer to train the model.
            reg_weight (float): Regularizer.

        """
        self._voc_size = voc_size
        self._emb_size = emb_size
        self._state_size = state_size
        self._semantic_weight = semantic_weight
        self._optimizer = optimizer
        self._reg_weight = reg_weight
        super(SeqPAE, self).__init__(name)

    def _build(self):
        input_seq0 = self._input_seq0 = ph.placeholder('input_seq0', (None, None, self._voc_size))
        input_seq1 = self._input_seq1 = ph.placeholder('input_seq1', (None, None, self._voc_size))
        encoder = self._encoder = seqae.Encoder(
            'encoder',
            voc_size=self._voc_size,
            emb_size=self._emb_size,
            state_size=self._state_size
        )
        emb0 = self._emb0 = encoder.setup(input_seq0)
        emb1 = self._emb1 = encoder.setup(input_seq1)

        self.predict = ph.Step(
            inputs=input_seq0,
            outputs=emb0
        )

        decoder = self._decoder = seqae.Decoder(
            'seq_decoder',
            self._voc_size,
            self._emb_size,
            self._state_size,
            encoder.emb_layer
        )
        max_len0 = tf.shape(input_seq0)[1]
        max_len1 = tf.shape(input_seq1)[1]
        rec0 = self._rec0 = decoder.setup(emb0, max_len0)
        rec1 = self._rec1 = decoder.setup(emb1, max_len1)

        #
        # reconstruction loss of the two sequences
        loss_rec0 = -ph.ops.log_likelihood(input_seq0, rec0, reduce=False)
        loss_rec0 *= tf.sequence_mask(ph.ops.sequence_length(input_seq0), dtype=ph.dtype)
        loss_rec0 = ph.ops.reduce_sum_loss(loss_rec0)
        loss_rec0 = tf.reduce_mean(loss_rec0)
        self._loss_rec0 = loss_rec0

        loss_rec1 = -ph.ops.log_likelihood(input_seq1, rec1, reduce=False)
        loss_rec1 *= tf.sequence_mask(ph.ops.sequence_length(input_seq1), dtype=ph.dtype)
        loss_rec1 = ph.ops.reduce_sum_loss(loss_rec1)
        loss_rec1 = tf.reduce_mean(loss_rec1)
        self._loss_rec1 = loss_rec1

        loss_rec = self._loss_rec = loss_rec0 + loss_rec1

        #
        # semantic loss
        # norm0 = tf.norm(emb0, axis=1, keepdims=True)
        # norm1 = tf.norm(emb1, axis=1, keepdims=True)
        # s = tf.reduce_sum(emb0 * emb1, axis=1) / (norm0 * norm1 + 1e-6)
        # s = tf.reduce_mean(s)
        #
        # loss_semantic = self._loss_semantic = 1.0 - s

        loss_semantic = tf.reduce_sum(tf.square(emb0 - emb1), axis=1)
        loss_semantic = tf.reduce_mean(loss_semantic)
        self._loss_semantic = loss_semantic

        #
        # train step
        loss = self._loss = loss_rec + self._semantic_weight * loss_semantic
        reg = ph.reg.Regularizer()
        reg.add_l1_l2(self.get_trainable_variables())
        update = self._optimizer.minimize(loss + reg.get_loss(self._reg_weight) if self._reg_weight > 0 else loss)
        self.train = ph.Step(
            inputs=(input_seq0, input_seq1),
            outputs={
                'loss': loss,
                'loss_rec': loss_rec,
                'loss_semantic': loss_semantic,
                'rec0': rec0,
                'rec1': rec1
            },
            updates=update
        )
