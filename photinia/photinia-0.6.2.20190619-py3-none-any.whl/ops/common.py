#!/usr/bin/env python3

"""
@author: xi
@since: 2017-03
"""

import tensorflow as tf

from .. import conf


def log(x, eps=1e-7, name=None):
    """log operation with smooth.

    Args:
        x: Input tensor.
        eps (float): Smooth factor.
        name (str): Operation name.

    Returns:
        Output tensor.

    """
    return tf.log(x + eps, name=name)


def softmax(logit,
            axis=None,
            mask=None,
            scale=None,
            name=None):
    if scale is not None:
        logit *= scale
    logit = tf.exp(logit)
    if mask is not None:
        logit *= mask
    z = tf.reduce_sum(logit, axis=axis, keepdims=True)
    logit = tf.div(logit, z, name=name)
    return logit


def lrelu(x, leak=1e-2, name=None):
    """Leaky ReLU activation function.

    f(x) =        x     , x >= 0,
           leak * x     , x < 0

    Args:
        x: Input tensor.
        leak (float): Leak value. Default is 1e-2.
        name (str): Operation name.

    Returns:
        Output tensor.

    """
    return tf.maximum(x, leak * x, name=name)


def swish(x, name=None):
    """Swish activation function.

    f(x) = x * sigmoid(x)

    Args:
        x: Input tensor.
        name (str): Operation name.

    Returns:
        Output tensor.

    """
    return tf.multiply(tf.nn.sigmoid(x), x, name=name)


def random_gumbel(shape,
                  mu=0.0,
                  beta=1.0,
                  dtype=conf.dtype,
                  seed=None,
                  name=None):
    """Outputs random values from a Gumbel distribution.

    Args:
        shape: A 1-D integer Tensor or Python array. The shape of the output tensor.
        mu (float): mu.
        beta (float): brta.
        dtype: Data type.
        seed (int): Random seed.
        name (str): Operation name.

    Returns:
        Output tensor.

    """
    u = tf.random_uniform(
        shape=shape,
        minval=0,
        maxval=1,
        dtype=dtype,
        seed=seed,
        name=name
    )
    g = -tf.log(-tf.log(u))
    g = mu + g * beta
    return g


def kl_normal(mu0,
              var0,
              mu1=0.0,
              var1=1.0,
              name=None):
    """KL divergence for normal distribution.
    Note that this is a simple version. We don't use covariance matrix (∑) here. Instead,
    var is the vector that indicates the elements in ∑'s main diagonal (diag(∑)).

    Args:
        mu0: mu0.
        var0: diag(∑0).
        mu1: mu1.
        var1: diag(∑1).
        name (str): Operation name.

    Returns:
        Output tensor.

    """
    e = 1e-4
    var0 += e
    if mu1 == 0.0 and var1 == 1.0:
        kl = var0 + mu0 ** 2 - 1 - tf.log(var0)
    else:
        var1 += e
        kl = var0 / var1 + (mu0 - mu1) ** 2 / var1 - 1 - tf.log(var0 / var1)
    kl = tf.multiply(0.5, tf.reduce_sum(kl, 1), name=name)
    return kl


def transpose_sequence(seq, seq_axis=1, name=None):
    """Transpose a batch of sequence, i.e., exchange the batch axis and the sequence axis.
    By default, the sequence axis is 1.

    Args:
        seq: Tensor shaped (batch_size, seq_length, ...).
        seq_axis: The sequence axis. Default is 1.
        name (str): Operation name.

    Returns:
        Output tensor. Tensor shaped (seq_length, batch_size, ...).

    """
    perm = [i for i in range(len(seq.shape))]
    perm[0], perm[seq_axis] = seq_axis, 0
    return tf.transpose(seq, perm, name=name)


def flatten(x):
    batch_size = tf.shape(x)[0]
    return tf.reshape(x, (batch_size, -1))


def sequence_length(seq, reduce_axis=None):
    """Compute the sequence length.

    Example 1) A batch of sequences with index elements.
    seq: [
        [1, 3, 5, 3, 1],
        [0, 0, 0, 0, 0],
        [2, 4, 6, 0, 0]
        [5, 2, 7, 1, 0]
    ]
    sequence_length(seq): [5, 0, 3, 4]

    Example 2) A batch of high dimensional sequences with index elements.
    seq: [
        [[1, 3, 5, 3, 1],
        [2, 4, 0, 0, 0],
        [2, 4, 6, 0, 0],
        [5, 2, 7, 1, 0]],

        [[1, 3, 5, 0, 0],
        [2, 4, 0, 0, 0],
        [1, 2, 3, 0, 0],
        [0, 0, 0, 0, 0]]
    ]
    sequence_length(seq): [
        [5, 2, 3, 4],
        [3, 2, 3, 0]
    ]

    Example 3) A batch of sequences with embedding elements.
    sequence_length(seq, reduce_axis=-1): [4, 3]

    Args:
        seq: The sequence tensor.
        reduce_axis: If the elements in the sequence is a tensor, we should first reduce those dimensions.
            The reduce_axis can be an integer or a list of integers.

    Returns:
        The sequence length tensor.

    """
    if reduce_axis is not None:
        seq = tf.reduce_max(tf.abs(seq), axis=reduce_axis)
    seq = tf.sign(seq)
    length = tf.reduce_sum(seq, axis=-1)
    length = tf.cast(length, tf.int32)
    return length


def last_elements(seq, seq_len):
    h, _ = tf.map_fn(
        fn=lambda elem: (elem[0][elem[1] - 1], elem[1]),
        elems=(seq, seq_len)
    )
    return h


def concat_similar(a, b, name=None):
    return tf.concat([a, b, a - b, a * b], axis=-1, name=name)


def variance(x, axis=-1):
    mu = tf.reduce_mean(x, axis=axis)
    return tf.reduce_mean(x ** 2) - mu ** 2


def skewness(x, axis=-1, epsilon=1e-5):
    mu = tf.reduce_mean(x, axis=axis, keep_dims=True)
    up = tf.reduce_mean((x - mu) ** 3, axis=axis)
    down = tf.reduce_mean((x - mu) ** 2, axis=axis)
    down = tf.sqrt(down) ** 3 + epsilon
    return up / down
