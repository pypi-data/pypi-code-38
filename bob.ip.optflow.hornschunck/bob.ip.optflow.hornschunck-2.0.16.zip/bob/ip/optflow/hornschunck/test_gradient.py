#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 10 Apr 20:43:59 2014 CEST
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland


"""Tests our Temporal Gradient utilities going through some example data.
"""

import numpy
import scipy.signal
from . import HornAndSchunckGradient, SobelGradient

def make_image_pair_1():
  """Creates two images for you to calculate the flow

  1 1 => 1 1
  1 1    1 2

  """
  im1 = numpy.ones((2,2), 'float64')
  im2 = im1.copy()
  im2[1,1] = 2
  return im1, im2

def make_image_pair_2():
  """Creates two images for you to calculate the flow

  10 10 10 10 10    10 10 10 10 10
  10  5  5  5  5    10 10 10 10 10
  10  5  5  5  5 => 10 10  5  5  5
  10 10 10 10 10    10 10  5  5  5
  10 10 10 10 10    10 10 10 10 10

  """
  im1 = 10 * numpy.ones((5,5), 'float64')
  im1[1:3, 1:] = 5
  im2 = 10 * numpy.ones((5,5), 'float64')
  im2[2:4, 2:] = 5
  return im1, im2

def make_image_tripplet_1():
  """Creates two images for you to calculate the flow

  10 10 10 10 10    10 10 10 10 10    10 10 10 10 10
  10  5  5  5  5    10 10 10 10 10    10 10 10 10 10
  10  5  5  5  5 => 10 10  5  5  5 => 10 10 10 10 10
  10 10 10 10 10    10 10  5  5  5    10 10 10  5  5
  10 10 10 10 10    10 10 10 10 10    10 10 10  5  5

  """
  im1 = 10* numpy.ones((5,5), 'float64')
  im1[1:3, 1:] = 5
  im2 = 10* numpy.ones((5,5), 'float64')
  im2[2:4, 2:] = 5
  im3 = 10* numpy.ones((5,5), 'float64')
  im3[3:, 3:] = 5
  return im1, im2, im3

def Forward_Ex(im1, im2):
  """Calculates the approximate forward derivative in X direction"""
  e = numpy.ndarray(im1.shape, 'float64')
  e.fill(0) #only last column should keep this value
  im1 = im1.astype('float64')
  im2 = im2.astype('float64')
  for i in range(im1.shape[0]-1):
    for j in range(im1.shape[1]-1):
      e[i,j] = 0.25 * ( im1[i,j+1] - im1[i,j] +
                        im1[i+1,j+1] - im1[i+1,j] +
                        im2[i,j+1] - im2[i,j] +
                        im2[i+1,j+1] - im2[i+1,j] )
  for j in range(im1.shape[1]-1): #last row there is no i+1
    e[-1,j] = 0.5 * ( im1[-1,j+1]-im1[-1,j]+im2[-1,j+1]-im2[-1,j] )
  return e

def Forward_Ey(im1, im2):
  """Calculates the approximate forward derivative in Y direction"""
  e = numpy.ndarray(im1.shape, 'float64')
  e.fill(0) #only last row should keep this value
  im1 = im1.astype('float64')
  im2 = im2.astype('float64')
  for i in range(im1.shape[0]-1):
    for j in range(im1.shape[1]-1):
      e[i,j] = 0.25 * ( im1[i+1,j] - im1[i,j] +
                        im1[i+1,j+1] - im1[i,j+1] +
                        im2[i+1,j] - im2[i,j] +
                        im2[i+1,j+1] - im2[i,j+1] )
  for i in range(im1.shape[0]-1): #last column there is no j+1
    e[i,-1] = 0.5 * ( im1[i+1,-1]-im1[i,-1]+im2[i+1,-1]-im2[i,-1] )
  return e

def Forward_Et(im1, im2):
  """Calculates the approximate derivative in T (time) direction"""
  e = numpy.ndarray(im1.shape, 'float64')
  e.fill(0) #only last row should keep this value
  im1 = im1.astype('float64')
  im2 = im2.astype('float64')
  for i in range(im1.shape[0]-1):
    for j in range(im1.shape[1]-1):
      e[i,j] = 0.25 * ( im2[i,j] - im1[i,j] +
                        im2[i+1,j] - im1[i+1,j] +
                        im2[i,j+1] - im1[i,j+1] +
                        im2[i+1,j+1] - im1[i+1,j+1] )
  for i in range(im1.shape[0]-1): #last column there is no j+1
    e[i,-1] = 0.5 * ( im2[i,-1] - im1[i,-1] + im2[i+1,-1] - im1[i+1,-1] )
  for j in range(im1.shape[1]-1): #last row there is no i+1
    e[-1,j] = 0.5 * ( im2[-1,j] - im1[-1,j] + im2[-1,j+1] - im1[-1,j+1] )
  e[-1, -1] = im2[-1,-1] - im1[-1,-1]
  return e

def LaplacianBorder(u):
  """Calculates the Laplacian border estimate"""
  result = numpy.ndarray(u.shape, 'float64')
  for i in range(1, u.shape[0]-1): #middle of the image
    for j in range(1, u.shape[1]-1):
      result[i,j] = 0.25 * ( 4*u[i,j] - u[i-1,j] - u[i,j+1] - u[i+1,j] - u[i,j-1] )

  #middle of border rows
  for j in range(1, u.shape[1]-1): #first row (i-1) => not bound
    result[0,j] = 0.25 * ( 3*u[0,j] - u[0,j+1] - u[1,j] - u[0,j-1] )
  for j in range(1, u.shape[1]-1): #last row (i+1) => not bound
    result[-1,j] = 0.25 * ( 3*u[-1,j] - u[-1,j+1] - u[-2,j] - u[-1,j-1] )
  #middle of border columns
  for i in range(1, u.shape[0]-1): #first column (j-1) => not bound
    result[i,0] = 0.25 * ( 3*u[i,0] - u[i-1,0] - u[i+1,0] - u[i,1] )
  for i in range(1, u.shape[0]-1): #last column (j+1) => not bound
    result[i,-1] = 0.25 * ( 3*u[i,-1] - u[i-1,-1] - u[i+1,-1] - u[i,-2] )

  #corner pixels
  result[0,0] = 0.25 * ( 2*u[0,0] - u[0,1] - u[1,0] )
  result[0,-1] = 0.25 * ( 2*u[0,-1] - u[0,-2] - u[1,-1] )
  result[-1,0] = 0.25 * ( 2*u[-1,0] - u[-2,0] - u[-1,1] )
  result[-1,-1] = 0.25 * ( 2*u[-1,-1] - u[-2,-1] - u[-1,-2] )

  return result

def Central_Ex(im1, im2, im3):
  """Calculates the approximate central derivative in X direction"""

  Kx = numpy.array([[+1, 0, -1], [+2, 0, -2], [+1, 0, -1]], 'float64')

  c1 = numpy.ndarray(im1.shape, 'float64')
  c2 = numpy.ndarray(im2.shape, 'float64')
  c3 = numpy.ndarray(im3.shape, 'float64')

  c1 = scipy.signal.convolve2d(im1.astype('float64'), Kx, 'same', 'symm')
  c2 = scipy.signal.convolve2d(im2.astype('float64'), Kx, 'same', 'symm')
  c3 = scipy.signal.convolve2d(im3.astype('float64'), Kx, 'same', 'symm')

  return c1 + 2*c2 + c3

def Central_Ey(im1, im2, im3):
  """Calculates the approximate central derivative in Y direction"""

  Ky = numpy.array([[+1, +2, +1], [0, 0, 0], [-1, -2, -1]], 'float64')

  c1 = numpy.ndarray(im1.shape, 'float64')
  c2 = numpy.ndarray(im2.shape, 'float64')
  c3 = numpy.ndarray(im3.shape, 'float64')

  c1 = scipy.signal.convolve2d(im1.astype('float64'), Ky, 'same', 'symm')
  c2 = scipy.signal.convolve2d(im2.astype('float64'), Ky, 'same', 'symm')
  c3 = scipy.signal.convolve2d(im3.astype('float64'), Ky, 'same', 'symm')

  return c1 + 2*c2 + c3

def Central_Et(im1, im2, im3):
  """Calculates the approximate central derivative in Y direction"""

  Kt = numpy.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], 'float64')

  c1 = numpy.zeros(im1.shape, 'float64')
  c3 = numpy.zeros(im3.shape, 'float64')

  c1 = scipy.signal.convolve2d(im1.astype('float64'), Kt, 'same', 'symm')
  c3 = scipy.signal.convolve2d(im3.astype('float64'), Kt, 'same', 'symm')

  return c3 - c1

def test_HornAndSchunckCxxAgainstPythonSynthetic():

  i1, i2 = make_image_pair_1()
  grad = HornAndSchunckGradient(i1.shape)
  ex_cxx, ey_cxx, et_cxx = grad(i1, i2)
  ex_python = Forward_Ex(i1, i2)
  ey_python = Forward_Ey(i1, i2)
  et_python = Forward_Et(i1, i2)
  assert numpy.array_equal(ex_cxx, ex_python)
  assert numpy.array_equal(ey_cxx, ey_python)
  assert numpy.array_equal(et_cxx, et_python)

  i1, i2 = make_image_pair_2()
  grad.shape = i1.shape
  ex_cxx, ey_cxx, et_cxx = grad(i1, i2)
  ex_python = Forward_Ex(i1, i2)
  ey_python = Forward_Ey(i1, i2)
  et_python = Forward_Et(i1, i2)
  assert numpy.array_equal(ex_cxx, ex_python)
  assert numpy.array_equal(ey_cxx, ey_python)
  assert numpy.array_equal(et_cxx, et_python)

def test_SobelCxxAgainstPythonSynthetic():

  i1, i2, i3 = make_image_tripplet_1()
  grad = SobelGradient(i1.shape)
  ex_python = Central_Ex(i1, i2, i3)
  ey_python = Central_Ey(i1, i2, i3)
  et_python = Central_Et(i1, i2, i3)
  ex_cxx, ey_cxx, et_cxx = grad(i1, i2, i3)
  assert numpy.array_equal(ex_cxx, ex_python)
  assert numpy.array_equal(ey_cxx, ey_python)
  assert numpy.array_equal(et_cxx, et_python)
