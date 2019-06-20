#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""A few checks at the Biosecure database.
"""

import os
import bob.db.biosecure

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'biosecure'))

  return wrapper


@db_available
def test_clients():
  # test that the clients() function returns reasonable output
  db = bob.db.biosecure.Database()

  assert len(db.groups()) == 3
  assert len(db.clients()) == 210
  # TODO: more specific tests


@db_available
def test_objects():
  # test that the objects() function returns reasonable output
  db = bob.db.biosecure.Database()

  assert len(db.objects()) == 2520
  # TODO: more specific tests


@db_available
def test_annotations():
  # Tests that for all files the annotated eye positions exist and are in correct order
  db = bob.db.biosecure.Database()
  for f in db.objects():
    annotations = db.annotations(f)
    assert annotations is not None
    assert len(annotations) == 2
    assert 'leye' in annotations
    assert 'reye' in annotations
    assert len(annotations['reye']) == 2
    assert len(annotations['leye']) == 2
    # assert that the eye positions are not exchanged
    assert annotations['leye'][1] > annotations['reye'][1]


@db_available
def test_driver_api():

  from bob.db.base.script.dbmanage import main

  assert main('biosecure dumplist --self-test'.split()) == 0
  assert main('biosecure dumplist --protocol=ca0 --class=client --group=dev --purpose=enroll --client=141 --self-test'.split()) == 0
  assert main('biosecure checkfiles --self-test'.split()) == 0
  assert main('biosecure reverse ca0/u141_s02_face_ds2-ca-0i_02 --self-test'.split()) == 0
  assert main('biosecure path 748 --self-test'.split()) == 0

