#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri Jan 27 13:43:22 2012 +0100
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests bob linear solvers A*x=b.
"""

import os, sys
from bob.math import linsolve, linsolve_sympos, linsolve_cg_sympos
import numpy
import nose.tools

def test_linsolve():

  # This test demonstrates how to solve a linear system A*x=b
  # symmetric positive-definite matrix

  N = 3
  # Matrices for the linear system
  A = numpy.array([1., 3., 5., 7., 9., 1., 3., 5., 7.], 'float64').reshape(N,N)
  b = numpy.array([2., 4., 6.], 'float64')

  # Reference solution
  x_ref = numpy.array([3., -2., 1.], 'float64')

  # Matrix for storing the result
  x1 = numpy.ndarray((3,), 'float64')

  # Computes the solution
  linsolve(A,b,x1)
  x2 = linsolve(A,b)

  # Compare to reference
  nose.tools.eq_( (abs(x1-x_ref) < 1e-10).all(), True )
  nose.tools.eq_( (abs(x2-x_ref) < 1e-10).all(), True )

def test_linsolveSympos():

  # This test demonstrates how to solve a linear system A*x=b
  # when A is a symmetric positive-definite matrix

  N = 3
  # Matrices for the linear system
  A = numpy.array([2., -1., 0., -1, 2., -1., 0., -1., 2.], 'float64').reshape(N,N)
  b = numpy.array([7., 5., 3.], 'float64')

  # Reference solution
  x_ref = numpy.array([8.5, 10., 6.5], 'float64')

  # Matrix for storing the result
  x1 = numpy.ndarray((3,), 'float64')

  # Computes the solution
  linsolve_sympos(A,b,x1)
  x2 = linsolve_sympos(A,b)

  # Compare to reference
  nose.tools.eq_( (abs(x1-x_ref) < 1e-10).all(), True )
  nose.tools.eq_( (abs(x2-x_ref) < 1e-10).all(), True )

def test_linsolveCGSympos():

  # This test demonstrates how to solve a linear system A*x=b
  # when A is a symmetric positive-definite matrix
  # using a conjugate gradient technique

  N = 3
  # Matrices for the linear system
  A = numpy.array([2., -1., 0., -1, 2., -1., 0., -1., 2.], 'float64').reshape(N,N)
  b = numpy.array([7., 5., 3.], 'float64')

  # Reference solution
  x_ref = numpy.array([8.5, 10., 6.5], 'float64')

  # Matrix for storing the result
  x1 = numpy.ndarray((3,), 'float64')

  # Computes the solution
  eps = 1e-6
  max_iter = 1000
  linsolve_cg_sympos(A,b,x1,eps,max_iter)
  x2 = linsolve_cg_sympos(A,b,eps,max_iter)

  # Compare to reference
  nose.tools.eq_( (abs(x1-x_ref) < 2e-6).all(), True )
  nose.tools.eq_( (abs(x2-x_ref) < 2e-6).all(), True )
