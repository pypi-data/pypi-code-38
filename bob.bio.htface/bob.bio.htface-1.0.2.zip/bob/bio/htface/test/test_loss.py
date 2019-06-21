#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
import numpy
from bob.bio.htface.loss import fdsu_contrastive_loss, style_dsu_contrastive_loss, style_gram_dsu_contrastive_loss
"""

def test_fsdu_contrastive_loss():
    numpy.random.seed(10)
    left_embedding  = numpy.random.normal(loc=0, size=(5,10,10,2)).astype("float32")
    right_embedding = numpy.random.normal(loc=2,size=(5,10,10,2)).astype("float32")

    sess = tf.Session()

    left_embedding = tf.convert_to_tensor(left_embedding)
    right_embedding = tf.convert_to_tensor(right_embedding)
    #import ipdb; ipdb.set_trace()
    loss = sess.run(fdsu_contrastive_loss([left_embedding, left_embedding], [right_embedding, right_embedding]))

    assert loss >0 


def test_style_contrastive_loss():
    numpy.random.seed(10)

    xt_source_n_content = tf.convert_to_tensor(numpy.random.normal(loc=0, size=(5, 128)).astype("float32")) 
    xt_source_0_content = tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5, 128)).astype("float32"))

    xt_target_n_style = tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,2)).astype("float32"))
    xs_target_n_style = tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,2)).astype("float32"))
 
    #import ipdb; ipdb.set_trace()
    sess = tf.Session()
    loss = sess.run(style_dsu_contrastive_loss( xt_source_n_content,  xt_source_0_content, xt_target_n_style,  xs_target_n_style))

    assert loss >0 


def test_style_gram_contrastive_loss():
    numpy.random.seed(10)

    xt_source_n_content = tf.convert_to_tensor(numpy.random.normal(loc=0, size=(5, 128)).astype("float32")) 
    xt_source_0_content = tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5, 128)).astype("float32"))

    # First layer
    xt_target_n_style = [tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,2)).astype("float32"))]
    xs_target_n_style = [tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,2)).astype("float32"))]
 
    # Second layer
    xt_target_n_style.append(tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,5)).astype("float32")))
    xs_target_n_style.append(tf.convert_to_tensor(numpy.random.normal(loc=2,size=(5,10,10,5)).astype("float32")))
 
    #import ipdb; ipdb.set_trace()
    sess = tf.Session()
    loss = sess.run(style_gram_dsu_contrastive_loss( xt_source_n_content,  xt_source_0_content, xt_target_n_style,  xs_target_n_style))

    assert loss >0    
"""
