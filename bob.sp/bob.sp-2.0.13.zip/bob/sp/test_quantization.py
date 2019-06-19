#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Ivana Chingovska <ivana.chingovska@idiap.ch>
# Thu Feb  7 20:02:48 CET 2013
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

# Tests blitz-based Quantization implementation

import numpy
from . import Quantization

def test_uint8():

  # Test quantization
  quant = Quantization('uint8')
  assert quant.num_levels == 256
  assert quant.max_level == 255
  assert quant.min_level == 0
  assert quant.quantization_type == "uniform"
  assert quant.quantization_level(5) == 5

def test_parameters_uint8():

  quant = Quantization('uint8', False, 4, 64, 192)
  assert quant.num_levels == 4
  assert quant.max_level == 192
  assert quant.min_level == 64
  assert (quant.quantization_table == numpy.array([64, 96, 128, 160])).all()
  img = numpy.array([[60, 95, 96], [127, 128, 129], [159, 160, 193]], dtype='uint8')
  res = quant(img)
  expected_res = numpy.array([[0, 0, 1], [1, 2, 2], [2, 3, 3]])
  assert (res == expected_res).all()

def test_uniform_uint16():

  quant = Quantization('uint16', False, 8)
  assert quant.num_levels == 8
  assert quant.max_level == 65535
  assert quant.min_level == 0
  img = numpy.array([8191, 8192, 16383, 16384], dtype='uint16')
  res = quant(img)
  assert (res == numpy.array([0,1,1,2])).all()

def test_table_uint8():

  quantization_table = numpy.array([50, 100, 150, 200, 250], dtype='uint8')
  quant = Quantization(quantization_table = quantization_table)
  assert quant.num_levels == 5
  assert quant.min_level == 50
  img = numpy.array([0, 50, 99, 100, 101, 250, 255], dtype='uint8')
  res = quant(img)
  assert (res == numpy.array([0,0,0,1,1,4,4])).all()

def test_uniform_rounding_uint8():

  quant = Quantization('uint8', True, 8)
  assert quant.num_levels == 8
  assert quant.max_level == 255
  assert quant.min_level == 0
  assert (quant.quantization_table == numpy.array([0,19,55,91,127,163,199, 235])).all()
