#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Tue Jun 25 20:44:40 CEST 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Tests on the roll/unroll functions
"""

import numpy
from . import Machine, roll, unroll, number_of_parameters

def test_roll_1():

  m = Machine((10,3,8,5))
  m.randomize()

  vec = unroll(m)
  m2 = Machine((10,3,8,5))
  roll(m2, vec)
  assert m == m2

  m3 = Machine((10,3,8,5))
  vec = unroll(m.weights, m.biases)
  roll(m3, vec)
  assert m == m3

def test_roll_2():

  w = [numpy.array([[2,3.]]), numpy.array([[2,3,4.],[5,6,7]])]
  b = [numpy.array([5.]), numpy.array([7.,8.])]
  vec = numpy.ndarray(number_of_parameters(w, b), numpy.float64)
  unroll(w, b, vec)

  w_ = [numpy.ndarray((1,2), numpy.float64), numpy.ndarray((2,3), numpy.float64)]
  b_ = [numpy.ndarray((1,), numpy.float64), numpy.ndarray((2,), numpy.float64)]
  roll(w_, b_, vec)

  assert (w_[0] == w[0]).all()
  assert (b_[0] == b[0]).all()
