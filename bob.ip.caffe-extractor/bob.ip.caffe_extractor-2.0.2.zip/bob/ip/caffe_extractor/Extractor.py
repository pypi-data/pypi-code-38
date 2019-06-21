#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Fri 17 Jun 2016 10:41:36 CEST


import caffe
import numpy


class Extractor(object):
    """
    Feature extractor using caffe

    """

    def __init__(self, deploy_architecture, model, end_cnn):
        """Loads the caffe model

        Parameters
        ----------
        deploy_architecture : str
            The path of the `prototxt` architecture file used for deployment.
            The header must have the following format.
            input: "data"
            input_dim: 1
            input_dim: c
            input_dim: w
            input_dim: h
            Where :math:`c` is the number of channels, :math:`w` is the width
            and $h$ is the height
        model : str
            The path of the trained caffe model
        end_cnn : str
            The name of the layer that you want to use as a feature
        """

        self.net = caffe.Net(deploy_architecture, model, caffe.TEST)
        self.end_cnn = end_cnn

    def __call__(self, image):
        """
        Forward the image with the loaded neural network

        Parameters
        ----------
        image : numpy.array
            Input image

        Returns
        -------
        numpy.array
            The features.

        """

        # The input must be 1,c,w,h
        # if RGB
        if len(image.shape) == 3:
            formatted_image = numpy.reshape(
                image, (1, image.shape[0], image.shape[1], image.shape[2]))
        else:
            formatted_image = numpy.reshape(
                image, (1, 1, image.shape[1], image.shape[2]))

        # Testing if the network input shape matches with the image input shape
        input_shape = self.net.blobs[self.net.inputs[0]].data.shape
        if input_shape != formatted_image.shape:
            raise ValueError("Provided image shape {0} is not different from the CNN shape {1}".format(
                formatted_image.shape, input_shape
            ))

        return self.net.forward(data=formatted_image, end=self.end_cnn)[self.end_cnn][0].copy()
