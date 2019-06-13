import tensorflow as tf
from .block import block

def chain(length, inputs, filters, kernel_size, name='chain', residual_q=True):
    with tf.variable_scope(name):
        x = a = block('a', inputs, filters, kernel_size, 'block_a0')

        for i in range(1, length):
            x = block('b', x, filters, kernel_size, 'block_b{}'.format(i))

        if residual_q:
            x = tf.layers.max_pooling1d(x, pool_size=kernel_size, strides=1, padding='same')

        return (a + x) if residual_q else x


def dist_chain(length, inputs, filters, kernel_size, name='chain', residual_q=True, devices=None):
    if devices is None: return chain(length, inputs, filters, kernel_size, name, residual_q)
    if type(devices) is not list: devices = [devices]

    with tf.variable_scope(name):
        with tf.device(devices[0]):
            x = a = block('a', inputs, filters, kernel_size, 'block_a0')

        for i in range(1, length):
            device = devices[i % len(devices)]
            with tf.device(device):
                x = block('b', x, filters, kernel_size, 'block_b{}'.format(i))

        if residual_q:
            with tf.device(devices[-1]):
                x = tf.layers.max_pooling1d(x, pool_size=kernel_size, strides=1, padding='same')

        return (a + x) if residual_q else x



def tower_chain(length, inputs, filter_sizes, kernel_sizes, name='tower_chain'):
    from .tower import tower
    with tf.variable_scope(name):
        x = inputs
        for fs in filter_sizes:
            x = tower(length, x, fs, kernel_sizes, 'tower_{}'.format(fs))
        return x


def dist_tower_chain(length, inputs, filter_sizes, kernel_sizes, name='tower_chain', devices=None):
    if devices is None: return tower_chain(length, inputs, filter_sizes, kernel_sizes, name)
    from .tower import dist_tower
    with tf.variable_scope(name):
        x = inputs
        for i, filter_size in enumerate(filter_sizes):
            device = devices[i % len(devices)]
            with tf.device(device):
                x = dist_tower(length, x, filter_size, kernel_sizes, 'tower_{}'.format(filter_size), devices)
        return x
