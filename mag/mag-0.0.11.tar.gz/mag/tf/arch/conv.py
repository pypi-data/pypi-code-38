import tensorflow as tf

def conv1d_chain(inputs, filter_sizes:list, kernel_size:int,  name='conv_1d_chain'):
    with tf.variable_scope(name):
        x = tf.layers.batch_normalization(inputs, reuse=tf.AUTO_REUSE)
        for i, filters in enumerate(filter_sizes):
            x = tf.layers.conv1d(inputs, filters, kernel_size, name='conv_{}'.format(i), padding='same', reuse=tf.AUTO_REUSE)
            x = tf.nn.relu(x)
        return x

def conv1d_to_labels(inputs, labels, kernel_size):
    with tf.variable_scope('conv_to_labels'):
        x = tf.layers.conv1d(inputs, labels, kernel_size, name='conv', padding='same', reuse=tf.AUTO_REUSE)
        return x
