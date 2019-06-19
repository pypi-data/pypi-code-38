#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 28 Apr 2014 13:32:55 CEST
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Tests on the Machine infrastructure.
"""

import time
import numpy
import nose.tools

from . import Machine
from .test_utils import Machine as PythonMachine

import bob.io.base
from bob.io.base.test_utils import temporary_filename
from bob.learn.activation import Logistic, HyperbolicTangent
from bob.core.random import mt19937

def test_2in_1out():

  m = Machine((2,1))
  nose.tools.eq_(m.shape, (2,1))
  nose.tools.eq_(m.input_divide.shape, (2,))
  nose.tools.eq_(m.input_subtract.shape, (2,))
  nose.tools.eq_(len(m.weights), 1)
  nose.tools.eq_(m.weights[0].shape, (2,1))
  assert numpy.allclose(m.weights[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(len(m.biases), 1)
  nose.tools.eq_(m.biases[0].shape, (1,))
  nose.tools.eq_(m.biases[0], 0.)
  nose.tools.eq_(m.hidden_activation, HyperbolicTangent())
  nose.tools.eq_(m.output_activation, HyperbolicTangent())

  # calculate and match
  weights = [numpy.random.rand(2,1)]
  biases = [numpy.random.rand(1)]

  m.weights = weights
  m.biases = biases

  pymac = PythonMachine(biases, weights, m.hidden_activation, m.output_activation)

  X = numpy.random.rand(10,2)
  assert numpy.allclose(m(X), pymac.forward(X), rtol=1e-10, atol=1e-15)

def test_2in_3_1out():

  m = Machine((2,3,1))
  nose.tools.eq_(m.shape, (2,3,1))
  nose.tools.eq_(m.input_divide.shape, (2,))
  nose.tools.eq_(m.input_subtract.shape, (2,))
  nose.tools.eq_(len(m.weights), 2)
  nose.tools.eq_(m.weights[0].shape, (2,3))
  assert numpy.allclose(m.weights[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.weights[1].shape, (3,1))
  assert numpy.allclose(m.weights[1], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(len(m.biases), 2)
  nose.tools.eq_(m.biases[0].shape, (3,))
  assert numpy.allclose(m.biases[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.biases[1].shape, (1,))
  assert numpy.allclose(m.biases[1], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.hidden_activation, HyperbolicTangent())
  nose.tools.eq_(m.output_activation, HyperbolicTangent())

  # calculate and match
  weights = [numpy.random.rand(2,3), numpy.random.rand(3,1)]
  biases = [numpy.random.rand(3), numpy.random.rand(1)]

  m.weights = weights
  m.biases = biases

  pymac = PythonMachine(biases, weights, m.hidden_activation, m.output_activation)

  X = numpy.random.rand(10,2)
  assert numpy.allclose(m(X), pymac.forward(X), rtol=1e-10, atol=1e-15)

def test_2in_3_5_1out():

  m = Machine((2,3,5,1))
  nose.tools.eq_(m.shape, (2,3,5,1))
  nose.tools.eq_(m.input_divide.shape, (2,))
  nose.tools.eq_(m.input_subtract.shape, (2,))
  nose.tools.eq_(len(m.weights), 3)
  nose.tools.eq_(m.weights[0].shape, (2,3))
  assert numpy.allclose(m.weights[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.weights[1].shape, (3,5))
  assert numpy.allclose(m.weights[1], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.weights[2].shape, (5,1))
  assert numpy.allclose(m.weights[2], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(len(m.biases), 3)
  nose.tools.eq_(m.biases[0].shape, (3,))
  assert numpy.allclose(m.biases[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.biases[1].shape, (5,))
  assert numpy.allclose(m.biases[1], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.biases[2].shape, (1,))
  assert numpy.allclose(m.biases[2], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(m.hidden_activation, HyperbolicTangent())
  nose.tools.eq_(m.output_activation, HyperbolicTangent())

  # calculate and match
  weights = [
      numpy.random.rand(2,3),
      numpy.random.rand(3,5),
      numpy.random.rand(5,1)
      ]
  biases = [
      numpy.random.rand(3),
      numpy.random.rand(5),
      numpy.random.rand(1),
      ]

  m.weights = weights
  m.biases = biases

  pymac = PythonMachine(biases, weights, m.hidden_activation, m.output_activation)

  X = numpy.random.rand(10,2)
  assert numpy.allclose(m(X), pymac.forward(X), rtol=1e-10, atol=1e-15)

def test_100in_100_10_4out():

  m = Machine((100,100,10,4))

  # calculate and match
  weights = [
      numpy.random.rand(100,100),
      numpy.random.rand(100,10),
      numpy.random.rand(10,4)
      ]
  biases = [
      numpy.random.rand(100),
      numpy.random.rand(10),
      numpy.random.rand(4),
      ]

  m.weights = weights
  m.biases = biases

  pymac = PythonMachine(biases, weights, m.hidden_activation, m.output_activation)

  X = numpy.random.rand(20,100)
  assert numpy.allclose(m(X), pymac.forward(X), rtol=1e-10, atol=1e-15)

def test_resize():

  m = Machine((2,3,5,1))
  m.shape = (2,1)
  m.hidden_activation = Logistic()
  m.output_activation = Logistic()

  nose.tools.eq_(m.shape, (2,1))
  nose.tools.eq_(m.input_divide.shape, (2,))
  nose.tools.eq_(m.input_subtract.shape, (2,))
  nose.tools.eq_(len(m.weights), 1)
  nose.tools.eq_(m.weights[0].shape, (2,1))
  assert numpy.allclose(m.weights[0], 0., rtol=1e-10, atol=1e-15)
  nose.tools.eq_(len(m.biases), 1)
  nose.tools.eq_(m.biases[0].shape, (1,))
  nose.tools.eq_(m.biases[0], 0.)
  nose.tools.eq_(m.hidden_activation, Logistic())
  nose.tools.eq_(m.output_activation, Logistic())

  # calculate and match
  weights = [numpy.random.rand(2,1)]
  biases = [numpy.random.rand(1)]

  m.weights = weights
  m.biases = biases

  pymac = PythonMachine(biases, weights, m.hidden_activation, m.output_activation)

  X = numpy.random.rand(10,2)
  assert numpy.allclose(m(X), pymac.forward(X), rtol=1e-10, atol=1e-15)

  # check that the input subtract and input_divide can be set
  m.input_subtract = 4
  assert (m.input_subtract == 4).all()
  m.input_divide = 2
  assert (m.input_divide == 2).all()
  m.input_subtract = numpy.arange(2.)
  assert m.input_subtract[0] == 0
  assert m.input_subtract[1] == 1
  m.input_divide = numpy.arange(2.)+1
  assert m.input_divide[0] == 1
  assert m.input_divide[1] == 2

def test_checks():

  # tests if Machines check wrong settings
  m = Machine((2,1))

  # the Machine shape cannot have a single entry
  nose.tools.assert_raises(RuntimeError, setattr, m, 'shape', (5,))

  # you cannot set the weights vector with the wrong size
  nose.tools.assert_raises(RuntimeError,
      setattr, m, 'weights', [numpy.zeros((3,1), 'float64')])

  # the same for the bias
  nose.tools.assert_raises(RuntimeError,
      setattr, m, 'biases', [numpy.zeros((5,), 'float64')])

  # it works though if the sizes are correct
  new_weights = [numpy.zeros((2,1), 'float64')]
  new_weights[0].fill(3.14)
  m.weights = new_weights

  nose.tools.eq_(len(m.weights), 1)

  assert (m.weights[0] == new_weights[0]).all()

  new_biases = [numpy.zeros((1,), 'float64')]
  new_biases[0].fill(5.71)
  m.biases = new_biases

  nose.tools.eq_(len(m.biases), 1)

  assert (m.biases[0] == new_biases[0]).all()

def test_persistence():

  # make shure we can save an load an Machine machine
  weights = []
  weights.append(numpy.array([[.2, -.1, .2], [.2, .3, .9]]))
  weights.append(numpy.array([[.1, .5], [-.1, .2], [-.1, 1.1]]))
  biases = []
  biases.append(numpy.array([-.1, .3, .1]))
  biases.append(numpy.array([.2, -.1]))

  m = Machine((2,3,2))
  m.weights = weights
  m.biases = biases

  # creates a file that will be used in the next test!
  machine_file = temporary_filename()
  m.save(bob.io.base.HDF5File(machine_file, 'w'))
  m2 = Machine(bob.io.base.HDF5File(machine_file))

  assert m.is_similar_to(m2)
  nose.tools.eq_(m, m2)
  nose.tools.eq_(m.shape, m2.shape)
  assert (m.input_subtract == m2.input_subtract).all()
  assert (m.input_divide == m2.input_divide).all()

  for i in range(len(m.weights)):
    assert (m.weights[i] == m2.weights[i]).all()
    assert (m.biases[i] == m2.biases[i]).all()

def test_randomization():

  m = Machine((2,3,2))
  m.randomize()

  for k in m.weights:
    assert (abs(k) <= 0.1).all()
    assert (k != 0).any()

  for k in m.biases:
    assert (abs(k) <= 0.1).all()
    assert (k != 0).any()

def test_randomization_margins():

  # we can also reset the margins for randomization
  for k in range(10):

    m = Machine((2,3,2))
    m.randomize(-0.001, 0.001)

    for k in m.weights:
      assert (abs(k) <= 0.001).all()
      assert (k != 0).any()

    for k in m.biases:
      assert (abs(k) <= 0.001).all()
      assert (k != 0).any()

def test_randomness_different():

  m1 = Machine((2,3,2))
  m1.randomize()

  for k in range(3):
    time.sleep(0.1)
    m2 = Machine((2,3,2))
    m2.randomize()

    for w1, w2 in zip(m1.weights, m2.weights):
      assert not (w1 == w2).all()

    for b1, b2 in zip(m1.biases, m2.biases):
      assert not (b1 == b2).all()

def test_randomness_same():

  m1 = Machine((2,3,2))
  rng = bob.core.random.mt19937(0) #fixed seed
  m1.randomize(rng=rng)

  for k in range(3):
    time.sleep(0.1)

    m2 = Machine((2,3,2))
    rng = bob.core.random.mt19937(0) #fixed seed
    m2.randomize(rng=rng)

    for w1, w2 in zip(m1.weights, m2.weights):
      assert (w1 == w2).all()

    for b1, b2 in zip(m1.biases, m2.biases):
      assert (b1 == b2).all()

def test_write():
  m = Machine((1,1,1))
  assert str(m) ==  "<bob.learn.mlp.Machine @(1, 1, 1) [act: f(z) = tanh(z)]>"
 
  
  
  
  
