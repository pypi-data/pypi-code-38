#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
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

"""A few checks for the CAS-PEAL database.
"""

import os, sys
import unittest
import bob.db.caspeal
import random

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'caspeal'))

  return wrapper


@db_available
def test_clients():
  # Checks the clients
  db = bob.db.caspeal.Database()

  # test that the expected number of clients is returned
  assert len(db.groups()) == 2
  assert len(db.client_ids()) == 1040
  assert len(db.client_ids(genders='M')) == 595
  assert len(db.client_ids(genders='F')) == 445
  assert len(db.client_ids(ages='Y')) == 1026
  assert len(db.client_ids(ages='M')) == 10
  assert len(db.client_ids(ages='O')) == 4
  assert len(db.client_ids(groups='world')) == 300
  assert len(db.client_ids(groups='dev')) == 1040

  assert db.model_ids() == [client.id for client in db.clients()]


@db_available
def test_objects():
  # Checks the objects
  db = bob.db.caspeal.Database()

  # test that the objects() function returns reasonable numbers of files
  assert len(db.objects()) == 31064 if db.has_protocol('pose') else 9232

  # number of world files for the two genders
  assert len(db.objects(groups='world')) == 1200
  assert len(db.objects(groups='world', genders='F')) == 512
  assert len(db.objects(groups='world', genders='M')) == 688
  # no world files for a pose other than 'M+00'
  assert len(db.objects(groups='world', poses='M+00')) == 1200
  assert len(db.objects(groups='world', poses='D+45')) == 0

  # enroll files are independent from the protocol
  assert len(db.objects(groups='dev', purposes='enroll')) == 1040

  # probe files, see description of the database
  assert len(db.objects(groups='dev', purposes='probe', protocol='accessory')) == 2285
  assert len(db.objects(groups='dev', purposes='probe', protocol='aging')) == 66
  assert len(db.objects(groups='dev', purposes='probe', protocol='background')) == 553
  assert len(db.objects(groups='dev', purposes='probe', protocol='distance')) == 275
  assert len(db.objects(groups='dev', purposes='probe', protocol='expression')) == 1570
  assert len(db.objects(groups='dev', purposes='probe', protocol='lighting')) == 2243

  # This does not work. It seems that there are more images than given in the database description
  #assert len(db.objects(groups='dev', purposes='probe', protocol='pose')) == 4998+4993+4998
  # On the web-page they claim to have 21840 pose images (3 elevations * 7 azimuth * 1040 people
  # but it seems that we ar missing some files...
  if db.has_protocol('pose'):
    assert len(db.objects(groups='dev', purposes='probe', protocol='pose')) == 21832
    # all pose images have neutral expression, frontal light, no accessoriesm the same distance, were taken at the same session with the same background
    assert len(db.objects(groups='dev', purposes='probe', protocol='pose', expressions='N', lightings='EU+00', accessories=0, distances=0, sessions=0, backgrounds='B')) == 21832


@db_available
def test_annotations():
  # Tests that the annotations are available for all files
  db = bob.db.caspeal.Database()

  # we test only one of the protocols
  for protocol in random.sample(db.m_protocols, 1):
    files = db.objects(protocol=protocol)
    # ...and some of the files
    for file in random.sample(files, 1000):
      annotations = db.annotations(file)
      assert 'leye' in annotations and 'reye' in annotations
      assert len(annotations['leye']) == 2
      assert len(annotations['reye']) == 2

@db_available
def test_driver_api():
  # Tests the bob_dbmanage.py driver interface
  from bob.db.base.script.dbmanage import main
  assert main('caspeal dumplist --self-test'.split()) == 0
  assert main('caspeal dumplist  --group=dev --purpose=enroll --client=622 --protocol=aging --session=0 --gender=F --expression=N --lighting=EU+00 --pose=M+00 --distance=0 --accessory=0 --age=Y --background=B --self-test'.split()) == 0
  assert main('caspeal checkfiles --self-test'.split()) == 0
  assert main('caspeal reverse FRONTAL/Aging/MY_000064_IEU+00_PM+00_EN_A0_D0_T2_BB_M0_R1_S0 --self-test'.split()) == 0
  assert main('caspeal path 42 --self-test'.split()) == 0

