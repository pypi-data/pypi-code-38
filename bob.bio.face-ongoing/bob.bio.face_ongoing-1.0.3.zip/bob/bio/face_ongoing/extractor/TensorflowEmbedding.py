#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
import bob.ip.tensorflow_extractor
from bob.bio.base.extractor import Extractor
import bob.io.image
import numpy


class TensorflowEmbedding(Extractor):
    """
    bob.bio.base Extractor that does the necessary image transformation 
    
    **Parameters**
      
      tf_extractor: :py:class:`bob.ip.tensorflow_extractor.Extractor`
        Class that loads the model
    """

    def __init__(
            self,
            tf_extractor
    ):
        Extractor.__init__(self, skip_extractor_training=True)
        self.tf_extractor = tf_extractor


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

        if image.ndim>2:
            image = bob.io.image.to_matplotlib(image)
            image = numpy.reshape(image, tuple([1] + list(image.shape)) )
            image = image.astype("float32")            
        else:
            image = numpy.reshape(image, tuple([1] + list(image.shape) + [1]) )
        
        features = self.tf_extractor(image)

        return features[0]

    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass

