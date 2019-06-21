#!/usr/bin/env python

"""Features for face recognition"""

import numpy  # this is needed for documentation

from bob.bio.base.extractor import Extractor
import bob.ip.caffe_extractor


class LightCNNExtractor(Extractor):
    """Feature extractor of face images using the LightCNNExtractor Caffe model.
    For more information please see :any:`bob.ip.caffe_extractor.LightCNN`

    Attributes
    ----------
    end_cnn : :obj:`str`, optional
        The name of the layer that you want to use as a feature.
    feature_extractor : :any:`bob.ip.caffe_extractor.LightCNN`
        The instance of feature extractor.
    model_version : :obj:`str`, optional
        Which model to use.
    """

    def __init__(
            self,
            end_cnn="eltwise_fc1",
            model_version="LightenedCNN_C",
    ):
        super(LightCNNExtractor, self).__init__(
            skip_extractor_training=True,
            end_cnn=end_cnn,
            model_version=model_version,
        )

        # initialize this when called for the first time
        # since caffe may not work if it is compiled to run with gpu
        self.feature_extractor = None
        self.end_cnn = end_cnn
        self.model_version = model_version

    def __call__(self, image):
        """Extracts features given a gray face image.

        Parameters
        ----------
        image : numpy.array
            The gray image. Please see
            :any:`bob.ip.caffe_extractor.LightCNN.__call__` for the required
            format. For convenience, if the image range is [0,255], it is
            divided by 255. This assumes that the original image is an int8
            image but be careful when relying on this feature.

        Returns
        -------
        numpy.array
            The extracted features.

        Raises
        ------
        ValueError
            If the image is not within [0,1] range.
        """
        if self.feature_extractor is None:
            self.feature_extractor = bob.ip.caffe_extractor.LightCNN(
                self.end_cnn, self.model_version)
        image = numpy.ascontiguousarray(image)
        maxv = image.max()
        if maxv >= 1.001:
            raise ValueError("The image values should be between 0 and 1 while"
                             " the max value is {}.".format(maxv))
        return self.feature_extractor(image)
