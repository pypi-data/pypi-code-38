#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Database definitions for Vein Recognition'''


import numpy


class AnnotatedArray(numpy.ndarray):
  """Defines a numpy array subclass that can carry its own metadata

  Copied from: https://docs.scipy.org/doc/numpy-1.12.0/user/basics.subclassing.html#slightly-more-realistic-example-attribute-added-to-existing-array
  """

  def __new__(cls, input_array, metadata=None):
      obj = numpy.asarray(input_array).view(cls)
      obj.metadata = metadata if metadata is not None else dict()
      return obj

  def __array_finalize__(self, obj):
      if obj is None: return
      self.metadata = getattr(obj, 'metadata', dict())
