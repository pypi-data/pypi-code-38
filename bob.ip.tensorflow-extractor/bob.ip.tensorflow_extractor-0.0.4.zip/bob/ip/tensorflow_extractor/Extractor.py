#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Fri 17 Jun 2016 10:41:36 CEST


import tensorflow as tf
import os
from tensorflow.python import debug as tf_debug


class Extractor(object):
    """
    Feature extractor using tensorflow

    """

    def __init__(self, checkpoint_filename, input_tensor, graph, debug=False):
        """Loads the tensorflow model

        Parameters
        ----------
        checkpoint_filename: str
            Path of your checkpoint. If the .meta file is providede the last checkpoint will be loaded.

        model :
            input_tensor: tf.Tensor used as a data entrypoint. It can be a **tf.placeholder**, the
            result of **tf.train.string_input_producer**, etc

        graph :
            A tf.Tensor containing the operations to be executed
        """

        self.input_tensor = input_tensor
        self.graph = graph

        # Initializing the variables of the current graph
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        # Loading the last checkpoint and overwriting the current variables
        saver = tf.train.Saver()

        if os.path.splitext(checkpoint_filename)[1] == ".meta":
            saver.restore(self.session, tf.train.latest_checkpoint(os.path.dirname(checkpoint_filename)))
        elif os.path.isdir(checkpoint_filename):
            saver.restore(self.session, tf.train.latest_checkpoint(checkpoint_filename))
        else:
            saver.restore(self.session, checkpoint_filename)

        # Activating the debug
        if debug:
            self.session = tf_debug.LocalCLIDebugWrapperSession(self.session)


    def __del__(self):
        tf.reset_default_graph()


    def __call__(self, data):
        """
        Forward the data with the loaded neural network

        Parameters
        ----------
        image : numpy.ndarray
            Input Data

        Returns
        -------
        numpy.ndarray
            The features.

        """
        return self.session.run(self.graph, feed_dict={self.input_tensor: data})

