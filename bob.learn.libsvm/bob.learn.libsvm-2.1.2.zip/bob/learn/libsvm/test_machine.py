#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Sat Dec 17 14:41:56 2011 +0100
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""Run tests on the libsvm machine infrastructure.
"""

import os
import numpy
import tempfile
import pkg_resources
import nose.tools
import bob.io.base

from . import File, Machine

def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

def tempname(suffix, prefix='bobtest_machine_'):
  (fd, name) = tempfile.mkstemp(suffix, prefix)
  os.close(fd)
  os.unlink(name)
  return name

TEST_MACHINE_NO_PROBS = F('heart_no_probs.svmmodel')

HEART_DATA = F('heart.svmdata') #13 inputs
HEART_MACHINE = F('heart.svmmodel') #supports probabilities
HEART_EXPECTED = F('heart.out') #expected probabilities

IRIS_DATA = F('iris.svmdata')
IRIS_MACHINE = F('iris.svmmodel')
IRIS_EXPECTED = F('iris.out') #expected probabilities

def load_expected(filename):
  """Loads libsvm's svm-predict output file with probabilities"""

  all_labels = sorted([int(k) for k in open(filename).readline().split()[1:]])
  data = numpy.loadtxt(filename, dtype='float64', skiprows=1)
  return all_labels, data[:,0].astype('int64'), data[:,1:]

#extracted by running svm-predict.c on the heart_scale example data
expected_heart_predictions = (1, -1, -1, 1, -1, -1, 1, 1, 1, 1, 1, 1, -1, -1,
    -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, -1, 1, 1,
    1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, 1, 1, -1, -1, -1, -1,
    -1, 1, -1, -1, 1, -1, 1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1,
    1, 1, -1, -1, -1, 1, 1, 1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1, 1,
    -1, 1, -1, -1, -1, -1, -1, 1, 1, 1, -1, 1, 1, -1, 1, -1, -1, -1, -1, -1, 1,
    1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1, -1, 1, 1, 1, -1, 1, 1, -1, -1, 1, -1,
    1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, -1, 1,
    -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1,
    -1, 1, 1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, -1,
    1, 1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, -1, -1, -1, 1, 1, -1, 1, 1,
    -1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, -1,
    1, -1, 1, 1, -1, -1, 1, 1, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1,
    -1, -1, -1, -1, -1, -1, 1)

expected_iris_predictions = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3,  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3, 3)

def test_can_load():

  machine = Machine(HEART_MACHINE)
  nose.tools.eq_(machine.shape, (13,1))
  nose.tools.eq_(machine.n_support_vectors, [64,68])
  nose.tools.eq_(machine.kernel_type, 'RBF')
  nose.tools.eq_(machine.machine_type, 'C_SVC')
  nose.tools.eq_(len(machine.labels), 2)
  assert -1 in machine.labels
  assert +1 in machine.labels
  assert abs(machine.gamma - 0.0769231) < 1e-6
  assert type(machine.__repr__()) is str

def test_can_save():

  machine = Machine(HEART_MACHINE)
  tmp = tempname('.model')
  machine.save(tmp)
  del machine

  # make sure that the save machine is the same as before
  machine = Machine(tmp)
  nose.tools.eq_(machine.shape, (13,1))
  nose.tools.eq_(machine.n_support_vectors, [64,68])
  nose.tools.eq_(machine.kernel_type, 'RBF')
  nose.tools.eq_(machine.machine_type, 'C_SVC')
  nose.tools.eq_(len(machine.labels), 2)
  assert -1 in machine.labels
  assert +1 in machine.labels
  assert abs(machine.gamma - 0.0769231) < 1e-6

  os.unlink(tmp)

def run_for_extension(ext):

  machine = Machine(HEART_MACHINE)
  tmp = tempname(ext)
  machine.save(bob.io.base.HDF5File(tmp, 'w'))
  del machine

  # make sure that the save machine is the same as before
  machine = Machine(bob.io.base.HDF5File(tmp))
  nose.tools.eq_(machine.shape, (13,1))
  nose.tools.eq_(machine.n_support_vectors, [64,68])
  nose.tools.eq_(machine.kernel_type, 'RBF')
  nose.tools.eq_(machine.machine_type, 'C_SVC')
  nose.tools.eq_(len(machine.labels), 2)
  assert -1 in machine.labels
  assert +1 in machine.labels
  assert abs(machine.gamma - 0.0769231) < 1e-6
  assert numpy.all(abs(machine.input_subtract - 0) < 1e-10)
  assert numpy.all(abs(machine.input_divide - 1) < 1e-10)

  os.unlink(tmp)

def test_can_save_arbitrary():
  run_for_extension('.arbitrary')

def test_can_save_h5():
  run_for_extension('.h5')

def test_can_save_hdf5():
  run_for_extension('.hdf5')

def test_data_loading():

  #tests if I can load data in libsvm format using SVMFile
  data = File(HEART_DATA)
  nose.tools.eq_(data.shape, (13,))
  nose.tools.eq_(data.good(), True)
  nose.tools.eq_(data.fail(), False)
  nose.tools.eq_(data.eof(), False)


  #tries loading the data, one by one
  all_data = []
  all_labels = []
  while data.good():
    entry = data.read()
    if entry is not None:
      all_labels.append(entry[0])
      all_data.append(entry[1])

  nose.tools.eq_(len(all_data), len(all_labels))
  nose.tools.eq_(len(all_data), 270)

  #tries loading the data with numpy arrays allocated internally
  counter = 0
  data.reset()
  entry = data.read()
  while entry:
    nose.tools.eq_( entry[0], all_labels[counter] )
    assert numpy.array_equal(entry[1], all_data[counter])
    counter += 1
    entry = data.read()


  #tries loading the file all in a single shot
  data.reset()
  labels, data = data.read_all()

  assert numpy.array_equal(labels, all_labels)
  for k, l in zip(data, all_data):
    assert numpy.array_equal(k, l)




  #makes sure the first 3 examples are correctly read
  ex = []
  ex.append(numpy.array([0.708333 , 1, 1, -0.320755 , -0.105023 , -1, 1,
    -0.419847 ,-1, -0.225806 ,0. ,1, -1], 'float64'))
  ex.append(numpy.array([0.583333, -1, 0.333333, -0.603774, 1, -1, 1,
    0.358779, -1, -0.483871, 0., -1, 1], 'float64'))
  ex.append(numpy.array([0.166667, 1, -0.333333, -0.433962, -0.383562, -1,
    -1, 0.0687023, -1, -0.903226, -1, -1, 1], 'float64'))
  ls = [+1, -1, +1]

  for k, (l, e) in enumerate(zip(ls, ex)):
    nose.tools.eq_( l, labels[k] )
    assert numpy.array_equal(e, data[k])


@nose.tools.raises(RuntimeError)
def test_raises():

  #tests that the normal machine raises because probabilities are not
  #supported on that model
  machine = Machine(TEST_MACHINE_NO_PROBS)
  labels, data = File(HEART_DATA).read_all()
  machine.predict_class_and_probabilities(data)

def test_correctness_heart():

  #tests the correctness of the libSVM bindings
  machine = Machine(HEART_MACHINE)
  labels, data = File(HEART_DATA).read_all()
  pred_label = machine.predict_class(data)

  assert numpy.array_equal(pred_label, expected_heart_predictions)

  #finally, we test if the values also work fine.
  pred_lab_values = [machine.predict_class_and_scores(k) for k in data]

  #tries the variant with multiple inputs
  pred_labels2, pred_scores2 = machine.predict_class_and_scores(data)
  assert numpy.array_equal(expected_heart_predictions,  pred_labels2)
  assert numpy.array_equal(tuple([k[1] for k in pred_lab_values]), pred_scores2)

  #tries to get the probabilities - note: for some reason, when getting
  #probabilities, the labels change, but notice the note bellow:

  # Note from the libSVM FAQ:
  # Q: Why using the -b option does not give me better accuracy?
  # There is absolutely no reason the probability outputs guarantee you
  # better accuracy. The main purpose of this option is to provide you the
  # probability estimates, but not to boost prediction accuracy. From our
  # experience, after proper parameter selections, in general with and
  # without -b have similar accuracy. Occasionally there are some
  # differences. It is not recommended to compare the two under just a fixed
  # parameter set as more differences will be observed.
  all_labels, real_labels, real_probs = load_expected(HEART_EXPECTED)

  pred_labels, pred_probs = machine.predict_class_and_probabilities(data)
  assert numpy.array_equal(pred_labels, real_labels)
  assert numpy.all(abs(pred_probs - real_probs) < 1e-2), abs(pred_probs - real_probs)

def test_correctness_iris():

  #same test as above, but with a 3-class problem.
  machine = Machine(IRIS_MACHINE)
  labels, data = File(IRIS_DATA).read_all()
  pred_label = machine.predict_class(data)

  assert numpy.array_equal(pred_label, expected_iris_predictions)

  #finally, we test if the values also work fine.
  pred_lab_values = [machine.predict_class_and_scores(k) for k in data]

  #tries the variant with multiple inputs
  pred_labels2, pred_scores2 = machine.predict_class_and_scores(data)
  assert numpy.array_equal(expected_iris_predictions,  pred_labels2)
  assert numpy.all(abs(numpy.vstack([k[1] for k in
    pred_lab_values]) - numpy.vstack(pred_scores2)) < 1e-20 )

  #tries to get the probabilities - note: for some reason, when getting
  #probabilities, the labels change, but notice the note bellow:

  all_labels, real_labels, real_probs = load_expected(IRIS_EXPECTED)

  pred_labels, pred_probs = machine.predict_class_and_probabilities(data)
  assert numpy.array_equal(pred_labels, real_labels)
  assert numpy.all(abs(numpy.vstack(pred_probs) - numpy.vstack(real_probs)) < 1e-6)


@nose.tools.raises(RuntimeError)
def test_correctness_inputsize_exceeds():

  #same test as above, but test for excess input
  machine = Machine(IRIS_MACHINE)
  labels, data = File(IRIS_DATA).read_all()

  # add extra columns to the input data
  data = numpy.hstack([data, numpy.ones((data.shape[0], 2), dtype=float)])

  pred_label = machine.predict_class(data)
