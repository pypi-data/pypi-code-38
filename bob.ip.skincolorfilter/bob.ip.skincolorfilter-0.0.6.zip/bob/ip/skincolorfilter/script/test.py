#!/usr/bin/env python
# encoding: utf-8
# Guillaume HEUSCH <guillaume.heusch@idiap.ch>
# Tue  5 Apr 11:20:29 CEST 2016

"""Test Units
"""

import nose.tools
import numpy

import bob.ip.skincolorfilter as scf

skin_filter = scf.SkinColorFilter()

#def test_circular_mask():
#  """
#  Test the generation of the circular mask
#  """
#  
#  # limit case: the center of the image is located at (0,0)
#  # so it's considered as inside (x**2 + y**2) = 0 < 0.4
#  image = numpy.zeros((3, 1, 1))
#  skin_filter.__generate_circular_mask(image)
#  assert numpy.all(skin_filter.circular_mask), "a 1x1 image should be True"
# 
#  # easy case - the "cross" should be true
#  image = numpy.zeros((3, 3, 3))
#  skin_filter.__generate_circular_mask(image)
#  assert skin_filter.circular_mask[0, 1], "middle-top should be inside" 
#  assert numpy.all(skin_filter.circular_mask[1, :]), "the whole middle line should be inside"
#  assert skin_filter.circular_mask[2, 1], "middle-bottom should be inside"
#  
#  # more realistic case - radius will be 0.4*15=6 pixels
#  image = numpy.zeros((3, 15, 15))
#  skin_filter.__generate_circular_mask(image)
#  print skin_filter.circular_mask
#  # left 
#  assert not(skin_filter.circular_mask[7, 1]), "(7,1) should not be inside" 
#  assert skin_filter.circular_mask[7, 2], "(7,2) should be inside" 
#  # top 
#  assert not(skin_filter.circular_mask[1, 7]), "(1,7) should not be inside" 
#  assert skin_filter.circular_mask[2, 7], "(2,7) should be inside" 
#  # right 
#  assert not(skin_filter.circular_mask[7, 13]), "(7,13) should not be inside" 
#  assert skin_filter.circular_mask[7, 12], "(7,12) should be inside" 
#  # bottom 
#  assert not(skin_filter.circular_mask[13, 7]), "(13, 7) should not be inside" 
#  assert skin_filter.circular_mask[12, 7], "(12, 7) should be inside" 
#
#
#def test_luma_mask():
#  """
#  Test the generation of the luma mask
#  """
#  
#  # generate a greyish image
#  image = numpy.ones((3, 11, 11))*(numpy.random.standard_normal((3,11,11)) + 128)
#  image[:, 0, :] = 0 # first line is black 
#  image[:, -1, :] = 255 # last line is white
#
#  # the circular mask (to compute mean and std luma)
#  skin_filter.__generate_circular_mask(image)
#  skin_filter.__remove_luma(image)
# 
#  # the first and last line should be all False - extreme values
#  assert not(numpy.all(skin_filter.luma_mask[:, 0]))
#  assert not(numpy.all(skin_filter.luma_mask[:, -1]))
#
#  # there should be at least one True everywhere else
#  assert numpy.any(skin_filter.luma_mask)


def test_estimate_parameters():
  """
  Test the ML estimation of the Gaussian parameters
  """
  # a red image
  image = numpy.zeros((3, 11, 11))
  image[0, :, :] = 255
  skin_filter.estimate_gaussian_parameters(image)
  assert (skin_filter.mean == [1.0, 0.0]).all(), "mean for a red image is not OK"
  assert (skin_filter.covariance == [[0.0, 0.0], [0.0, 0.0]]).all(), "covariance for red image is not OK"

  # a green image
  image = numpy.zeros((3, 11, 11))
  image[1, :, :] = 255
  skin_filter.estimate_gaussian_parameters(image)
  assert (skin_filter.mean == [0.0, 1.0]).all(), "mean for a green image is not OK"
  assert (skin_filter.covariance == [[0.0, 0.0], [0.0, 0.0]]).all(), "covariance for green image is not OK"
