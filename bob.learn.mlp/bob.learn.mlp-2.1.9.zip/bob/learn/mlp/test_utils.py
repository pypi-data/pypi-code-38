#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 13 Jun 2013 15:54:19 CEST

"""Pythonic implementations of Multi-Layer Perceptrons for code testing
"""

import numpy

class Machine:
  """Represents a Multi-Layer Perceptron Machine with a single hidden layer"""

  def __init__(self, bias, weights, hidden_activation, output_activation):
    """Initializes the MLP with a number of inputs and outputs. Weights are
    initialized randomly with the specified seed.

    Keyword parameters:

    bias
      A list of 1D numpy.ndarray's with 64-bit floating-point numbers
      representing the biases for each layer of the MLP. Each ndarray must have
      as many entries as neurons in that particular layer. If set to `None`,
      disables the use of biases.

    weights
      A list of 2D numpy.ndarray's with 64-bit floating-point numbers
      representing the weights for the MLP. The more entries, the more layers
      the MLP has. The weight matrix includes the bias terms weights and is
      organized so that every neuron input is in a single column. The first
      row always represents the bias connections.

    hidden_activation
      The activation function to use for the hidden neurons of the network.
      Should be one of the classes derived from
      :py:class:`bob.learn.activation.Activation`.

    output_activation
      The activation function to use for the output neurons of the network.
      Should be one of the classes derived from
      :py:class:`bob.learn.activation.Activation`.
    """

    if bias is None:
      self.weights = weights
      self.has_bias = False
    else:
      self.weights = [numpy.vstack([bias[k], weights[k]]) for k in range(len(bias))]
      self.has_bias = True

    self.hidden_activation = hidden_activation
    self.output_activation = output_activation

  def forward(self, X):
    """Executes the forward step of the N-layer neural network.

    Remember that:

    1. z = X . w

    and

    2. Output: a = g(z), with g being the activation function

    Keyword attributes:

    X
      The input vector containing examples organized in rows. The input
      matrix does **not** contain the bias term.

    Returns the outputs of the network for each row in X. Accumulates hidden
    layer outputs and activations (for backward step). At the end of this
    procedure:

    self.a
      Input, including the bias term for all layers. 1 example per row. Bias =
      first column.

    self.z
      Activations for every input X on given layer. z1 = a0 * w1
    """
    if self.has_bias:
      self.a = [numpy.hstack([numpy.ones((len(X),1)), X])]
    else:
      self.a = [X]

    self.z = []

    for w in self.weights[:-1]:
      self.z.append(numpy.dot(self.a[-1], w))
      self.a.append(self.hidden_activation(self.z[-1]))
      if self.has_bias:
        self.a[-1] = numpy.hstack([numpy.ones((len(self.a[-1]),1)), self.a[-1]])

    self.z.append(numpy.dot(self.a[-1], self.weights[-1]))
    self.a.append(self.output_activation(self.z[-1]))

    return self.a[-1]

class TrainableMachine(Machine):
  """Represents a Multi-Layer Perceptron Machine with a single hidden layer"""

  def backward(self, b):
    """Executes the backward step for training.

    In this phase, we calculate the error on the output layer and then use
    back-propagation to estimate the error on the hidden layer. We then use
    this estimated error to calculate the differences between what the layer
    output and the expected value.

    Keyword attributes:

    b
      This is the error back-propagated through the last neuron by any of the
      available :py:class:`bob.learn.mlp.Cost` functors. Every row in b matches
      one example.

    self.d

      The updates for each synapse are simply the multiplication of the a's and
      errors's on each end. One important remark to get this computation right:
      one must generate a weight change matrix that is of the same size as the
      weight matrix. If that is not the case, something is wrong on the logic

      self.d[L] = self.a[L-1] * self.b[L].T / number-of-examples

      N.B.: This **is** a matrix multiplication, despite the fact that ``a``
      and ``b`` are vectors.

    Returns the derivative estimations for every weight in the network
    """

    self.b = [b]

    # calculate the estimated errors on each layer ($\delta$)
    for k,w in reversed(list(enumerate(self.weights[1:]))):
      if self.has_bias:
        delta = numpy.dot(self.b[0], w[1:].T)
        act = self.a[k+1][:,1:]
      else:
        delta = numpy.dot(self.b[0], w.T)
        act = self.a[k+1]
      self.b.insert(0, delta*self.hidden_activation.f_prime_from_f(act))

    self.d = []
    for a,b in zip(self.a[:-1], self.b):
      self.d.append(numpy.dot(a.T, b) / len(b))

    return self.d

  def cost(self, cost_object, target):
    """Calculates the cost given the target.

    This method must be called after `forward` has been called.
    """

    return cost_object.f(self.a[-1], target).mean(axis=0).sum()

  def unroll(self):
    """Unroll its own parameters so it becomes a linear vector"""

    return numpy.hstack([k.flat for k in self.weights])

  def roll(self, v):
    """Roll-up the parameters again, undoes ``unroll()`` above."""

    retval = []
    marks = list(numpy.cumsum([k.size for k in self.weights]))
    marks.insert(0, 0)

    for k,w in enumerate(self.weights):
      retval.append(v[marks[k]:marks[k+1]].reshape(w.shape))

    return retval

def estimate_gradient(f, x, epsilon=1e-4, args=()):
  """Estimate the gradient for a given callable f

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

def estimate_gradient_for_machine(machine, X, cost, target):

  def func(weights):
    old = machine.weights
    machine.weights = machine.roll(weights)
    retval = cost.f(machine.forward(X), target).mean(axis=0).sum()
    machine.weights = old
    return retval

  weights = machine.unroll()
  est = estimate(func, weights)
  machine.weights = machine.roll(weights)

  return machine.roll(est) #format using the machine's organization
