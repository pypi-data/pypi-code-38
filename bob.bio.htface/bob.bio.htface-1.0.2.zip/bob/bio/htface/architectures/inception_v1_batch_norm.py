#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
Here we implement several structures crafted for Siamese networks where parts of the network
are shared and parts are not.

"""

import tensorflow as tf
import tensorflow.contrib.slim as slim

# Base nets
from .inception_v1 import inception_resnet_v1_adapt_first_head as adapt_first
from .inception_v1 import inception_resnet_v1_adapt_layers_1_2_head as adapt_1_2
from .inception_v1 import inception_resnet_v1_adapt_layers_1_4_head as adapt_1_4
from .inception_v1 import inception_resnet_v1_adapt_layers_1_5_head as adapt_1_5
from .inception_v1 import inception_resnet_v1_adapt_layers_1_6_head as adapt_1_6


def inception_resnet_v1_adapt_first_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV1',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left=True,
                                         weight_decay=5e-05,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the FIRST LAYER.

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

      is_siamese: bool
        If True is Siamese, otherwise is triplet

      is_left: bool
        Is the left side of the Siamese?

      force_weights_shutdown: bool
        If True will shutdown the weights no matter the weights are set in trainable_variables.
        Default **False**


    **Returns**:

      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """

    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [tf.GraphKeys.GLOBAL_VARIABLES],

    }

    with slim.arg_scope(
        [slim.conv2d, slim.fully_connected],
            weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
            weights_regularizer=slim.l2_regularizer(weight_decay),
            normalizer_fn=slim.batch_norm,
            normalizer_params=batch_norm_params):

        net, end_points = adapt_first(inputs,
                                      dropout_keep_prob=dropout_keep_prob,
                                      bottleneck_layer_size=bottleneck_layer_size,
                                      reuse=reuse,
                                      scope=scope,
                                      mode=mode,
                                      trainable_variables=trainable_variables,
                                      is_siamese=is_siamese,
                                      is_left=is_left,
                                      force_weights_shutdown=force_weights_shutdown)

    return net, end_points


def inception_resnet_v1_adapt_layers_1_2_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV1',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left = True,
                                              weight_decay=5e-05,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the
    FIRST AND SECOND LAYERS

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

      is_siamese: bool
        If True is Siamese, otherwise is triplet

      is_left: bool
        Is the left side of the Siamese?

      force_weights_shutdown: bool
        If True will shutdown the weights no matter the weights are set in trainable_variables.
        Default **False**


    **Returns**:

      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """

    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [tf.GraphKeys.GLOBAL_VARIABLES],

    }

    with slim.arg_scope(
        [slim.conv2d, slim.fully_connected],
            weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
            weights_regularizer=slim.l2_regularizer(weight_decay),
            normalizer_fn=slim.batch_norm,
            normalizer_params=batch_norm_params):

        net, end_points = adapt_1_2(inputs,
                                    dropout_keep_prob=dropout_keep_prob,
                                    bottleneck_layer_size=bottleneck_layer_size,
                                    reuse=reuse,
                                    scope=scope,
                                    mode=mode,
                                    trainable_variables=trainable_variables,
                                    is_siamese=is_siamese,
                                    is_left=is_left,
                                    force_weights_shutdown=force_weights_shutdown)

    return net, end_points


def inception_resnet_v1_adapt_layers_1_4_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV1',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left=True,
                                              weight_decay=5e-05,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the
    FIRST AND FORTH LAYERS

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

      is_siamese: bool
        If True is Siamese, otherwise is triplet

      is_left: bool
        Is the left side of the Siamese?

      force_weights_shutdown: bool
        If True will shutdown the weights no matter the weights are set in trainable_variables.
        Default **False**


    **Returns**:

      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """

    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [tf.GraphKeys.GLOBAL_VARIABLES],

    }

    with slim.arg_scope(
        [slim.conv2d, slim.fully_connected],
            weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
            weights_regularizer=slim.l2_regularizer(weight_decay),
            normalizer_fn=slim.batch_norm,
            normalizer_params=batch_norm_params):

        net, end_points = adapt_1_4(inputs,
                                    dropout_keep_prob=dropout_keep_prob,
                                    bottleneck_layer_size=bottleneck_layer_size,
                                    reuse=reuse,
                                    scope=scope,
                                    mode=mode,
                                    trainable_variables=trainable_variables,
                                    is_siamese=is_siamese,
                                    is_left=is_left,
                                    force_weights_shutdown=force_weights_shutdown)

    return net, end_points


def inception_resnet_v1_adapt_layers_1_5_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV1',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left = True,
                                         weight_decay=5e-05,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the
    FIRST AND FIFTH LAYERS

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

      is_siamese: bool
        If True is Siamese, otherwise is triplet

      is_left: bool
        Is the left side of the Siamese?

      force_weights_shutdown: bool
        If True will shutdown the weights no matter the weights are set in trainable_variables.
        Default **False**


    **Returns**:

      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """

    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [tf.GraphKeys.GLOBAL_VARIABLES],

    }

    with slim.arg_scope(
        [slim.conv2d, slim.fully_connected],
            weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
            weights_regularizer=slim.l2_regularizer(weight_decay),
            normalizer_fn=slim.batch_norm,
            normalizer_params=batch_norm_params):

        net, end_points = adapt_1_5(inputs,
                                    dropout_keep_prob=dropout_keep_prob,
                                    bottleneck_layer_size=bottleneck_layer_size,
                                    reuse=reuse,
                                    scope=scope,
                                    mode=mode,
                                    trainable_variables=trainable_variables,
                                    is_siamese=is_siamese,
                                    is_left=is_left,
                                    force_weights_shutdown=force_weights_shutdown)

    return net, end_points


def inception_resnet_v1_adapt_layers_1_6_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV1',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left=True,
                                              weight_decay=5e-05,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the
    FIRST AND SIXTH LAYERS

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

      is_siamese: bool
        If True is Siamese, otherwise is triplet

      is_left: bool
        Is the left side of the Siamese?

      force_weights_shutdown: bool
        If True will shutdown the weights no matter the weights are set in trainable_variables.
        Default **False**


    **Returns**:

      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.
    """

    batch_norm_params = {
        # Decay for the moving averages.
        'decay': 0.995,
        # epsilon to prevent 0s in variance.
        'epsilon': 0.001,
        # force in-place updates of mean and variance estimates
        'updates_collections': None,
        # Moving averages ends up in the trainable variables collection
        'variables_collections': [tf.GraphKeys.GLOBAL_VARIABLES],

    }

    with slim.arg_scope(
        [slim.conv2d, slim.fully_connected],
            weights_initializer=tf.truncated_normal_initializer(stddev=0.1),
            weights_regularizer=slim.l2_regularizer(weight_decay),
            normalizer_fn=slim.batch_norm,
            normalizer_params=batch_norm_params):

        net, end_points = adapt_1_6(inputs,
                                    dropout_keep_prob=dropout_keep_prob,
                                    bottleneck_layer_size=bottleneck_layer_size,
                                    reuse=reuse,
                                    scope=scope,
                                    mode=mode,
                                    trainable_variables=trainable_variables,
                                    is_siamese=is_siamese,
                                    is_left=is_left,
                                    force_weights_shutdown=force_weights_shutdown)

    return net, end_points

