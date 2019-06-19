""" Session """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def generator(fetches):
    # TODO: Multi-thread
    with tf.Session() as sess:
        while True:
            try:
                yield sess.run(fetches)
            except tf.errors.OutOfRangeError:
                tf.logging.info('tflibs.session.generator: Done')
                break
