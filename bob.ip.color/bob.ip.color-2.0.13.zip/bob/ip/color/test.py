#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri  4 Apr 15:33:36 2014 CEST
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Test color conversions available in color
"""

import os
import platform
import numpy
import colorsys
import pkg_resources
import nose.tools
import bob.io.base

from . import *

def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

@nose.tools.raises(NotImplementedError)
def test_int_raises():

  r = rgb_to_yuv(3, 4, 5)

@nose.tools.raises(NotImplementedError)
def test_int_raises_gray():

  r = rgb_to_gray(3, 4, 5)

@nose.tools.raises(NotImplementedError)
def test_string_raises():

  r = rgb_to_hsl("3", "4", "5")

@nose.tools.raises(NotImplementedError)
def test_string_raises_gray():

  r = rgb_to_gray("3", "4", "5")


def test_gray():

  # This test verifies that gray-scale conversion works in both directions, for both images and numbers
  gray_image = numpy.random.random((30,30))
  color_image = bob.ip.color.gray_to_rgb(gray_image)

  new_gray_image = bob.ip.color.rgb_to_gray(color_image)
  assert numpy.allclose(gray_image, new_gray_image)

  for y in range(30):
    for x in range(30):
      r, g, b = bob.ip.color.gray_to_rgb(gray_image[y,x])
      gray = bob.ip.color.rgb_to_gray(r, g, b)

      assert abs(gray - gray_image[y,x]) < 1e-6


def test_hsv():

  # This test verifies that color conversion is reversible for HSV <=> RGB
  # It also shows how you can convert single pixel representations from RGB
  # to HSV and vice-versa, testing the output of bob color converters
  # against python's.

  step = 0.02
  for r in numpy.arange(0, 1+step, step):
    for g in numpy.arange(0, 1+step, step):
      for b in numpy.arange(0, 1+step, step):
        # First test the correctness
        ht, st, vt = rgb_to_hsv(r, g, b)
        hp, sp, vp = colorsys.rgb_to_hsv(r, g, b)
        assert abs(ht - hp) < 1e-6
        assert abs(st - sp) < 1e-6
        assert abs(vt - vp) < 1e-6
        # And that we can invert the result using bob
        r2, g2, b2 = hsv_to_rgb(ht, st, vt)
        assert abs(r2 - r) < 1e-6
        assert abs(g2 - g) < 1e-6
        assert abs(b2 - b) < 1e-6

  v0 = 1e-10
  v1 = 1. - v0
  l = [v0, v1]
  for r in l:
    for g in l:
      for b in l:
        # First test the correctness
        ht, st, vt = rgb_to_hsv(r, g, b)
        hp, sp, vp = colorsys.rgb_to_hsv(r, g, b)
        assert abs(ht - hp) < 1e-6
        assert abs(st - sp) < 1e-6
        assert abs(vt - vp) < 1e-6
        # And that we can invert the result using bob
        r2, g2, b2 = hsv_to_rgb(ht, st, vt)
        assert abs(r2 - r) < 1e-6
        assert abs(g2 - g) < 1e-6
        assert abs(b2 - b) < 1e-6

def test_hsl():

  # This test verifies that color conversion is reversible for HSL <=> RGB
  # It also shows how you can convert single pixel representations from RGB
  # to HSL and vice-versa, testing the output of bob color converters
  # against python's.

  step = 0.02
  for r in numpy.arange(0, 1+step, step):
    for g in numpy.arange(0, 1+step, step):
      for b in numpy.arange(0, 1+step, step):
        # First test the correctness
        ht, st, lt = rgb_to_hsl(r, g, b)
        hp, lp, sp = colorsys.rgb_to_hls(r, g, b)
        assert abs(ht - hp) < 1e-6
        assert abs(st - sp) < 1e-6
        assert abs(lt - lp) < 1e-6
        # And that we can invert the result using bob
        r2, g2, b2 = hsl_to_rgb(ht, st, lt)
        assert abs(r2 - r) < 1e-6
        assert abs(g2 - g) < 1e-6
        assert abs(b2 - b) < 1e-6

  v0 = 1e-10
  v1 = 1. - v0
  l = [v0, v1]
  for r in l:
    for g in l:
      for b in l:
        # First test the correctness
        ht, st, lt = rgb_to_hsl(r, g, b)
        hp, lp, sp = colorsys.rgb_to_hls(r, g, b)
        assert abs(ht - hp) < 1e-6
        assert abs(st - sp) < 1e-6
        assert abs(lt - lp) < 1e-6
        # And that we can invert the result using bob
        r2, g2, b2 = hsl_to_rgb(ht, st, lt)
        assert abs(r2 - r) < 1e-6
        assert abs(g2 - g) < 1e-6
        assert abs(b2 - b) < 1e-6

def test_yuv():

  # This test verifies that color conversion is reversible for YUV <=> RGB
  # It also shows how you can convert single pixel representations from RGB
  # to YUV and vice-versa.

  step = 0.02
  for r in numpy.arange(0, 1+step, step):
    for g in numpy.arange(0, 1+step, step):
      for b in numpy.arange(0, 1+step, step):
        # First test the correctness
        yt, ut, vt = rgb_to_yuv(r, g, b)
        # And that we can invert the result using bob
        r2, g2, b2 = yuv_to_rgb(yt, ut, vt)
        assert abs(r2 - r) < 1e-4
        assert abs(g2 - g) < 1e-4
        assert abs(b2 - b) < 1e-4

def test_int_conversions():

  # You can also use integer based conversions in which case the ranges
  # should occupy the whole valid range for the type. We support unsigned
  # integers with 8 (uint8_t) or 16 bits (uint16_t). The ranges are 0 to 255
  # for 8-bit unsigned integers and 0 to 65535 for 16-bit unsigned ones. '0'
  # represents total black while the maximum value, total white. Internally,
  # bob converts the integers into float representations and calculate the
  # the conversions just like in tests 01 to 03 above. The last step is a
  # back conversion into integer scale. This procedure may lead differences
  # in the representations and the two-way conversion.

  # Just test a subrange or the test will take too long

  # Expected errors
  #
  # OSX 10.6 |    HSV     |    HSL     |    YUV
  # ---------+------------+------------+-------------
  # uint8_t  | (3) 1.18%  | (4) 1.57%  | (1) 0.39%
  # uint16_t | (3) 0.005% | (4) 0.006% | (1) 0.006%

  u8 = numpy.uint8
  mx = 2
  for r in list(range(0,5)) + list(range(120,130)) + list(range(253,256)):
    for g in list(range(0,6)) + list(range(125,135)) + list(range(252,256)):
      for b in list(range(0,7)) + list(range(127,137)) + list(range(252,256)):
        yt, ut, vt = rgb_to_yuv(u8(r), u8(g), u8(b))
        r2, g2, b2 = yuv_to_rgb(u8(yt), u8(ut), u8(vt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #correct within a 2% margin
        #if mx2 > mx and (mx2/255.) < 0.02: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("uint8_t RGB/YCbCr/RGB error: %d (%.2f%%)" % (mx, 100*mx/255.))

  mx = 4
  for r in list(range(0,5)) + list(range(120,130)) + list(range(253,256)):
    for g in list(range(0,6)) + list(range(125,135)) + list(range(252,256)):
      for b in list(range(0,7)) + list(range(127,137)) + list(range(252,256)):
        ht, st, vt = rgb_to_hsv(u8(r), u8(g), u8(b))
        r2, g2, b2 = hsv_to_rgb(u8(ht), u8(st), u8(vt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #correct within a 2% margin
        #if mx2 > mx and (mx2/255.) < 0.02: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("uint8_t RGB/HSV/RGB error: %d (%.2f%%)" % (mx, 100*mx/255.))

  mx = 5
  for r in list(range(0,5)) + list(range(120,130)) + list(range(253,256)):
    for g in list(range(0,6)) + list(range(125,135)) + list(range(252,256)):
      for b in list(range(0,7)) + list(range(127,137)) + list(range(252,256)):
        ht, st, lt = rgb_to_hsl(u8(r), u8(g), u8(b))
        r2, g2, b2 = hsl_to_rgb(u8(ht), u8(st), u8(lt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #correct within a 2% margin
        #if mx2 > mx and (mx2/255.) < 0.02: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("uint8_t RGB/HSL/RGB error: %d (%.2f%%)" % (mx, 100*mx/255.))

  # Just test a subrange or the test will take too long
  u16 = numpy.uint16
  mx = 4
  for r in list(range(0,10)) + list(range(120,130)) + list(range(250,256)):
    for g in list(range(5,12)) + list(range(125,135)) + list(range(240,252)):
      for b in list(range(7,15)) + list(range(127,137)) + list(range(235,251)):
        yt, ut, vt = rgb_to_yuv(u16(r), u16(g), u16(b))
        r2, g2, b2 = yuv_to_rgb(u16(yt), u16(ut), u16(vt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #if mx2 > mx and (mx2/65535.) < 0.0001: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("16-bit unsigned integer RGB/YCbCr/RGB error: %d (%.4f%%)" % (mx, 100*mx/65535.))

  mx = 3
  for r in list(range(0,5)) + list(range(30000,30005)) + list(range(65530,65536)):
    for g in list(range(0,6)) + list(range(30002,3007)) + list(range(65525,65532)):
      for b in list(range(0,7)) + list(range(3003,3008)) + list(range(65524,65531)):
        ht, st, vt = rgb_to_hsv(u16(r), u16(g), u16(b))
        r2, g2, b2 = hsv_to_rgb(u16(ht), u16(st), u16(vt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #if mx2 > mx and (mx2/65535.) < 0.0001: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("16-bit unsigned integer RGB/HSV/RGB error: %d (%.4f%%)" % (mx, 100*mx/65535.))

  mx = 4
  for r in list(range(0,5)) + list(range(30000,30005)) + list(range(65530,65536)):
    for g in list(range(0,6)) + list(range(30002,3007)) + list(range(65525,65532)):
      for b in list(range(0,7)) + list(range(3003,3008)) + list(range(65524,65531)):
        ht, st, lt = rgb_to_hsl(u16(r), u16(g), u16(b))
        r2, g2, b2 = hsl_to_rgb(u16(ht), u16(st), u16(lt))
        #mx2 = max(abs(r2-r), abs(g2-g), abs(b2-b))
        #if mx2 > mx and (mx2/65535.) < 0.0001: mx = mx2
        assert abs(r2 - r) <= mx
        assert abs(g2 - g) <= mx
        assert abs(b2 - b) <= mx
  #print("16-bit unsigned integer RGB/HSL/RGB error: %d (%.4f%%)" % (mx, 100*mx/65535.))

def test_gray_halves():

  # tests some border-line cases for gray-scale conversion and makes sure
  # we don't have precision problems.

  if platform.architecture()[0] == '64bit':
    # do a full test, require all values to be the same
    correct = bob.io.base.load(F('gray-u8-mids.hdf5'))
    for k in range(correct.shape[0]):
      nose.tools.eq_(correct[k,3],
          rgb_to_gray(*[numpy.uint8(z) for z in correct[k,:3]]))
  else:
    # do a full test, require all values to be the same
    # use a special 32-bit file. About 1600 cases do not match the 64-bit
    # ones.
    correct = bob.io.base.load(F('gray-u8-mids-32bits.hdf5'))
    for k in range(correct.shape[0]):
      nose.tools.eq_(correct[k,3],
          rgb_to_gray(*[numpy.uint8(z) for z in correct[k,:3]]))
