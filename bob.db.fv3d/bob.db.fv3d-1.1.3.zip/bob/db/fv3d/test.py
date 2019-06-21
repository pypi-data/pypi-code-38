#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the 3D Fingervein database.
"""

import os
import numpy

from .query import Database

import nose.tools
from nose.plugins.skip import SkipTest

DATABASE_PATH = '/idiap/project/3dfingervein/database+stitched'


def metadata_available(test):
  """Decorator for detecting if the metadata is available"""

  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The interface SQL file (%s) is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'fv3d'))

  return wrapper


def db_available(test):
  """Decorator for detecting if the database files are available"""

  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    if os.path.exists(DATABASE_PATH):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database path (%s) is not available" % (DATABASE_PATH))

  return wrapper


@nose.tools.nottest
@metadata_available
def test_recreate():

  from bob.db.base.script.dbmanage import main
  nose.tools.eq_(main('fv3d create --recreate'.split()), None)


@metadata_available
def test_basic_queries():

  # test whether the correct number of clients is returned
  db = Database()

  protocols = db.protocol_names()
  nose.tools.eq_(len(protocols), 4)
  assert 'left' in protocols
  assert 'central' in protocols
  assert 'right' in protocols
  assert 'stitched' in protocols

  nose.tools.eq_(db.groups(), ('train', 'dev', 'eval'))
  nose.tools.eq_(db.purposes(), ('train', 'enroll', 'probe'))
  nose.tools.eq_(db.genders(), ('m', 'f'))
  nose.tools.eq_(db.sides(), ('l', 'r'))
  nose.tools.eq_(db.fingers(), ('t', 'i', 'm', 'r', 'l'))


@metadata_available
def test_left():

  # test whether the correct number of clients is returned
  db = Database()

  # FDV: 89 subjects * 2 fingers * 5 snapshots * 1 attempt = 890
  # IDI: 2 subjects * 6 fingers * 2 snapshots = 48
  # Total: 938 images
  train_samples = db.objects(protocol='left', groups='train')
  nose.tools.eq_(len(train_samples), 938)

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts = 1200 images
  dev_enroll_samples = db.objects(protocol='left', groups='dev',
      purposes='enroll')
  nose.tools.eq_(len(dev_enroll_samples), 1200)
  model_ids = db.model_ids(protocol='left')
  nose.tools.eq_(len(dev_enroll_samples), len(model_ids))

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts * 2 sessions
  # = 2400 images
  dev_probe_samples = db.objects(protocol='left', groups='dev',
      purposes='probe')
  nose.tools.eq_(len(dev_probe_samples), 2400)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='left', groups='dev',
    purposes='probe', model_ids = model_ids[0])), 2400)

  # 1 image per model
  # tests that we can filter by model ids
  nose.tools.eq_(len(db.objects(protocol='left', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # check file ids for train, dev enroll and dev probe are exclusive
  assert len(set(train_samples+dev_enroll_samples+dev_probe_samples)) == 4538


@metadata_available
def test_central():

  # test whether the correct number of clients is returned
  db = Database()

  # FDV: 89 subjects * 2 fingers * 5 snapshots * 1 attempt = 890
  # IDI: 2 subjects * 6 fingers * 2 snapshots = 48
  # Total: 938 images
  train_samples = db.objects(protocol='central', groups='train')
  nose.tools.eq_(len(train_samples), 938)

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts = 1200 images
  dev_enroll_samples = db.objects(protocol='central', groups='dev',
      purposes='enroll')
  nose.tools.eq_(len(dev_enroll_samples), 1200)
  model_ids = db.model_ids(protocol='central')
  nose.tools.eq_(len(dev_enroll_samples), len(model_ids))

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts * 2 sessions
  # = 2400 images
  dev_probe_samples = db.objects(protocol='central', groups='dev',
      purposes='probe')
  nose.tools.eq_(len(dev_probe_samples), 2400)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='central', groups='dev',
    purposes='probe', model_ids = model_ids[0])), 2400)

  # 1 image per model
  # tests that we can filter by model ids
  nose.tools.eq_(len(db.objects(protocol='central', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # check file ids for train, dev enroll and dev probe are exclusive
  assert len(set(train_samples+dev_enroll_samples+dev_probe_samples)) == 4538


@metadata_available
def test_right():

  # test whether the correct number of clients is returned
  db = Database()

  # FDV: 89 subjects * 2 fingers * 5 snapshots * 1 attempt = 890
  # IDI: 2 subjects * 6 fingers * 2 snapshots = 48
  # Total: 938 images
  train_samples = db.objects(protocol='right', groups='train')
  nose.tools.eq_(len(train_samples), 938)

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts = 1200 images
  dev_enroll_samples = db.objects(protocol='right', groups='dev',
      purposes='enroll')
  nose.tools.eq_(len(dev_enroll_samples), 1200)
  model_ids = db.model_ids(protocol='right')
  nose.tools.eq_(len(dev_enroll_samples), len(model_ids))

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts * 2 sessions
  # = 2400 images
  dev_probe_samples = db.objects(protocol='right', groups='dev',
      purposes='probe')
  nose.tools.eq_(len(dev_probe_samples), 2400)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='right', groups='dev',
    purposes='probe', model_ids = model_ids[0])), 2400)

  # 1 image per model
  # tests that we can filter by model ids
  nose.tools.eq_(len(db.objects(protocol='right', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # check file ids for train, dev enroll and dev probe are exclusive
  assert len(set(train_samples+dev_enroll_samples+dev_probe_samples)) == 4538


@metadata_available
def test_stitched():

  # test whether the correct number of clients is returned
  db = Database()

  # FDV: 89 subjects * 2 fingers * 5 snapshots * 1 attempt = 890
  # IDI: 2 subjects * 6 fingers * 2 snapshots = 48
  # Total: 938 images
  train_samples = db.objects(protocol='stitched', groups='train')
  nose.tools.eq_(len(train_samples), 938)

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts = 1200 images
  dev_enroll_samples = db.objects(protocol='stitched', groups='dev',
      purposes='enroll')
  nose.tools.eq_(len(dev_enroll_samples), 1200)
  model_ids = db.model_ids(protocol='stitched')
  nose.tools.eq_(len(dev_enroll_samples), len(model_ids))

  # IDI: 50 subjects * 6 fingers * 2 snapshots * 2 attempts * 2 sessions
  # = 2400 images
  dev_probe_samples = db.objects(protocol='stitched', groups='dev',
      purposes='probe')
  nose.tools.eq_(len(dev_probe_samples), 2400)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='stitched', groups='dev',
    purposes='probe', model_ids = model_ids[0])), 2400)

  # 1 image per model
  # tests that we can filter by model ids
  nose.tools.eq_(len(db.objects(protocol='stitched', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # check file ids for train, dev enroll and dev probe are exclusive
  assert len(set(train_samples+dev_enroll_samples+dev_probe_samples)) == 4538


@metadata_available
def test_driver_api():

  from bob.db.base.script.dbmanage import main

  nose.tools.eq_(main('fv3d dumplist --self-test'.split()), 0)
  nose.tools.eq_(main('fv3d dumplist --protocol=left --group=dev --purpose=enroll --model=110-rm-12 --self-test'.split()), 0)
  nose.tools.eq_(main('fv3d dumplist --protocol=central --group=dev --purpose=enroll --model=101-lm-12 --self-test'.split()), 0)
  nose.tools.eq_(main('fv3d dumplist --protocol=right --group=dev --purpose=enroll --model=149-lr-21 --self-test'.split()), 0)
  nose.tools.eq_(main('fv3d dumplist --protocol=stitched --group=dev --purpose=enroll --model=153-rr-22 --self-test'.split()), 0)
  nose.tools.eq_(main('fv3d checkfiles --self-test'.split()), 0)


@metadata_available
@db_available
def test_load():

  db = Database()

  for f in db.objects()[:5]:

    # loads an image from the database
    image = f.load(DATABASE_PATH)
    assert isinstance(image, numpy.ndarray)
    nose.tools.eq_(len(image.shape), 2) #it is a 2D array
    nose.tools.eq_(image.dtype, numpy.uint8)


@metadata_available
def test_model_id_to_finger_name_conversion():

  db = Database()

  for k in db.model_ids()[:5]:

    assert len(db.finger_name_from_model_id(k)) == 6
