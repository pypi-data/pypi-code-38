#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import numpy
import bob.core
import bob.ip.base
from bob.bio.base.preprocessor import Preprocessor


class HistogramEqualization(Preprocessor):
  '''Applies histogram equalization on the input image

  Ported from: antispoofing.fvcompetition_icb2015 (now deprecated)
  '''


  def __init__(self):
    super(HistogramEqualization, self).__init__()


  def __call__(self, image, annotations=None):

    image_heq = numpy.zeros(image.shape, dtype=numpy.uint8)
    bob.ip.base.histogram_equalization(image, image_heq)
    return bob.core.convert(image_heq, numpy.float64, (0,1), (0,255))
