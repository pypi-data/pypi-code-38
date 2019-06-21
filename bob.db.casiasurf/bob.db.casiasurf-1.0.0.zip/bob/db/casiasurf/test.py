#!/usr/bin/env python
# encoding: utf-8


"""A few checks on CASIA-SURF database 
"""
import os, sys
import bob.db.base
import bob.db.casiasurf

def db_available(test):
  """Decorator for detecting if the database file is available"""
  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'casiasurf'))

  return wrapper


def test_objects():

  # tests if the right number of sample objects is returned
  
  db = bob.db.casiasurf.Database()
  assert len(db.objects(groups=('train',), purposes=('real',))) == 8942
  assert len(db.objects(groups=('train',), purposes=('attack',))) == 20324
  assert len(db.objects(groups=('validation',), purposes=('real',))) == 2994
  assert len(db.objects(groups=('validation',), purposes=('attack',))) == 6614
  assert len(db.objects(groups=('validation',), purposes=('real','attack'))) == 9608
  assert len(db.objects(groups=('test',), purposes=('unknown',))) == 57710
