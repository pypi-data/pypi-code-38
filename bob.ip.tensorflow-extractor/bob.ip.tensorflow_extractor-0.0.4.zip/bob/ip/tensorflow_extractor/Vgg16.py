#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
from tensorflow.contrib.slim.python.slim.nets import vgg
import tensorflow.contrib.slim as slim
from tensorflow.contrib.layers.python.layers import layers as layers_lib
from tensorflow.contrib import layers
from tensorflow.contrib.framework.python.ops import arg_scope
from .Extractor import Extractor
import numpy
import bob.extension.download
import os

def vgg_16(inputs,
           reuse=None,
           dropout_keep_prob=0.5,
           weight_decay=0.0005,
           mode=tf.estimator.ModeKeys.TRAIN, **kwargs):
    """
    Oxford Net VGG 16-Layers version E Example from tf-slim

    Adapted from here.
    https://raw.githubusercontent.com/tensorflow/models/master/research/slim/nets/vgg.py

    **Parameters**:

        inputs: a 4-D tensor of size [batch_size, height, width, 3].

        reuse: whether or not the network and its variables should be reused. To be
               able to reuse 'scope' must be given.

        mode:
           Estimator mode keys
    """
    end_points = dict()
    with tf.variable_scope('vgg_16', reuse=reuse):

        with arg_scope([layers.conv2d, layers_lib.fully_connected],
                        activation_fn=tf.nn.relu,
                        weights_regularizer=None,
                        biases_initializer=tf.zeros_initializer(),
                        trainable=mode==tf.estimator.ModeKeys.PREDICT):
 
            # Collect outputs for conv2d, fully_connected and max_pool2d.
                
            net = layers_lib.repeat(inputs, 2, layers.conv2d, 64, [3, 3], scope='conv1')
            net = layers_lib.max_pool2d(net, [2, 2], scope='pool1')
            end_points['conv1'] = net

            net = layers_lib.repeat(net, 2, layers.conv2d, 128, [3, 3], scope='conv2')
            net = layers_lib.max_pool2d(net, [2, 2], scope='pool2')
            end_points['conv2'] = net

            net = layers_lib.repeat(net, 3, layers.conv2d, 256, [3, 3], scope='conv3')
            net = layers_lib.max_pool2d(net, [2, 2], scope='pool3')
            end_points['conv3'] = net

            net = layers_lib.repeat(net, 3, layers.conv2d, 512, [3, 3], scope='conv4')
            net = layers_lib.max_pool2d(net, [2, 2], scope='pool4')
            end_points['conv4'] = net
           
            net = layers_lib.repeat(net, 3, layers.conv2d, 512, [3, 3], scope='conv5')
            net = layers_lib.max_pool2d(net, [2, 2], scope='pool5')
            end_points['conv5'] = net
           
            net = slim.flatten(net)

            net = layers.fully_connected(net, 4096, scope='fc6')
            end_points['fc6'] = net
            
            net = layers.fully_connected(net, 4096, scope='fc7', activation_fn=None)
            
            end_points['fc7'] = net

    return net, end_points


class VGGFace(Extractor):
    """
    Extract features using the VGG model
    http://www.robots.ox.ac.uk/~vgg/software/vgg_face/
    
    This was converted with the script https://github.com/tiagofrepereira2012

    """

    def __init__(self, checkpoint_filename=None, debug=False):
        # Average image provided in
        # http://www.robots.ox.ac.uk/~vgg/software/vgg_face/
        self.average_img = [129.1863, 104.7624, 93.5940]

        if checkpoint_filename is None:
            checkpoint_filename = os.path.join(VGGFace.get_vggpath(),"vgg_face_tf")

        # Downloading the model if necessary
        if not os.path.exists(checkpoint_filename):            
            zip_file = os.path.join(VGGFace.get_vggpath(), "vgg_face_tf.tar.gz")

            urls = [
                # This is a private link at Idiap to save bandwidth.
                "https://www.idiap.ch/software/bob/data/bob/bob.ip.tensorflow_extractor/master/"
                "vgg_face_tf.tar.gz",
                "http://www.idiap.ch/software/bob/data/bob/bob.ip.tensorflow_extractor/master/"
                "vgg_face_tf.tar.gz",                
            ]

            bob.extension.download.download_and_unzip(urls, zip_file)

        input_tensor = tf.placeholder(tf.float32, shape=(1, 224, 224, 3))
        graph = vgg_16(input_tensor)[0]

        super(VGGFace, self).__init__(checkpoint_filename=os.path.join(checkpoint_filename),
                                      input_tensor=input_tensor,
                                      graph=graph,
                                      debug=debug)

        
    def __call__(self, image):
        
        if len(image.shape) == 3:        

            # Converting from RGB to BGR            
            R = image[0, :, :] - self.average_img[0]
            G = image[1, :, :] - self.average_img[1]
            B = image[2, :, :] - self.average_img[2]

            # Converting to
            bgr_image = numpy.zeros(shape=image.shape)
            bgr_image[0, :, :] = B
            bgr_image[1, :, :] = G
            bgr_image[2, :, :] = R
                        
            # SWAPING TO CxHxW to HxWxC
            bgr_image = numpy.moveaxis(bgr_image,0,-1)
            bgr_image  = numpy.expand_dims(bgr_image,0)
            
            if self.session is None:
                self.session = tf.InteractiveSession()            
            return self.session.run(self.graph, feed_dict={self.input_tensor: bgr_image})[0]
        else:
            raise ValueError("Image should have 3 channels")
        
            
    @staticmethod
    def get_vggpath():
        import pkg_resources
        return pkg_resources.resource_filename(__name__, 'data')

