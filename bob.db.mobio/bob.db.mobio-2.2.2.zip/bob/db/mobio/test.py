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

"""A few checks at the MOBIO database.
"""

import os, sys
import bob.db.mobio
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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'mobio'))

  return wrapper


@db_available
def test_clients():

  db = bob.db.mobio.Database()

  assert len(db.groups()) == 3
  clients = db.clients()
  assert len(clients) == 150
  # Number of clients in each set
  c_dev = db.clients(groups='dev')
  assert len(c_dev) == 42
  c_eval = db.clients(groups='eval')
  assert len(c_eval) == 58
  c_world = db.clients(groups='world')
  assert len(c_world) == 50
  # Check client ids
  assert db.has_client_id(204)
  assert not db.has_client_id(395)
  # Check subworld
  assert len(db.clients(groups='world', subworld='onethird')) == 16
  assert len(db.clients(groups='world', subworld='twothirds')) == 34
  assert len(db.clients(groups='world', subworld='twothirds-subsampled')) == 34
  # Check files relationship
  c = db.client(204)
  assert len(c.files) == 213
  # Check T-Norm and Z-Norm clients
  assert len(db.tclients(protocol='mobile0-female')) == 16
  assert len(db.tclients(protocol='mobile0-male')) == 16
  assert len(db.tclients(protocol='mobile1-female')) == 16
  assert len(db.tclients(protocol='mobile1-male')) == 16
  assert len(db.tclients(protocol='laptop1-female')) == 16
  assert len(db.tclients(protocol='laptop1-male')) == 16
  assert len(db.tclients(protocol='laptop_mobile1-female')) == 16
  assert len(db.tclients(protocol='laptop_mobile1-male')) == 16
  assert len(db.tclients(protocol='male')) == 16
  assert len(db.tclients(protocol='female')) == 16
  assert len(db.zclients()) == 16
  assert len(db.zclients(protocol='mobile0-female')) == 16
  assert len(db.zclients(protocol='mobile0-male')) == 16
  assert len(db.zclients(protocol='mobile1-female')) == 16
  assert len(db.zclients(protocol='mobile1-male')) == 16
  assert len(db.zclients(protocol='laptop1-female')) == 16
  assert len(db.zclients(protocol='laptop1-male')) == 16
  assert len(db.zclients(protocol='laptop_mobile1-female')) == 16
  assert len(db.zclients(protocol='laptop_mobile1-male')) == 16
  assert len(db.zclients(protocol='male')) == 16
  assert len(db.zclients(protocol='female')) == 16
  # Check T-Norm models
  assert len(db.tmodels(protocol='mobile0-female')) == 192
  assert len(db.tmodels(protocol='mobile0-male')) == 192
  assert len(db.tmodels(protocol='mobile1-female')) == 208
  assert len(db.tmodels(protocol='mobile1-male')) == 208
  assert len(db.tmodels(protocol='laptop1-female')) == 208
  assert len(db.tmodels(protocol='laptop1-male')) == 208
  assert len(db.tmodels(protocol='laptop_mobile1-female')) == 208
  assert len(db.tmodels(protocol='laptop_mobile1-male')) == 208
  assert len(db.tmodels(protocol='male')) == 192
  assert len(db.tmodels(protocol='female')) == 192


@db_available
def test_protocols():

  db = bob.db.mobio.Database()

  assert len(db.protocols()) == 8
  assert len(db.protocol_names()) == 8
  assert db.has_protocol('mobile0-male')
  assert db.has_protocol('mobile0-female')
  assert db.has_protocol('mobile1-male')
  assert db.has_protocol('mobile1-female')
  assert db.has_protocol('laptop1-male')
  assert db.has_protocol('laptop1-female')
  assert db.has_protocol('laptop_mobile1-male')
  assert db.has_protocol('laptop_mobile1-female')
  assert db.has_protocol('male') # alias to 'mobile0-male'
  assert db.has_protocol('female') # alias 'mobile0-female'

  assert len(db.subworlds()) == 3
  assert len(db.subworld_names()) == 3
  assert db.has_subworld('onethird')


@db_available
def test_objects():

  db = bob.db.mobio.Database()

  # Protocol mobile0-female
  # World group
  assert len(db.objects(protocol='mobile0-female', groups='world')) == 9600
  assert len(db.objects(protocol='mobile0-female', groups='world', purposes='train')) == 9600
  assert len(db.objects(protocol='mobile0-female', groups='world', gender='female')) == 2496
  assert len(db.objects(protocol='mobile0-female', groups='world', purposes='train', model_ids=204)) == 192

  # Dev group
  assert len(db.objects(protocol='mobile0-female', groups='dev')) == 1980
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='enroll')) == 90
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='probe')) == 1890
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='probe', classes='client')) == 1890
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='probe', classes='impostor')) == 1890
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='probe', classes='client', model_ids=118)) == 105
  assert len(db.objects(protocol='mobile0-female', groups='dev', purposes='probe', classes='impostor', model_ids=118)) == 1785

  # Eval group
  assert len(db.objects(protocol='mobile0-female', groups='eval')) == 2200
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='enroll')) == 100
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='probe')) == 2100
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='probe', classes='client')) == 2100
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='probe', classes='impostor')) == 2100
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='probe', classes='client', model_ids=7)) == 105
  assert len(db.objects(protocol='mobile0-female', groups='eval', purposes='probe', classes='impostor', model_ids=7)) == 1995

  # Protocol mobile0-male
  # World group
  assert len(db.objects(protocol='mobile0-male', groups='world')) == 9600
  assert len(db.objects(protocol='mobile0-male', groups='world', purposes='train')) == 9600
  assert len(db.objects(protocol='mobile0-male', groups='world', gender='male')) == 7104
  assert len(db.objects(protocol='mobile0-male', groups='world', purposes='train', model_ids=204)) == 192

  # Dev group
  assert len(db.objects(protocol='mobile0-male', groups='dev')) == 2640
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='enroll')) == 120
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='probe')) == 2520
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='probe', classes='client')) == 2520
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='probe', classes='impostor')) == 2520
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='probe', classes='client', model_ids=103)) == 105
  assert len(db.objects(protocol='mobile0-male', groups='dev', purposes='probe', classes='impostor', model_ids=103)) == 2415

  # Eval group
  assert len(db.objects(protocol='mobile0-male', groups='eval')) == 4180
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='enroll')) == 190
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='probe')) == 3990
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='probe', classes='client')) == 3990
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='probe', classes='impostor')) == 3990
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='probe', classes='client', model_ids=1)) == 105
  assert len(db.objects(protocol='mobile0-male', groups='eval', purposes='probe', classes='impostor', model_ids=1)) == 3885


  # Protocol mobile1-female
  # World group
  assert len(db.objects(protocol='mobile1-female', groups='world')) == 10650
  assert len(db.objects(protocol='mobile1-female', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='mobile1-female', groups='world', gender='female')) == 2769
  assert len(db.objects(protocol='mobile1-female', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='mobile1-female', groups='dev')) == 1980
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='enroll')) == 90
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='probe')) == 1890
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='probe', classes='client')) == 1890
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='probe', classes='impostor')) == 1890
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='probe', classes='client', model_ids=118)) == 105
  assert len(db.objects(protocol='mobile1-female', groups='dev', purposes='probe', classes='impostor', model_ids=118)) == 1785

  # Eval group
  assert len(db.objects(protocol='mobile1-female', groups='eval')) == 2200
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='enroll')) == 100
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='probe')) == 2100
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='probe', classes='client')) == 2100
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='probe', classes='impostor')) == 2100
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='probe', classes='client', model_ids=7)) == 105
  assert len(db.objects(protocol='mobile1-female', groups='eval', purposes='probe', classes='impostor', model_ids=7)) == 1995

  # Protocol mobile1-male
  # World group
  assert len(db.objects(protocol='mobile1-male', groups='world')) == 10650
  assert len(db.objects(protocol='mobile1-male', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='mobile1-male', groups='world', gender='male')) == 7881
  assert len(db.objects(protocol='mobile1-male', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='mobile1-male', groups='dev')) == 2640
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='enroll')) == 120
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='probe')) == 2520
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='probe', classes='client')) == 2520
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='probe', classes='impostor')) == 2520
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='probe', classes='client', model_ids=103)) == 105
  assert len(db.objects(protocol='mobile1-male', groups='dev', purposes='probe', classes='impostor', model_ids=103)) == 2415

  # Eval group
  assert len(db.objects(protocol='mobile1-male', groups='eval')) == 4180
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='enroll')) == 190
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='probe')) == 3990
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='probe', classes='client')) == 3990
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='probe', classes='impostor')) == 3990
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='probe', classes='client', model_ids=1)) == 105
  assert len(db.objects(protocol='mobile1-male', groups='eval', purposes='probe', classes='impostor', model_ids=1)) == 3885


  # Protocol laptop1-female
  # World group
  assert len(db.objects(protocol='laptop1-female', groups='world')) == 10650
  assert len(db.objects(protocol='laptop1-female', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='laptop1-female', groups='world', gender='female')) == 2769
  assert len(db.objects(protocol='laptop1-female', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='laptop1-female', groups='dev')) == 1980
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='enroll')) == 90
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='probe')) == 1890
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='probe', classes='client')) == 1890
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='probe', classes='impostor')) == 1890
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='probe', classes='client', model_ids=118)) == 105
  assert len(db.objects(protocol='laptop1-female', groups='dev', purposes='probe', classes='impostor', model_ids=118)) == 1785

  # Eval group
  assert len(db.objects(protocol='laptop1-female', groups='eval')) == 2200
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='enroll')) == 100
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='probe')) == 2100
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='probe', classes='client')) == 2100
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='probe', classes='impostor')) == 2100
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='probe', classes='client', model_ids=7)) == 105
  assert len(db.objects(protocol='laptop1-female', groups='eval', purposes='probe', classes='impostor', model_ids=7)) == 1995

  # Protocol laptop1-male
  # World group
  assert len(db.objects(protocol='laptop1-male', groups='world')) == 10650
  assert len(db.objects(protocol='laptop1-male', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='laptop1-male', groups='world', gender='male')) == 7881
  assert len(db.objects(protocol='laptop1-male', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='laptop1-male', groups='dev')) == 2640
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='enroll')) == 120
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='probe')) == 2520
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='probe', classes='client')) == 2520
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='probe', classes='impostor')) == 2520
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='probe', classes='client', model_ids=103)) == 105
  assert len(db.objects(protocol='laptop1-male', groups='dev', purposes='probe', classes='impostor', model_ids=103)) == 2415

  # Eval group
  assert len(db.objects(protocol='laptop1-male', groups='eval')) == 4180
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='enroll')) == 190
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='probe')) == 3990
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='probe', classes='client')) == 3990
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='probe', classes='impostor')) == 3990
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='probe', classes='client', model_ids=1)) == 105
  assert len(db.objects(protocol='laptop1-male', groups='eval', purposes='probe', classes='impostor', model_ids=1)) == 3885


  # Protocol laptop_mobile1-female
  # World group
  assert len(db.objects(protocol='laptop_mobile1-female', groups='world')) == 10650
  assert len(db.objects(protocol='laptop_mobile1-female', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='laptop_mobile1-female', groups='world', gender='female')) == 2769
  assert len(db.objects(protocol='laptop_mobile1-female', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev')) == 2070
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='enroll')) == 180
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='probe')) == 1890
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='probe', classes='client')) == 1890
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='probe', classes='impostor')) == 1890
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='probe', classes='client', model_ids=118)) == 105
  assert len(db.objects(protocol='laptop_mobile1-female', groups='dev', purposes='probe', classes='impostor', model_ids=118)) == 1785

  # Eval group
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval')) == 2300
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='enroll')) == 200
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='probe')) == 2100
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='probe', classes='client')) == 2100
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='probe', classes='impostor')) == 2100
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='probe', classes='client', model_ids=7)) == 105
  assert len(db.objects(protocol='laptop_mobile1-female', groups='eval', purposes='probe', classes='impostor', model_ids=7)) == 1995

  # Protocol laptop_mobile1-male
  # World group
  assert len(db.objects(protocol='laptop_mobile1-male', groups='world')) == 10650
  assert len(db.objects(protocol='laptop_mobile1-male', groups='world', purposes='train')) == 10650
  assert len(db.objects(protocol='laptop_mobile1-male', groups='world', gender='male')) == 7881
  assert len(db.objects(protocol='laptop_mobile1-male', groups='world', purposes='train', model_ids=204)) == 213

  # Dev group
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev')) == 2760
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='enroll')) == 240
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='probe')) == 2520
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='probe', classes='client')) == 2520
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='probe', classes='impostor')) == 2520
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='probe', classes='client', model_ids=103)) == 105
  assert len(db.objects(protocol='laptop_mobile1-male', groups='dev', purposes='probe', classes='impostor', model_ids=103)) == 2415

  # Eval group
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval')) == 4370
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='enroll')) == 380
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='probe')) == 3990
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='probe', classes='client')) == 3990
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='probe', classes='impostor')) == 3990
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='probe', classes='client', model_ids=1)) == 105
  assert len(db.objects(protocol='laptop_mobile1-male', groups='eval', purposes='probe', classes='impostor', model_ids=1)) == 3885


  # Protocol female
  # World group
  assert len(db.objects(protocol='female', groups='world')) == 9600
  assert len(db.objects(protocol='female', groups='world', purposes='train')) == 9600
  assert len(db.objects(protocol='female', groups='world', gender='female')) == 2496
  assert len(db.objects(protocol='female', groups='world', purposes='train', model_ids=204)) == 192

  # Dev group
  assert len(db.objects(protocol='female', groups='dev')) == 1980
  assert len(db.objects(protocol='female', groups='dev', purposes='enroll')) == 90
  assert len(db.objects(protocol='female', groups='dev', purposes='probe')) == 1890
  assert len(db.objects(protocol='female', groups='dev', purposes='probe', classes='client')) == 1890
  assert len(db.objects(protocol='female', groups='dev', purposes='probe', classes='impostor')) == 1890
  assert len(db.objects(protocol='female', groups='dev', purposes='probe', classes='client', model_ids=118)) == 105
  assert len(db.objects(protocol='female', groups='dev', purposes='probe', classes='impostor', model_ids=118)) == 1785

  # Eval group
  assert len(db.objects(protocol='female', groups='eval')) == 2200
  assert len(db.objects(protocol='female', groups='eval', purposes='enroll')) == 100
  assert len(db.objects(protocol='female', groups='eval', purposes='probe')) == 2100
  assert len(db.objects(protocol='female', groups='eval', purposes='probe', classes='client')) == 2100
  assert len(db.objects(protocol='female', groups='eval', purposes='probe', classes='impostor')) == 2100
  assert len(db.objects(protocol='female', groups='eval', purposes='probe', classes='client', model_ids=7)) == 105
  assert len(db.objects(protocol='female', groups='eval', purposes='probe', classes='impostor', model_ids=7)) == 1995

  # Protocol male
  # World group
  assert len(db.objects(protocol='male', groups='world')) == 9600
  assert len(db.objects(protocol='male', groups='world', purposes='train')) == 9600
  assert len(db.objects(protocol='male', groups='world', gender='male')) == 7104
  assert len(db.objects(protocol='male', groups='world', purposes='train', model_ids=204)) == 192

  # Dev group
  assert len(db.objects(protocol='male', groups='dev')) == 2640
  assert len(db.objects(protocol='male', groups='dev', purposes='enroll')) == 120
  assert len(db.objects(protocol='male', groups='dev', purposes='probe')) == 2520
  assert len(db.objects(protocol='male', groups='dev', purposes='probe', classes='client')) == 2520
  assert len(db.objects(protocol='male', groups='dev', purposes='probe', classes='impostor')) == 2520
  assert len(db.objects(protocol='male', groups='dev', purposes='probe', classes='client', model_ids=103)) == 105
  assert len(db.objects(protocol='male', groups='dev', purposes='probe', classes='impostor', model_ids=103)) == 2415

  # Eval group
  assert len(db.objects(protocol='male', groups='eval')) == 4180
  assert len(db.objects(protocol='male', groups='eval', purposes='enroll')) == 190
  assert len(db.objects(protocol='male', groups='eval', purposes='probe')) == 3990
  assert len(db.objects(protocol='male', groups='eval', purposes='probe', classes='client')) == 3990
  assert len(db.objects(protocol='male', groups='eval', purposes='probe', classes='impostor')) == 3990
  assert len(db.objects(protocol='male', groups='eval', purposes='probe', classes='client', model_ids=1)) == 105
  assert len(db.objects(protocol='male', groups='eval', purposes='probe', classes='impostor', model_ids=1)) == 3885


  # T-Norm and Z-Norm files
  # T-Norm
  assert len(db.tobjects(protocol='mobile0-female')) == 3072
  assert len(db.tobjects(protocol='mobile0-male')) == 3072
  assert len(db.tobjects(protocol='mobile1-female')) == 3408
  assert len(db.tobjects(protocol='mobile1-male')) == 3408
  assert len(db.tobjects(protocol='laptop1-female')) == 3408
  assert len(db.tobjects(protocol='laptop1-male')) == 3408
  assert len(db.tobjects(protocol='laptop_mobile1-female')) == 3408
  assert len(db.tobjects(protocol='laptop_mobile1-male')) == 3408
  assert len(db.tobjects(protocol='male', speech_type='p')) == 960
  assert len(db.tobjects(protocol='female', speech_type='p')) == 960
  assert len(db.tobjects(protocol='male',  speech_type='p', model_ids=('204_01_mobile',))) == 5

  # Z-Norm files
  assert len(db.zobjects()) == 1920
  assert len(db.zobjects(model_ids=(204,))) == 120
  assert len(db.zobjects(protocol='male', speech_type=['p','r','l','f'])) == 3072
  assert len(db.zobjects(protocol='male', speech_type=['p','r','l','f'], model_ids=(204,))) == 192


@db_available
def test_annotations():
  # read some annotation files and test it's content
  dir = "/idiap/resource/database/mobio/IMAGE_ANNOTATIONS"
  if not os.path.exists(dir):
    raise SkipTest("The annotation directory '%s' is not available, annotations can't be tested." % dir)
  db = bob.db.mobio.Database(annotation_directory = dir)
  import random
  files = random.sample(db.all_files(), 1000)
  for file in files:
    annotations = db.annotations(file)
    assert annotations is not None
    assert 'leye' in annotations
    assert 'reye' in annotations
    assert len(annotations['leye']) == 2
    assert len(annotations['reye']) == 2


@db_available
def test_driver_api():

  from bob.db.base.script.dbmanage import main
  assert main('mobio dumplist --self-test'.split()) == 0
  assert main('mobio dumplist --protocol=mobile0-male --class=client --group=dev --purpose=enroll --client=115 --self-test'.split()) == 0
  assert main('mobio dumplist --protocol=male --class=client --group=dev --purpose=enroll --client=115 --self-test'.split()) == 0
  assert main('mobio checkfiles --self-test'.split()) == 0
  assert main('mobio reverse uoulu/m313/01_mobile/m313_01_p01_i0_0 --self-test'.split()) == 0
  assert main('mobio path 21132 --self-test'.split()) == 0

