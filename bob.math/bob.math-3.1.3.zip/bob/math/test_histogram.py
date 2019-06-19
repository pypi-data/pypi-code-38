#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>
# Tue May  1 18:12:43 CEST 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests bob interior point Linear Programming solvers
"""

import os, sys
from bob.math import histogram_intersection, kullback_leibler, chi_square
import numpy
import nose.tools

def py_chi_square(h1, h2):
  """Computes the chi-square distance between two histograms (or histogram
  sequences)"""

  d = 0
  for i in range(h1.shape[0]):
    if h1[i] != h2[i]: d += int(((h1[i] - h2[i])**2) / (h1[i] + h2[i]))
  return d

def py_histogram_intersection(h1, h2):
  """Computes the intersection measure of the given histograms (or histogram
  sequences)"""

  dist = 0
  for i in range(h1.shape[0]):
    dist += min(h1[i], h2[i])
  return dist


# initialize histograms to test the two measures
m_h1 = numpy.array([0,15,3,7,4,0,3,0,17,12], dtype = numpy.int32)
m_h2 = numpy.array([2,7,14,3,25,0,7,1,0,4], dtype = numpy.int32)

m_h3 = numpy.random.random_integers(0,99,size=(100000,))
m_h4 = numpy.random.random_integers(0,99,size=(100000,))

m_h5 = numpy.array([1,0,0,1,0,0,1,0,1,1], dtype = numpy.float64)
m_h6 = numpy.array([1,0,1,0,0,0,1,0,1,1], dtype = numpy.float64)

index_1 = numpy.array([0,3,6,8,9], dtype = numpy.uint16)
index_2 = numpy.array([0,2,6,8,9], dtype = numpy.uint16)
values = numpy.array([1,1,1,1,1], dtype = numpy.float64)

def test_histogram_intersection():

  # compare our implementation with bob.math
  nose.tools.eq_(histogram_intersection(m_h1, m_h2), py_histogram_intersection(m_h1, m_h2))
  nose.tools.eq_(histogram_intersection(m_h3, m_h4), py_histogram_intersection(m_h3, m_h4))

  # test specific (simple) case
  nose.tools.eq_(histogram_intersection(m_h5, m_h5), 5.)
  nose.tools.eq_(histogram_intersection(m_h5, m_h6), 4.)

  nose.tools.eq_(histogram_intersection(index_1, values, index_1, values), 5.)
  nose.tools.eq_(histogram_intersection(index_1, values, index_2, values), 4.)

def test_chi_square():

  # compare our implementation with bob.math
  nose.tools.eq_(chi_square(m_h1, m_h2), py_chi_square(m_h1, m_h2))
  nose.tools.eq_(chi_square(m_h3, m_h4), py_chi_square(m_h3, m_h4))

  # test specific (simple) case
  nose.tools.eq_(chi_square(m_h5, m_h5), 0.)
  nose.tools.eq_(chi_square(m_h5, m_h6), 2.)

  nose.tools.eq_(chi_square(index_1, values, index_1, values), 0.)
  nose.tools.eq_(chi_square(index_1, values, index_2, values), 2.)

def test_kullback_leibler():

  # compare our implementation with bob.math
  nose.tools.eq_(chi_square(m_h1, m_h2), py_chi_square(m_h1, m_h2))
  nose.tools.eq_(chi_square(m_h3, m_h4), py_chi_square(m_h3, m_h4))

  # test specific (simple) case
  nose.tools.eq_(kullback_leibler(m_h5, m_h5), 0.)
  nose.tools.assert_almost_equal(kullback_leibler(m_h5, m_h6), 23.0256, 4)

  nose.tools.eq_(kullback_leibler(index_1, values, index_1, values), 0.)
  nose.tools.assert_almost_equal(kullback_leibler(index_1, values, index_2, values), 23.0256, 4)
