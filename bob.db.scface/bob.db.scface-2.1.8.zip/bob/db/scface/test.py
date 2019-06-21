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

"""A few checks at the SCface database.
"""

import os, sys
import bob.db.scface

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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'scface'))

  return wrapper

#from bob.db.scface.models import *

@db_available
def test_clients():

  db = bob.db.scface.Database()

  assert len(db.groups()) == 3 # 3 groups
  clients = db.clients()
  assert len(clients) == 130 #130 clients used by the protocols
  # Number of clients in each set
  c_dev = db.clients(groups='dev')
  assert len(c_dev) == 44 #44 clients in the dev set
  c_eval = db.clients(groups='eval')
  assert len(c_eval) == 43 #43 clients in the eval set
  c_world = db.clients(groups='world')
  assert len(c_world) == 43 #43 clients in the world set
  # Check client ids
  assert db.has_client_id(1)
  assert not db.has_client_id(395)
  # Check subworld
  assert len(db.clients(groups='world', subworld='onethird')) == 14
  assert len(db.clients(groups='world', subworld='twothirds')) == 29
  # Check files relationship
  c = db.client(1)
  assert len(c.files) == 23


@db_available
def test_protocols():

  db = bob.db.scface.Database()

  assert len(db.protocols()) == 5
  assert len(db.protocol_names()) == 5
  assert db.has_protocol('combined')

  assert len(db.subworlds()) == 2
  assert len(db.subworld_names()) == 2
  assert db.has_subworld('onethird')


@db_available
def test_objects():

  db = bob.db.scface.Database()

  # Protocol combined
  # World group
  assert len(db.objects(protocol='combined', groups='world')) == 688
  assert len(db.objects(protocol='combined', groups='world', purposes='train')) == 688
  assert len(db.objects(protocol='combined', groups='world', purposes='train', model_ids=3)) == 16

  # Dev group
  assert len(db.objects(protocol='combined', groups='dev')) == 704
  assert len(db.objects(protocol='combined', groups='dev', purposes='enroll')) == 44
  assert len(db.objects(protocol='combined', groups='dev', purposes='probe')) == 660
  assert len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='client')) == 660
  assert len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='impostor')) == 660
  assert len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='client', model_ids=47)) == 15
  assert len(db.objects(protocol='combined', groups='dev', purposes='probe', classes='impostor', model_ids=47)) == 645

  # Eval group
  assert len(db.objects(protocol='combined', groups='eval')) == 688
  assert len(db.objects(protocol='combined', groups='eval', purposes='enroll')) == 43
  assert len(db.objects(protocol='combined', groups='eval', purposes='probe')) == 645
  assert len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='client')) == 645
  assert len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='impostor')) == 645
  assert len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='client', model_ids=100)) == 15
  assert len(db.objects(protocol='combined', groups='eval', purposes='probe', classes='impostor', model_ids=100)) == 630

  # Protocol close
  # World group
  assert len(db.objects(protocol='close', groups='world')) == 688
  assert len(db.objects(protocol='close', groups='world', purposes='train')) == 688
  assert len(db.objects(protocol='close', groups='world', purposes='train', model_ids=3)) == 16

  # Dev group
  assert len(db.objects(protocol='close', groups='dev')) == 264
  assert len(db.objects(protocol='close', groups='dev', purposes='enroll')) == 44
  assert len(db.objects(protocol='close', groups='dev', purposes='probe')) == 220
  assert len(db.objects(protocol='close', groups='dev', purposes='probe', classes='client')) == 220
  assert len(db.objects(protocol='close', groups='dev', purposes='probe', classes='impostor')) == 220
  assert len(db.objects(protocol='close', groups='dev', purposes='probe', classes='client', model_ids=47)) == 5
  assert len(db.objects(protocol='close', groups='dev', purposes='probe', classes='impostor', model_ids=47)) == 215

  # Eval group
  assert len(db.objects(protocol='close', groups='eval')) == 258
  assert len(db.objects(protocol='close', groups='eval', purposes='enroll')) == 43
  assert len(db.objects(protocol='close', groups='eval', purposes='probe')) == 215
  assert len(db.objects(protocol='close', groups='eval', purposes='probe', classes='client')) == 215
  assert len(db.objects(protocol='close', groups='eval', purposes='probe', classes='impostor')) == 215
  assert len(db.objects(protocol='close', groups='eval', purposes='probe', classes='client', model_ids=100)) == 5
  assert len(db.objects(protocol='close', groups='eval', purposes='probe', classes='impostor', model_ids=100)) == 210

  # Protocol medium
  # World group
  assert len(db.objects(protocol='medium', groups='world')) == 688
  assert len(db.objects(protocol='medium', groups='world', purposes='train')) == 688
  assert len(db.objects(protocol='medium', groups='world', purposes='train', model_ids=3)) == 16

  # Dev group
  assert len(db.objects(protocol='medium', groups='dev')) == 264
  assert len(db.objects(protocol='medium', groups='dev', purposes='enroll')) == 44
  assert len(db.objects(protocol='medium', groups='dev', purposes='probe')) == 220
  assert len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='client')) == 220
  assert len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='impostor')) == 220
  assert len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='client', model_ids=47)) == 5
  assert len(db.objects(protocol='medium', groups='dev', purposes='probe', classes='impostor', model_ids=47)) == 215

  # Eval group
  assert len(db.objects(protocol='medium', groups='eval')) == 258
  assert len(db.objects(protocol='medium', groups='eval', purposes='enroll')) == 43
  assert len(db.objects(protocol='medium', groups='eval', purposes='probe')) == 215
  assert len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='client')) == 215
  assert len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='impostor')) == 215
  assert len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='client', model_ids=100)) == 5
  assert len(db.objects(protocol='medium', groups='eval', purposes='probe', classes='impostor', model_ids=100)) == 210

  # Protocol far
  # World group
  assert len(db.objects(protocol='far', groups='world')) == 688
  assert len(db.objects(protocol='far', groups='world', purposes='train')) == 688
  assert len(db.objects(protocol='far', groups='world', purposes='train', model_ids=3)) == 16

  # Dev group
  assert len(db.objects(protocol='far', groups='dev')) == 264
  assert len(db.objects(protocol='far', groups='dev', purposes='enroll')) == 44
  assert len(db.objects(protocol='far', groups='dev', purposes='probe')) == 220
  assert len(db.objects(protocol='far', groups='dev', purposes='probe', classes='client')) == 220
  assert len(db.objects(protocol='far', groups='dev', purposes='probe', classes='impostor')) == 220
  assert len(db.objects(protocol='far', groups='dev', purposes='probe', classes='client', model_ids=47)) == 5
  assert len(db.objects(protocol='far', groups='dev', purposes='probe', classes='impostor', model_ids=47)) == 215

  # Eval group
  assert len(db.objects(protocol='far', groups='eval')) == 258
  assert len(db.objects(protocol='far', groups='eval', purposes='enroll')) == 43
  assert len(db.objects(protocol='far', groups='eval', purposes='probe')) == 215
  assert len(db.objects(protocol='far', groups='eval', purposes='probe', classes='client')) == 215
  assert len(db.objects(protocol='far', groups='eval', purposes='probe', classes='impostor')) == 215
  assert len(db.objects(protocol='far', groups='eval', purposes='probe', classes='client', model_ids=100)) == 5
  assert len(db.objects(protocol='far', groups='eval', purposes='probe', classes='impostor', model_ids=100)) == 210

  # Protocol IR
  # World group
  assert len(db.objects(protocol='IR', groups='world')) == 301
  assert len(db.objects(protocol='IR', groups='world', purposes='train')) == 301
  assert len(db.objects(protocol='IR', groups='world', purposes='train', model_ids=3)) == 7

  # Dev group
  assert len(db.objects(protocol='IR', groups='dev')) == 88
  assert len(db.objects(protocol='IR', groups='dev', purposes='enroll')) == 44
  assert len(db.objects(protocol='IR', groups='dev', purposes='probe')) == 44
  assert len(db.objects(protocol='IR', groups='dev', purposes='probe', classes='client')) == 44
  assert len(db.objects(protocol='IR', groups='dev', purposes='probe', classes='impostor')) == 44
  assert len(db.objects(protocol='IR', groups='dev', purposes='probe', classes='client', model_ids=47)) == 1
  assert len(db.objects(protocol='IR', groups='dev', purposes='probe', classes='impostor', model_ids=47)) == 43

  # Eval group
  assert len(db.objects(protocol='IR', groups='eval')) == 86
  assert len(db.objects(protocol='IR', groups='eval', purposes='enroll')) == 43
  assert len(db.objects(protocol='IR', groups='eval', purposes='probe')) == 43
  assert len(db.objects(protocol='IR', groups='eval', purposes='probe', classes='client')) == 43
  assert len(db.objects(protocol='IR', groups='eval', purposes='probe', classes='impostor')) == 43
  assert len(db.objects(protocol='IR', groups='eval', purposes='probe', classes='client', model_ids=100)) == 1
  assert len(db.objects(protocol='IR', groups='eval', purposes='probe', classes='impostor', model_ids=100)) == 42

  # TODO: T-norm and Z-norm files


@db_available
def test_annotations():
  # Tests that for all files the annotated eye positions exist and are in correct order
  db = bob.db.scface.Database()

  for f in db.objects():
    annotations = db.annotations(f)
    assert annotations is not None
    assert len(annotations) == 4
    assert 'leye' in annotations
    assert 'reye' in annotations
    assert 'nose' in annotations
    assert 'mouth' in annotations
    assert len(annotations['reye']) == 2
    assert len(annotations['leye']) == 2
    assert len(annotations['nose']) == 2
    assert len(annotations['mouth']) == 2
    # assert that the eye positions are not exchanged
    assert annotations['leye'][1] > annotations['reye'][1]
    # assert that the vertical positions of eyes, nose and mouth fit
    assert annotations['leye'][0] < annotations['nose'][0]
    assert annotations['reye'][0] < annotations['nose'][0]
    assert annotations['nose'][0] < annotations['mouth'][0]


@db_available
def test_driver_api():
  # Tests the bob_dbmanage.py driver API
  from bob.db.base.script.dbmanage import main
  assert main('scface dumplist --self-test'.split()) == 0
  assert main('scface dumplist --protocol=combined --class=client --group=dev --purpose=enroll --client=66 --self-test'.split()) == 0
  assert main('scface checkfiles --self-test'.split()) == 0
  assert main('scface reverse mugshot_frontal_cropped_all/066_frontal --self-test'.split()) == 0
  assert main('scface path 65 --self-test'.split()) == 0
