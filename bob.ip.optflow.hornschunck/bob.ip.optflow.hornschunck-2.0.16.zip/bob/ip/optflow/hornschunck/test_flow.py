#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed Mar 16 15:01:13 2011 +0100
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Tests our Optical Flow utilities going through some example data.
"""

import os
import numpy
import nose.tools
import pkg_resources


from . import VanillaFlow, HornAndSchunckGradient, laplacian_avg_hs

def F(f):
  """Returns the test file on the "data" subdirectory"""
  return pkg_resources.resource_filename(__name__, os.path.join('data', f))

FRAME10 = F(os.path.join('rubberwhale', 'frame10_gray.png'))
FRAME11 = F(os.path.join('rubberwhale', 'frame11_gray.png'))

def make_image_tripplet():
  """Creates two images for you to calculate the flow

  255 255 255 255 255    255 255 255 255 255    255 255 255 255 255
  255   0   0   0   0    255 255 255 255 255    255 255 255 255 255
  255   0   0   0   0 => 255 255   0   0   0 => 255 255 255 255 255
  255 255 255 255 255    255 255   0   0   0    255 255 255   0   0
  255 255 255 255 255    255 255 255 255 255    255 255 255   0   0

  """
  im1 = 255 * numpy.ones((5,5), 'uint8')
  im1[1:3, 1:] = 0
  im2 = 255 * numpy.ones((5,5), 'uint8')
  im2[2:4, 2:] = 0
  im3 = 255 * numpy.ones((5,5), 'uint8')
  im3[3:, 3:] = 0
  return im1.astype('float64')/255., im2.astype('float64')/255., im3.astype('float64')/255.

def HornAndSchunckFlowPython(alpha, im1, im2, im3, u0, v0):
  """Calculates the H&S flow in pure python"""
  grad = HornAndSchunckGradient(im1.shape)
  ex, ey, et = grad(im1, im2)
  u = laplacian_avg_hs(u0)
  v = laplacian_avg_hs(v0)
  common_term = (ex*u + ey*v + et) / (ex**2 + ey**2 + alpha**2)
  return u - ex*common_term, v - ey*common_term

def compute_flow_opencv(alpha, iterations, ifile1, ifile2):
  import cv
  i1 = cv.LoadImageM(os.path.join("flow", ifile1), iscolor=False)
  i2 = cv.LoadImageM(os.path.join("flow", ifile2), iscolor=False)
  u = cv.CreateMat(i1.rows, i1.cols, cv.CV_32F)
  cv.SetZero(u)
  v = cv.CreateMat(i1.rows, i1.cols, cv.CV_32F)
  cv.SetZero(v)
  l = 1.0/(alpha**2)
  cv.CalcOpticalFlowHS(i1, i2, 0, u, v, l, (cv.CV_TERMCRIT_ITER, iterations, 0))
  # return blitz arrays
  return numpy.array(u, 'float64'), numpy.array(v, 'float64')

def test_synthetic():

  # Tests and examplifies usage of the vanilla HS algorithm while comparing
  # the C++ implementation to a pythonic implementation of the same algorithm

  # We create a new estimator specifying the alpha parameter (first value)
  # and the number of iterations to perform (second value).
  N = 1200
  alpha = 1.5

  # The OpticalFlow estimator always receives a blitz::Array<uint8_t,2> as
  # the image input. The output has the same rank and shape but is in
  # doubles.
  i1, i2, i3 = make_image_tripplet()
  u_cxx = numpy.zeros(i1.shape, 'float64')
  v_cxx = numpy.zeros(i1.shape, 'float64')
  u_py  = numpy.zeros(i1.shape, 'float64')
  v_py  = numpy.zeros(i1.shape, 'float64')
  flow  = VanillaFlow(i1.shape)
  for i in range(N):
    flow(alpha, 1, i1, i2, u_cxx, v_cxx)
    u_py, v_py = HornAndSchunckFlowPython(alpha, i1, i2, i3, u_py, v_py)
    cxx_se2 = flow.eval_ec2(u_cxx, v_cxx)
    cxx_be = flow.eval_eb(i1, i2, u_cxx, v_cxx)
    py_se2 = flow.eval_ec2(u_py, v_py)
    py_be = flow.eval_eb(i1, i2, u_py, v_py)
    cxx_avg_err = (cxx_se2 * (alpha**2) + cxx_be**2).sum()
    py_avg_err = (py_se2 * (alpha**2) + py_be**2).sum()
    '''
    print("Error %2d: %.3e (%.3e) %.3e (%.3e) %.3e (%.3e)" % \
        (
         i,
         cxx_se2.sum()**0.5,
         py_se2.sum()**0.5,
         cxx_be.sum(),
         py_be.sum(),
         cxx_avg_err**0.5,
         py_avg_err**0.5
        )
        )
    '''
  assert  numpy.allclose(u_cxx, u_py, atol=1e-15)
  assert  numpy.allclose(v_cxx, v_py, atol=1e-15)


#TODO: When enabaling this test, import bob.io.base and bob.io.image
#TODO: This includes making this package dependent on bob.io.base and bob.io.image
@nose.tools.nottest
def test_demo():

  N = 64
  alpha = 1.1

  i1 = bob.io.base.load(FRAME10)
  i2 = bob.io.base.load(FRAME11)

  u = numpy.zeros(i1.shape, 'float64')
  v = numpy.zeros(i1.shape, 'float64')
  flow = VanillaFlow(i1.shape)
  for i in range(N):
    flow(alpha, 1, i1, i2, u, v)
    #array = (255.0*bob.ip.flowutils.flow2hsv(u,v)).astype('uint8')
    #array.save("hs_rubberwhale-%d.png" % i)
    se2 = flow.eval_ec2(u, v)
    be = flow.eval_eb(i1, i2, u, v)
    avg_err = (se2 * (alpha**2) + be**2).sum()
    print("Error %2d| Ec2: %.3e Eb: %.3e E2 (avg.): %.3e" % \
        (
         i,
         se2.sum()**0.5,
         be.sum(),
         avg_err**0.5,
        )
        )
    #from . import flow_error
    #print("error:", (flow_error(i1, i2, u, v)**2).sum())

@nose.tools.nottest
def test_opencv():

  # Tests and examplifies usage of the vanilla HS algorithm while comparing
  # the C++ implementation to a OpenCV implementation of the same algorithm.
  # Please note that the comparision is not fair as the OpenCV uses
  # different kernels for the evaluation of the image gradient.

  # This test is only here to help you debug problems.

  # We create a new estimator specifying the alpha parameter (first value)
  # and the number of iterations to perform (second value).
  N = 64
  alpha = 15

  # The OpticalFlow estimator always receives a blitz::Array<uint8_t,2> as
  # the image input. The output has the same rank and shape but is in
  # doubles.

  # This will load the test images: Rubber Whale sequence
  if1 = os.path.join("rubberwhale", "frame10_gray.png")
  if2 = os.path.join("rubberwhale", "frame11_gray.png")
  i1 = load_gray(if1)
  i2 = load_gray(if2)

  u_cxx = numpy.zeros(i1.shape, 'float64')
  v_cxx = numpy.zeros(i1.shape, 'float64')
  flow = VanillaFlow(i1.shape)
  flow(alpha, N, i1, i2, u_cxx, v_cxx)
  se2 = flow.eval_ec2(u_cxx, v_cxx)
  be = flow.eval_eb(i1, i2, u_cxx, v_cxx)
  avg_err = (se2 * (alpha**2) + be**2).sum()
  print("bob H&S Error (%2d iterations) : %.3e %.3e %.3e" % (N, se2.sum()**0.5, be.sum(), avg_err**0.5))

  u_ocv1, v_ocv1 = compute_flow_opencv(alpha, N/4, if1, if2)
  u_ocv2, v_ocv2 = compute_flow_opencv(alpha, N/2, if1, if2)
  u_ocv, v_ocv = compute_flow_opencv(alpha, N, if1, if2)
  se2 = flow.eval_ec2(u_ocv, v_ocv)
  be = flow.eval_eb(i1, i2, u_ocv, v_ocv)
  avg_err = (se2 * (alpha**2) + be**2).sum()
  print("OpenCV H&S Error (%2d iterations): %.3e %.3e %.3e" % (N, se2.sum()**0.5, be.sum(), avg_err**0.5))

  u_c = u_cxx/u_ocv
  v_c = v_cxx/v_ocv
  assert u_c.mean() < 1.1 #check for within 10%
  assert v_c.mean() < 1.1 #check for within 10%
  print("mean(u_ratio), mean(v_ratio): %.3e %.3e" % (u_c.mean(), v_c.mean()),
      "(as close to 1 as possible)")
