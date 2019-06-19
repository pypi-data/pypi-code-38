#!/usr/bin/env python3

"""
@author: xi, anmx
@since: 2017-04-23
"""

import numpy as np
import tensorflow as tf

import photinia as ph


def one_hot(index, dims, dtype=np.uint8):
    """Create one hot vector(s) with the given index(indices).

    :param index: int or list(tuple) of int. Indices.
    :param dims: int. Dimension of the one hot vector.
    :param dtype: Numpy data type.
    :return: Numpy array. If index is an int, then return a (1 * dims) vector,
        else return a (len(index), dims) matrix.
    """
    if isinstance(index, int):
        ret = np.zeros((dims,), dtype)
        ret[index] = 1
    elif isinstance(index, (list, tuple)):
        seq_len = len(index)
        ret = np.zeros((seq_len, dims), dtype)
        ret[range(seq_len), index] = 1.0
    else:
        raise ValueError('index should be int or list(tuple) of int.')
    return ret


def get_trainable_variables(include, exclude=None):
    if isinstance(include, ph.Trainable):
        include = [include]
    if isinstance(exclude, ph.Trainable):
        exclude = [exclude]
    exclude_prefix = [w.prefix for w in exclude]
    tvars = []
    for w in include:
        for tvar in w.get_trainable_variables():
            add = True
            name = tvar.name
            for prefix in exclude_prefix:
                if name.startswith(prefix):
                    add = False
                    break
            if add:
                tvars.append(tvar)
    return tvars


def read_variables(var_or_list):
    """Get the value from a variable.

    :param var_or_list: tf.Variable.
    :return: numpy.array value.
    """
    session = ph.get_session()
    return session.run(var_or_list)


def write_variables(var_or_list, values):
    """Set the value to a variable.

    :param var_or_list: tf.Variable.
    :param values: numpy.array value.
    """
    session = ph.get_session()
    if isinstance(var_or_list, (tuple, list)):
        for var, value in zip(var_or_list, values):
            var.load(value, session)
    else:
        var_or_list.load(values, session)


def get_operation(name):
    return tf.get_default_graph().get_operation_by_name(name)


def get_tensor(name):
    """Get tensor by name.

    https://stackoverflow.com/questions/37849322/how-to-understand-the-term-tensor-in-tensorflow

    TensorFlow doesn't have first-class Tensor objects, meaning that there are no notion of Tensor in the
    underlying graph that's executed by the runtime.
    Instead the graph consists of op nodes connected to each other, representing operations.
    An operation allocates memory for its outputs, which are available on endpoints :0, :1, etc,
    and you can think of each of these endpoints as a Tensor.
    If you have tensor corresponding to nodename:0 you can fetch its value as sess.run(tensor) or
    sess.run('nodename:0').
    Execution granularity happens at operation level, so the run method will execute op which will compute all of the
    endpoints, not just the :0 endpoint.
    It's possible to have an Op node with no outputs (like tf.group) in which case there are no tensors
    associated with it.
    It is not possible to have tensors without an underlying Op node.

    :param name: Tensor name (must be full name).
    :return: The tensor.
    """
    if name.rfind(':') == -1:
        name += ':0'
    return tf.get_default_graph().get_tensor_by_name(name)


def get_variable(name):
    if name.rfind(':') == -1:
        name += ':0'
    for var in tf.get_local_variable():
        if name == var.name:
            return var
    return None


def get_basename(name):
    index = name.rfind('/')
    index_ = name.rfind(':')
    if index_ == -1:
        index_ = len(name)
    return name[index + 1: index_]
