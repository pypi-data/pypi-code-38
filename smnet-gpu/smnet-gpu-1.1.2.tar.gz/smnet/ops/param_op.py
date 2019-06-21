# -----------------
# SMNet
# Written by smarsu
# -----------------

"""Use tensorflow for create glorot uniform"""
import tensorflow as tf
tf.set_random_seed(196)
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def glorot_uniform(shape):
    initializer = tf.glorot_uniform_initializer()
    weights = initializer(shape)
    with tf.Session() as sess:
        weights = sess.run(weights)
    return weights
