#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

from bob.ip.mtcnn import FaceDetector
from bob.bio.face.preprocessor import Base
import bob.ip.base
import bob.ip.color
import numpy

import logging
logger = logging.getLogger("bob.bio.htface")

class DoG_Pyramid(Base):
    """Implements the DoG Piramid

    **Parameters:**

    multidog_features:
    List of DoG filteres
    """

    def __init__(
      self,
      filters=[],
      **kwargs
    ):
        # call base class constructors
        self.filters = filters

        Base.__init__(self, **kwargs)

    def __call__(self, image, annotations=None):
        """__call__(image, annotations = None) -> face

        Crops the face using the mtcnn face detector

        **Parameters:**

        image : 3D :py:class:`numpy.ndarray`
          The face image to be processed (3 channels only(.

        annotations : any
          Ignored.

        **Returns:**

        face : 3D :py:class:`numpy.ndarray`
          The cropped face.
        """

        filtered_images = []
        for f in self.filters:
            filtered_images.append(f(image,annotations=annotations))
            
        return numpy.array(filtered_images)

