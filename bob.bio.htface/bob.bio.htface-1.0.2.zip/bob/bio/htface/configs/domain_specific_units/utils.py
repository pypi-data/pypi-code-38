#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
from bob.learn.tensorflow.network import inception_resnet_v2
from bob.bio.htface.architectures.Transfer import build_transfer_graph


def transfer_128_64_128(inputs, reuse=None, mode = tf.estimator.ModeKeys.TRAIN, **kwargs):
    """
    Build a joint encoder on top of the inception network
    """
    graph,_ = inception_resnet_v2(inputs, mode=mode, reuse=reuse, **kwargs)
    graph, end_points = build_transfer_graph(graph, reuse=reuse, bottleneck_layers=[64], outputs=128)

    return graph, end_points


def get_dsu_training_setup():
    """
    Standard training setup for the DSU
    """

    training_setup = dict()

    # Training setup
    training_setup["data_shape"] = (160, 160, 1)  # size of atnt images
    training_setup["output_shape"] = None
    training_setup["data_type"] = tf.uint8

    training_setup["batch_size"] = 90
    training_setup["validation_batch_size"] = 250
    training_setup["epochs"] = 100
    training_setup["embedding_validation"] = True
    training_setup["steps"] = 2000000

    training_setup["learning_rate_values"] = [0.1, 0.01, 0.001]
    #training_setup["learning_rate_values"] = [1., 0.1, 0.01]

    return training_setup
