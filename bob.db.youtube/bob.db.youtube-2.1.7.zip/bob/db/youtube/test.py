#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the YouTube database.
"""

import os, sys
import random
import bob.db.youtube
from nose.plugins.skip import SkipTest

def db_available(test):
  """Decorator for detecting if OpenCV/Python bindings are available"""
  from bob.io.base.test_utils import datafile
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'youtube'))

  return wrapper


# expected numbers of clients
# restricted; unrestricted; dev; eval
_expected_clients = {
    'fold1': (1014, 294, 139),
    'fold2': (1021, 285, 141),
    'fold3': (1018, 280, 149),
    'fold4': (1014, 290, 143),
    'fold5': (1009, 292, 146),
    'fold6': (1013, 289, 145),
    'fold7': (1006, 291, 150),
    'fold8': (1012, 295, 140),
    'fold9': (1009, 290, 148),
    'fold10': (1013, 288, 146)
  }

_expected_models = {
    'fold1': (498, 244),
    'fold2': (491, 271),
    'fold3': (515, 254),
    'fold4': (525, 253),
    'fold5': (507, 238),
    'fold6': (491, 248),
    'fold7': (486, 250),
    'fold8': (498, 243),
    'fold9': (493, 251),
    'fold10': (494, 247)
  }

_expected_probes = {
    'fold1': (484, 238),
    'fold2': (475, 256),
    'fold3': (494, 244),
    'fold4': (500, 244),
    'fold5': (488, 244),
    'fold6': (488, 251),
    'fold7': (495, 252),
    'fold8': (503, 233),
    'fold9': (485, 247),
    'fold10': (480, 237)
  }

_expected_restricted_training_images = {
    'fold1': 985,
    'fold2': 958,
    'fold3': 959,
    'fold4': 976,
    'fold5': 963,
    'fold6': 965,
    'fold7': 948,
    'fold8': 962,
    'fold9': 977,
    'fold10': 985
  }

_expected_unrestricted_training_images = {
    'fold1': 2301,
    'fold2': 2274,
    'fold3': 2262,
    'fold4': 2261,
    'fold5': 2301,
    'fold6': 2300,
    'fold7': 2280,
    'fold8': 2292,
    'fold9': 2291,
    'fold10': 2314
  }


@db_available
def test_clients():
  # Tests if the clients() and models() functions work as expected
  db = bob.db.youtube.Database()
  # check the number of clients per protocol
  for p,l in _expected_clients.items():
    assert len(db.clients(protocol=p, groups='world', world_type='unrestricted')) == l[0]
    assert len(db.clients(protocol=p, groups='world', world_type='restricted')) == l[0]
    assert len(db.clients(protocol=p, groups='dev')) == l[1]
    assert len(db.clients(protocol=p, groups='eval')) == l[2]

  # check the number of models per protocol
  for p,l in _expected_models.items():
    assert len(db.models(protocol=p, groups='dev')) == l[0]
    assert len(db.models(protocol=p, groups='eval')) == l[1]


@db_available
def test_objects():
  # Tests if the files() function returns the expected number and type of files
  db = bob.db.youtube.Database()

  # first, count all objects
  assert len(db.objects()) == 3268
  assert len(db.objects(world_type='restricted')) == 3226

  # check that the files() function returns the same number of elements as the models() function does
  for p,l in _expected_models.items():
    assert len(db.objects(protocol=p, groups='dev', purposes='enroll')) == l[0]
    assert len(db.objects(protocol=p, groups='eval', purposes='enroll')) == l[1]

  # check the number of probe files is correct
  for p,l in _expected_probes.items():
    assert len(db.objects(protocol=p, groups='dev', purposes='probe')) == l[0]
    assert len(db.objects(protocol=p, groups='eval', purposes='probe')) == l[1]

  # check that the training files in the restricted configuration fit
  for p,l in _expected_restricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='restricted', subworld='threefolds')) == l

  # also check that the training files in the unrestricted configuration fit
  for p,l in _expected_unrestricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='unrestricted', subworld='sevenfolds')) == l

  # check that the probe files sum up to 1000 (view1) or 600 (view2)
  for p in _expected_models.keys():
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
  db = bob.db.youtube.Database()
  # check the number of pairs
  numbers = (3500, 1000, 500)
  for p in sorted(_expected_models.keys()):
    assert len(db.pairs(protocol=p, groups='world')) == 3500
    assert len(db.pairs(protocol=p, groups='dev')) == 1000
    assert len(db.pairs(protocol=p, groups='eval')) == 500


@db_available
def test_unrestricted():
  # Tests the unrestricted configuration
  db = bob.db.youtube.Database()
  # check that the training files in the unrestricted configuration fit
  for p,l in _expected_unrestricted_training_images.items():
    assert len(db.objects(protocol=p, groups='world', world_type='unrestricted')) == l
    # for dev and eval, restricted and unrestricted should return the same number of files
    assert len(db.objects(protocol=p, groups='dev', purposes='enroll', world_type='unrestricted')) == _expected_models[p][0]
    assert len(db.objects(protocol=p, groups='eval', purposes='enroll', world_type='unrestricted')) == _expected_models[p][1]
    assert len(db.objects(protocol=p, groups='dev', purposes='probe', world_type='unrestricted')) == _expected_probes[p][0]
    assert len(db.objects(protocol=p, groups='eval', purposes='probe', world_type='unrestricted')) == _expected_probes[p][1]


@db_available
def test_zt():
  # checks that the correct ZT norm objects are returned
  db = bob.db.youtube.Database()
  models = db.model_ids(protocol='fold1', groups='dev')
  tmodels = db.tmodel_ids(protocol='fold3', groups='dev')
  assert sorted(models) == sorted(tmodels)

  tfiles = db.tobjects(protocol='fold1')
  zfiles = db.zobjects(protocol='fold1')

  world_files = db.objects(protocol='fold1', groups='world', subworld='sevenfolds')

  for f in tfiles + zfiles:
    assert f in world_files

  short_world_files = db.objects(protocol='fold1', groups='world', subworld='fivefolds')
  for f in tfiles + zfiles:
    assert f not in short_world_files


@db_available
def test_annotations():
  dir = "/idiap/resource/database/YouTubeFaces/frame_images_DB"
  if not os.path.exists(dir):
    raise SkipTest("The annotation directory '%s' is not available, annotations can't be tested." % dir)
  # Tests the unrestricted configuration
  db = bob.db.youtube.Database(original_directory = dir)
  # get all files
  dirs = random.sample(list(db.objects()), 100) # if the random sampling fails, please remove it to get all files checked.
  # iterate over all files
  for k in dirs:
    # get the files
    import glob
    images = glob.glob(db.original_file_name(k))
    # get the annotations for 10 images
    annotations = db.annotations(k)
    # check that images and annotations are from the same image ID
    assert len(images) == len(annotations), '%r != %r at directory %s' % \
        (len(images), len(annotations), k)

    # check a subset of the annotations
    image_names = sorted(set([os.path.basename(images[random.randrange(len(images))]) for i in range(10)]))
    annotations = db.annotations(k, image_names = image_names)
    assert len(annotations) <= 10
    for i, image_id in enumerate(sorted(annotations.keys())):
      assert image_id == image_names[i]
      assert 'topleft' in annotations[image_id]
      assert 'bottomright' in annotations[image_id]
      assert len(annotations[image_id]['topleft']) == 2
      assert len(annotations[image_id]['bottomright']) == 2


@db_available
def test_driver_api():
  from bob.db.base.script.dbmanage import main
  assert main('youtube dumplist --self-test'.split()) == 0
  assert main('youtube dumplist --protocol=fold8 --group=dev --purpose=enroll --self-test'.split()) == 0
  assert main('youtube dumppairs --self-test'.split()) == 0
  assert main('youtube dumppairs --protocol=fold8 --group=dev --class=client --self-test'.split()) == 0
  assert main('youtube checkfiles --self-test'.split()) == 0
  assert main('youtube reverse Gerald_Ford/2 --self-test'.split()) == 0
  dir = "/idiap/resource/database/YouTubeFaces/frame_images_DB"
  if os.path.exists(dir):
    assert main(('youtube annotations 1437 --directory %s --self-test'%dir).split()) == 0
  assert main('youtube path 1437 --self-test'.split()) == 0

