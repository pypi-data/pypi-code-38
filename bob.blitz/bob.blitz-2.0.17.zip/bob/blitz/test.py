#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 20 Sep 14:45:01 2013

"""Tests for blitz.array glue methods
"""

import sys
import nose
import numpy
from . import array as bzarray
from . import as_blitz

import platform
IS_32BIT = platform.architecture()[0] == '32bit'

def test_array_from_scratch():

  bz = bzarray(10, dtype='uint8')
  nose.tools.eq_(bz.shape, (10,))
  nose.tools.eq_(len(bz), 10)
  nose.tools.eq_(bz.dtype, numpy.uint8)

  bz = bzarray((20000,), dtype='bool')
  nose.tools.eq_(bz.shape, (20000,))
  nose.tools.eq_(len(bz), 20000)
  nose.tools.eq_(bz.dtype, numpy.bool_)

  bz = bzarray((3,3), dtype='uint32')
  nose.tools.eq_(bz.shape, (3,3))
  nose.tools.eq_(len(bz), 9)
  nose.tools.eq_(bz.dtype, numpy.uint32)

@nose.tools.raises(ValueError)
def test_array_negative_size():

  bz = bzarray(-2, dtype='uint8')

@nose.tools.raises(ValueError)
def test_array_zero_size():

  bz = bzarray(0, dtype='uint8')
  nose.tools.eq_(len(bz), 0)

def test_array_assign_and_read_u8():

  bz = bzarray(2, dtype='uint8')

  # assign a value to each position, check back
  bz[0] = 3
  nose.tools.eq_(bz[0].dtype, numpy.uint8)
  nose.tools.eq_(bz[0], 3)
  bz[1] = 12
  nose.tools.eq_(bz[0].dtype, numpy.uint8)
  nose.tools.eq_(bz[1], 12)

def test_array_assign_and_read_u32():

  bz = bzarray(2, dtype='uint32')

  # assign a value to each position, check back
  bz[0] = 3
  nose.tools.eq_(bz[0].dtype, numpy.uint32)
  nose.tools.eq_(bz[0], 3)
  bz[1] = 0
  nose.tools.eq_(bz[0].dtype, numpy.uint32)
  nose.tools.eq_(bz[1], 0)

def test_array_assign_and_read_u32d2():

  bz = bzarray((2,2), dtype='uint32')

  # assign a value to each position, check back
  bz[0,0] = 3
  bz[0,1] = 12
  bz[1,0] = 25
  bz[1,1] = 255
  nose.tools.eq_(bz[0,0].dtype, numpy.uint32)
  nose.tools.eq_(bz[0,0], 3)
  nose.tools.eq_(bz[0,1].dtype, numpy.uint32)
  nose.tools.eq_(bz[0,1], 12)
  nose.tools.eq_(bz[1,0].dtype, numpy.uint32)
  nose.tools.eq_(bz[1,0], 25)
  nose.tools.eq_(bz[1,1].dtype, numpy.uint32)
  nose.tools.eq_(bz[1,1], 255)

def test_array_assign_and_read_c128d2():

  bz = bzarray((2,2), dtype='complex128')
  bz[0,0] = complex(3, 4.2)
  bz[0,1] = complex(1.5, 2)
  bz[1,0] = complex(33, 4)
  bz[1,1] = complex(2, 2)
  nose.tools.eq_(bz[0,0].dtype, numpy.complex128)
  nose.tools.eq_(bz[0,0], complex(3,4.2))
  nose.tools.eq_(bz[0,1].dtype, numpy.complex128)
  nose.tools.eq_(bz[0,1], complex(1.5,2))
  nose.tools.eq_(bz[1,0].dtype, numpy.complex128)
  nose.tools.eq_(bz[1,0], complex(33,4))
  nose.tools.eq_(bz[1,1].dtype, numpy.complex128)
  nose.tools.eq_(bz[1,1], complex(2,2))

@nose.tools.raises(IndexError)
def test_array_protect_segfault_high_get():

  bz = bzarray(2, dtype='complex64')
  k = bz[3]

@nose.tools.raises(IndexError)
def test_array_protect_segfault_high_set():

  bz = bzarray(2, dtype='complex64')
  bz[3] = complex(2,3)

@nose.tools.raises(IndexError)
def test_array_protect_segfault_low_get():

  bz = bzarray(2, dtype='complex128')
  k = bz[-3]

@nose.tools.raises(IndexError)
def test_array_protect_segfault_low_set():

  bz = bzarray(2, dtype='complex128')
  bz[-3] = complex(2,3)

def test_u8d1_as_ndarray():

  bz = bzarray(2, dtype='uint8')
  bz[0] = 32
  bz[1] = 10
  nd = numpy.array(bz)
  nose.tools.eq_(nd.shape, bz.shape)
  nose.tools.eq_(bz[0], nd[0])
  nose.tools.eq_(bz[1], nd[1])
  nose.tools.eq_(nd.base, None)
  assert nd.flags.owndata
  assert nd.flags.behaved
  assert nd.flags.c_contiguous
  assert nd.flags.writeable
  nose.tools.eq_(nd.dtype, numpy.dtype('uint8'))
  del bz
  nose.tools.eq_(nd[0], 32)
  nose.tools.eq_(nd[1], 10)

def test_u64d1_as_ndarray():

  bz = bzarray(2, dtype='uint64')
  bz[0] = 2**33
  bz[1] = 2**64 - 1
  nd = numpy.array(bz)
  nose.tools.eq_(nd.shape, bz.shape)
  nose.tools.eq_(bz[0], nd[0])
  nose.tools.eq_(bz[1], nd[1])
  nose.tools.eq_(nd.base, None)
  assert nd.flags.owndata
  assert nd.flags.behaved
  assert nd.flags.c_contiguous
  assert nd.flags.writeable
  nose.tools.eq_(nd.dtype, numpy.dtype('uint64'))
  del bz
  nose.tools.eq_(nd[0], 2**33)
  nose.tools.eq_(nd[1], 2**64-1)

def test_u32d1_as_ndarray():

  bz = bzarray(2, dtype='uint32')
  bz[0] = 2**32-1
  bz[1] = 0
  nd = numpy.array(bz)
  nose.tools.eq_(nd.shape, bz.shape)
  nose.tools.eq_(bz[0], nd[0])
  nose.tools.eq_(bz[1], nd[1])
  nose.tools.eq_(nd.base, None)
  del bz
  assert nd.flags.owndata
  assert nd.flags.behaved
  assert nd.flags.c_contiguous
  assert nd.flags.writeable
  nose.tools.eq_(nd.dtype, numpy.dtype('uint32'))
  nose.tools.eq_(nd[0], 2**32-1)
  nose.tools.eq_(nd[1], 0)

def test_s64d2_shallow_array():

  bz = bzarray((2,2), dtype='int64')
  bz[0,0] = 1
  bz[0,1] = 2
  bz[1,0] = 3
  bz[1,1] = -1
  nd = bz.as_ndarray()
  nose.tools.eq_(nd.shape, bz.shape)
  nose.tools.eq_(bz[0,0], nd[0,0])
  nose.tools.eq_(bz[0,1], nd[0,1])
  nose.tools.eq_(bz[1,0], nd[1,0])
  nose.tools.eq_(bz[1,1], nd[1,1])
  nose.tools.eq_(nd.base, bz)
  del bz
  assert nd.flags.behaved
  assert nd.flags.c_contiguous
  assert nd.flags.writeable
  nose.tools.eq_(nd.flags.owndata, False)

  nose.tools.eq_(nd.dtype, numpy.dtype('int64'))
  nose.tools.eq_(nd[0,0], 1)
  nose.tools.eq_(nd[0,1], 2)
  nose.tools.eq_(nd[1,0], 3)
  nose.tools.eq_(nd[1,1], -1)

  nd[1,0] = 32
  nose.tools.eq_(nd.base[1,0], nd[1,0])

  # tests blitz::Array<> out lives attached ndarray
  bz = nd.base
  del nd
  nose.tools.eq_(bz.shape, (2,2))
  nose.tools.eq_(bz[0,0], 1)
  nose.tools.eq_(bz[0,1], 2)
  nose.tools.eq_(bz[1,0], 32)
  nose.tools.eq_(bz[1,1], -1)

def test_s64d2_indirect_array():

  bz = bzarray((2,2), dtype='int64')
  bz[0,0] = 1
  bz[0,1] = 2
  bz[1,0] = 3
  bz[1,1] = -1
  nd = numpy.array(bz, copy=False)
  nose.tools.eq_(nd.base, bz)

@nose.tools.raises(ValueError)
def test_s64d2_cannot_resize_shallow():

  bz = bzarray((2,2), dtype='int64')
  bz[0,0] = 1
  bz[0,1] = 2
  bz[1,0] = 3
  bz[1,1] = -1
  nd = bz.as_ndarray()
  nd.resize(3,3)

def test_from_ndarray_shallow():

  nd = numpy.array(range(6), 'uint8').reshape(2,3)
  bz = as_blitz(nd)

  # checks we actually have a shallow copy
  nose.tools.eq_(id(bz.base), id(nd))

  # checks that the memory is actually bound
  nd[1,2] = -18
  nose.tools.eq_(nd[1,2], bz[1,2])
  nd[0,1] = 42
  nose.tools.eq_(nd[0,1], bz[0,1])


def test_from_2darray_transposed():

  nd = numpy.array([1, 2, 3, -1]).reshape(2,2).T
  bz = as_blitz(nd)
  nose.tools.eq_(bz[0,0], nd[0,0])
  nose.tools.eq_(bz[0,1], nd[0,1])
  nose.tools.eq_(bz[1,0], nd[1,0])
  nose.tools.eq_(bz[1,1], nd[1,1])

def test_from_3darray_transposed():

  nd = numpy.random.randint(0, 255, (3,200,300)).astype('uint8')
  bz = as_blitz(nd.transpose(2,0,1))
  for i in range(2):
    for j in range(2):
      for k in range(2):
        nose.tools.eq_(bz[k,i,j], nd[i,j,k])

@nose.tools.raises(ValueError)
def test_detects_unsupported_dims():

  nd = numpy.array(range(32)).reshape(2,2,2,2,2)
  bz = as_blitz(nd)

def test_can_use_int_as_dtype():

  bz = bzarray(2, int)
  if IS_32BIT: nose.tools.eq_(bz.dtype, numpy.int32)
  else: nose.tools.eq_(bz.dtype, numpy.int64)
  bz[0] = 33
  if IS_32BIT: nose.tools.eq_(bz[0].dtype, numpy.int32)
  else: nose.tools.eq_(bz[0].dtype, numpy.int64)
  nose.tools.eq_(bz[0], 33)

def skip_if_at_32bit_arch(func):
  from nose.plugins.skip import SkipTest
  def _():
    if IS_32BIT: raise SkipTest('test makes no sense on 32-bit platforms')
  _.__name__ = func.__name__
  return _

@skip_if_at_32bit_arch
def test_can_use_float128_as_dtype():

  bz = bzarray(2, 'float128')
  nose.tools.eq_(bz.dtype, numpy.float128)
  bz[1] = 0.125
  nose.tools.eq_(bz[1].dtype, numpy.float128)
  nose.tools.eq_(bz[1], 0.125)

@skip_if_at_32bit_arch
def test_can_use_complex256_as_dtype():

  bz = bzarray(2, 'complex256')
  nose.tools.eq_(bz.dtype, numpy.complex256)
  bz[0] = complex(4,4)
  nose.tools.eq_(bz[0].dtype, numpy.complex256)
  nose.tools.eq_(bz[0], complex(4,4))

def test_re_wrapping_bzarray():

  bz = bzarray((2,2), int)
  nd = bz.as_ndarray()
  bz2 = as_blitz(nd)
  nose.tools.eq_(id(bz), id(bz2))

def test_re_wrapping_ndarray():

  nd = numpy.ndarray((2,2), int)
  bz = as_blitz(nd)
  nd2 = bz.as_ndarray()
  nose.tools.eq_(id(nd), id(nd2))

def test_can_use_bz_with_npy_ops():

  bz = bzarray(2, numpy.uint64)
  bz[0] = 1
  bz[1] = 3
  npy = numpy.array([1,3], dtype=numpy.uint64)
  assert numpy.all(numpy.abs(bz-npy) < 1e-4)

def test_as_ndarray_cast():

  bz = bzarray((2,2), int)
  bz[0,0] = 1
  bz[0,1] = 3
  bz[1,0] = 2
  bz[1,1] = 4
  nd = bz.as_ndarray(complex)
  nose.tools.eq_(nd.base, None)
  nose.tools.eq_(nd.dtype, numpy.complex128)
  nose.tools.eq_(nd[0,0], 1+0j)
  nose.tools.eq_(nd[0,1], 3+0j)
  nose.tools.eq_(nd[1,0], 2+0j)
  nose.tools.eq_(nd[1,1], 4+0j)

def test_as_ndarray_nocast():

  bz = bzarray((2,2), int)
  bz[0,0] = 1
  bz[0,1] = 3
  bz[1,0] = 2
  bz[1,1] = 4
  if IS_32BIT: nd = bz.as_ndarray(numpy.int32)
  else: nd = bz.as_ndarray(numpy.int64)
  nose.tools.eq_(nd.base, bz)
  if IS_32BIT: nose.tools.eq_(nd.dtype, numpy.int32)
  else: nose.tools.eq_(nd.dtype, numpy.int64)
  nose.tools.eq_(nd[0,0], nd[0,0])
  nose.tools.eq_(nd[0,1], nd[0,1])
  nose.tools.eq_(nd[1,0], nd[1,0])
  nose.tools.eq_(nd[1,1], nd[1,1])

def test_array_cast():

  bz = bzarray((2,2), float)
  bz[0,0] = 1.
  bz[0,1] = 3.14
  bz[1,0] = 2.27
  bz[1,1] = 4.05
  bz2 = bz.cast(int)
  if IS_32BIT: nose.tools.eq_(bz2.dtype, numpy.int32)
  else: nose.tools.eq_(bz2.dtype, numpy.int64)
  nose.tools.eq_(bz2[0,0], 1)
  nose.tools.eq_(bz2[0,1], 3)
  nose.tools.eq_(bz2[1,0], 2)
  nose.tools.eq_(bz2[1,1], 4)

def test_constness():
  from ._library import _test_const_numpy
  data = _test_const_numpy()
  assert data.flags['WRITEABLE'] == False

  def _should_raise(x,y):
    x[0] = y
  nose.tools.assert_raises((ValueError,RuntimeError), _should_raise, data, 4)
