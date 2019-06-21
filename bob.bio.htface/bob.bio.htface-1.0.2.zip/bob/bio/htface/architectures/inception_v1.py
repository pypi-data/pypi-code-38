#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
Here we implement several structures crafted for Siamese networks where parts of the network
are shared and parts are not.

"""

import tensorflow as tf
from bob.learn.tensorflow.network.InceptionResnetV1 import block35, block17, block8, reduction_a, reduction_b
from .utils import compute_layer_name, is_trainable_variable, is_reusable_variable
import tensorflow.contrib.slim as slim


def inception_resnet_v1_core(inputs,
                             dropout_keep_prob=0.8,
                             bottleneck_layer_size=128,
                             reuse=None,
                             scope='InceptionResnetV1',
                             mode=tf.estimator.ModeKeys.TRAIN,
                             trainable_variables=None,
                             **kwargs):
    """
    Creates the Inception Resnet V1 model.

    Parameters
    ----------

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      num_classes: number of predicted classes.

      is_training: whether is training or not.

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

    Returns
    -------
      logits: the logits outputs of the model.
      end_points: the set of end_points from the inception model.

    """
    net = inputs

    # 10 x Inception-Resnet-B
    name = "block17"# Possible issue with repeat
    net = slim.repeat(
        net,
        10,
        block17,
        scope=name,
        scale=0.10,
        trainable_variables=False,
        reuse=reuse)

    # Reduction-B
    name = "Mixed_7a"
    # trainable = is_trainable(name, trainable_variables)
    with tf.variable_scope(name):
        net = reduction_b(
            net,
            trainable_variables=False,
            reuse=reuse)

    # 5 x Inception-Resnet-C
    name = "block8"
    # trainable = is_trainable(name, trainable_variables)
    net = slim.repeat(
        net,
        5,
        block8,
        scope=name,
        scale=0.20,
        trainable_variables=False,
        reuse=reuse)
    name = "Mixed_8b"
    # trainable = is_trainable(name, trainable_variables)
    net = block8(
        net,
        scope=name,
        activation_fn=None,
        trainable_variables=False,
        reuse=reuse)

    with tf.variable_scope('Logits'):
        #pylint: disable=no-member
        net = slim.avg_pool2d(
            net,
            net.get_shape()[1:3],
            padding='VALID',
            scope='AvgPool_1a_8x8')
        net = slim.flatten(net)

        net = slim.dropout(
            net,
            dropout_keep_prob,
            is_training=(mode == tf.estimator.ModeKeys.TRAIN),
            scope='Dropout')

    name = "Bottleneck"
    # trainable = is_trainable(name, trainable_variables)
    net = slim.fully_connected(
        net,
        bottleneck_layer_size,
        activation_fn=None,
        scope=name,
        reuse=reuse,
        trainable=False)

    return net


def inception_resnet_v1_adapt_first_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV1',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left=True,
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

    end_points = {}
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
                    # CORE OF THE THE ADAPTATION

                    # 149 x 149 x 32
                    name = "Conv2d_1a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        inputs,
                        32,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # 147 x 147 x 32
                    name = "Conv2d_2a_3x3"
                    net = slim.conv2d(
                        net,
                        32,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 147 x 147 x 64
                    name = "Conv2d_2b_3x3"
                    net = slim.conv2d(
                        net,
                        64,
                        3,
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net
                    # 73 x 73 x 64
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_3a_3x3')
                    end_points['MaxPool_3a_3x3'] = net

                    # 73 x 73 x 80
                    name = "Conv2d_3b_1x1"
                    net = slim.conv2d(
                        net,
                        80,
                        1,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 71 x 71 x 192
                    name = "Conv2d_4a_3x3"
                    net = slim.conv2d(
                        net,
                        192,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 35 x 35 x 256
                    name = "Conv2d_4b_3x3"
                    net = slim.conv2d(
                        net,
                        256,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 5 x Inception-resnet-A
                    name = "block35"
                    net = slim.repeat(
                        net,
                        5,
                        block35,
                        scope=name,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)
                    end_points[name] = net

                    # Reduction-A
                    name = "Mixed_6a"
                    with tf.variable_scope(name):
                        net = reduction_a(
                            net,
                            192,
                            192,
                            256,
                            384,
                            trainable_variables=False,
                            reuse=reuse)
                    end_points[name] = net

                    net = inception_resnet_v1_core(
                                         net,
                                         dropout_keep_prob=dropout_keep_prob,
                                         bottleneck_layer_size=bottleneck_layer_size,
                                         reuse=reuse,
                                         scope=scope,
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

    return net, end_points


def inception_resnet_v1_adapt_layers_1_2_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV1',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left=True,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the FIRST AND SECOND LAYERS

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

    end_points = {}
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
                    # CORE OF THE THE ADAPTATION

                    # 149 x 149 x 32
                    name = "Conv2d_1a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        inputs,
                        32,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 32
                    name = "Conv2d_2a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        32,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 64
                    name = "Conv2d_2b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        64,
                        3,
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 73 x 73 x 64
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_3a_3x3')
                    end_points['MaxPool_3a_3x3'] = net

                    # 73 x 73 x 80
                    name = "Conv2d_3b_1x1"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        80,
                        1,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # 71 x 71 x 192
                    name = "Conv2d_4a_3x3"
                    net = slim.conv2d(
                        net,
                        192,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 35 x 35 x 256
                    name = "Conv2d_4b_3x3"
                    net = slim.conv2d(
                        net,
                        256,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=False,
                        reuse=reuse)
                    end_points[name] = net

                    # 5 x Inception-resnet-A
                    name = "block35"
                    net = slim.repeat(
                        net,
                        5,
                        block35,
                        scope=name,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)
                    end_points[name] = net

                    # Reduction-A
                    name = "Mixed_6a"
                    with tf.variable_scope(name):
                        net = reduction_a(
                            net,
                            192,
                            192,
                            256,
                            384,
                            trainable_variables=False,
                            reuse=reuse)
                    end_points[name] = net

                    net = inception_resnet_v1_core(
                                         net,
                                         dropout_keep_prob=dropout_keep_prob,
                                         bottleneck_layer_size=bottleneck_layer_size,
                                         reuse=reuse,
                                         scope=scope,
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

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
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the FIRST AND FORTH LAYERS

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

    end_points = {}
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
                    # CORE OF THE THE ADAPTATION

                    # 149 x 149 x 32
                    name = "Conv2d_1a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        inputs,
                        32,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 32
                    name = "Conv2d_2a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        32,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 64
                    name = "Conv2d_2b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        64,
                        3,
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 73 x 73 x 64
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_3a_3x3')
                    end_points['MaxPool_3a_3x3'] = net

                    # 73 x 73 x 80
                    name = "Conv2d_3b_1x1"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        80,
                        1,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 71 x 71 x 192
                    name = "Conv2d_4a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        192,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 35 x 35 x 256
                    name = "Conv2d_4b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        256,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # 5 x Inception-resnet-A
                    name = "block35"
                    net = slim.repeat(
                        net,
                        5,
                        block35,
                        scope=name,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)
                    end_points[name] = net

                    # Reduction-A
                    name = "Mixed_6a"
                    with tf.variable_scope(name):
                        net = reduction_a(
                            net,
                            192,
                            192,
                            256,
                            384,
                            trainable_variables=False,
                            reuse=reuse)
                    end_points[name] = net

                    net = inception_resnet_v1_core(
                                         net,
                                         dropout_keep_prob=dropout_keep_prob,
                                         bottleneck_layer_size=bottleneck_layer_size,
                                         reuse=reuse,
                                         scope=scope,
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

    return net, end_points


def inception_resnet_v1_adapt_layers_1_5_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV1',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left=True,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the FIRST AND FIFTH LAYERS

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

    end_points = {}
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
                    # CORE OF THE THE ADAPTATION

                    # 149 x 149 x 32
                    name = "Conv2d_1a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        inputs,
                        32,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 32
                    name = "Conv2d_2a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        32,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 64
                    name = "Conv2d_2b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        64,
                        3,
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 73 x 73 x 64
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_3a_3x3')
                    end_points['MaxPool_3a_3x3'] = net

                    # 73 x 73 x 80
                    name = "Conv2d_3b_1x1"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        80,
                        1,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 71 x 71 x 192
                    name = "Conv2d_4a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        192,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 35 x 35 x 256
                    name = "Conv2d_4b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        256,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 5 x Inception-resnet-A
                    name = "block35"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.repeat(
                        net,
                        5,
                        block35,
                        scope=name,
                        scale=0.17,
                        trainable_variables=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # Reduction-A
                    name = "Mixed_6a"
                    with tf.variable_scope(name):
                        net = reduction_a(
                            net,
                            192,
                            192,
                            256,
                            384,
                            trainable_variables=False,
                            reuse=reuse)
                    end_points[name] = net

                    net = inception_resnet_v1_core(
                                         net,
                                         dropout_keep_prob=dropout_keep_prob,
                                         bottleneck_layer_size=bottleneck_layer_size,
                                         reuse=reuse,
                                         scope=scope,
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

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
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V1 model for the adaptation of the FIRST AND SIXTH LAYERS

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

    end_points = {}
    with tf.variable_scope(scope, 'InceptionResnetV1', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
                    # CORE OF THE THE ADAPTATION

                    # 149 x 149 x 32
                    name = "Conv2d_1a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        inputs,
                        32,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 32
                    name = "Conv2d_2a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        32,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 147 x 147 x 64
                    name = "Conv2d_2b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        64,
                        3,
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 73 x 73 x 64
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_3a_3x3')
                    end_points['MaxPool_3a_3x3'] = net

                    # 73 x 73 x 80
                    name = "Conv2d_3b_1x1"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        80,
                        1,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 71 x 71 x 192
                    name = "Conv2d_4a_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        192,
                        3,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 35 x 35 x 256
                    name = "Conv2d_4b_3x3"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.conv2d(
                        net,
                        256,
                        3,
                        stride=2,
                        padding='VALID',
                        scope=name,
                        trainable=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # 5 x Inception-resnet-A
                    name = "block35"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.repeat(
                        net,
                        5,
                        block35,
                        scope=name,
                        scale=0.17,
                        trainable_variables=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable)
                    end_points[name] = net

                    # Reduction-A
                    name = "Mixed_6a"
                    name = compute_layer_name(name, is_left, is_siamese)
                    with tf.variable_scope(name):
                        net = reduction_a(
                            net,
                            192,
                            192,
                            256,
                            384,
                            trainable_variables=is_trainable and not force_weights_shutdown,
                            reuse=is_reusable)
                    end_points[name] = net

                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    net = inception_resnet_v1_core(
                                         net,
                                         dropout_keep_prob=dropout_keep_prob,
                                         bottleneck_layer_size=bottleneck_layer_size,
                                         reuse=reuse,
                                         scope=scope,
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

    return net, end_points
