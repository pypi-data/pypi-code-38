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

"""A few checks at the AR Face database.
"""

import os, sys
import unittest
import bob.db.arface

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'arface'))

  return wrapper


@db_available
def test_clients():
  # test that the expected number of clients is returned
  db = bob.db.arface.Database()
  assert len(db.groups()) == 3
  assert len(db.client_ids()) == 136
  assert len(db.client_ids(genders='m')) == 76
  assert len(db.client_ids(genders='w')) == 60
  assert len(db.client_ids(groups='world')) == 50
  assert len(db.client_ids(groups='dev')) == 43
  assert len(db.client_ids(groups='eval')) == 43
  assert len(db.client_ids(groups='dev', genders='m')) == 24
  assert len(db.client_ids(groups='eval', genders='m')) == 24

  assert db.model_ids() == [client.id for client in db.clients()]


@db_available
def test_files():
  # test that the files() function returns reasonable numbers of files
  db = bob.db.arface.Database()
  assert len(db.objects(protocol='all')) == 3312

  # number of world files for the two genders
  assert len(db.objects(groups='world', protocol='all')) == 1076
  assert len(db.objects(groups='world', genders='m', protocol='all')) == 583
  assert len(db.objects(groups='world', genders='w', protocol='all')) == 493

  # number of world files are identical for all protocols
  assert len(db.objects(groups='world', protocol='expression')) == 1076
  assert len(db.objects(groups='world', protocol='illumination')) == 1076
  assert len(db.objects(groups='world', protocol='occlusion')) == 1076
  assert len(db.objects(groups='world', protocol='occlusion_and_illumination')) == 1076

  for g in ['dev', 'eval']:
    # assert that each dev and eval client has 26 files
    model_ids = db.model_ids(groups=g)
    assert len(db.objects(groups=g, protocol='all')) == 26 * len(model_ids)
    for protocol in db.m_protocols:
      assert len(db.objects(groups=g, purposes='enroll', protocol=protocol)) == 2 * len(model_ids)
    for model_id in model_ids:
      # two enroll files for all protocols
      for protocol in db.m_protocols:
        assert len(db.objects(groups=g, model_ids = model_id, purposes='enroll', protocol=protocol)) == 2

      # 24 probe files for the (default) 'all' protocol
      assert len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='all')) == 24 * len(model_ids)
      # 6 probe files for the 'expression' protocol
      assert len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='expression')) == 6 * len(model_ids)
      # 6 probe files for the 'illumination' protocol
      assert len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='illumination')) == 6 * len(model_ids)
      # 4 probe files for the 'occlusion' protocol
      assert len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='occlusion')) == 4 * len(model_ids)
      # and finally 8 probe files for the 'occlusion_and_illumination' protocol
      assert len(db.objects(groups=g, model_ids = model_id, purposes='probe', protocol='occlusion_and_illumination')) == 8 * len(model_ids)


@db_available
def test_annotations():
  # Tests that for all files the annotated eye positions exist and are in correct order
  db = bob.db.arface.Database()
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
  assert main('arface dumplist --self-test'.split()) == 0
  assert main('arface dumplist --group=dev --protocol=expression --purpose=probe --session=first --client=m-001 --gender=m --expression=anger --illumination=front --occlusion=none --self-test'.split()) == 0
  assert main('arface checkfiles --self-test'.split()) == 0
  # actually, path's and id's are identical in ARface. Nonetheless, test the API:
  assert main('arface reverse m-038-20 --self-test'.split()) == 0
  assert main('arface path m-038-20 --self-test'.split()) == 0


