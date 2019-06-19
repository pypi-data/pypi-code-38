#!/usr/bin/env python3

"""
@author: xi
@since: 2019-01-30
"""

import tensorflow as tf

import photinia as ph


class MLPAttention(ph.Widget):

    def __init__(self,
                 name,
                 key_size,
                 attention_size,
                 query_vec_size=None,
                 query_seq_size=None,
                 with_bias=False,
                 w_init=ph.init.GlorotUniform(),
                 b_init=ph.init.Zeros(),
                 activation=ph.ops.lrelu):
        self._key_size = key_size
        self._attention_size = attention_size
        self._query_vec_size = query_vec_size
        self._query_seq_size = query_seq_size
        self._with_bias = with_bias
        self._w_init = w_init
        self._b_init = b_init
        self._activation = activation
        super(MLPAttention, self).__init__(name)

    @property
    def key_size(self):
        return self._key_size

    @property
    def attention_size(self):
        return self._attention_size

    @property
    def query_vec_size(self):
        return self._query_vec_size

    @property
    def query_seq_size(self):
        return self._query_seq_size

    @property
    def with_bias(self):
        return self._with_bias

    def _build(self):
        self._key_layer = ph.Linear(
            'key_layer',
            input_size=self._key_size,
            output_size=self._attention_size,
            with_bias=self._with_bias
        )
        self._att_layer = ph.Linear(
            'att_layer',
            input_size=self._attention_size,
            output_size=1,
            with_bias=self._with_bias
        )
        if self._query_vec_size is not None:
            self._query_vec_layer = ph.Linear(
                'query_vec_layer',
                input_size=self._query_vec_size,
                output_size=self._attention_size,
                with_bias=self._with_bias
            )
        if self._query_seq_size is not None:
            self._query_seq_layer = ph.Linear(
                'query_seq_layer',
                input_size=self._query_seq_size,
                output_size=self._attention_size,
                with_bias=self._with_bias
            )

    def _setup(self,
               key,
               value=None,
               query_vec=None,
               query_seq=None,
               key_mask=None,
               query_mask=None):
        if value is None:
            value = key

        # (batch_size, key_len, key_size)
        # key_score => (batch_size, key_len, attention_size)
        score = self._key_layer.setup(key)

        if query_seq is None:
            if query_vec is not None:
                # (batch_size, query_size)
                # query_vec_score => (batch_size, attention_size)
                query_vec_score = self._query_vec_layer.setup(query_vec)
                # query_vec_score => (batch_size, 1, attention_size)
                query_vec_score = tf.expand_dims(query_vec_score, axis=1)
                score += query_vec_score

            if self._activation is not None:
                score = self._activation(score)

            if key_mask is not None:
                key_mask = tf.expand_dims(key_mask, axis=-1)

            # (batch_size, key_len, attention_size)
            # => (batch_size, key_len, 1)
            score = self._att_layer.setup(score)
            score = ph.ops.softmax(score, axis=1, mask=key_mask)

            value = tf.reduce_sum(score * value, axis=1)
            return value, score
        else:
            query_seq_shape = tf.shape(query_seq)

            # key_score => (batch_size, 1, key_len, attention_size)
            # value => (batch_size, 1, key_len, value_size)
            # key_mask => (batch_size, 1, key_len)
            score = tf.expand_dims(score, axis=1)
            value = tf.expand_dims(value, axis=1)

            # (batch_size, query_len, query_size)
            # query_seq_score => (batch_size, query_len, attention_size)
            query_seq_score = self._query_seq_layer.setup(query_seq)
            # query_seq_score => (batch_size, query_len, 1, attention_size)
            query_seq_score = tf.expand_dims(query_seq_score, axis=2)

            score += query_seq_score
            if query_vec is not None:
                # (batch_size, query_size)
                # query_score => (batch_size, attention_size)
                query_vec_score = self._query_vec_layer.setup(query_vec)
                # query_score => (batch_size, 1, 1, attention_size)
                query_vec_score = tf.reshape(query_vec_score, shape=(-1, 1, 1, self._attention_size))
                score += query_vec_score

            if self._activation is not None:
                score = self._activation(score)

            if key_mask is not None:
                key_mask = tf.expand_dims(key_mask, axis=1)
                key_mask = tf.expand_dims(key_mask, axis=-1)

            # (batch_size, query_len, key_len, attention_size)
            # => (batch_size, query_len, key_len, 1)
            score = self._att_layer.setup(score)
            score = ph.ops.softmax(score, axis=1, mask=key_mask)

            if query_mask is not None:
                query_mask = tf.reshape(query_mask, shape=(query_seq_shape[0], query_seq_shape[1], 1, 1))
                score *= query_mask

            # value => (batch_size, query_len, value_size)
            value = tf.reduce_sum(score * value, axis=2)
            return value, score


class DotProductAttention(ph.Widget):

    def __init__(self,
                 name,
                 dropout=None):
        """DotProductAttention.

        Args:
            name (str): The Widget name.
            dropout (photinia.Dropout): The dropout widget.

        """
        self._dropout = dropout
        super(DotProductAttention, self).__init__(name)

    def _build(self):
        pass

    def _setup(self,
               key,
               value=None,
               query_vec=None,
               query_seq=None,
               key_mask=None,
               query_mask=None,
               activation=None,
               scale=True):
        if value is None:
            value = key

        if query_seq is None:
            if query_vec is None:
                raise ValueError('You must set at least one of "query_vec" or "query_seq".')
            else:
                # (batch_size, feature_size) @ (batch_size, key_len, feature_size)
                # => (batch_size, key_len)
                score = tf.einsum('bf,bkf->bk', query_vec, key)
        else:
            if query_vec is None:
                # (batch_size, query_len, feature_size) @ (batch_size, key_len, feature_size)
                # => (batch_size, query_len, key_len)
                score = tf.einsum('bqf,bkf->bqk', query_seq, key)
            else:
                # (batch_size, feature_size) @ (batch_size, key_len, feature_size)
                # => (batch_size, key_len)
                # => (batch_size, 1, key_len)
                score = tf.einsum('bf,bkf->bk', query_vec, key)
                score = tf.expand_dims(score, axis=1)

                # (batch_size, query_len, feature_size) @ (batch_size, key_len, feature_size)
                # => (batch_size, query_len, key_len)
                score += tf.einsum('bqf,bkf->bqk', query_seq, key)

        if query_seq is None:
            if scale:
                feature_size = tf.cast(tf.shape(query_vec)[-1], ph.float)
                score /= tf.sqrt(feature_size)
            if activation is not None:
                score = activation(score)

            score = ph.ops.softmax(score, axis=1, mask=key_mask)
            # (batch_size, key_len) @ (batch_size, key_len, feature_size)
            # => (batch_size, feature_size)
            value = tf.einsum('bk,bkf->bf', score, value)
            return value, score
        else:
            if scale:
                feature_size = tf.cast(tf.shape(query_seq)[-1], ph.float)
                score /= tf.sqrt(feature_size)
            if activation is not None:
                score = activation(score)

            # (batch_size, key_len)
            # => (batch_size, 1, key_len)
            key_mask = tf.expand_dims(key_mask, axis=1)

            score = ph.ops.softmax(score, axis=2, mask=key_mask)

            # (batch_size, query_len)
            # => (batch_size, query_len, 1)
            query_mask = tf.expand_dims(query_mask, axis=2)

            score *= query_mask
            # (batch_size, query_len, key_len) @ (batch_size, key_len, feature_size)
            # => (batch_size, query_len, feature_size)
            value = tf.einsum('bqk,bkf->bqf', score, value)
            return value, score


class BiLinearAttention(ph.Widget):

    def __init__(self,
                 name,
                 key_size,
                 attention_size,
                 query_vec_size=None,
                 query_seq_size=None,
                 w_init=ph.init.GlorotUniform()):
        self._key_size = key_size
        self._attention_size = attention_size
        self._query_vec_size = query_vec_size
        self._query_seq_size = query_seq_size
        self._w_init = w_init
        super(BiLinearAttention, self).__init__(name)

    @property
    def key_size(self):
        return self._key_size

    @property
    def attention_size(self):
        return self._attention_size

    @property
    def query_vec_size(self):
        return self._query_vec_size

    @property
    def query_seq_size(self):
        return self._query_seq_size

    def _build(self):
        if self._query_vec_size is None and self._query_seq_size is None:
            raise ValueError('You should set at least one of "query_vec_size" or "query_seq_size".')
        if self._query_vec_size is not None:
            self._w_vec = self._variable(
                'w_vec',
                initializer=self._w_init,
                shape=(self._query_vec_size, self._key_size),
                dtype=ph.float
            )
        if self._query_seq_size is not None:
            self._w_seq = self._variable(
                'w_seq',
                initializer=self._w_init,
                shape=(self._query_seq_size, self._key_size),
                dtype=ph.float
            )

    def _setup(self,
               key,
               value=None,
               query_vec=None,
               query_seq=None,
               key_mask=None,
               query_mask=None):
        if value is None:
            value = key

        if query_seq is None:
            if query_vec is None:
                raise ValueError('You must set at least one of "query_vec" or "query_seq".')
            else:
                # (batch_size, query_vec_size) @ (query_vec_size, key_size)
                # => (batch_size, key_size)
                score = tf.matmul(query_vec, self._w_vec)

                # (batch_size, key_size) @ (batch_size, key_len, key_size)
                # => (batch_size, key_len)
                score = tf.einsum('bg,bkg->bk', score, key)

                # => (batch_size, key_len, 1)
                score = ph.ops.softmax(score, axis=1, mask=key_mask)
                score = tf.expand_dims(score, axis=-1)

                # (batch_size, key_len, 1) * (batch_size, key_len, feature_size)
                # => (batch_size, key_len, feature_size)
                value *= score
                value = tf.reduce_sum(value, axis=1)
                return value, score
        else:
            if query_vec is None:
                # (batch_size, query_len, query_seq_size) @ (query_seq_size, key_size)
                # => (batch_size, query_len, key_size)
                score = tf.einsum('bqf,fg->bqg', query_seq, self._w_seq)

                # (batch_size, query_len, key_size) @ (batch_size, key_len, key_size)
                # => (batch_size, query_len, key_len)
                score = tf.einsum('bqg,bkg->bqk', score, key)

                # (batch_size, key_len)
                # => (batch_size, 1, key_len)
                key_mask = tf.expand_dims(key_mask, axis=1)

                # => (batch_size, query_len, key_len, 1)
                score = ph.ops.softmax(score, axis=2, mask=key_mask)
                score = tf.expand_dims(score, axis=-1)

                # => (batch_size, 1, key_len, key_size)
                value = tf.expand_dims(value, axis=1)

                # (batch_size, query_len, key_len, 1) @ (batch_size, 1, key_len, key_size)
                # => (batch_size, query_len, key_len, key_size)
                # => (batch_size, query_len, key_size)
                value *= score
                value = tf.reduce_sum(value, axis=2)
                return value, score
            else:
                # (batch_size, query_vec_size) @ (query_vec_size, key_size)
                # => (batch_size, key_size)
                # => (batch_size, 1, key_size)
                score = tf.matmul(query_vec, self._w_vec)
                score = tf.expand_dims(score, axis=1)

                # (batch_size, query_len, query_seq_size) @ (query_seq_size, key_size)
                # => (batch_size, query_len, key_size)
                score += tf.einsum('bqf,fg->bqg', query_seq, self._w_seq)

                # (batch_size, query_len, key_size) @ (batch_size, key_len, key_size)
                # => (batch_size, query_len, key_len)
                score = tf.einsum('bqg,bkg->bqk', score, key)

                # (batch_size, key_len)
                # => (batch_size, 1, key_len)
                key_mask = tf.expand_dims(key_mask, axis=1)

                # => (batch_size, query_len, key_len, 1)
                score = ph.ops.softmax(score, axis=2, mask=key_mask)
                score = tf.expand_dims(score, axis=-1)

                # => (batch_size, 1, key_len, key_size)
                value = tf.expand_dims(value, axis=1)

                # (batch_size, query_len, key_len, 1) @ (batch_size, 1, key_len, key_size)
                # => (batch_size, query_len, key_len, key_size)
                # => (batch_size, query_len, key_size)
                value *= score
                value = tf.reduce_sum(value, axis=2)
                return value, score
