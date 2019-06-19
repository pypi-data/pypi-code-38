#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sun Dec 9 16:32:00 2012 +0100
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests for the PAVA-like algorithm
"""

import os, sys
from bob.math import pavx, pavxWidth, pavxWidthHeight
import numpy

def pavx_check(y, ghat_ref, w_ref, h_ref):
  """Make a full test for a given sample"""

  ghat = pavx(y)
  assert numpy.all(numpy.abs(ghat - ghat_ref) < 1e-4)
  pavx(y, ghat)
  assert numpy.all(numpy.abs(ghat - ghat_ref) < 1e-4)
  w=pavxWidth(y, ghat)
  assert numpy.all(numpy.abs(w - w_ref) < 1e-4)
  assert numpy.all(numpy.abs(ghat - ghat_ref) < 1e-4)
  ret=pavxWidthHeight(y, ghat)
  assert numpy.all(numpy.abs(ghat - ghat_ref) < 1e-4)
  assert numpy.all(numpy.abs(ret[0] - w_ref) < 1e-4)
  assert numpy.all(numpy.abs(ret[1] - h_ref) < 1e-4)

def test_pavx_sample1():

  # Reference obtained using bosaris toolkit 1.06
  y = numpy.array([ 58.4666,  67.1040,  73.1806,  77.0896,  85.8816,
    89.6381, 101.6651, 102.5587, 109.7933, 117.5715,
    118.1671, 138.3151, 141.9755, 145.7352, 159.1108,
    156.8654, 168.6932, 175.2756])
  ghat_ref = numpy.array([ 58.4666,  67.1040,  73.1806,  77.0896,  85.8816,
    89.6381, 101.6651, 102.5587, 109.7933, 117.5715,
    118.1671, 138.3151, 141.9755, 145.7352, 157.9881,
    157.9881, 168.6932, 175.2756])
  w_ref = numpy.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1])
  h_ref = numpy.array([ 58.4666,  67.1040,  73.1806,  77.0896,  85.8816,
    89.6381, 101.6651, 102.5587, 109.7933, 117.5715,
    118.1671, 138.3151, 141.9755, 145.7352, 157.9881,
    168.6932, 175.2756])

  pavx_check(y, ghat_ref, w_ref, h_ref)

def test_pavx_sample2():

  # Reference obtained using bosaris toolkit 1.06
  y = numpy.array([ 46.1093,  64.3255,  76.5252,  89.0061, 100.4421,
    92.8593,  84.0840,  98.5769, 102.3841, 143.5045,
    120.8439, 141.4807, 139.0758, 156.8861, 147.3515,
    147.9773, 154.7762, 180.8819])
  ghat_ref = numpy.array([ 46.1093,  64.3255,  76.5252,  89.0061,  92.4618,
    92.4618,  92.4618,  98.5769, 102.3841, 132.1742,
    132.1742, 140.2783, 140.2783, 150.7383, 150.7383,
    150.7383, 154.7762, 180.8819])
  w_ref = numpy.array([1, 1, 1, 1, 3, 1, 1, 2, 2, 3, 1, 1])
  h_ref = numpy.array([ 46.1093,  64.3255,  76.5252,  89.0061,  92.4618,
    98.5769, 102.3841, 132.1742, 140.2783, 150.7383,
    154.7762,  180.8819])

  pavx_check(y, ghat_ref, w_ref, h_ref)
