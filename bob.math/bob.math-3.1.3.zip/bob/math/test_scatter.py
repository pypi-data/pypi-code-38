#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon Jun 20 16:15:36 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Tests for statistical methods
"""

import os, sys
from bob.math import scatter, scatters
import numpy
import nose.tools

def means(data):
  return numpy.mean(data, axis=0)

def py_scatters(data):
  # Step 1: compute the class means mu_c, starting from the sum_c
  mu_c = numpy.array([numpy.mean(data[k][:], axis=0) for k in range(len(data))])

  # Step 2: computes the number of elements in each class
  n_c = numpy.array([data[k].shape[0] for k in range(len(data))])

  # Step 3: computes the global mean mu
  mu = numpy.sum(mu_c.T * n_c, axis=1) / sum(data[k].shape[0] for k in range(len(data)))

  # Step 4: compute the between-class scatter Sb
  mu_c_mu = (mu_c - mu)
  Sb = numpy.dot(n_c * mu_c_mu.T, mu_c_mu)

  # Step 5: compute the within-class scatter Sw
  Sw = numpy.zeros((data[0].shape[1], data[0].shape[1]), dtype=float)
  for k in range(len(data)):
    X_c_mu_c = (data[k][:] - mu_c[k,:])
    Sw += numpy.dot(X_c_mu_c.T, X_c_mu_c)

  return (Sw, Sb, mu)

def test_scatter():

  data = numpy.random.rand(50,4)

  # This test demonstrates how to use the scatter matrix function of bob.
  S, M = scatter(data)
  S /= (data.shape[0]-1)

  # Do the same with numpy and compare. Note that with numpy we are computing
  # the covariance matrix which is the scatter matrix divided by (N-1).
  K = numpy.cov(data.T)
  M_ = means(data)
  assert  (abs(S-K) < 1e-10).all()
  assert  (abs(M-M_) < 1e-10).all()

def test_scatter_variation_1():

  data = numpy.random.rand(50,4)

  # This test demonstrates how to use the scatter matrix function of bob.
  M = numpy.ndarray((data.shape[1],), dtype=float)
  S = scatter(data, m=M)
  S = S[0]
  S /= (data.shape[0]-1)

  # Do the same with numpy and compare. Note that with numpy we are computing
  # the covariance matrix which is the scatter matrix divided by (N-1).
  K = numpy.cov(data.T)
  M_ = means(data)
  assert  (abs(S-K) < 1e-10).all()
  assert  (abs(M-M_) < 1e-10).all()

def test_scatter_variation_2():

  data = numpy.random.rand(50,4)

  # This test demonstrates how to use the scatter matrix function of bob.
  S = numpy.ndarray((data.shape[1], data.shape[1]), dtype=float)
  M = scatter(data, s=S)
  M = M[0]
  S /= (data.shape[0]-1)

  # Do the same with numpy and compare. Note that with numpy we are computing
  # the covariance matrix which is the scatter matrix divided by (N-1).
  K = numpy.cov(data.T)
  M_ = means(data)
  assert  (abs(S-K) < 1e-10).all()
  assert  (abs(M-M_) < 1e-10).all()

def test_scatter_variation_3():

  data = numpy.random.rand(50,4)

  # This test demonstrates how to use the scatter matrix function of bob.
  S = numpy.ndarray((data.shape[1], data.shape[1]), dtype=float)
  M = numpy.ndarray((data.shape[1],), dtype=float)
  retval = scatter(data, m=M, s=S)
  assert not retval
  S /= (data.shape[0]-1)

  # Do the same with numpy and compare. Note that with numpy we are computing
  # the covariance matrix which is the scatter matrix divided by (N-1).
  K = numpy.cov(data.T)
  M_ = means(data)
  assert  (abs(S-K) < 1e-10).all()
  assert  (abs(M-M_) < 1e-10).all()

def test_fast_scatter():

  data = numpy.random.rand(50,4)

  # This test demonstrates how to use the scatter matrix function of bob.
  S = numpy.ndarray((data.shape[1], data.shape[1]), dtype=float)
  M = numpy.ndarray((data.shape[1],), dtype=float)
  scatter(data, S, M)
  S /= (data.shape[0]-1)

  # Do the same with numpy and compare. Note that with numpy we are computing
  # the covariance matrix which is the scatter matrix divided by (N-1).
  K = numpy.cov(data.T)
  M_ = means(data)
  assert  (abs(S-K) < 1e-10).all()
  assert  (abs(M-M_) < 1e-10).all()

def test_scatters():

  data = [
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      ]

  Sw_, Sb_, m_ = py_scatters(data)
  Sw, Sb, m = scatters(data)
  assert numpy.allclose(Sw, Sw_)
  assert numpy.allclose(Sb, Sb_)
  assert numpy.allclose(m, m_)

def test_scatters_variation_1():

  data = [
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      ]

  Sw_, Sb_, m_ = py_scatters(data)

  N = data[0].shape[1]
  Sw = numpy.ndarray((N,N), numpy.float64)
  Sb = numpy.ndarray((N,N), numpy.float64)
  m = numpy.ndarray((N,), numpy.float64)
  assert not scatters(data, Sw, Sb, m)
  assert numpy.allclose(Sw, Sw_)
  assert numpy.allclose(Sb, Sb_)
  assert numpy.allclose(m, m_)

def test_scatters_variation_2():

  data = [
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      ]

  Sw_, Sb_, m_ = py_scatters(data)

  N = data[0].shape[1]
  Sw = numpy.ndarray((N,N), numpy.float64)
  Sb = numpy.ndarray((N,N), numpy.float64)
  assert len(scatters(data, Sw, Sb)) == 1
  assert numpy.allclose(Sw, Sw_)
  assert numpy.allclose(Sb, Sb_)

def test_fast_scatters():

  data = [
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      numpy.random.rand(50,4),
      ]

  Sw_, Sb_, m_ = py_scatters(data)

  Sw = numpy.empty_like(Sw_)
  Sb = numpy.empty_like(Sb_)
  m = numpy.empty_like(m_)
  scatters(data, Sw, Sb, m)
  assert numpy.allclose(Sw, Sw_)
  assert numpy.allclose(Sb, Sb_)
  assert numpy.allclose(m, m_)
