# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import absolute_import

import functools
import itertools
import six

from . import NotSet
from six.moves import range, filter as _filter, filterfalse as _filterfalse, zip_longest

_next = next


class _dualmethod(object):
  """
  A combination of #classmethod() and instance methods. Methods decorated
  with this class can be called from the class and instance level. The first
  parameter will then refer to the class or the instance, respectively.
  """

  def __init__(self, func):
    self.func = func
    functools.update_wrapper(self, func)

  def __get__(self, instance, owner):
    assert owner is not None
    if instance is not None:
      return functools.partial(self.func, owner, instance)
    return functools.partial(self.func, owner)


class stream(object):
  """
  A wrapper for iterables that provides the stream processor functions of
  this module in an object-oriented interface.
  """

  def __init__(self, iterable):
    self.iterable = iter(iterable)

  def __iter__(self):
    return iter(self.iterable)

  def __next__(self):
    return _next(self.iterable)

  def __getitem__(self, val):
    if isinstance(val, slice):
      return self.slice(val.start, val.stop, val.step)
    else:
      raise TypeError('{} object is only subscriptable with slices'.format(type(self).__name__))

  @_dualmethod
  def call(cls, iterable, *a, **kw):
    """
    Calls every item in *iterable* with the specified arguments.
    """

    return cls(x(*a, **kw) for x in iterable)

  @_dualmethod
  def map(cls, iterable, func, *a, **kw):
    """
    Iterable-first replacement of Python's built-in `map()` function.
    """

    return cls(func(x, *a, **kw) for x in iterable)

  @_dualmethod
  def flatmap(cls, iterable, func):
    """
    Same as #map() but flattens the result.
    """

    def generator():
      for x in iterable:
        for y in func(x):
          yield y
    return cls(generator())

  @_dualmethod
  def filter(cls, iterable, cond, *a, **kw):
    """
    Iterable-first replacement of Python's built-in `filter()` function.
    """

    return cls(x for x in iterable if cond(x, *a, **kw))

  @_dualmethod
  def unique(cls, iterable, key=None):
    """
    Yields unique items from *iterable* whilst preserving the original order.
    """

    if key is None:
      key = lambda x: x
    def generator():
      seen = set()
      seen_add = seen.add
      for item in iterable:
        key_val = key(item)
        if key_val not in seen:
          seen_add(key_val)
          yield item
    return cls(generator())

  @_dualmethod
  def chunks(cls, iterable, n, fill=None):
    """
    Collects elements in fixed-length chunks.
    """

    return cls(zip_longest(*[iter(iterable)] * n, fillvalue=fill))

  @_dualmethod
  def concat(cls, iterables):
    """
    Similar to #itertools.chain.from_iterable().
    """

    def generator():
      for it in iterables:
        for element in it:
          yield element
    return cls(generator())

  @_dualmethod
  def chain(cls, *iterables):
    """
    Similar to #itertools.chain.from_iterable().
    """

    def generator():
      for it in iterables:
        for element in it:
          yield element
    return cls(generator())

  @_dualmethod
  def attr(cls, iterable, attr_name):
    """
    Applies #getattr() on all elements of *iterable*.
    """

    return cls(getattr(x, attr_name) for x in iterable)

  @_dualmethod
  def item(cls, iterable, key, default=NotSet):
    """
    Applies `__getitem__` on all elements of *iterable*.
    """

    if default is NotSet:
      return cls(x[key] for x in iterable)
    else:
      return cls(x.get(key, default) for x in iterable)

  @_dualmethod
  def of_type(cls, iterable, types):
    """
    Filters using #isinstance().
    """

    return cls(x for x in iterable if isinstance(x, types))

  @_dualmethod
  def partition(cls, iterable, pred):
    """
    Use a predicate to partition items into false and true entries.
    Returns a tuple of two streams with the first containing all elements
    for which *pred* returned #False and the other containing all elements
    where *pred* returned #True.
    """

    t1, t2 = itertools.tee(iterable)
    return cls(_filterfalse(pred, t1)), cls(_filter(pred, t2))

  @_dualmethod
  def dropwhile(cls, iterable, pred):
    return cls(itertools.dropwhile(pred, iterable))

  @_dualmethod
  def takewhile(cls, iterable, pred):
    return cls(itertools.takewhile(pred, iterable))

  @_dualmethod
  def groupby(cls, iterable, key=None):
    return cls(itertools.groupby(iterable, key))

  @_dualmethod
  def slice(cls, iterable, *args, **kwargs):
    return cls(itertools.islice(iterable, *args, **kwargs))

  if six.PY2:
    @_dualmethod
    def next(cls, iterable):
      if isinstance(iterable, stream):
        return iterable.__next__()
      else:
        return _next(iter(iterable))
  else:
    @_dualmethod
    def next(cls, iterable):
      return _next(iter(iterable))

  @_dualmethod
  def length(cls, iterable):
    """
    Returns the number of items in an iterable.
    """

    iterable = iter(iterable)
    count = 0
    while True:
      try:
        _next(iterable)
      except StopIteration:
        break
      count += 1
    return count

  @_dualmethod
  def consume(cls, iterable, n=None):
    if n is not None:
      for _ in range(n):
        try:
          _next(iterable)
        except StopIteration:
          break
    else:
      while True:
        try:
          _next(iterable)
        except StopIteration:
          break
    return iterable

  @_dualmethod
  def collect(cls, iterable, collect_cls=None, *args, **kwargs):
    return (collect_cls or list)(iterable, *args, **kwargs)

  @_dualmethod
  def batch(cls, iterable, n, collect_cls=None):
    """
    Produces a stream that yields lists of max *n* elements taken from
    *iterable*. The *collect_cls* can be overwritten to modify the collection
    type for the batched elements.

    If *collect_cls* is an identity function (`lambda x: x`), the elements
    of the new stream will be generators yielding at max *n* elements.
    """

    iterable = iter(iterable)
    if collect_cls is None:
      collect_cls = list

    def take(first):
      yield first
      count = 1
      while count < n:
        try:
          yield next(iterable)
        except StopIteration:
          break
        count += 1

    def generate_batches():
      while True:
        try:
          first = next(iterable)
        except StopIteration:
          break
        yield collect_cls(take(first))

    return cls(generate_batches())


import sys
_module = sys.modules[__name__]
sys.modules[__name__] = stream
