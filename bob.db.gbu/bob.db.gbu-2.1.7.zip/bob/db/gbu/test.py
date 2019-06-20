#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Fri May 11 17:20:46 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Sanity checks for the GBU database.
"""

import os, sys
import random
import bob.db.gbu

from bob.db.gbu.models import Client, File

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'gbu'))

  return wrapper


@db_available
def test_clients():
  # Tests that the 'clients()', 'client_ids()', 'models()' and 'model_ids()' functions return the desired number of elements
  db = bob.db.gbu.Database()

  # the protocols training, dev, idiap
  subworlds = db.m_sub_worlds
  protocols = db.m_protocols

  assert len(db.groups()) == 2

  # client counter
  assert len(db.client_ids()) == 782
  assert len(db.clients(groups='world')) == 345
  for subworld in subworlds:
    assert len(db.clients(groups='world', subworld=subworld)) == 345

  assert len(db.clients(groups='dev')) == 437
  for protocol in protocols:
    assert len(db.clients(groups='dev', protocol=protocol)) == 437

  # model counter
  assert len(db.model_ids(protocol_type='gbu', groups='world')) == 345
  assert len(db.model_ids(protocol_type='multi', groups='world')) == 345
  assert len(db.model_ids(protocol_type='gbu', groups='dev')) == 3255
  assert len(db.model_ids(protocol_type='multi', groups='dev')) == 437
  for subworld in subworlds:
    assert len(db.model_ids(protocol_type='multi', groups='world', subworld=subworld)) == 345
  for protocol in protocols:
    assert len(db.model_ids(protocol_type='gbu', groups='dev', protocol=protocol)) == 1085
    assert len(db.model_ids(protocol_type='multi', groups='dev', protocol=protocol)) == 437

  for protocol in protocols:
    # assert that all models of the 'gbu' protocol type
    #  start with "nd1R" or "nd2R", i.e., the file id
    for model in db.models(protocol_type='gbu', protocol=protocol):
      assert isinstance(model, File)
    # assert that all models of the 'multi' protocol type
    #  start with "nd1S", i.e., the client id
    for model in db.models(protocol_type='multi', protocol=protocol):
      assert isinstance(model, Client)


@db_available
def test_objects():
  # Tests that the 'objects()' function returns reasonable output
  db = bob.db.gbu.Database()

  # the training subworlds and the protocols
  subworlds = db.m_sub_worlds
  protocols = db.m_protocols

  for protocol in protocols:
    # The number of files for each purpose is equal to the number of models
    assert len(db.objects(groups='dev', protocol=protocol, purposes='enroll')) == len(db.models(protocol_type='gbu', groups='dev', protocol=protocol))
    assert len(db.objects(groups='dev', protocol=protocol, purposes='probe')) == len(db.models(protocol_type='gbu', groups='dev', protocol=protocol))

  # The following tests might take a while...
  protocol = protocols[0]
  probe_file_count = len(db.objects(protocol_type='gbu', groups='dev', protocol=protocol, purposes='probe'))
  # check that for 'gbu' protocol types, exactly one file per model is returned
  for model_id in random.sample(db.model_ids(protocol_type='gbu', groups='dev', protocol=protocol), 10):
    # assert that there is exactly one file for each enroll purposes per model
    assert len(db.objects(protocol_type='gbu', groups='dev', protocol=protocol, model_ids=[model_id], purposes='enroll')) == 1
    # probe files should always be the same
    assert len(db.objects(protocol_type='gbu', groups='dev', protocol=protocol, model_ids=[model_id], purposes='probe')) == probe_file_count

  # for the 'multi' protocols, there is AT LEAST one file per model (client)
  for model_id in random.sample(db.model_ids(protocol_type='multi', groups='dev', protocol=protocol), 10):
    # assert that there is exactly one file for each enroll purposes per model
    assert len(db.objects(protocol_type='multi', groups='dev', protocol=protocol, model_ids=[model_id], purposes='enroll')) >= 1
    # probe files should always be the same
    assert len(db.objects(protocol_type='multi', groups='dev', protocol=protocol, model_ids=[model_id], purposes='probe')) == probe_file_count


@db_available
def test_file_ids():
  # Tests that the client id's returned by the 'get_client_id_from_file_id()' and 'get_client_id_from_model_id()' functions are correct
  db = bob.db.gbu.Database()

  # we test only one of the protocols
  protocol = random.sample(db.m_protocols,1)

  # for 'gbu' protocols, get_client_id_from_file_id and get_client_id_from_model_id should return the same value
  for model_id in random.sample(db.model_ids(protocol_type='gbu', groups='dev', protocol=protocol), 10):
    for file in db.objects(protocol_type='gbu', groups='dev', protocol=protocol, model_ids=[model_id], purposes='enroll'):
      assert db.get_client_id_from_file_id(file.id) == db.get_client_id_from_model_id(model_id, protocol_type='gbu')

  for model_id in random.sample(db.model_ids(protocol_type='multi', groups='dev', protocol=protocol), 10):
    # for 'multi' protocols, get_client_id_from_model_id should return the client id.
    assert db.get_client_id_from_model_id(model_id, protocol_type='multi') == model_id
    # and also get_client_id_from_file_id should return the model id
    for file in db.objects(protocol_type='multi', groups='dev', protocol=protocol, model_ids=[model_id], purposes='enroll'):
      assert db.get_client_id_from_file_id(file.id) == model_id


@db_available
def test_annotations():
  # Tests that the annotations are available for all files
  db = bob.db.gbu.Database()

  # we test only one of the protocols
  for protocol in random.sample(db.m_protocols, 1):
    files = db.objects(protocol=protocol)
    for file in random.sample(files, 1000):
      annotations = db.annotations(file)
      assert 'leye' in annotations and 'reye' in annotations
      assert len(annotations['leye']) == 2
      assert len(annotations['reye']) == 2


@db_available
def test_driver_api():
  # Tests the functions of the driver API
  from bob.db.base.script.dbmanage import main
  assert main('gbu dumplist --self-test'.split()) == 0
  assert main('gbu dumplist --group=dev --subworld=x8 --protocol=Good --purpose=enroll --self-test'.split()) == 0
  assert main('gbu checkfiles --self-test'.split()) == 0
  assert main('gbu reverse Target/Original/04542d172 --self-test'.split()) == 0
  assert main('gbu path 513 --self-test'.split()) == 0

