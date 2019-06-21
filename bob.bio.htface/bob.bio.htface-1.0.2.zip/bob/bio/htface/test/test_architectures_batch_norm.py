#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


import tensorflow as tf
from bob.bio.htface.architectures.inception_v2_batch_norm import inception_resnet_v2_adapt_first_head, \
    inception_resnet_v2_adapt_layers_1_2_head, \
    inception_resnet_v2_adapt_layers_1_4_head, \
    inception_resnet_v2_adapt_layers_1_5_head, \
    inception_resnet_v2_adapt_layers_1_6_head


from bob.bio.htface.architectures.inception_v1_batch_norm import inception_resnet_v1_adapt_first_head, \
    inception_resnet_v1_adapt_layers_1_2_head, \
    inception_resnet_v1_adapt_layers_1_4_head, \
    inception_resnet_v1_adapt_layers_1_5_head, \
    inception_resnet_v1_adapt_layers_1_6_head


def test_inceptionv2_siamese():
    # Elements for checking
    functions = [inception_resnet_v2_adapt_first_head,
                 inception_resnet_v2_adapt_layers_1_2_head,
                 inception_resnet_v2_adapt_layers_1_4_head,
                 inception_resnet_v2_adapt_layers_1_5_head,
                 inception_resnet_v2_adapt_layers_1_6_head]

    n_trainable_variables = [2, 8, 10, 24, 24 + 14 * 10]

    for function, n, in zip(functions, n_trainable_variables):
        input_left = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_right = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        left, _ = function(input_left,
                           dropout_keep_prob=0.8,
                           bottleneck_layer_size=128,
                           reuse=None,
                           scope='InceptionResnetV2',
                           mode=tf.estimator.ModeKeys.TRAIN,
                           trainable_variables=None,
                           is_siamese=True,
                           is_left=True)

        right, _ = function(input_right,
                            dropout_keep_prob=0.8,
                            bottleneck_layer_size=128,
                            reuse=True,
                            scope='InceptionResnetV2',
                            mode=tf.estimator.ModeKeys.TRAIN,
                            trainable_variables=None,
                            is_siamese=True,
                            is_left=False)

        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0


def test_inceptionv2_siamese_weights_shutdown():
    # Elements for checking
    functions = [inception_resnet_v2_adapt_first_head,
                 inception_resnet_v2_adapt_layers_1_2_head,
                 inception_resnet_v2_adapt_layers_1_4_head,
                 inception_resnet_v2_adapt_layers_1_5_head,
                 inception_resnet_v2_adapt_layers_1_6_head]

    n_trainable_variables = [1, 4, 5, 12, 12 + 6 * 10]
    for function, n, in zip(functions, n_trainable_variables):
        input_left = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_right = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        left, _ = function(input_left,
                           dropout_keep_prob=0.8,
                           bottleneck_layer_size=128,
                           reuse=None,
                           scope='InceptionResnetV2',
                           mode=tf.estimator.ModeKeys.TRAIN,
                           trainable_variables=None,
                           is_siamese=True,
                           is_left=True,
                           force_weights_shutdown=True)

        right, _ = function(input_right,
                            dropout_keep_prob=0.8,
                            bottleneck_layer_size=128,
                            reuse=True,
                            scope='InceptionResnetV2',
                            mode=tf.estimator.ModeKeys.TRAIN,
                            trainable_variables=None,
                            is_siamese=True,
                            is_left=False,
                            force_weights_shutdown=True
                            )

        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0


def test_inceptionv2_triplet_weights_shutdown():
    # Elements for checking
    functions = [inception_resnet_v2_adapt_first_head,
                 inception_resnet_v2_adapt_layers_1_2_head,
                 inception_resnet_v2_adapt_layers_1_4_head,
                 inception_resnet_v2_adapt_layers_1_5_head,
                 inception_resnet_v2_adapt_layers_1_6_head]

    n_trainable_variables = [1, 4, 5, 12, 12 + 6 * 10]
    for function, n, in zip(functions, n_trainable_variables):
        input_anchor = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_positive = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_negative = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        anchor, _ = function(input_anchor,
                             dropout_keep_prob=0.8,
                             bottleneck_layer_size=128,
                             reuse=None,
                             scope='InceptionResnetV2',
                             mode=tf.estimator.ModeKeys.TRAIN,
                             trainable_variables=None,
                             is_siamese=False,
                             is_left=True,
                             force_weights_shutdown=True)

        positive, _ = function(input_positive,
                               dropout_keep_prob=0.8,
                               bottleneck_layer_size=128,
                               reuse=True,
                               scope='InceptionResnetV2',
                               mode=tf.estimator.ModeKeys.TRAIN,
                               trainable_variables=None,
                               is_siamese=False,
                               is_left=False,
                               force_weights_shutdown=True
                               )

        negative, _ = function(input_negative,
                               dropout_keep_prob=0.8,
                               bottleneck_layer_size=128,
                               reuse=True,
                               scope='InceptionResnetV2',
                               mode=tf.estimator.ModeKeys.TRAIN,
                               trainable_variables=None,
                               is_siamese=False,
                               is_left=False,
                               force_weights_shutdown=True
                               )

        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0


def test_inceptionv2_triplet():
    # Elements for checking
    # Elements for checking
    functions = [inception_resnet_v2_adapt_first_head,
                 inception_resnet_v2_adapt_layers_1_2_head,
                 inception_resnet_v2_adapt_layers_1_4_head,
                 inception_resnet_v2_adapt_layers_1_5_head,
                 inception_resnet_v2_adapt_layers_1_6_head]
    n_trainable_variables = [2, 8, 10, 24, 24 + 14 * 10]

    for function, n, in zip(functions, n_trainable_variables):
        input_anchor = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_positive = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_negative = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        anchor, _ = function(input_anchor,
                             dropout_keep_prob=0.8,
                             bottleneck_layer_size=128,
                             reuse=None,
                             scope='InceptionResnetV2',
                             mode=tf.estimator.ModeKeys.TRAIN,
                             trainable_variables=None,
                             is_siamese=False,
                             is_left=True)

        positive, _ = function(input_positive,
                               dropout_keep_prob=0.8,
                               bottleneck_layer_size=128,
                               reuse=True,
                               scope='InceptionResnetV2',
                               mode=tf.estimator.ModeKeys.TRAIN,
                               trainable_variables=None,
                               is_siamese=False,
                               is_left=False)

        negative, _ = function(input_negative,
                               dropout_keep_prob=0.8,
                               bottleneck_layer_size=128,
                               reuse=True,
                               scope='InceptionResnetV2',
                               mode=tf.estimator.ModeKeys.TRAIN,
                               trainable_variables=None,
                               is_siamese=False,
                               is_left=False)

        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0


def test_inceptionv1_siamese():
    # Elements for checking
    functions = [inception_resnet_v1_adapt_first_head,
                 inception_resnet_v1_adapt_layers_1_2_head,
                 inception_resnet_v1_adapt_layers_1_4_head,
                 inception_resnet_v1_adapt_layers_1_5_head,
                 inception_resnet_v1_adapt_layers_1_6_head]

    n_trainable_variables = [2, 8, 12, 12+5*14, 12+5*14 + 8]

    for function, n, in zip(functions, n_trainable_variables):
        input_left = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_right = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        left, _ = function(input_left,
                           dropout_keep_prob=0.8,
                           bottleneck_layer_size=128,
                           reuse=None,
                           scope='InceptionResnetV1',
                           mode=tf.estimator.ModeKeys.TRAIN,
                           trainable_variables=None,
                           is_siamese=True,
                           is_left=True)

        right, _ = function(input_right,
                            dropout_keep_prob=0.8,
                            bottleneck_layer_size=128,
                            reuse=True,
                            scope='InceptionResnetV1',
                            mode=tf.estimator.ModeKeys.TRAIN,
                            trainable_variables=None,
                            is_siamese=True,
                            is_left=False)

        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0


def test_inceptionv1_siamese_weights_shutdown():
    # Elements for checking
    functions = [inception_resnet_v1_adapt_first_head,
                 inception_resnet_v1_adapt_layers_1_2_head,
                 inception_resnet_v1_adapt_layers_1_4_head,
                 inception_resnet_v1_adapt_layers_1_5_head,
                 inception_resnet_v1_adapt_layers_1_6_head]

    n_trainable_variables = [1, 4, 6, 6+5*6, 6+5*6 + 4]

    for function, n, in zip(functions, n_trainable_variables):
        input_left = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))
        input_right = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

        left, _ = function(input_left,
                           dropout_keep_prob=0.8,
                           bottleneck_layer_size=128,
                           reuse=None,
                           scope='InceptionResnetV1',
                           mode=tf.estimator.ModeKeys.TRAIN,
                           trainable_variables=None,
                           is_siamese=True,
                           is_left=True,
                           force_weights_shutdown=True)

        right, _ = function(input_right,
                            dropout_keep_prob=0.8,
                            bottleneck_layer_size=128,
                            reuse=True,
                            scope='InceptionResnetV1',
                            mode=tf.estimator.ModeKeys.TRAIN,
                            trainable_variables=None,
                            is_siamese=True,
                            is_left=False,
                            force_weights_shutdown=True)


        assert len(tf.trainable_variables()) == n

        tf.reset_default_graph()
        assert len(tf.global_variables()) == 0

