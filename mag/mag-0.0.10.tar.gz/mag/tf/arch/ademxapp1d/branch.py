import tensorflow as tf

def branch_a(inputs, filters, kernel_size,  name='branch_a'):
    with tf.variable_scope(name):
        x = tf.layers.conv1d(inputs, filters, kernel_size, name='conv_1', padding='same', reuse=tf.AUTO_REUSE)
        x = tf.nn.relu(x)
        x = tf.layers.conv1d(x, filters, kernel_size, name='conv_2', padding='same', reuse=tf.AUTO_REUSE)
        return x

def branch_b(inputs, filters, kernel_size, name='branch_b'):
    with tf.variable_scope(name):
        x = tf.layers.conv1d(inputs, filters, kernel_size, name='conv_1', padding='same', reuse=tf.AUTO_REUSE)
        return x
