#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import logging
logger = logging.getLogger("bob.learn.tensorflow")
import tensorflow as tf
from bob.learn.tensorflow.utils import compute_euclidean_distance
import numpy
from bob.learn.tensorflow.loss import linear_gram_style_loss, denoising_loss, content_loss


def fdsu_contrastive_loss(left_embedding,
                          right_embedding,
                          contrastive_margin=2.0):
    """
    Compute the FDSU Siamese loss
 

    **Parameters**

    left_feature:
      First element of the pair

    right_feature:
      Second element of the pair

    margin:
      Contrastive margin

    """

    with tf.name_scope("fsdu_contranstive_loss"):

        losses = []
        for l,r in zip(left_embedding, right_embedding):

            _, height, width, number = map(lambda i: i.value, l.get_shape())
            size = height * width * number
        
            # reshaping per channel
            l = tf.reshape(l, (-1, size))
            r = tf.reshape(r, (-1, size))

            # gram 
            #left_gram = tf.matmul(tf.transpose(l), l) / size
            #right_gram = tf.matmul(tf.transpose(r), r) / size

            #losses.append(tf.nn.l2_loss(left_gram - right_gram))
            losses.append(tf.reduce_mean(tf.square(compute_euclidean_distance(l, r))))
            

        loss = reduce(tf.add, losses)

        return loss


def style_dsu_contrastive_loss(input_pl,
                               xt_source_n_content,
                               xt_source_0_content,
                               
                               xt_target_n_style,
                               xs_target_n_style):
    """
    Compute the STYLE DSU Siamese loss USING MMD


    **Parameters**

    left_feature:
      First element of the pair

    right_feature:
      Second element of the pair

    margin:
      Contrastive margin

    """

    # Content
    c_loss = 0
    with tf.name_scope("style_loss"):
        for content_n, content_0 in zip(xt_source_n_content, xt_source_0_content): 
            c_n = tf.reduce_mean(content_n, axis=0)
            c_0 = tf.reduce_mean(content_0, axis=0)
            
            c_loss += (2 * tf.nn.l2_loss(c_n - c_0))/ c_n.shape.num_elements()
        tf.summary.scalar('content_loss', c_loss)

        # Style loss
        s_loss = 0
        for style_source, style_target in zip(xt_target_n_style, xs_target_n_style):

            style_source = tf.reduce_mean(style_source, axis=0)
            style_target = tf.reduce_mean(style_target, axis=0)

            height, width, number = map(lambda i: i.value, style_source.get_shape())
            size = height * width * number

            feats_s = tf.reshape(style_source , (-1, number))
            feats_t = tf.reshape(style_target , (-1, number))

            gram_s = tf.matmul(tf.transpose(feats_s), feats_s) / size
            gram_t = tf.matmul(tf.transpose(feats_t), feats_t) / size
 
            #s_loss += linear_gram_style_loss([gram_s], [gram_t])
            s_loss += (2 * tf.nn.l2_loss(gram_s - gram_t))/ gram_s.shape.num_elements()
        tf.summary.scalar('style_loss', s_loss)

        # Total loss
        raw_loss = tf.add(5.*c_loss, 500.*s_loss, name="raw_total_loss")
        tf.add_to_collection(tf.GraphKeys.LOSSES, raw_loss)
        tf.summary.scalar('raw_loss', raw_loss)

        # Regularization
        regularization_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
        
        loss = tf.add_n([raw_loss] + regularization_losses, name="total_loss")
        tf.summary.scalar('total_loss', loss)
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)

    return loss


    #import ipdb; ipdb.set_trace()
    #with tf.name_scope("denoising_loss"):
    #    d_loss = denoising_loss(input_pl)
    #return 5.* c_loss + 500.*s_loss + 100.*d_loss
    #return 5.* c_loss + 500.*s_loss

    """

    # Content
    with tf.name_scope("content_loss"):
        content_loss = tf.reduce_mean(tf.square(compute_euclidean_distance(xt_source_n_content, xt_source_0_content)), name="content_loss")
        tf.add_to_collection(tf.GraphKeys.LOSSES, content_loss)
        tf.summary.scalar('content_loss', content_loss)

    with tf.name_scope("style_loss"):
        # Style
        # reshaping per channel
        xt_target_n_style = tf.reduce_mean(tf.layers.flatten(xt_target_n_style), axis=0)
        xs_target_n_style = tf.reduce_mean(tf.layers.flatten(xs_target_n_style), axis=0)

        style_loss = tf.sqrt(tf.reduce_sum(tf.square(xt_target_n_style - xs_target_n_style), name="style_loss"))
        tf.add_to_collection(tf.GraphKeys.LOSSES, style_loss)
        tf.summary.scalar('style_class', style_loss)


    with tf.name_scope("total_loss"):
        loss = tf.add(0.50*content_loss, 0.50*style_loss, name="total_loss_raw")
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)
        tf.summary.scalar('raw_loss', loss)

        # Regularization
        regularization_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
        
        loss = tf.add_n([loss] + regularization_losses, name="total_loss")
        tf.summary.scalar('total_loss', loss)
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)

        return loss
    """

def style_gram_dsu_contrastive_loss(xt_source_n_content,
                               xt_source_0_content,
                               
                               xt_target_n_style,
                               xs_target_n_style):
    """
     Compute the STYLE DSU Siamese loss USING GRAM MATRICES


    **Parameters**

    left_feature:
      First element of the pair

    right_feature:
      Second element of the pair

    margin:
      Contrastive margin

    """

    # Content
    with tf.name_scope("content_loss"):
        #content_loss = tf.reduce_mean(tf.square(compute_euclidean_distance(xt_source_n_content, xt_source_0_content)), name="content_loss")
        elements, dim = map(lambda i: i.value, xt_source_n_content.get_shape())
        content_loss = tf.reduce_mean( 2*tf.nn.l2_loss(xt_source_n_content - xt_source_0_content)/dim  , name="content_loss")

        tf.add_to_collection(tf.GraphKeys.LOSSES, content_loss)
        tf.summary.scalar('content_loss', content_loss)

    with tf.name_scope("style_loss"):
        # Style
        # reshaping per channel
        style_losses = []
        for style_source, style_target in zip(xt_target_n_style, xs_target_n_style):

            style_source = tf.reduce_mean(style_source, axis=0)
            style_target = tf.reduce_mean(style_target, axis=0)

            height, width, number = map(lambda i: i.value, style_source.get_shape())
            size = height * width * number

            feats_s = tf.reshape(style_source , (-1, number))
            feats_t = tf.reshape(style_target , (-1, number))

            gram_s = tf.matmul(tf.transpose(feats_s), feats_s) / size
            gram_t = tf.matmul(tf.transpose(feats_t), feats_t) / size
            partial_style_loss = 2 * tf.nn.l2_loss(gram_s - gram_t, name="style_loss") / numpy.prod(gram_s.shape.as_list())

            #tf.summary.histogram("gram_s", gram_s)
            #tf.summary.histogram("gram_t", gram_t)
            #tf.summary.histogram("gram_s-gram_t", gram_s - gram_t)

            #style_loss = tf.sqrt(tf.reduce_sum(tf.square(xt_target_n_style - xs_target_n_style), name="style_loss"))
            style_losses.append(partial_style_loss)

        style_loss = reduce(tf.add, style_losses)
        tf.add_to_collection(tf.GraphKeys.LOSSES, style_loss)
        tf.summary.scalar('style_loss', style_loss)

    with tf.name_scope("total_loss"):
        loss = tf.add(1.*content_loss, 10.0*style_loss, name="total_loss_raw")
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)
        tf.summary.scalar('raw_loss', loss)

        # Regularization
        regularization_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
        
        loss = tf.add_n([loss] + regularization_losses, name="total_loss")
        tf.summary.scalar('total_loss', loss)
        tf.add_to_collection(tf.GraphKeys.LOSSES, loss)

        return loss

