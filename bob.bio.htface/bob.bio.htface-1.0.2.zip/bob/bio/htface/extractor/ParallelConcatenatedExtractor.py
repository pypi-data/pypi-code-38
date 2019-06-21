#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.ip.base
import numpy
import math

from bob.bio.base.extractor import ParallelExtractor

class ParallelConcatenatedExtractor (ParallelExtractor):
    """
    Concatenates the output of a PArallel extractor    
    """

    def __init__(
        self,
        processors, **kwargs
    ):
      """Initializes the local Gabor binary pattern histogram sequence tool chain with the given file selector object"""

      # call base class constructor
      super(ParallelConcatenatedExtractor, self).__init__(processors)


    def __call__(self, image):
        """Concatenates the output"""
        
        epsilon = 1e-10
        
        features = list(super(ParallelConcatenatedExtractor, self).__call__(image))

        # stacking
        features = numpy.array(numpy.concatenate([f for f in features]))
        
        features /= numpy.sqrt(max(numpy.sum(features**2), epsilon))
        
        return features

