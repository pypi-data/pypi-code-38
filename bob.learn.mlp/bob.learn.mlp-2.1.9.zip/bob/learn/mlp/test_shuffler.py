#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 29 Apr 2014 16:16:33 CEST
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""All kinds of tests on the DataShuffler class
"""

import time
import numpy
import nose.tools

from . import DataShuffler

import bob.core.random

# Some data structures used for the tests
fixture = dict()
fixture['set1'] = []
fixture['data1'] = numpy.array([1, 0, 0], dtype='float64')
fixture['target1'] = numpy.array([1], dtype='float64')
fixture['set1'].append(fixture['data1'])
fixture['set1'].append(fixture['data1']*2)
fixture['set1'].append(fixture['data1']*3)
fixture['set1'] = numpy.array(fixture['set1'])

fixture['set2'] = []
fixture['data2'] = numpy.array([0, 1, 0], dtype='float64')
fixture['target2'] = numpy.array([2], dtype='float64')
fixture['set2'].append(fixture['data2'])
fixture['set2'].append(fixture['data2']*2)
fixture['set2'].append(fixture['data2']*3)
fixture['set2'] = numpy.array(fixture['set2'])

fixture['set3'] = []
fixture['data3'] = numpy.array([0, 0, 1], dtype='float64')
fixture['target3'] = numpy.array([3], dtype='float64')
fixture['set3'].append(fixture['data3'])
fixture['set3'].append(fixture['data3']*2)
fixture['set3'].append(fixture['data3']*3)
fixture['set3'] = numpy.array(fixture['set3'])

def test_initialization():

  # Test if we can correctly initialize the shuffler

  shuffle = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])

  nose.tools.eq_(shuffle.data_width, 3)
  nose.tools.eq_(shuffle.target_width, 1)

def test_initialization_with_arrays():

  # Test if we can initialize the shuffler with simple arrays
  data = [
      numpy.zeros((10,2), 'float64'),
      numpy.ones ((10,2), 'float64'),
      ]

  target = [
    numpy.array([+1,+1], 'float64'),
    numpy.array([-1,-1], 'float64'),
    ]

  shuffle = DataShuffler(data, target)
  nose.tools.eq_(shuffle.data_width, 2)
  nose.tools.eq_(shuffle.target_width, 2)

def test_drawing():

  # Tests that drawing works in a particular way

  N = 6 #multiple of number of classes

  shuffle = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])

  [data, target] = shuffle(N)

  nose.tools.eq_(data.shape, (N, shuffle.data_width))
  nose.tools.eq_(target.shape, (N, shuffle.target_width))

  # Finally, we also test if the data is well separated. We have to have 2
  # of each class since N is multiple of 9
  class1_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data1']) != 0])
  nose.tools.eq_(class1_count, 2)
  class2_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data2']) != 0])
  nose.tools.eq_(class2_count, 2)
  class3_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data3']) != 0])
  nose.tools.eq_(class3_count, 2)

  N = 28 #not multiple anymore

  [data, target] = shuffle(N)

  nose.tools.eq_(data.shape, (N, shuffle.data_width))
  nose.tools.eq_(target.shape, (N, shuffle.target_width))

  # Finally, we also test if the data is well separated. We have to have 2
  # of each class since N is multiple of 9
  class1_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data1']) != 0])
  nose.tools.eq_(class1_count, 10)
  class2_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data2']) != 0])
  nose.tools.eq_(class2_count, 9)
  class3_count = len([data[i,:] for i in range(N) \
      if numpy.dot(data[i,:], fixture['data3']) != 0])
  nose.tools.eq_(class3_count, 9)

def test_seeding():

  # Test if we can correctly set the seed and that this act is effective

  # First test that, by making two shufflers, we get different replies
  shuffle1 = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])
  shuffle2 = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])

  N = 100

  # This will use the current time as seed.
  [data1, target1] = shuffle1(N)
  time.sleep(0.1) # Sleeps 0.1 second to make sure we get different seeds
  [data2, target2] = shuffle2(N)

  assert not (data1 == data2).all()
  # Note targets will always be the same given N because of the internal
  # design of the C++ DataShuffler.

  # Now show that by drawing twice does not get the same replies!
  # This indicates that the internal random generator is updated at each draw
  # as one expects.
  [data1_2, target1_2] = shuffle1(N)

  assert not (data1 == data1_2).all()

  # Finally show that, by setting the seed, we can get the same results
  shuffle1 = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])
  shuffle2 = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])

  # Use the same seed for 2 different random number generators
  rng1 = bob.core.random.mt19937(32)
  rng2 = bob.core.random.mt19937(32)

  [data1, target1] = shuffle1(N, rng=rng1)
  [data2, target2] = shuffle2(N, rng=rng2)

  assert (data1 == data2).all()

def test_normalization():

  # Tests that the shuffler can get the std. normalization right
  # Compares results to numpy
  shuffle = DataShuffler([fixture['set1'], fixture['set2'], fixture['set3']],
      [fixture['target1'], fixture['target2'], fixture['target3']])

  npy = numpy.array([[1,0,0], [2,0,0], [3,0,0],
    [0,1,0], [0,2,0], [0,3,0],
    [0,0,1], [0,0,2], [0,0,3]], 'float64')
  precalc_mean = numpy.array(numpy.mean(npy,0))
  precalc_stddev = numpy.array(numpy.std(npy,0, ddof=1))
  [mean, stddev] = shuffle.stdnorm()

  assert (mean == precalc_mean).all()
  assert (stddev == precalc_stddev).all()

  # Now we set the stdnorm flag on and expect data
  assert not shuffle.auto_stdnorm
  shuffle.auto_stdnorm = True
  assert shuffle.auto_stdnorm

  [data, target] = shuffle(10000)

  # Makes sure the data is approximately zero mean and has std.dev. ~ 1
  # Note: Results will not be of a better precision because we only have 9
  # samples in the Shuffler...
  nose.tools.eq_(round(data.mean()), 0)
  nose.tools.eq_(round(numpy.std(data, ddof=1)), 1)

def test_normalization_big():

  rng = bob.core.random.mt19937()

  set1 = []
  draw25 = bob.core.random.normal(mean=2.0, sigma=5.0, dtype=float)
  for i in range(10000):
    set1.append(numpy.array([draw25(rng)], dtype='float64'))
  set1 = numpy.array(set1)
  target1 = numpy.array([1], dtype='float64')

  set2 = []
  draw32 = bob.core.random.normal(mean=3.0, sigma=2.0, dtype=float)
  for i in range(10000):
    set2.append(numpy.array([draw32(rng)], dtype='float64'))
  set2 = numpy.array(set2)
  target2 = numpy.array([2], dtype='float64')

  shuffle = DataShuffler([set1, set2], [target1, target2])
  shuffle.auto_stdnorm = True
  prev_mean, prev_stddev = shuffle.stdnorm()

  [data, target] = shuffle(200000)
  assert abs(data.mean()) < 1e-1
  assert abs(numpy.std(data, ddof=1) - 1.0) < 1e-1

  #note that resetting auto_stdnorm will make the whole go back to normal,
  #but the std normalization values remain the same...
  shuffle.auto_stdnorm = False
  back_mean, back_stddev = shuffle.stdnorm()
  assert abs(back_mean   - prev_mean).sum() < 1e-1
  assert abs(back_stddev - prev_stddev).sum() < 1e-10
