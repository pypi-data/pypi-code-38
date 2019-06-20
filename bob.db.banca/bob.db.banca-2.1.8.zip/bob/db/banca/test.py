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

"""A few checks at the BANCA database.
"""

import os, sys
import bob.db.banca

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'banca'))

  return wrapper


@db_available
def test_clients():
  # test whether the correct number of clients is returned
  db = bob.db.banca.Database()
  assert len(db.groups()) == 3
  assert len(db.clients()) == 82
  assert len(db.clients(groups='world')) == 30
  assert len(db.clients(groups='world', subworld='onethird')) == 10
  assert len(db.clients(groups='world', subworld='twothirds')) == 20
  assert len(db.clients(groups='dev')) == 26
  assert len(db.clients(groups='eval')) == 26
  assert len(db.tclients(groups='dev')) == 26
  assert len(db.tclients(groups='eval')) == 26

  assert len(db.clients(genders='f')) == 41
  assert len(db.clients(genders='m')) == 41


@db_available
def test_objects():
  # tests if the right number of File objects is returned
  db = bob.db.banca.Database()
  assert len(db.objects()) == 6540
  assert len(db.objects(groups='world')) == 300
  assert len(db.objects(groups='world', subworld='onethird')) == 100
  assert len(db.objects(groups='world', subworld='twothirds')) == 200
  assert len(db.objects(groups='dev')) == 3120
  assert len(db.objects(groups='eval')) == 3120

  # test for the different protocols
  for protocol in db.protocols():
    # assure that the number of enroll files is independent from the protocol
    for group in ('dev', 'eval'):
      assert len(db.objects(groups=group, purposes='enroll')) == 390
      for model_id in db.model_ids(groups=group):
        assert len(db.objects(groups=group, purposes='enroll', model_ids=model_id)) == 15
      for model_id in db.tmodel_ids(groups=group):
        assert len(db.tobjects(groups=group, model_ids=model_id)) == 15

    # check the number of probe files
    for group in ('dev', 'eval'):
      assert len(db.objects(groups=group, purposes='probe')) == 2730
      for model_id in db.model_ids(groups=group):
        assert len(db.objects(groups=group, purposes='probe', model_ids=model_id)) == 105
      for model_id in db.tmodel_ids(groups=group):
        assert len(db.zobjects(groups=group, model_ids=model_id)) == 105


@db_available
def test_annotations():
  # Tests that for all files the annotated eye positions exist and are in correct order
  db = bob.db.banca.Database()
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
  # Tests the bob_dbmanage.py driver API
  from bob.db.base.script.dbmanage import main
  assert main('banca dumplist --self-test'.split()) == 0
  assert main('banca dumplist --protocol=P --class=client --group=dev --purpose=enroll --model-id=1008 --self-test'.split()) == 0
  assert main('banca checkfiles --self-test'.split()) == 0
  assert main('banca reverse 05/1021_f_g2_s05_1026_en_3 --self-test'.split()) == 0
  assert main('banca path 2327 --self-test'.split()) == 0

