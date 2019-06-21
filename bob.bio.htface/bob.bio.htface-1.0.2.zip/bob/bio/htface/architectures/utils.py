#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>



from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def compute_layer_name(name, is_left, is_siamese=True):
    """
    Compute the layer name for a siamese/triplet
    """
    if is_siamese:
        # Siamese is either left or right
        if is_left:
            name = name + "_left"
        else:
            name = name + "_right"
    else:
       # if is not siamese is triplet.
        if is_left:
            # Left is the anchor
            name = name + "_anchor"
        else:
            # now we need to decide if it is positive or negative
            name = name + "_positive-negative"

    return name


def is_trainable_variable(is_left, mode=tf.estimator.ModeKeys.TRAIN):
    """
    Defining if it's trainable or not
    """

    # Left is never trainable
    return mode == tf.estimator.ModeKeys.TRAIN and not is_left


def is_reusable_variable(is_siamese, is_left):
    """
    Defining if is reusable or not
    """

    # Left is NEVER reusable
    if is_left:
        return False
    else:
        if is_siamese:
            # The right part of siamese is never reusable
            return False
        else:
            # If it's triplet and either posibe and negative branch is already declared,
            # it is reusable
            for v in tf.global_variables():
                if "_positive-negative" in v.name:
                    return True

            return False
