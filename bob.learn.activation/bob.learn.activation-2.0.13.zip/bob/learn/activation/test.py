#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Sun  2 Jun 16:42:52 2013

"""Test activation functions
"""

import numpy
import math

from . import Identity, Linear, Logistic, HyperbolicTangent, \
    MultipliedHyperbolicTangent

def estimate_gradient(f, x, epsilon=1e-4, args=()):
  """Estimates the gradient for a given callable f

  Suppose you have a function :math:`f'(x)` that purportedly computes
  :math`\frac{\partial f(x)}{\partial x}`. You'd like to check if :math:`f'(x)`
  is outputting correct derivative values. You can then use this function to
  estimate the gradient around a point and compare it to the output of
  :math:`f'(x)`. The estimation can have a precision of up to a few decimal
  houses.

  Imagine a random value for :math:`x`, called :math:`x_t` (for test). Now
  imagine you modify one of the elements in :math:`x_t` so that
  :math:`x_{t+\epsilon}` has that element added with a small (positive) value
  :math:`\epsilon` and :math:`x_{t-\epsilon}` has the same value subtracted.

  In this case, one can use a truncated Taylor expansion of the derivative
  to calculate the approximate supposed value:

  .. math::
    f'(x_t) \sim \frac{f(x_{t+\epsilon}) - f(x_{t-\epsilon})}{2\epsilon}

  The degree to which these two values should approximate each other will
  depend on the details of :math:`f(x)`. But assuming :math:`\epsilon =
  10^{-4}`, you’ll usually find that the left- and right-hand sides of the
  above will agree to at least 4 significant digits (and often many more).

  Keyword arguments:

  f
    The function which you'd like to have the gradient estimated for.

  x
    The input to ``f``. This must be the first parameter ``f`` receives. If
    that is not the case, you must write a wrapper around ``f`` so it does the
    parameter inversion and provide that wrapper instead.

    If f expects a multi-dimensional array, than this entry should be a
    :py:class:`numpy.ndarray` with as many dimensions as required for f.

  precision
    The epsilon step

  args (optional)
    Extra arguments (a tuple) to ``f``

  This function returns the estimated value for :math:`f'(x)` given ``x``.

  .. note::

    Gradient estimation is a powerful tool for testing if a function is
    correctly computing the derivative of another function, but can be quite
    slow. It therefore is not a good replacement for writing specific code that
    can compute the derivative of ``f``.
  """
  epsilon = 1e-4

  if isinstance(x, numpy.ndarray):

    retval = numpy.ndarray(x.shape, dtype=x.dtype)
    for k in range(x.size):
      xt_plus = x.copy()
      xt_plus.flat[k] += epsilon
      xt_minus = x.copy()
      xt_minus.flat[k] -= epsilon
      retval.flat[k] = (f(xt_plus,*args) - f(xt_minus,*args)) / (2*epsilon)
    return retval

  else: # x is scalar
    return (f(x+epsilon, *args) - f(x-epsilon, *args)) / (2*epsilon)

def is_close(x, y, eps=1e-10):
  return (abs(x - y) < eps)

def test_identity():

  op = Identity()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f(k), k), 'Identity does not perform identity %g != %g' % (op.f(k), k)

def test_identity_derivative():

  op = Identity()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f_prime(k), 1.), 'Identity derivative is not equal to 1.: %g != 1.' % (op.f_prime(k),)

  # tries to estimate the gradient and check
  for k in x:
    absdiff = abs(op.f_prime(k)-estimate_gradient(op.f,k))
    assert absdiff < 1e-4, 'Identity derivative and estimation do not match to 10^-4: |%g-%g| = %g' % (op.f_prime(k), estimate_gradient(op.f,k), absdiff)

def test_linear():

  C = numpy.random.rand()
  op = Linear(C)
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f(k), (C*k)), 'Linear does not match expected value: %g != %g' % (op.f(k), C*k)

def test_linear_derivative():

  C = numpy.random.rand()
  op = Linear(C)
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f_prime(k), C), 'Linear derivative does not match expected value: %g != %g' % (op.f_prime(k), k)

  # tries to estimate the gradient and check
  for k in x:
    absdiff = abs(op.f_prime(k)-estimate_gradient(op.f,k))
    assert absdiff < 1e-4, 'Identity derivative and estimation do not match to 10^-4: |%g-%g| = %g' % (op.f_prime(k), estimate_gradient(op.f,k), absdiff)

def test_hyperbolic_tangent():

  op = HyperbolicTangent()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f(k), math.tanh(k)), 'HyperbolicTangent does not match expected value: %g != %g' % (op.f(k), math.tanh(k))

def test_hyperbolic_tangent_derivative():

  op = HyperbolicTangent()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    precise = 1 - op.f(k)**2
    assert is_close(op.f_prime(k), precise), 'HyperbolicTangent derivative does not match expected value: %g != %g' % (op.f_prime(k), precise)

  # tries to estimate the gradient and check
  for k in x:
    absdiff = abs(op.f_prime(k)-estimate_gradient(op.f,k))
    assert absdiff < 1e-4, 'HyperbolicTangent derivative and estimation do not match to 10^-4: |%g-%g| = %g' % (op.f_prime(k), estimate_gradient(op.f,k), absdiff)

def test_logistic():

  op = Logistic()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    precise = 1. / (1. + math.exp(-k))
    assert is_close(op.f(k), precise), 'Logistic does not match expected value: %g != %g' % (op.f(k), precise)

def test_logistic_derivative():

  op = Logistic()
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    precise = op.f(k) * (1 - op.f(k))
    assert is_close(op.f_prime(k), precise), 'Logistic derivative does not match expected value: %g != %g' % (op.f_prime(k), precise)

  # tries to estimate the gradient and check
  for k in x:
    absdiff = abs(op.f_prime(k)-estimate_gradient(op.f,k))
    assert absdiff < 1e-4, 'Logistic derivative and estimation do not match to 10^-4: |%g-%g| = %g' % (op.f_prime(k), estimate_gradient(op.f,k), absdiff)

def test_multiplied_tanh():

  C = numpy.random.rand()
  M = numpy.random.rand()
  op = MultipliedHyperbolicTangent(C, M)
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    assert is_close(op.f(k), C*math.tanh(M*k)), 'MultipliedHyperbolicTangent does not match expected value: %g != %g' % (op.f(k), C*math.tanh(M*k))

def test_multiplied_tanh_derivative():

  C = numpy.random.rand()
  M = numpy.random.rand()
  op = MultipliedHyperbolicTangent(C, M)
  x = numpy.random.rand(10) #10 random numbers between 0 and 1

  # go for an exact match
  for k in x:
    precise = C*M*(1-math.pow(math.tanh(M*k),2))
    assert is_close(op.f_prime(k),precise), 'MultipliedHyperbolicTangent derivative does not match expected value: %g != %g' % (op.f_prime(k), precise)

  # tries to estimate the gradient and check
  for k in x:
    absdiff = abs(op.f_prime(k)-estimate_gradient(op.f,k))
    assert absdiff < 1e-4, 'MultipliedHyperbolicTangent derivative and estimation do not match to 10^-4: |%g-%g| = %g' % (op.f_prime(k), estimate_gradient(op.f,k), absdiff)

def test_1d_ndarray():

  C = numpy.random.rand()
  op = Linear(C)
  X = numpy.random.rand(10) #10 random numbers between 0 and 1

  Y = op(X)
  assert Y.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f = op.f(X)
  assert Y_f.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f_prime = op.f_prime(X)
  assert Y_f_prime.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f_prime_from_f = op.f_prime_from_f(X)
  assert Y_f_prime_from_f.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  for k,x in enumerate(X):
    assert is_close(op(x), Y[k])
    assert is_close(op.f(x), Y_f[k])
    assert is_close(op.f_prime(x), Y_f_prime[k])
    assert is_close(op.f_prime_from_f(x), Y_f_prime_from_f[k])

def test_2d_ndarray():

  C = numpy.random.rand()
  op = Linear(C)
  X = numpy.random.rand(4, 4)

  Y = op(X)
  assert Y.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f = op.f(X)
  assert Y_f.shape == X.shape
  assert Y_f.dtype == numpy.dtype(float)

  Y_f_prime = op.f_prime(X)
  assert Y_f_prime.shape == X.shape
  assert Y_f_prime.dtype == numpy.dtype(float)

  Y_f_prime_from_f = op.f_prime_from_f(X)
  assert Y_f_prime_from_f.shape == X.shape
  assert Y_f_prime_from_f.dtype == numpy.dtype(float)

  for k,x in enumerate(X.flat):
    assert is_close(op(x), Y.flat[k])
    assert is_close(op.f(x), Y_f.flat[k])
    assert is_close(op.f_prime(x), Y_f_prime.flat[k])
    assert is_close(op.f_prime_from_f(x), Y_f_prime_from_f.flat[k])

def test_3d_ndarray():

  C = numpy.random.rand()
  op = Linear(C)
  X = numpy.random.rand(3, 3, 3)

  Y = op(X)
  assert Y.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f = op.f(X)
  assert Y_f.shape == X.shape
  assert Y_f.dtype == numpy.dtype(float)

  Y_f_prime = op.f_prime(X)
  assert Y_f_prime.shape == X.shape
  assert Y_f_prime.dtype == numpy.dtype(float)

  Y_f_prime_from_f = op.f_prime_from_f(X)
  assert Y_f_prime_from_f.shape == X.shape
  assert Y_f_prime_from_f.dtype == numpy.dtype(float)

  for k,x in enumerate(X.flat):
    assert is_close(op(x), Y.flat[k])
    assert is_close(op.f(x), Y_f.flat[k])
    assert is_close(op.f_prime(x), Y_f_prime.flat[k])
    assert is_close(op.f_prime_from_f(x), Y_f_prime_from_f.flat[k])

def test_4d_ndarray():

  C = numpy.random.rand()
  op = Linear(C)
  X = numpy.random.rand(2, 2, 2, 2)

  Y = op(X)
  assert Y.shape == X.shape
  assert Y.dtype == numpy.dtype(float)

  Y_f = op.f(X)
  assert Y_f.shape == X.shape
  assert Y_f.dtype == numpy.dtype(float)

  Y_f_prime = op.f_prime(X)
  assert Y_f_prime.shape == X.shape
  assert Y_f_prime.dtype == numpy.dtype(float)

  Y_f_prime_from_f = op.f_prime_from_f(X)
  assert Y_f_prime_from_f.shape == X.shape
  assert Y_f_prime_from_f.dtype == numpy.dtype(float)

  for k,x in enumerate(X.flat):
    assert is_close(op(x), Y.flat[k])
    assert is_close(op.f(x), Y_f.flat[k])
    assert is_close(op.f_prime(x), Y_f_prime.flat[k])
    assert is_close(op.f_prime_from_f(x), Y_f_prime_from_f.flat[k])
