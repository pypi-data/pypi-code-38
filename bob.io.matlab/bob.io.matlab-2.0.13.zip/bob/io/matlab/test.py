#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 14 May 15:41:02 2014 CEST
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Test our Matlab(R) support
"""

import os
import sys
import numpy
import nose.tools

from bob.io.base import load, test_utils
from bob.io.base.test_file import transcode, array_readwrite, arrayset_readwrite

from . import read_varnames, read_matrix

def test_all():

  # array writing tests
  a1 = numpy.random.normal(size=(2,3)).astype('float32')
  a2 = numpy.random.normal(size=(2,3,4)).astype('float64')
  a3 = numpy.random.normal(size=(2,3,4,5)).astype('complex128')
  a4 = (10 * numpy.random.normal(size=(3,3))).astype('uint64')

  array_readwrite('.mat', a1)
  array_readwrite(".mat", a2)
  array_readwrite('.mat', a3)
  array_readwrite(".mat", a4)

  # arrayset writing tests
  a1 = []
  a2 = []
  a3 = []
  a4 = []
  for k in range(10):
    a1.append(numpy.random.normal(size=(2,3)).astype('float32'))
    a2.append(numpy.random.normal(size=(2,3,4)).astype('float64'))
    a3.append(numpy.random.normal(size=(2,3,4,5)).astype('complex128'))
    a4.append((10*numpy.random.normal(size=(3,3))).astype('uint64'))

  arrayset_readwrite('.mat', a1)
  arrayset_readwrite(".mat", a2)
  arrayset_readwrite('.mat', a3)
  arrayset_readwrite(".mat", a4)

  # complete transcoding tests
  transcode(test_utils.datafile('test_1d.mat', __name__)) #pseudo 1D - matlab does not support true 1D
  transcode(test_utils.datafile('test_2d.mat', __name__))
  transcode(test_utils.datafile('test_3d.mat', __name__))
  transcode(test_utils.datafile('test_4d.mat', __name__))
  transcode(test_utils.datafile('test_1d_cplx.mat', __name__)) #pseudo 1D - matlab does not support 1D
  transcode(test_utils.datafile('test_2d_cplx.mat', __name__))
  transcode(test_utils.datafile('test_3d_cplx.mat', __name__))
  transcode(test_utils.datafile('test_4d_cplx.mat', __name__))
  transcode(test_utils.datafile('test.mat', __name__)) #3D complex, large

@nose.tools.nottest
def test_mat_file_io_does_not_crash():

  data = load(test_utils.datafile('test_cell.mat', __name__))

def test_interface():

  # test that we can read the 'x' variable in the test file
  cell_file = test_utils.datafile('test_2d.mat', __name__)
  sorted(['x', 'y']) == sorted(read_varnames(cell_file))

  # read x matrix
  x = read_matrix(cell_file, 'x')
  assert x.shape == (2,3)
  y = read_matrix(cell_file, 'y')
  assert y.shape == (3,2)

  for i in range(2):
    for j in range(3):
      assert x[i,j] == float(j*2+i+1)
      assert y[j,i] == float(j*2+i+1)
