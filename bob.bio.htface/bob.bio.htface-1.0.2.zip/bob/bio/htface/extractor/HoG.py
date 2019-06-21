#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.ip.base
import numpy
import math

from bob.bio.base.extractor import Extractor
import math
class HoG(Extractor):
    """
    Extracts block based multiscale LBP Histogram sequence.
    
    **Parameters**
      hog_operator: bob.ip.base.HOG
        Window size
    """

    def __init__(
        self,
        # Block setup
        hog_operator
    ):
      """Initializes the local Gabor binary pattern histogram sequence tool chain with the given file selector object"""

      # call base class constructor
      Extractor.__init__(
          self,
          hog_operator=hog_operator
      )
      self.hog_operator = hog_operator

    def __call__(self, image):
        """Extracts the local binary pattern histogram sequence from the given image"""
        
        if image.ndim == 2:
            return self.hog_operator(image).flatten()
        else:
            hists = []
            for i in range(image.shape[0]):
                hists += list(self.hog_operator(image[i,:,:]).flatten())
            return numpy.array(hists)

