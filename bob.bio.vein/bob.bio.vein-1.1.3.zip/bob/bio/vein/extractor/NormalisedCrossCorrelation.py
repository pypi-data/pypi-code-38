#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy

import bob.io.base

from bob.bio.base.extractor import Extractor


class NormalisedCrossCorrelation (Extractor):
  """Normalised Cross-Correlation feature extractor

  Based on M. Kono, H. Ueki, and S.Umemura. Near-infrared finger vein patterns
  for personal identification. Appl. Opt. 41(35):7429-7436, 2002
  """

  def __init__(self):
    Extractor.__init__(self)


  def __call__(self, image, mask):
    """Reads the input image, extract the features based on Normalised
    Cross-Correlation of the fingervein image, and writes the resulting
    template"""

    finger_image = image    #Normalized image with histogram equalization
    finger_mask = mask

    image_vein = finger_image*finger_mask

    #TODO

    return image_vein.astype(numpy.float64)
