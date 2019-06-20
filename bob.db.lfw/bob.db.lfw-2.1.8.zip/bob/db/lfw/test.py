#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
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

"""A few checks at the Labeled Faces in the Wild database.
"""

import os, sys
import random
import bob.db.lfw


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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'lfw'))

  return wrapper


# expected numbers of clients
# restricted; unrestricted; dev; eval
expected_clients = {
    'view1': (4038, 2132, 1711, 0),
    'fold1': (3959, 2956, 1189, 601),
    'fold2': (3984, 2986, 1210, 555),
    'fold3': (4041, 3040, 1156, 552),
    'fold4': (4082, 3052, 1107, 560),
    'fold5': (4070, 3039, 1112, 567),
    'fold6': (4095, 3017, 1127, 527),
    'fold7': (4058, 2997, 1094, 597),
    'fold8': (4024, 2976, 1124, 601),
    'fold9': (3971, 2956, 1198, 580),
    'fold10': (3959, 2948, 1181, 609)
  }

expected_models = {
    'view1': (853, 0),
    'fold1': (916, 472),
    'fold2': (930, 462),
    'fold3': (934, 440),
    'fold4': (902, 459),
    'fold5': (899, 436),
    'fold6': (895, 441),
    'fold7': (877, 476),
    'fold8': (917, 462),
    'fold9': (938, 458),
    'fold10': (920, 458)
  }

expected_probes = {
    'view1': (863, 0),
    'fold1': (931, 473),
    'fold2': (947, 454),
    'fold3': (927, 439),
    'fold4': (893, 451),
    'fold5': (890, 449),
    'fold6': (900, 450),
    'fold7': (899, 467),
    'fold8': (917, 462),
    'fold9': (929, 457),
    'fold10': (919, 474)
  }

expected_restricted_training_images = {
    'view1': 3443,
    'fold1': 2267,
    'fold2': 2228,
    'fold3': 2234,
    'fold4': 2293,
    'fold5': 2341,
    'fold6': 2362,
    'fold7': 2334,
    'fold8': 2356,
    'fold9': 2368,
    'fold10': 2320
  }

expected_unrestricted_training_images = {
    'view1': 9525,
    'fold1': 8874,
    'fold2': 8714,
    'fold3': 9408,
    'fold4': 9453,
    'fold5': 9804,
    'fold6': 9727,
    'fold7': 9361,
    'fold8': 9155,
    'fold9': 9114,
    'fold10': 9021
  }


@db_available
def test_clients():
  # Tests if the clients() and models() functions work as expected
  db = bob.db.lfw.Database()
  # check the number of clients per protocol
  for p,l in expected_clients.items():
    assert len(db.clients(protocol=p, groups='world', world_type='unrestricted')) == l[0]
    assert len(db.clients(protocol=p, groups='world', world_type='restricted')) == l[1]
    assert len(db.clients(protocol=p, groups='dev')) == l[2]
    assert len(db.clients(protocol=p, groups='eval')) == l[3]

  # check the number of models per protocol
  for p,l in expected_models.items():
    assert len(db.models(protocol=p, groups='dev')) == l[0]
    assert len(db.models(protocol=p, groups='eval')) == l[1]


@db_available
def test_objects():
  # Tests if the files() function returns the expected number and type of files
  db = bob.db.lfw.Database()

  # first, count all objects
  assert len(db.objects()) == 13233
  assert len(db.objects(world_type='restricted')) == 9056

  # check that the files() function returns the same number of elements as the models() function does
  for p,l in expected_models.items():
    assert len(db.objects(protocol=p, groups='dev', purposes='enroll')) == l[0]
    assert len(db.objects(protocol=p, groups='eval', purposes='enroll')) == l[1]

  # check the number of probe files is correct
  for p,l in expected_probes.items():
    assert len(db.objects(protocol=p, groups='dev', purposes='probe')) == l[0]
    assert len(db.objects(protocol=p, groups='eval', purposes='probe')) == l[1]

  # check that the training files in the restricted configuration fit
  for p,l in expected_restricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='restricted', subworld='threefolds')) == l

  # also check that the training files in the unrestricted configuration fit
  for p,l in expected_unrestricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='unrestricted', subworld='sevenfolds')) == l

  # check that the probe files sum up to 1000 (view1) or 600 (view2)
  for p in expected_models.keys():
    expected_probe_count = len(db.pairs(protocol=p, groups='dev'))
    # count the probes for each model
    current_probe_count = 0
    models = db.models(protocol=p, groups='dev')
    for model_id in [model.id for model in models]:
      current_probe_count += len(db.objects(protocol=p, groups='dev', purposes='probe', model_ids = (model_id,)))
    # assure that the number of probes is equal to the number of pairs
    assert current_probe_count == expected_probe_count


@db_available
def test_pairs():
  # Tests if the pairs() function returns the desired output
  db = bob.db.lfw.Database()
  # check the number of pairs
  numbers = ((2200, 1000, 0), (4200, 1200, 600))
  index = 10
  for p in sorted(expected_models.keys()):
    assert len(db.pairs(protocol=p, groups='world')) == numbers[index > 0][0]
    assert len(db.pairs(protocol=p, groups='dev')) == numbers[index > 0][1]
    assert len(db.pairs(protocol=p, groups='eval')) == numbers[index > 0][2]
    # evil trick to get the first 10 times the numbers for view2, and once the numbers for view1
    index -= 1


@db_available
def test_unrestricted():
  # Tests the unrestricted configuration
  db = bob.db.lfw.Database()
  # check that the training files in the unrestricted configuration fit
  for p,l in expected_unrestricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='unrestricted')) == l
    # for dev and eval, restricted and unrestricted should return the same number of files
    assert len(db.objects(protocol=p, groups='dev', purposes='enroll', world_type='unrestricted')) == expected_models[p][0]
    assert len(db.objects(protocol=p, groups='eval', purposes='enroll', world_type='unrestricted')) == expected_models[p][1]
    assert len(db.objects(protocol=p, groups='dev', purposes='probe', world_type='unrestricted')) == expected_probes[p][0]
    assert len(db.objects(protocol=p, groups='eval', purposes='probe', world_type='unrestricted')) == expected_probes[p][1]


@db_available
def test_annotations():
  # Tests the unrestricted configuration
  db = bob.db.lfw.Database()
  # get all files
  files = random.sample(list(db.objects()), 1000) # if the random sampling fails, please remove it to get all files checked.
  # iterate over all files
  for annotation_type in db.annotation_types():
    for file in files:
      annotations = db.annotations(file, annotation_type)
      if annotation_type == 'funneled':
        assert 'leye' in annotations and 'reye' in annotations
      if 'leye' in annotations:
         assert len(annotations['leye']) == 2
      if 'reye' in annotations:
        assert len(annotations['reye']) == 2


@db_available
def test_driver_api():
  from bob.db.base.script.dbmanage import main
  assert main('lfw dumplist --self-test'.split()) == 0
  assert main('lfw dumplist --protocol=fold8 --group=dev --purpose=enroll --self-test'.split()) == 0
  assert main('lfw dumppairs --self-test'.split()) == 0
  assert main('lfw dumppairs --protocol=fold8 --group=dev --class=client --self-test'.split()) == 0
  assert main('lfw checkfiles --self-test'.split()) == 0
  assert main('lfw reverse Thomas_Watjen/Thomas_Watjen_0001 --self-test'.split()) == 0
  assert main('lfw annotations 1437 --self-test'.split()) == 0
  assert main('lfw path 1437 --self-test'.split()) == 0

