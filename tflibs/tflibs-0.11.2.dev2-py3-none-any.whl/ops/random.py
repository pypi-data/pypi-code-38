""" Random """

import tensorflow as tf


def randomly_pick_op(ops: list):
    with tf.name_scope('randomly_pick'):
        rand_var = tf.random_uniform(()) * len(ops)

        def picked(inputs: tf.Tensor):
            pred_fn_pairs = dict(
                [(tf.logical_and(tf.greater_equal(rand_var, i), tf.less(rand_var, i + 1)), lambda: op(inputs)) for i, op
                 in enumerate(ops)])

            return tf.case(pred_fn_pairs, exclusive=True)

        return picked
