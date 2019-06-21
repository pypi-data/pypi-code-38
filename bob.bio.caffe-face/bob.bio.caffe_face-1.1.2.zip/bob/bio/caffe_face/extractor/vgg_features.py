#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""Features for face recognition"""

import numpy

from bob.bio.base.extractor import Extractor
from bob.ip.caffe_extractor import VGGFace


class VGGFeatures(Extractor):
    """Extract features using the VGG model http://www.robots.ox.ac.uk/~vgg/software/vgg_face/

    **Parameters:**

    feature_layer: The layer to be used as features. Possible values are `fc6`, `fc7` or `fc8`.

    """

    def __init__(
            self,
            feature_layer="fc7",
    ):
        if feature_layer not in ("fc7", "fc6", "fc8"):
            raise ValueError("Wrong value for the feature layer `{0}`. Possible values are `fc6`, `fc7` or `fc8`."
                             .format(feature_layer))
        Extractor.__init__(self, skip_extractor_training=True)

        # block parameters
        # initialize this when called for the first time
        # since caffe may not work if it is compiled to run with gpu
        self.vgg_extractor = None
        self.feature_layer = feature_layer


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
        if self.vgg_extractor is None:
            self.vgg_extractor = VGGFace(self.feature_layer)
        assert isinstance(image, numpy.ndarray)
        assert image.ndim == 3
        assert image.shape[1] == 224
        assert image.shape[2] == 224

        return self.vgg_extractor(image)
