import tensorflow as tf
from .chain import chain, dist_chain

def tower(length, inputs, filters, kernel_sizes, name='tower'):
    with tf.variable_scope(name):
        x = tf.layers.batch_normalization(inputs, reuse=tf.AUTO_REUSE)
        chains = [chain(length, x, filters, ks, 'chain_{}'.format(ks)) for ks in kernel_sizes]
        return sum(chains)


def dist_tower(length, inputs, filters, kernel_sizes, name='tower', devices=None):
    if devices is None: return tower(length, inputs, filters, kernel_sizes, name)

    with tf.variable_scope(name):
        x = tf.layers.batch_normalization(inputs, reuse=tf.AUTO_REUSE)
        chains = []
        for i, kernel_size in enumerate(kernel_sizes):
            device = devices[i % len(devices)]
            with tf.device(device):
                cname = 'chain_{}'.format(kernel_size)
                chains.append(dist_chain(length, x, filters, kernel_size, cname, devices=[device]))
        return sum(chains)
