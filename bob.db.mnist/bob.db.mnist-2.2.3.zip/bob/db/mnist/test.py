#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""A few checks at the MNIST database.
"""

from . import Database


def db_available(test):
  """Decorator for detecting if we're running the test at Idiap"""

  import os
  import functools
  from nose.plugins.skip import SkipTest

  @functools.wraps(test)
  def wrapper(*args, **kwargs):

    from .driver import Interface
    f = Interface().files()

    for k in f:
      if not os.path.exists(k):
        raise SkipTest("Raw database files are not available")

    return test(*args, **kwargs)

  return wrapper


@db_available
def test_query():
  db = Database()

  f = db.labels()
  assert len(f) == 10 # number of labels (digits 0 to 9)
  for i in range(0,10):
    assert i in f

  f = db.groups()
  assert len(f) == 2 # Two groups
  assert 'train' in f
  assert 'test' in f

  # Test the number of samples/labels
  d, l = db.data(groups='train')
  assert d.shape[0] == 60000
  assert d.shape[1] == 784
  assert l.shape[0] == 60000
  d, l = db.data(groups='test')
  assert d.shape[0] == 10000
  assert d.shape[1] == 784
  assert l.shape[0] == 10000
  d, l = db.data()
  assert d.shape[0] == 70000
  assert d.shape[1] == 784
  assert l.shape[0] == 70000
