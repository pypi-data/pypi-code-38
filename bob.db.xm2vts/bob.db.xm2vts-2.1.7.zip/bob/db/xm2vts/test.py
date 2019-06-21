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

"""A few checks at the XM2VTS database.
"""

import os, sys
import bob.db.xm2vts


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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'xm2vts'))

  return wrapper


@db_available
def test_clients():
  db = bob.db.xm2vts.Database()
  assert len(db.groups()) == 3
  assert len(db.clients()) == 295
  assert len(db.clients(groups='client')) == 200
  assert len(db.clients(groups='dev')) == 200
  assert len(db.clients(groups='eval')) == 200
  assert len(db.clients(groups='world')) == 200
  assert len(db.clients(groups='impostorDev')) == 25
  assert len(db.clients(groups='impostorEval')) == 70
  assert len(db.models()) == 295
  assert len(db.models(groups='client')) == 200
  assert len(db.models(groups='dev')) == 200
  assert len(db.models(groups='eval')) == 200
  assert len(db.models(groups='world')) == 200
  assert len(db.models(groups='impostorDev')) == 25
  assert len(db.models(groups='impostorEval')) == 70


@db_available
def test_objects():
  db = bob.db.xm2vts.Database()
  assert len(db.objects()) == 3440
  # LP1
  assert len(db.objects(protocol='lp1')) == 2360
  assert len(db.objects(protocol='lp1', groups='world')) == 600
  assert len(db.objects(protocol='lp1', groups='dev')) == 1400
  assert len(db.objects(protocol='lp1', groups='dev', purposes='enroll')) == 600
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe')) == 800
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', classes='client')) == 600
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', classes='impostor')) == 800
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3])) == 800
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3], classes='client')) == 3
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3], classes='impostor')) == 797
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3,4])) == 800
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3,4], classes='client')) == 6
  assert len(db.objects(protocol='lp1', groups='dev', purposes='probe', model_ids=[3,4], classes='impostor')) == 800
  assert len(db.objects(protocol='lp1', groups='eval')) == 1560
  assert len(db.objects(protocol='lp1', groups='eval', purposes='enroll')) == 600
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe')) == 960
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', classes='client')) == 400
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', classes='impostor')) == 960
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3])) == 960
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3], classes='client')) == 2
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3], classes='impostor')) == 958
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3,4])) == 960
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3,4], classes='client')) == 4
  assert len(db.objects(protocol='lp1', groups='eval', purposes='probe', model_ids=[3,4], classes='impostor')) == 960
  # LP2
  assert len(db.objects(protocol='lp2')) == 2360
  assert len(db.objects(protocol='lp2', groups='world')) == 800
  assert len(db.objects(protocol='lp2', groups='dev')) == 1400
  assert len(db.objects(protocol='lp2', groups='dev', purposes='enroll')) == 800
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe')) == 600
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3])) == 600
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3], classes='client')) == 2
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3], classes='impostor')) == 598
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3,4])) == 600
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3,4], classes='client')) == 4
  assert len(db.objects(protocol='lp2', groups='dev', purposes='probe', model_ids=[3,4], classes='impostor')) == 600
  assert len(db.objects(protocol='lp2', groups='eval')) == 1760
  assert len(db.objects(protocol='lp2', groups='eval', purposes='enroll')) == 800
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe')) == 960
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3])) == 960
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3], classes='client')) == 2
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3], classes='impostor')) == 958
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3,4])) == 960
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3,4], classes='client')) == 4
  assert len(db.objects(protocol='lp2', groups='eval', purposes='probe', model_ids=[3,4], classes='impostor')) == 960
  # Darkened-LP1
  assert len(db.objects(protocol='darkened-lp1')) == 2480
  assert len(db.objects(protocol='darkened-lp1', groups='world')) == 600
  assert len(db.objects(protocol='darkened-lp1', groups='dev')) == 1400
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='enroll')) == 600
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe')) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', classes='client')) == 600
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', classes='impostor')) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3])) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3], classes='client')) == 3
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3], classes='impostor')) == 797
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3,4])) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3,4], classes='client')) == 6
  assert len(db.objects(protocol='darkened-lp1', groups='dev', purposes='probe', model_ids=[3,4], classes='impostor')) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='eval')) == 1680
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='enroll')) == 600
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe')) == 1080
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', classes='client')) == 800
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', classes='impostor')) == 1080
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3])) == 1080
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3], classes='client')) == 4
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3], classes='impostor')) == 1076
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3,4])) == 1080
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3,4], classes='client')) == 8
  assert len(db.objects(protocol='darkened-lp1', groups='eval', purposes='probe', model_ids=[3,4], classes='impostor')) == 1080
  # Darkened-LP2
  assert len(db.objects(protocol='darkened-lp2')) == 2480
  assert len(db.objects(protocol='darkened-lp2', groups='world')) == 800
  assert len(db.objects(protocol='darkened-lp2', groups='dev')) == 1400
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='enroll')) == 800
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe')) == 600
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3])) == 600
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3], classes='client')) == 2
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3], classes='impostor')) == 598
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3,4])) == 600
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3,4], classes='client')) == 4
  assert len(db.objects(protocol='darkened-lp2', groups='dev', purposes='probe', model_ids=[3,4], classes='impostor')) == 600
  assert len(db.objects(protocol='darkened-lp2', groups='eval')) == 1880
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='enroll')) == 800
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe')) == 1080
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3])) == 1080
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3], classes='client')) == 4
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3], classes='impostor')) == 1076
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3,4])) == 1080
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3,4], classes='client')) == 8
  assert len(db.objects(protocol='darkened-lp2', groups='eval', purposes='probe', model_ids=[3,4], classes='impostor')) == 1080


@db_available
def test_annotations():
  # Tests that for all files the annotated eye positions exist and are in correct order
  db = bob.db.xm2vts.Database()

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
  assert main('xm2vts dumplist --self-test'.split()) == 0
  assert main('xm2vts dumplist --protocol=lp1 --class=client --group=dev --purpose=enroll --client=10 --self-test'.split()) == 0
  assert main('xm2vts checkfiles --self-test'.split()) == 0
  assert main('xm2vts reverse frontal/342/342_2_1 --self-test'.split()) == 0
  assert main('xm2vts path 3011 --self-test'.split()) == 0

