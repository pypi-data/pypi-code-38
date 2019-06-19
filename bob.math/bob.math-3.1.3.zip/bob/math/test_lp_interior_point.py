#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Fri Jan 27 21:06:59 2012 +0100
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests bob interior point Linear Programming solvers
"""

import os, sys
from bob.math import LPInteriorPointShortstep, LPInteriorPointPredictorCorrector, LPInteriorPointLongstep
import numpy
import nose.tools

def generateProblem(n):
  A = numpy.ndarray((n,2*n), numpy.float64)
  b = numpy.ndarray((n,), numpy.float64)
  c = numpy.ndarray((2*n,), numpy.float64)
  x0 = numpy.ndarray((2*n,), numpy.float64)
  sol = numpy.ndarray((n,), numpy.float64)
  A[:] = 0.
  c[:] = 0.
  sol[:] = 0.
  for i in range(n):
    A[i,i] = 1.
    A[i,n+i] = 1.
    for j in range(i+1,n):
      A[j,i] = pow(2., 1+j)
    b[i] = pow(5.,i+1)
    c[i] = -pow(2., n-1-i)
    x0[i] = 1.
  ones = numpy.ndarray((n,), numpy.float64)
  ones[:] = 1.
  A1_1 = numpy.dot(A[:,0:n], ones)
  for i in range(n):
    x0[n+i] = b[i] - A1_1[i]
  sol[n-1] = pow(5.,n)
  return (A,b,c,x0,sol)

def test_solvers():

  # This test demonstrates how to solve a Linear Programming problem
  # with the provided interior point methods

  eps = 1e-4
  acc = 1e-7
  for N in range(1,10):
    A, b, c, x0, sol = generateProblem(N)

    # short step
    op1 = LPInteriorPointShortstep(A.shape[0], A.shape[1], 0.4, acc)
    x = op1.solve(A, b, c, x0)
    # Compare to reference solution
    nose.tools.eq_( (abs(x-sol) < eps).all(), True )

    # predictor corrector
    op2 = LPInteriorPointPredictorCorrector(A.shape[0], A.shape[1], 0.5, 0.25, acc)
    x = op2.solve(A, b, c, x0)
    # Compare to reference solution
    nose.tools.eq_( (abs(x-sol) < eps).all(), True )

    # long step
    op3 = LPInteriorPointLongstep(A.shape[0], A.shape[1], 1e-3, 0.1, acc)
    x = op3.solve(A, b, c, x0)
    # Compare to reference solution
    nose.tools.eq_( (abs(x-sol) < eps).all(), True )

def test_parameters():

  op1 = LPInteriorPointShortstep(2, 4, 0.4, 1e-6)
  nose.tools.eq_(op1.m, 2)
  nose.tools.eq_(op1.n, 4)
  nose.tools.eq_(op1.theta, 0.4)
  nose.tools.eq_(op1.epsilon, 1e-6)
  op1b = LPInteriorPointShortstep(op1)
  nose.tools.eq_(op1, op1b)
  assert not (op1 != op1b)
  op1b.theta = 0.5
  assert not (op1 == op1b)
  assert op1 != op1b
  op1b.reset(3, 6)
  op1b.epsilon = 1e-5
  nose.tools.eq_(op1b.m, 3)
  nose.tools.eq_(op1b.n, 6)
  nose.tools.eq_(op1b.theta, 0.5)
  nose.tools.eq_(op1b.epsilon, 1e-5)

  op2 = LPInteriorPointPredictorCorrector(2, 4, 0.5, 0.25, 1e-6)
  nose.tools.eq_(op2.m, 2)
  nose.tools.eq_(op2.n, 4)
  nose.tools.eq_(op2.theta_pred, 0.5)
  nose.tools.eq_(op2.theta_corr, 0.25)
  nose.tools.eq_(op2.epsilon, 1e-6)
  op2b = LPInteriorPointPredictorCorrector(op2)
  nose.tools.eq_(op2, op2b)
  assert not (op2 != op2b)
  op2b.theta_pred = 0.4
  assert not (op2 == op2b)
  assert op2 != op2b
  op2b.reset(3, 6)
  op2b.theta_corr = 0.2
  op2b.epsilon = 1e-5
  nose.tools.eq_(op2b.m, 3)
  nose.tools.eq_(op2b.n, 6)
  nose.tools.eq_(op2b.theta_pred, 0.4)
  nose.tools.eq_(op2b.theta_corr, 0.2)
  nose.tools.eq_(op2b.epsilon, 1e-5)
  op2b.m = 4
  op2b.n = 8
  nose.tools.eq_(op2b.m, 4)
  nose.tools.eq_(op2b.n, 8)

  op3 = LPInteriorPointLongstep(2, 4, 0.4, 0.6, 1e-6)
  nose.tools.eq_(op3.m, 2)
  nose.tools.eq_(op3.n, 4)
  nose.tools.eq_(op3.gamma, 0.4)
  nose.tools.eq_(op3.sigma, 0.6)
  nose.tools.eq_(op3.epsilon, 1e-6)
  op3b = LPInteriorPointLongstep(op3)
  nose.tools.eq_(op3, op3b)
  assert not (op3 != op3b)
  op3b.gamma = 0.5
  assert not (op3 == op3b)
  assert op3 != op3b
  op3b.reset(3, 6)
  op3b.sigma = 0.7
  op3b.epsilon = 1e-5
  nose.tools.eq_(op3b.m, 3)
  nose.tools.eq_(op3b.n, 6)
  nose.tools.eq_(op3b.gamma, 0.5)
  nose.tools.eq_(op3b.sigma, 0.7)
  nose.tools.eq_(op3b.epsilon, 1e-5)
  op3b.m = 4
  op3b.n = 8
  nose.tools.eq_(op3b.m, 4)
  nose.tools.eq_(op3b.n, 8)

def test_dual():

  A = numpy.array([[1., 0., 1., 0.], [4., 1., 0., 1.]])
  c = numpy.array([-2., -1., 0., 0.])
  op = LPInteriorPointShortstep(2, 4, 0.4, 1e-6)
  op.initialize_dual_lambda_mu(A, c)
  lambda_ = op.lambda_
  mu = op.mu
  assert numpy.all(mu >= 0.)

  eps = 1e-4
  At = A.transpose(1,0)
  ref = numpy.dot(At, lambda_) + mu
  assert numpy.all(numpy.fabs(ref - c <= eps))
