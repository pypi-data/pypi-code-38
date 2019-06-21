#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import math
import numpy
import bob.sp
from bob.bio.base.extractor import Extractor


class FourierFeatures(Extractor):
  '''Calculates the FFT features established on [TREA15]_.

  Ported from: antispoofing.fvcompetition_icb2015 (now deprecated)
  '''


  def __init__(self):
    super(FourierFeatures, self).__init__()


  def __call__(self, data):

    height, width = data.shape

    # Determine lower half starting point vertically
    if numpy.mod(height, 2) == 0:
      half_height = int(height/2 + 1)
    else:
      half_height = int(numpy.ceil(height/2))

    # Determine lower half starting point horizontally
    if numpy.mod(width, 2) == 0:
      half_width = int(width/2 + 1)
    else:
      half_width = int(numpy.ceil(width/2))

    Ffreq = bob.sp.fftshift(bob.sp.fft(data.astype(numpy.complex128))/math.sqrt(height*width))
    F = numpy.log10(abs(Ffreq)**2)

    offset_window = 10
    img_half_section_v = F[:,(half_width-offset_window):(half_width+offset_window)]

    pv = numpy.mean(img_half_section_v, 1)

    dBthreshold = -3
    Bwv = numpy.size(numpy.where(pv>dBthreshold))*1.0 / height

    return Bwv
