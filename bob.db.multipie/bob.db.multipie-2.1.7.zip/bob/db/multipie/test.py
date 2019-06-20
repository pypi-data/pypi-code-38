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

"""A few checks at the Multi-PIE database.
"""

import os, sys
import bob.db.multipie
from nose.plugins.skip import SkipTest

def db_available(test):
  """Decorator for detecting if OpenCV/Python bindings are available"""
  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'multipie'))

  return wrapper


@db_available
def test_clients():

  db = bob.db.multipie.Database()

  assert len(db.groups()) == 3

  clients = db.clients()
  assert len(clients) == 337 #337 clients overall
  # Number of clients in each set
  c_dev = db.clients(groups='dev')
  assert len(c_dev) == 64 #64 clients in the dev set
  c_eval = db.clients(groups='eval')
  assert len(c_eval) == 65 #65 clients in the eval set
  c_world = db.clients(groups='world')
  assert len(c_world) == 208 #208 clients in the world set
  # Check client ids
  assert db.has_client_id(1)
  assert not db.has_client_id(395)
  # Check subworld
  assert len(db.clients(groups='world', subworld='sub41')) == 41
  assert len(db.clients(groups='world', subworld='sub81')) == 81
  assert len(db.clients(groups='world', subworld='sub121')) == 121
  assert len(db.clients(groups='world', subworld='sub161')) == 161

  # check models and t-models
  assert len(db.model_ids(groups='dev')) == 64
  assert len(db.model_ids(groups='eval')) == 65
  assert len(db.tmodel_ids(groups='dev')) == 65
  assert len(db.tmodel_ids(groups='eval')) == 64

  # Check files relationship
  c = db.client(1)
  len(c.files) # Number depends on the way the database was created (pose only, etc.)


@db_available
def test_protocols():

  db = bob.db.multipie.Database()

  # TODO: Depends on the way the database was created (pose only, etc.)
  #assert len(db.protocols()) == 4
  #assert len(db.protocol_names()) == 4
  #assert db.has_protocol('M')

  assert len(db.subworlds()) == 4
  assert len(db.subworld_names()) == 4
  assert db.has_subworld('sub41')


@db_available
def test_objects():

  # TODO: depends on the way the database was created (pose only, etc.)
  db = bob.db.multipie.Database()

  # TODO: better tests for this
  assert len(db.objects()) > 0
  assert len(db.zobjects()) > 0
  assert len(db.tobjects()) > 0


@db_available
def test_annotations():
  # read some annotation files and test it's content
  dir = "/idiap/group/biometric/annotations/multipie"
  if not os.path.exists(dir):
    raise SkipTest("The annotation directory '%s' is not available, annotations can't be tested." % dir)
  db = bob.db.multipie.Database(annotation_directory = dir)
  import random
  files = random.sample(db.all_files(), 1000)
  for file in files:
    annotations = db.annotations(file)
    assert annotations is not None


@db_available
def test_driver_api():

  from bob.db.base.script.dbmanage import main

  db = bob.db.multipie.Database()
  assert main('multipie dumplist --self-test'.split()) == 0
  if db.has_protocol('M'):
    assert main('multipie dumplist --protocol=M --class=client --group=dev --purpose=enroll --self-test'.split()) == 0
  elif db.has_protocol('P051'):
    assert main('multipie dumplist --protocol=P051 --class=client --group=dev --purpose=enroll --self-test'.split()) == 0
  assert main('multipie checkfiles --self-test'.split()) == 0
  assert main('multipie reverse session02/multiview/108/01/05_1/108_02_01_051_17 --self-test'.split()) == 0
  assert main('multipie path 6578 --self-test'.split()) == 0

