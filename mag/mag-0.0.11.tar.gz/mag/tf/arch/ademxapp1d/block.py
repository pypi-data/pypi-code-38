import tensorflow as tf
from .branch import branch_a, branch_b

def block_a(inputs, filters, kernel_size, name='block_a'):
    '''1D version of block_a from ademxapp model.

    inputs ---> branch_a ---> outputs
            |              |
            ⌊__ branch_b __⌋
    '''
    with tf.variable_scope(name):
        x = tf.layers.batch_normalization(inputs, name='bn', reuse=tf.AUTO_REUSE)
        x = tf.nn.relu(x)
        b_a = branch_a(x, filters, kernel_size)
        b_b = branch_b(x, filters, kernel_size)
        return (b_a + b_b)

def block_b(inputs, filters, kernel_size, name='block_b'):
    '''1D version of block_b from ademxapp model.

    inputs ---> branch_a ---> outputs
            |              |
            ⌊______________⌋
    '''
    with tf.variable_scope(name):
        x = tf.layers.batch_normalization(inputs, name='bn', reuse=tf.AUTO_REUSE)
        x = tf.nn.relu(x)
        b_a = branch_a(x, filters, kernel_size)
        return (inputs + b_a)

def block(btype, inputs, filters, kernel_size, name='block'):
    blck = block_a if btype.lower() == 'a' else block_b
    name = '{}_{}'.format(name, btype.lower()) if name == 'block' else name
    return blck(inputs, filters, kernel_size, name)
