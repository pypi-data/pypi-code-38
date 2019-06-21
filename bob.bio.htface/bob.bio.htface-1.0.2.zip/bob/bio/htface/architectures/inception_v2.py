#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""
Here we implement several structures crafted for Siamese networks where parts of the network
are shared and parts are not.

"""

import tensorflow as tf
from .utils import compute_layer_name, is_trainable_variable, is_reusable_variable
from bob.learn.tensorflow.network.InceptionResnetV2 import block35, block17, block8
import tensorflow.contrib.slim as slim


def inception_resnet_v2_core(inputs,
                             dropout_keep_prob=0.8,
                             bottleneck_layer_size=128,
                             reuse=None,
                             scope='InceptionResnetV2',
                             mode=tf.estimator.ModeKeys.TRAIN,
                             trainable_variables=False,
                             **kwargs):
    """

    Core of the Inception Resnet V2 model.
    Here we consider the core from the layer `Mixed_6a`

    **Parameters**:

      inputs: a 4-D tensor of size [batch_size, height, width, 3].

      dropout_keep_prob: float, the fraction to keep before final layer.

      reuse: whether or not the network and its variables should be reused. To be
        able to reuse 'scope' must be given.

      scope: Optional variable_scope.

      trainable_variables: list
        List of variables to be trainable=True

    **Returns**:

      logits: the logits outputs of the model.
    """
    end_points = dict()

    net = inputs

    # 17 x 17 x 1024
    name = "Mixed_6a"
    with tf.variable_scope(name):
        with tf.variable_scope('Branch_0'):
            tower_conv = slim.conv2d(
                net,
                384,
                3,
                stride=2,
                padding='VALID',
                scope='Conv2d_1a_3x3',
                trainable=False,
                reuse=reuse)
        with tf.variable_scope('Branch_1'):
            tower_conv1_0 = slim.conv2d(
                net,
                256,
                1,
                scope='Conv2d_0a_1x1',
                trainable=False,
                reuse=reuse)
            tower_conv1_1 = slim.conv2d(
                tower_conv1_0,
                256,
                3,
                scope='Conv2d_0b_3x3',
                trainable=False,
                reuse=reuse)
            tower_conv1_2 = slim.conv2d(
                tower_conv1_1,
                384,
                3,
                stride=2,
                padding='VALID',
                scope='Conv2d_1a_3x3',
                trainable=False,
                reuse=reuse)
        with tf.variable_scope('Branch_2'):
            tower_pool = slim.max_pool2d(
                net,
                3,
                stride=2,
                padding='VALID',
                scope='MaxPool_1a_3x3')
        net = tf.concat([tower_conv, tower_conv1_2, tower_pool], 3)
        end_points[name] = net

    # BLOCK 17
    name = "Block17"
    net = slim.repeat(
        net,
        20,
        block17,
        scale=0.10,
        trainable_variables=False,
        reuse=reuse)
    end_points[name] = net

    name = "Mixed_7a"
    with tf.variable_scope(name):
        with tf.variable_scope('Branch_0'):
            tower_conv = slim.conv2d(
                net,
                256,
                1,
                scope='Conv2d_0a_1x1',
                trainable=False,
                reuse=reuse)
            tower_conv_1 = slim.conv2d(
                tower_conv,
                384,
                3,
                stride=2,
                padding='VALID',
                scope='Conv2d_1a_3x3',
                trainable=False,
                reuse=reuse)
        with tf.variable_scope('Branch_1'):
            tower_conv1 = slim.conv2d(
                net,
                256,
                1,
                scope='Conv2d_0a_1x1',
                trainable=False,
                reuse=reuse)
            tower_conv1_1 = slim.conv2d(
                tower_conv1,
                288,
                3,
                stride=2,
                padding='VALID',
                scope='Conv2d_1a_3x3',
                trainable=False,
                reuse=reuse)
        with tf.variable_scope('Branch_2'):
            tower_conv2 = slim.conv2d(
                net,
                256,
                1,
                scope='Conv2d_0a_1x1',
                trainable=False,
                reuse=reuse)
            tower_conv2_1 = slim.conv2d(
                tower_conv2,
                288,
                3,
                scope='Conv2d_0b_3x3',
                trainable=False,
                reuse=reuse)
            tower_conv2_2 = slim.conv2d(
                tower_conv2_1,
                320,
                3,
                stride=2,
                padding='VALID',
                scope='Conv2d_1a_3x3',
                trainable=False,
                reuse=reuse)
        with tf.variable_scope('Branch_3'):
            tower_pool = slim.max_pool2d(
                net,
                3,
                stride=2,
                padding='VALID',
                scope='MaxPool_1a_3x3')
        net = tf.concat([
            tower_conv_1, tower_conv1_1, tower_conv2_2, tower_pool
        ], 3)
        end_points[name] = net

    # Block 8
    name = "Block8"
    net = slim.repeat(
        net,
        9,
        block8,
        scale=0.20,
        trainable_variables=False,
        reuse=reuse)
    net = block8(
        net,
        activation_fn=None,
        trainable_variables=False,
        reuse=reuse)
    end_points[name] = net

    name = "Conv2d_7b_1x1"
    net = slim.conv2d(
        net, 1536, 1, scope=name, trainable=False, reuse=reuse)
    end_points[name] = net


    with tf.variable_scope('Logits'):
        # pylint: disable=no-member
        net = slim.avg_pool2d(
            net,
            net.get_shape()[1:3],
            padding='VALID',
            scope='AvgPool_1a_8x8')
        net = slim.flatten(net)

        net = slim.dropout(net, dropout_keep_prob, scope='Dropout', is_training=(mode == tf.estimator.ModeKeys.TRAIN))
        end_points['PreLogitsFlatten'] = net

    name = "Bottleneck"
    net = slim.fully_connected(
        net,
        bottleneck_layer_size,
        activation_fn=None,
        scope=name,
        reuse=reuse,
        trainable=False)
    end_points[name] = net

    return net, end_points


def inception_resnet_v2_adapt_first_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV2',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left = True,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V2 model for the adaptation of the FIRST LAYER.
   
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

    end_points = dict()

    with tf.variable_scope(scope, 'InceptionResnetV2', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not            
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            # In case you want to reuse the left part
            # TODO: CHECK THIS PATCH
            if is_left and reuse:
                is_reusable = True

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
                        net, 64, 3, scope=name, trainable=False, reuse=reuse)
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

                    # 35 x 35 x 192
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_5a_3x3')
                    end_points['MaxPool_5a_3x3'] = net

                    # 35 x 35 x 320
                    name = "Mixed_5b"
                    with tf.variable_scope(name):
                        with tf.variable_scope('Branch_0'):
                            tower_conv = slim.conv2d(
                                net,
                                96,
                                1,
                                scope='Conv2d_1x1',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_1'):
                            tower_conv1_0 = slim.conv2d(
                                net,
                                48,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv1_1 = slim.conv2d(
                                tower_conv1_0,
                                64,
                                5,
                                scope='Conv2d_0b_5x5',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_2'):
                            tower_conv2_0 = slim.conv2d(
                                net,
                                64,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_1 = slim.conv2d(
                                tower_conv2_0,
                                96,
                                3,
                                scope='Conv2d_0b_3x3',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_2 = slim.conv2d(
                                tower_conv2_1,
                                96,
                                3,
                                scope='Conv2d_0c_3x3',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_3'):
                            tower_pool = slim.avg_pool2d(
                                net,
                                3,
                                stride=1,
                                padding='SAME',
                                scope='AvgPool_0a_3x3')
                            tower_pool_1 = slim.conv2d(
                                tower_pool,
                                64,
                                1,
                                scope='Conv2d_0b_1x1',
                                trainable=False,
                                reuse=reuse)
                        net = tf.concat([
                            tower_conv, tower_conv1_1, tower_conv2_2, tower_pool_1
                        ], 3)
                    end_points[name] = net

                    # BLOCK 35
                    name = "Block35"
                    net = slim.repeat(
                        net,
                        10,
                        block35,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)

                    net, core_endpoints = inception_resnet_v2_core(
                                         net,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=reuse,
                                         scope='InceptionResnetV2',
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs                    
                    )
                    
    end_points.update(core_endpoints)
    return net, end_points


def inception_resnet_v2_adapt_layers_1_2_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV2',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left = True,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V2 model for the adaptation of the
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


    end_points = dict()

    with tf.variable_scope(scope, 'InceptionResnetV2', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not            
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            # ADAPTABLE PART
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
                        net,
                        3,
                        stride=2,
                        padding='VALID',
                        scope='MaxPool_3a_3x3')

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

            # NON ADAPTABLE PART
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

                    # 35 x 35 x 192
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_5a_3x3')
                    end_points['MaxPool_5a_3x3'] = net

                    # 35 x 35 x 320
                    name = "Mixed_5b"
                    with tf.variable_scope(name):
                        with tf.variable_scope('Branch_0'):
                            tower_conv = slim.conv2d(
                                net,
                                96,
                                1,
                                scope='Conv2d_1x1',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_1'):
                            tower_conv1_0 = slim.conv2d(
                                net,
                                48,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv1_1 = slim.conv2d(
                                tower_conv1_0,
                                64,
                                5,
                                scope='Conv2d_0b_5x5',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_2'):
                            tower_conv2_0 = slim.conv2d(
                                net,
                                64,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_1 = slim.conv2d(
                                tower_conv2_0,
                                96,
                                3,
                                scope='Conv2d_0b_3x3',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_2 = slim.conv2d(
                                tower_conv2_1,
                                96,
                                3,
                                scope='Conv2d_0c_3x3',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_3'):
                            tower_pool = slim.avg_pool2d(
                                net,
                                3,
                                stride=1,
                                padding='SAME',
                                scope='AvgPool_0a_3x3')
                            tower_pool_1 = slim.conv2d(
                                tower_pool,
                                64,
                                1,
                                scope='Conv2d_0b_1x1',
                                trainable=False,
                                reuse=reuse)
                        net = tf.concat([
                            tower_conv, tower_conv1_1, tower_conv2_2, tower_pool_1
                        ], 3)
                    end_points[name] = net

                    # BLOCK 35
                    name = "Block35"
                    net = slim.repeat(
                        net,
                        10,
                        block35,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)

                    net, core_endpoints = inception_resnet_v2_core(
                                         net,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=reuse,
                                         scope='InceptionResnetV2',
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )
    end_points.update(core_endpoints)
    return net, end_points


def inception_resnet_v2_adapt_layers_1_4_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV2',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left = True,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V2 model for the adaptation of the
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

    end_points = dict()

    with tf.variable_scope(scope, 'InceptionResnetV2', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not            
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            # In case you want to reuse the left part
            # TODO: CHECK THIS PATCH
            if is_left and reuse:
                is_reusable = True


            # ADAPTABLE PART
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
                        net,
                        3,
                        stride=2,
                        padding='VALID',
                        scope='MaxPool_3a_3x3')

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


            # NON ADAPTABLE PART
            with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # 35 x 35 x 192
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_5a_3x3')
                    end_points['MaxPool_5a_3x3'] = net

                    # 35 x 35 x 320
                    name = "Mixed_5b"
                    with tf.variable_scope(name):
                        with tf.variable_scope('Branch_0'):
                            tower_conv = slim.conv2d(
                                net,
                                96,
                                1,
                                scope='Conv2d_1x1',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_1'):
                            tower_conv1_0 = slim.conv2d(
                                net,
                                48,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv1_1 = slim.conv2d(
                                tower_conv1_0,
                                64,
                                5,
                                scope='Conv2d_0b_5x5',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_2'):
                            tower_conv2_0 = slim.conv2d(
                                net,
                                64,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_1 = slim.conv2d(
                                tower_conv2_0,
                                96,
                                3,
                                scope='Conv2d_0b_3x3',
                                trainable=False,
                                reuse=reuse)
                            tower_conv2_2 = slim.conv2d(
                                tower_conv2_1,
                                96,
                                3,
                                scope='Conv2d_0c_3x3',
                                trainable=False,
                                reuse=reuse)
                        with tf.variable_scope('Branch_3'):
                            tower_pool = slim.avg_pool2d(
                                net,
                                3,
                                stride=1,
                                padding='SAME',
                                scope='AvgPool_0a_3x3')
                            tower_pool_1 = slim.conv2d(
                                tower_pool,
                                64,
                                1,
                                scope='Conv2d_0b_1x1',
                                trainable=False,
                                reuse=reuse)
                        net = tf.concat([
                            tower_conv, tower_conv1_1, tower_conv2_2, tower_pool_1
                        ], 3)
                    end_points[name] = net

                    # BLOCK 35
                    name = "Block35"
                    net = slim.repeat(
                        net,
                        10,
                        block35,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)

                    net, core_endpoints = inception_resnet_v2_core(
                                         net,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=reuse,
                                         scope='InceptionResnetV2',
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )

    end_points.update(core_endpoints)

    return net, end_points


def inception_resnet_v2_adapt_layers_1_5_head(inputs,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=None,
                                         scope='InceptionResnetV2',
                                         mode=tf.estimator.ModeKeys.TRAIN,
                                         trainable_variables=None,
                                         is_siamese=True,
                                         is_left = True,
                                         force_weights_shutdown=False,
                                         **kwargs):
    """Creates the Inception Resnet V2 model for the adaptation of the
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

    end_points = dict()

    with tf.variable_scope(scope, 'InceptionResnetV2', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not            
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)
            
            # In case you want to reuse the left part
            # TODO: CHECK THIS PATCH
            if is_left and reuse:
                is_reusable = True
            

            # ADAPTABLE PART
            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                # CORE OF THE THE ADAPTATION
                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
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
                        net,
                        3,
                        stride=2,
                        padding='VALID',
                        scope='MaxPool_3a_3x3')

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

                    # 35 x 35 x 192
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_5a_3x3')
                    end_points['MaxPool_5a_3x3'] = net

                    # 35 x 35 x 320
                    name = "Mixed_5b"
                    name = compute_layer_name(name, is_left, is_siamese)
                    with tf.variable_scope(name):
                        with tf.variable_scope('Branch_0'):
                            tower_conv = slim.conv2d(
                                net,
                                96,
                                1,
                                scope='Conv2d_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_1'):
                            tower_conv1_0 = slim.conv2d(
                                net,
                                48,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv1_1 = slim.conv2d(
                                tower_conv1_0,
                                64,
                                5,
                                scope='Conv2d_0b_5x5',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_2'):
                            tower_conv2_0 = slim.conv2d(
                                net,
                                64,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv2_1 = slim.conv2d(
                                tower_conv2_0,
                                96,
                                3,
                                scope='Conv2d_0b_3x3',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv2_2 = slim.conv2d(
                                tower_conv2_1,
                                96,
                                3,
                                scope='Conv2d_0c_3x3',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_3'):
                            tower_pool = slim.avg_pool2d(
                                net,
                                3,
                                stride=1,
                                padding='SAME',
                                scope='AvgPool_0a_3x3')
                            tower_pool_1 = slim.conv2d(
                                tower_pool,
                                64,
                                1,
                                scope='Conv2d_0b_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        net = tf.concat([
                            tower_conv, tower_conv1_1, tower_conv2_2, tower_pool_1
                        ], 3)
                    end_points[name] = net


            # NON ADAPTABLE PART
            with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    # BLOCK 35
                    name = "Block35"
                    net = slim.repeat(
                        net,
                        10,
                        block35,
                        scale=0.17,
                        trainable_variables=False,
                        reuse=reuse)

                    net, core_endpoints = inception_resnet_v2_core(
                                         net,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=reuse,
                                         scope='InceptionResnetV2',
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs
                    )
    end_points.update(core_endpoints)

    return net, end_points


def inception_resnet_v2_adapt_layers_1_6_head(inputs,
                                              dropout_keep_prob=0.8,
                                              bottleneck_layer_size=128,
                                              reuse=None,
                                              scope='InceptionResnetV2',
                                              mode=tf.estimator.ModeKeys.TRAIN,
                                              trainable_variables=None,
                                              is_siamese=True,
                                              is_left=True,
                                              force_weights_shutdown=False,
                                              **kwargs):
    """Creates the Inception Resnet V2 model for the adaptation of the
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

    end_points = dict()

    with tf.variable_scope(scope, 'InceptionResnetV2', [inputs]):

        with slim.arg_scope([slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                             stride=1,
                             padding='SAME'):

            # Defining if the branches are reusable or not            
            is_trainable = is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN)
            is_reusable = is_reusable_variable(is_siamese, is_left)

            # In case you want to reuse the left part
            # TODO: CHECK THIS PATCH
            if is_left and reuse:
                is_reusable = True

            # ADAPTABLE PART
            with slim.arg_scope([slim.dropout], is_training=(mode == tf.estimator.ModeKeys.TRAIN)):

                # CORE OF THE THE ADAPTATION
                with slim.arg_scope([slim.batch_norm], trainable=is_trainable, is_training=is_trainable):
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
                        net,
                        3,
                        stride=2,
                        padding='VALID',
                        scope='MaxPool_3a_3x3')

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

                    # 35 x 35 x 192
                    net = slim.max_pool2d(
                        net, 3, stride=2, padding='VALID', scope='MaxPool_5a_3x3')
                    end_points['MaxPool_5a_3x3'] = net

                    # 35 x 35 x 320
                    name = "Mixed_5b"
                    name = compute_layer_name(name, is_left, is_siamese)
                    with tf.variable_scope(name):
                        with tf.variable_scope('Branch_0'):
                            tower_conv = slim.conv2d(
                                net,
                                96,
                                1,
                                scope='Conv2d_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_1'):
                            tower_conv1_0 = slim.conv2d(
                                net,
                                48,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv1_1 = slim.conv2d(
                                tower_conv1_0,
                                64,
                                5,
                                scope='Conv2d_0b_5x5',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_2'):
                            tower_conv2_0 = slim.conv2d(
                                net,
                                64,
                                1,
                                scope='Conv2d_0a_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv2_1 = slim.conv2d(
                                tower_conv2_0,
                                96,
                                3,
                                scope='Conv2d_0b_3x3',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                            tower_conv2_2 = slim.conv2d(
                                tower_conv2_1,
                                96,
                                3,
                                scope='Conv2d_0c_3x3',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        with tf.variable_scope('Branch_3'):
                            tower_pool = slim.avg_pool2d(
                                net,
                                3,
                                stride=1,
                                padding='SAME',
                                scope='AvgPool_0a_3x3')
                            tower_pool_1 = slim.conv2d(
                                tower_pool,
                                64,
                                1,
                                scope='Conv2d_0b_1x1',
                                trainable=is_trainable and not force_weights_shutdown,
                                reuse=is_reusable)
                        net = tf.concat([
                            tower_conv, tower_conv1_1, tower_conv2_2, tower_pool_1
                        ], 3)
                    end_points[name] = net


                    # BLOCK 35
                    name = "block35"
                    name = compute_layer_name(name, is_left, is_siamese)
                    net = slim.repeat(
                        net,
                        10,
                        block35,
                        scale=0.17,
                        scope=name,
                        trainable_variables=is_trainable and not force_weights_shutdown,
                        reuse=is_reusable
                    )
                    end_points[name] = net

                # CORE OF THE THE ADAPTATION
                with slim.arg_scope([slim.batch_norm], trainable=False, is_training=False):

                    net, core_endpoints = inception_resnet_v2_core(
                                         net,
                                         dropout_keep_prob=0.8,
                                         bottleneck_layer_size=128,
                                         reuse=reuse,
                                         scope='InceptionResnetV2',
                                         mode=mode,
                                         trainable_variables=None,
                                         **kwargs)
    end_points.update(core_endpoints)

    return net, end_points
