#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

# Calling our base setup
from bob.bio.htface.architectures.inception_v1_batch_norm import inception_resnet_v1_adapt_layers_1_4_head

import os
import tensorflow as tf
#from tensorflow.python import debug as tf_debug

from bob.bio.htface.dataset.triplet_htface import shuffle_data_and_labels_image_augmentation
from bob.learn.tensorflow.utils import reproducible
from bob.bio.htface.estimators import   TripletAdaptation
from bob.learn.tensorflow.utils.hooks import LoggerHookEstimator
from bob.learn.tensorflow.loss import triplet_loss
from bob.learn.tensorflow.utils import reproducible
from bob.bio.htface.utils import get_cnn_model_name, get_stair_case_learning_rates
from bob.extension import rc


def get_estimator(experiment_dir, database, protocol, samples_per_epoch, training_setup):

    # Training parameters
    architecture = inception_resnet_v1_adapt_layers_1_4_head
    model_name = "triplet_inceptionv1_layers_1_4_nonshared_batch_norm"

    # Setting seed
    session_config, run_config,_,_,_ = reproducible.set_seed()
    run_config = run_config.replace(save_checkpoints_steps=500)


    # Let's do 75% with 0.1 - 15% with 0.01 and 10% with 0.001
    learning_rate_boundaries = get_stair_case_learning_rates(samples_per_epoch, 
                                                             training_setup["batch_size"],
                                                             training_setup["epochs"])

    # Preparing model file name
    model_dir = get_cnn_model_name(experiment_dir, model_name,
                                   database.name, protocol)

    #INCEPTION V2 LAYER ["Conv2d_1a_3x3", "Conv2d_2a_3x3", "Conv2d_2b_3x3", "Conv2d_3b_1x1", "Conv2d_4a_3x3",
    #             "Mixed_5b", "Block35", "Mixed_6a", "Block17", "Mixed_7a",
    #             "Block8", "Conv2d_7b_1x1", "Bottleneck"]

    # Preparing the checkpoint loading
    left_scope = dict()
    left_scope['InceptionResnetV1/Conv2d_1a_3x3/'] = "InceptionResnetV1/Conv2d_1a_3x3_anchor/"
    left_scope['InceptionResnetV1/Conv2d_2a_3x3/'] = "InceptionResnetV1/Conv2d_2a_3x3_anchor/"
    left_scope['InceptionResnetV1/Conv2d_2b_3x3/'] = "InceptionResnetV1/Conv2d_2b_3x3_anchor/"
    left_scope['InceptionResnetV1/Conv2d_3b_1x1/'] = "InceptionResnetV1/Conv2d_3b_1x1_anchor/"
    left_scope['InceptionResnetV1/Conv2d_4a_3x3/'] = "InceptionResnetV1/Conv2d_4a_3x3_anchor/"
    left_scope['InceptionResnetV1/Conv2d_4b_3x3/'] = "InceptionResnetV1/Conv2d_4b_3x3_anchor/"


    left_scope['InceptionResnetV1/Repeat/'] = "InceptionResnetV1/block35/" # TF-SLIM ADD the prefix repeat unde each repeat
    left_scope['InceptionResnetV1/Mixed_6a/'] = "InceptionResnetV1/Mixed_6a/" # TF-SLIM ADD the prefix repeat unde each repeat
    left_scope['InceptionResnetV1/Repeat_1/'] = "InceptionResnetV1/block17/" # TF-SLIM ADD the prefix repeat unde each repeat    
    left_scope['InceptionResnetV1/Mixed_7a/'] = "InceptionResnetV1/Mixed_7a/"
    left_scope['InceptionResnetV1/Repeat_2/'] = "InceptionResnetV1/block8/" # TF-SLIM ADD the prefix repeat unde each repeat    
    left_scope['InceptionResnetV1/Block8/'] = "InceptionResnetV1/Mixed_8b/" # TF-SLIM ADD the prefix repeat unde each repeat    
    left_scope['InceptionResnetV1/Logits/'] = "InceptionResnetV1/Logits/"
    left_scope['InceptionResnetV1/Bottleneck/'] = "InceptionResnetV1/Bottleneck/"

    right_scope = dict()
    right_scope['InceptionResnetV1/Conv2d_1a_3x3/'] = "InceptionResnetV1/Conv2d_1a_3x3_positive-negative/"
    right_scope['InceptionResnetV1/Conv2d_2a_3x3/'] = "InceptionResnetV1/Conv2d_2a_3x3_positive-negative/"
    right_scope['InceptionResnetV1/Conv2d_2b_3x3/'] = "InceptionResnetV1/Conv2d_2b_3x3_positive-negative/"
    right_scope['InceptionResnetV1/Conv2d_3b_1x1/'] = "InceptionResnetV1/Conv2d_3b_1x1_positive-negative/"
    right_scope['InceptionResnetV1/Conv2d_4a_3x3/'] = "InceptionResnetV1/Conv2d_4a_3x3_positive-negative/"
    right_scope['InceptionResnetV1/Conv2d_4b_3x3/'] = "InceptionResnetV1/Conv2d_4b_3x3_positive-negative/"

    # Preparing the prior
    extra_checkpoint = {"checkpoint_path": rc["bob.bio.face_ongoing.msceleb-inception-v1_batchnorm_gray"],
                        "scopes": [left_scope, right_scope]
                       }


    def train_input_fn():
        return shuffle_data_and_labels_image_augmentation(database, protocol,
                                                      training_setup["data_shape"],
                                                      training_setup["data_type"],
                                                      training_setup["batch_size"],
                                                      epochs=training_setup["epochs"],
                                                      buffer_size=10**3,
                                                      gray_scale=False, 
                                                      output_shape=None,
                                                      random_flip=True, random_brightness=False,
                                                      random_contrast=False,
                                                      random_saturation=False,
                                                      per_image_normalization=True, 
                                                      groups="world", purposes="train",
                                                      extension="hdf5")

    # Defining our estimator
    optimizer = tf.train.AdagradOptimizer
    estimator = TripletAdaptation(model_dir=model_dir,
                                  architecture=architecture,
                                  optimizer=optimizer,
                                  validation_batch_size=training_setup["validation_batch_size"],
                                  config=run_config,
                                  loss_op=triplet_loss,
                                  extra_checkpoint=extra_checkpoint,
                                  learning_rate_values=training_setup["learning_rate_values"],
                                  learning_rate_boundaries=learning_rate_boundaries,
                                  )

    # Defining our hook mechanism
    hooks = [LoggerHookEstimator(estimator, 16, 1),
             tf.train.SummarySaverHook(save_steps=5,
                                   output_dir=model_dir,
                                   scaffold=tf.train.Scaffold(),
                                   summary_writer=tf.summary.FileWriter(model_dir))]

    return estimator, train_input_fn, hooks, "htface_idiap_msceleb_inception_v1_centerloss_gray"
