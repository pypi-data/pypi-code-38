import numpy as np
import tensorflow as tf
from . import util


def get_vars(scopes):
    vars = []
    for scope in scopes:
        vars += tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=scope)
    return vars


def gumbel_softmax(logits, gamma, eps=1e-20):
    U = tf.random_uniform(tf.shape(logits))
    G = -tf.log(-tf.log(U + eps) + eps)
    return tf.nn.softmax((logits + G) / gamma)
    #return tf.nn.softmax((logits+eps) / gamma)


def rnn_decode(cell, inputs, loop_func, max_len, initial_state=None):
    outs = []; hs = []
    h = initial_state
    for t in range(max_len):
        cell_out, h = cell(inputs, h)
        hs.append(h)
        inputs, out = loop_func(cell_out)
        outs.append(out)
    hs = tf.stack(hs, 1)
    if isinstance(initial_state, tuple):
        if len(initial_state) == 1:
            hs = tf.squeeze(hs, 0)  # [time, batch_size,::]
            hs = transpose(hs, 0, 1)  # [batch_size, time, ::]

    return hs, tf.stack(outs, 1)


def transpose_nd(tensor, dims1, dims2):
    assert len(dims1) == len(dims2), 'num of dims must be same'
    assert len(dims1+dims2) == len(set(dims1+dims2)), 'there must have no dup of dim'
    ndims = tensor.shape.ndims
    shape = np.arange(ndims)
    for dim1, dim2 in zip(dims1, dims2):
        dim = shape[dim1]
        shape[dim1] = shape[dim2]
        shape[dim2] = dim
    return tf.transpose(tensor, shape)


def transpose(tensor, dim1, dim2):
    return transpose_nd(tensor, [dim1], [dim2])


def create_rnn_cell(dims, cell_cls='tf.nn.rnn_cell.GRUCell', dropout=None):
    """
     
    :param dims: list of cell dim [128, 128]
    :param cell_cls:
    :return:
    """
    cell_cls = util.get_class(cell_cls)
    cells = []
    for dim in dims:
        cell = cell_cls(dim)
        if dropout is not None:
            cell = tf.nn.rnn_cell.DropoutWrapper(cell, input_keep_prob=dropout)
        cells.append(cell)
    multi_cell = tf.nn.rnn_cell.MultiRNNCell(cells, state_is_tuple=True)
    return multi_cell
