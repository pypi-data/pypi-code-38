#!/usr/bin/env python
# encoding: utf-8

'''Test units for bob.ip.facelandmarks'''

import os
import numpy
import nose.tools
import pkg_resources

import bob.io.base
import bob.io.base.test_utils

from .utils import detect_landmarks, draw_landmarks, save_landmarks, Result
from .utils import detect_landmarks_on_boundingbox
from .script.detect_landmarks import main as app


F = lambda n: pkg_resources.resource_filename(__name__, os.path.join('data', n))


def test_lena():
  data = bob.io.base.load(F('lena.jpg'))
  result = detect_landmarks(data, 1)
  nose.tools.eq_(len(result), 1)
  draw_landmarks(data, result)


def test_lena_on_boundingbox():
  data = bob.io.base.load(F('lena.jpg'))
  result = detect_landmarks(data, 1)
  nose.tools.eq_(len(result), 1)
  points = detect_landmarks_on_boundingbox(data, result[0].bounding_box)
  assert (numpy.abs(points-result[0].landmarks) <= 0.00001).all()


def test_multiple():
  data = bob.io.base.load(F('multiple-faces.jpg'))
  result = detect_landmarks(data, 5)
  nose.tools.eq_(len(result), 5)
  draw_landmarks(data, result)


def test_app_lena_outputting_image():
  image = F('lena.jpg')
  output = bob.io.base.test_utils.temporary_filename(prefix="bobtest_",
      suffix='.png')
  status = app(['-n1', image, output])
  nose.tools.eq_(status, 0)


def test_app_multiple_outputting_image():
  image = F('multiple-faces.jpg')
  output = bob.io.base.test_utils.temporary_filename(prefix="bobtest_",
      suffix='.png')
  status = app(['-n5', image, output])
  nose.tools.eq_(status, 0)
  assert os.path.exists(output)
  os.remove(output)


def test_app_lena_outputting_image():
  image = F('lena.jpg')
  output = bob.io.base.test_utils.temporary_filename(prefix="bobtest_",
      suffix='.png')
  status = app(['-n1', image, output])
  nose.tools.eq_(status, 0)
  assert os.path.exists(output)
  os.remove(output)


def test_app_lena_outputting_hdf5():
  image = F('lena.jpg')
  output = bob.io.base.test_utils.temporary_filename(prefix="bobtest_",
      suffix='.hdf5')
  status = app(['-n1', image, output])
  nose.tools.eq_(status, 0)
  assert os.path.exists(output)

  tf = bob.io.base.HDF5File(output)
  assert tf.has_dataset('menpo_landmarks68')
  lm = tf.read('menpo_landmarks68')
  nose.tools.eq_(lm.shape, (68,2))
  nose.tools.eq_(lm.dtype, numpy.float64)
  assert tf.has_group('face_detector')
  assert tf.has_key('/face_detector/quality')
  nose.tools.eq_(tf.read('/face_detector/quality').dtype, numpy.float64)
  nose.tools.eq_(tf.read('/face_detector/quality').shape, tuple())
  assert tf.has_key('/face_detector/topleft_y')
  nose.tools.eq_(tf.read('/face_detector/topleft_y').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/topleft_y').shape, tuple())
  assert tf.has_key('/face_detector/topleft_x')
  nose.tools.eq_(tf.read('/face_detector/topleft_x').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/topleft_x').shape, tuple())
  assert tf.has_key('/face_detector/height')
  nose.tools.eq_(tf.read('/face_detector/height').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/height').shape, tuple())
  assert tf.has_key('/face_detector/width')
  nose.tools.eq_(tf.read('/face_detector/width').shape, tuple())
  nose.tools.eq_(tf.read('/face_detector/width').dtype, numpy.int32)
  os.remove(output)


def test_app_multiple_outputting_hdf5():
  image = F('lena.jpg')
  output = bob.io.base.test_utils.temporary_filename(prefix="bobtest_",
      suffix='.hdf5')
  status = app(['-n5', image, output])
  nose.tools.eq_(status, 0)
  assert os.path.exists(output)

  tf = bob.io.base.HDF5File(output)
  assert tf.has_dataset('menpo_landmarks68')
  lm = tf.read('menpo_landmarks68')
  nose.tools.eq_(lm.shape, (5,68,2))
  nose.tools.eq_(lm.dtype, numpy.float64)
  assert tf.has_group('face_detector')
  assert tf.has_key('/face_detector/quality')
  nose.tools.eq_(tf.read('/face_detector/quality').dtype, numpy.float64)
  nose.tools.eq_(tf.read('/face_detector/quality').shape, (5,))
  assert tf.has_key('/face_detector/topleft_y')
  nose.tools.eq_(tf.read('/face_detector/topleft_y').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/topleft_y').shape, (5,))
  assert tf.has_key('/face_detector/topleft_x')
  nose.tools.eq_(tf.read('/face_detector/topleft_x').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/topleft_x').shape, (5,))
  assert tf.has_key('/face_detector/height')
  nose.tools.eq_(tf.read('/face_detector/height').dtype, numpy.int32)
  nose.tools.eq_(tf.read('/face_detector/height').shape, (5,))
  assert tf.has_key('/face_detector/width')
  nose.tools.eq_(tf.read('/face_detector/width').shape, (5,))
  nose.tools.eq_(tf.read('/face_detector/width').dtype, numpy.int32)
  os.remove(output)
