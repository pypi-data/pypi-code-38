#!/usr/bin/env python
# encoding: utf-8


import numpy
import tensorflow as tf
import os
from bob.extension import rc
import logging
import bob.extension.download
import bob.io.base
logger = logging.getLogger(__name__)


class batch_norm(object):
    """Code modification of http://stackoverflow.com/a/33950177"""

    def __init__(self, epsilon=1e-5, momentum=0.9, name="batch_norm"):
        with tf.variable_scope(name):
            self.epsilon = epsilon
            self.momentum = momentum
            self.name = name

    def __call__(self, x, train=True, reuse=False):
        return tf.contrib.layers.batch_norm(x,
                                            decay=self.momentum,
                                            updates_collections=None,
                                            epsilon=self.epsilon,
                                            scale=True,
                                            reuse=reuse,
                                            is_training=train,
                                            scope=self.name)


def conv2d(input_, output_dim,
           k_h=3, k_w=3, d_h=2, d_w=2, stddev=0.02,
           name="conv2d", reuse=False):
    with tf.variable_scope(name, reuse=reuse):
        w = tf.get_variable('w', [k_h, k_w, input_.get_shape()[-1], output_dim],
                            initializer=tf.truncated_normal_initializer(stddev=stddev))
        conv = tf.nn.conv2d(
            input_, w, strides=[
                1, d_h, d_w, 1], padding='SAME')

        biases = tf.get_variable(
            'biases',
            [output_dim],
            initializer=tf.constant_initializer(0.0))
        conv = tf.reshape(tf.nn.bias_add(conv, biases), conv.get_shape())

        return conv


def elu(x, name='elu'):
    return tf.nn.elu(x, name)


class DRGAN(object):
    """
    class implementing the DR GAN, as described in


    Note: this code has orginally been done by L.Tran @ MSU, and is heavily influenced
          by the DCGAN code here:

          I simplified it to the maximum to increase readability, and to limit its usage
          to face image encoding.

    **Parameters**

    image_size: int
      The size of the (squared) image.

    gf_dim: int
      The number of feature maps in the first convolutional layer (encoder and discriminator).

    gfc_dim: int
      The dimension of the encoded id (output of the encoder).
    """

    def __init__(self, image_size=96, gf_dim=32, gfc_dim=320):

        self.image_size = image_size
        self.gf_dim = gf_dim
        self.gfc_dim = gfc_dim

        # batch normalization
        self.g_bn0_0 = batch_norm(name='g_k_bn0_0')
        self.g_bn0_1 = batch_norm(name='g_k_bn0_1')
        self.g_bn0_2 = batch_norm(name='g_k_bn0_2')
        self.g_bn0_3 = batch_norm(name='g_k_bn0_3')
        self.g_bn1_0 = batch_norm(name='g_k_bn1_0')
        self.g_bn1_1 = batch_norm(name='g_k_bn1_1')
        self.g_bn1_2 = batch_norm(name='g_k_bn1_2')
        self.g_bn1_3 = batch_norm(name='g_k_bn1_3')
        self.g_bn2_0 = batch_norm(name='g_k_bn2_0')
        self.g_bn2_1 = batch_norm(name='g_k_bn2_1')
        self.g_bn2_2 = batch_norm(name='g_k_bn2_2')
        self.g_bn2_3 = batch_norm(name='g_k_bn2_3')
        self.g_bn3_0 = batch_norm(name='g_k_bn3_0')
        self.g_bn3_1 = batch_norm(name='g_k_bn3_1')
        self.g_bn3_2 = batch_norm(name='g_k_bn3_2')
        self.g_bn3_3 = batch_norm(name='g_k_bn3_3')
        self.g_bn4_0 = batch_norm(name='g_k_bn4_0')
        self.g_bn4_1 = batch_norm(name='g_k_bn4_1')
        self.g_bn4_2 = batch_norm(name='g_k_bn4_2')
        self.g_bn4_c = batch_norm(name='g_h_bn4_c')
        self.g_bn5 = batch_norm(name='g_k_bn5')

    def generator_encoder(self, image, is_reuse=False, is_training=True):
        """ Function that define the graph doing the encoding of a face image.

        **Parameters**

        image: numpy array
          The input image

        is_reuse: bool
          Reuse variables.

        is_training: bool
          Flag for training mode

        **Returns**
          The encoded id
        """
        s16 = int(self.image_size / 16)
        k0_0 = image

        k0_1 = elu(
            self.g_bn0_1(
                conv2d(
                    k0_0,
                    self.gf_dim * 1,
                    d_h=1,
                    d_w=1,
                    name='g_k01_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k01_prelu')
        k0_2 = elu(
            self.g_bn0_2(
                conv2d(
                    k0_1,
                    self.gf_dim * 2,
                    d_h=1,
                    d_w=1,
                    name='g_k02_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k02_prelu')

        k1_0 = elu(
            self.g_bn1_0(
                conv2d(
                    k0_2,
                    self.gf_dim * 2,
                    d_h=2,
                    d_w=2,
                    name='g_k10_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k10_prelu')
        k1_1 = elu(
            self.g_bn1_1(
                conv2d(
                    k1_0,
                    self.gf_dim * 2,
                    d_h=1,
                    d_w=1,
                    name='g_k11_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k11_prelu')
        k1_2 = elu(
            self.g_bn1_2(
                conv2d(
                    k1_1,
                    self.gf_dim * 4,
                    d_h=1,
                    d_w=1,
                    name='g_k12_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k12_prelu')

        k2_0 = elu(
            self.g_bn2_0(
                conv2d(
                    k1_2,
                    self.gf_dim * 4,
                    d_h=2,
                    d_w=2,
                    name='g_k20_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k20_prelu')
        k2_1 = elu(
            self.g_bn2_1(
                conv2d(
                    k2_0,
                    self.gf_dim * 3,
                    d_h=1,
                    d_w=1,
                    name='g_k21_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k21_prelu')
        k2_2 = elu(
            self.g_bn2_2(
                conv2d(
                    k2_1,
                    self.gf_dim * 6,
                    d_h=1,
                    d_w=1,
                    name='g_k22_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k22_prelu')

        k3_0 = elu(
            self.g_bn3_0(
                conv2d(
                    k2_2,
                    self.gf_dim * 6,
                    d_h=2,
                    d_w=2,
                    name='g_k30_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k30_prelu')
        k3_1 = elu(
            self.g_bn3_1(
                conv2d(
                    k3_0,
                    self.gf_dim * 4,
                    d_h=1,
                    d_w=1,
                    name='g_k31_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k31_prelu')
        k3_2 = elu(
            self.g_bn3_2(
                conv2d(
                    k3_1,
                    self.gf_dim * 8,
                    d_h=1,
                    d_w=1,
                    name='g_k32_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k32_prelu')

        k4_0 = elu(
            self.g_bn4_0(
                conv2d(
                    k3_2,
                    self.gf_dim * 8,
                    d_h=2,
                    d_w=2,
                    name='g_k40_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k40_prelu')
        k4_1 = elu(
            self.g_bn4_1(
                conv2d(
                    k4_0,
                    self.gf_dim * 5,
                    d_h=1,
                    d_w=1,
                    name='g_k41_conv',
                    reuse=is_reuse),
                train=is_training,
                reuse=is_reuse),
            name='g_k41_prelu')
        k4_2 = self.g_bn4_2(
            conv2d(
                k4_1,
                self.gfc_dim,
                d_h=1,
                d_w=1,
                name='g_k42_conv',
                reuse=is_reuse),
            train=is_training,
            reuse=is_reuse)

        k5 = tf.nn.avg_pool(
            k4_2, ksize=[
                1, s16, s16, 1], strides=[
                1, 1, 1, 1], padding='VALID')
        k5 = tf.reshape(k5, [-1, self.gfc_dim])

        # dropout if training
        if (is_training):
            k5 = tf.nn.dropout(k5, keep_prob=0.6)

        return k5


class DrGanMSUExtractor(object):
    """Wrapper for the free DRGan by L.Tran @ MSU:

    To use this class as a bob.bio.base extractor::

        from bob.bio.base.extractor import Extractor
        class DrGanMSUExtractorBioBase(DrGanMSUExtractor, Extractor):
            pass
        extractor = DrGanMSUExtractorBioBase()


    **Parameters:**

      model_file:
        Path to the model
        
      image_size: list
        The input image size (WxHxC)
      
    """

    def __init__(self, model_path=rc["bob.ip.tensorflow_extractor.drgan_modelpath"], image_size=[96, 96, 3]):

        self.image_size = image_size
        self.session = tf.Session()

        # placeholder for the input image
        data_shape = [1] + self.image_size
        self.X = tf.placeholder(tf.float32, shape=data_shape)

        # the encoder
        self.drgan = DRGAN()
        self.encode = self.drgan.generator_encoder(
            self.X, is_reuse=False, is_training=False)

        # If the path is not, set the default path
        if model_path is None:
            model_path = self.get_modelpath()            

        # If does not exist, download
        if not os.path.exists(model_path):
            bob.io.base.create_directories_safe(DrGanMSUExtractor.get_modelpath())
            zip_file = os.path.join(DrGanMSUExtractor.get_modelpath(),
                                    "DR_GAN_model.zip")
            urls = [
                # This is a private link at Idiap to save bandwidth.
                "http://beatubulatest.lab.idiap.ch/private/wheels/gitlab/"
                "DR_GAN_model.zip",
            ]

            bob.extension.download.download_and_unzip(urls, zip_file)

        self.saver = tf.train.Saver()
        # Reestore either from the last checkpoint or from a particular checkpoint
        if os.path.isdir(model_path):
            self.saver.restore(self.session,
                               tf.train.latest_checkpoint(model_path))
        else:
            self.saver.restore(self.session, model_path)

    @staticmethod
    def get_modelpath():
        
        # Priority to the RC path
        model_path = rc[DrGanMSUExtractor.get_rcvariable()]

        if model_path is None:
            import pkg_resources
            model_path = pkg_resources.resource_filename(__name__,
                                                 'data/DR_GAN_model')

        return model_path


    @staticmethod
    def get_rcvariable():
        return "bob.ip.tensorflow_extractor.drgan_modelpath"


    def __call__(self, image):
        """__call__(image) -> feature

        Extract features

        **Parameters:**

        image : 3D :py:class:`numpy.ndarray` (floats)
          The image to extract the features from.

        **Returns:**

        feature : 2D :py:class:`numpy.ndarray` (floats)
          The extracted features
        """
        def bob2skimage(bob_image):
            """
            Convert bob color image to the skcit image
            """

            if len(bob_image.shape) == 3:
                skimage = numpy.zeros(
                    shape=(
                        bob_image.shape[1],
                        bob_image.shape[2],
                        3),
                    dtype=numpy.uint8)
                skimage[:, :, 0] = bob_image[0, :, :]
                skimage[:, :, 1] = bob_image[1, :, :]
                skimage[:, :, 2] = bob_image[2, :, :]
            else:
                skimage = numpy.zeros(
                    shape=(
                        bob_image.shape[0],
                        bob_image.shape[1],
                        1))
                skimage[:, :, 0] = bob_image[:, :]
            return skimage

        def rescaleToUint8(image):
            result = numpy.zeros_like(image)
            for channel in range(image.shape[2]):
                min_image = numpy.min(image[:, :, channel])
                max_image = numpy.max(image[:, :, channel])
                if (max_image - min_image) != 0:
                    result[:, :, channel] = 255.0 * \
                        ((image[:, :, channel] - min_image) / (max_image - min_image))
                else:
                    result[:, :, channel] = 0
                result = result.astype('uint8')
            return result

        # encode the provided image
        image = rescaleToUint8(image)
        image = bob2skimage(image)
        image = numpy.array(image / 127.5 - 1).astype(numpy.float32)
        shape = [1] + list(image.shape)
        img = numpy.reshape(image, tuple(shape))
        encoded_id = self.session.run(self.encode, feed_dict={self.X: img})
        return encoded_id

