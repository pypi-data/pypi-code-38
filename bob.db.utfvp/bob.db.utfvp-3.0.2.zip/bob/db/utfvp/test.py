#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the UTFVP Fingervein database.
"""

import os
import numpy

from . import Database

import nose.tools
from nose.plugins.skip import SkipTest

# base directories where the UTFVP files sit
DATABASE_PATH = "/idiap/resource/database/UTFVP/data"


def sql3_available(test):
  """Decorator for detecting if the sql3 file is available"""

  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The interface SQL file (%s) is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'vera'))

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


@sql3_available
def test_overall_characteristics():

  # test whether the correct number of clients is returned
  db = Database()

  nose.tools.eq_(db.groups(), ('train', 'dev', 'eval'))

  protocols = db.protocol_names()
  nose.tools.eq_(len(protocols), 15)
  assert '1vsall' in protocols
  assert 'full' in protocols
  assert 'fullLeftRing' in protocols
  assert 'fullLeftMiddle' in protocols
  assert 'fullLeftIndex' in protocols
  assert 'fullRightRing' in protocols
  assert 'fullRightMiddle' in protocols
  assert 'fullRightIndex' in protocols
  assert 'nom' in protocols
  assert 'nomLeftRing' in protocols
  assert 'nomLeftMiddle' in protocols
  assert 'nomLeftIndex' in protocols
  assert 'nomRightRing' in protocols
  assert 'nomRightMiddle' in protocols
  assert 'nomRightIndex' in protocols

  nose.tools.eq_(db.purposes(), ('train', 'enroll', 'probe'))
  nose.tools.eq_(db.genders(), ('M', 'F'))
  nose.tools.eq_(db.finger_names(), ('1', '2', '3', '4', '5', '6'))


def check_proto(db, name, n_train, n_dev, n_dev_models, n_dev_probes,
    dev_probes_per_model, n_eval, n_eval_models, n_eval_probes,
    eval_probes_per_model):

  nose.tools.eq_(len(db.objects(protocol=name, groups='train')), n_train)

  nose.tools.eq_(len(db.objects(protocol=name, groups='dev')), n_dev)
  nose.tools.eq_(len(db.objects(protocol=name, groups='dev',
    purposes='enroll')), n_dev_models)
  nose.tools.eq_(len(db.objects(protocol=name, groups='dev',
    purposes='probe')), n_dev_probes)

  nose.tools.eq_(len(db.objects(protocol=name, groups='eval')), n_eval)
  nose.tools.eq_(len(db.objects(protocol=name, groups='eval',
    purposes='enroll')), n_eval_models)
  nose.tools.eq_(len(db.objects(protocol=name, groups='eval',
    purposes='probe')), n_eval_probes)

  # make sure that we can filter by model ids (1 model = 1 sample, always)
  dev_model_ids = db.model_ids(protocol=name, groups='dev')
  nose.tools.eq_(len(dev_model_ids), n_dev_models)

  # filtering by model ids on probes, returns all
  if n_eval != 0:
    nose.tools.eq_(len(db.objects(protocol=name, groups='dev',
      purposes='probe', model_ids=dev_model_ids[0])), dev_probes_per_model)

    eval_model_ids = db.model_ids(protocol=name, groups='eval')
    nose.tools.eq_(len(eval_model_ids), n_eval_models)

    # filtering by model ids on probes, returns all
    nose.tools.eq_(len(db.objects(protocol=name, groups='eval',
      purposes='probe', model_ids=eval_model_ids[0])), eval_probes_per_model)


@sql3_available
def test_protocol_1vsall():

  db = Database()
  check_proto(db, '1vsall', 140, 1300, 1300, 1300, 1299, 0, 0, 0, 0)


@sql3_available
def test_protocol_full():

  db = Database()
  check_proto(db, 'full', 0, 1440, 1440, 1440, 1440, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullLeftRing():

  db = Database()
  check_proto(db, 'fullLeftRing', 0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullLeftMiddle():

  db = Database()
  check_proto(db, 'fullLeftMiddle', 0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullLeftIndex():

  db = Database()
  check_proto(db, 'fullLeftIndex',  0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullRightRing():

  db = Database()
  check_proto(db, 'fullRightRing', 0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullRightMiddle():

  db = Database()
  check_proto(db, 'fullRightMiddle', 0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_fullRightIndex():

  db = Database()
  check_proto(db, 'fullRightIndex', 0,  240,  240,  240,  240, 0, 0, 0, 0)


@sql3_available
def test_protocol_nom():

  db = Database()
  check_proto(db, 'nom', 240, 432, 216, 216, 216, 768, 384, 384, 384)


@sql3_available
def test_protocol_nomLeftRing():

  db = Database()
  check_proto(db, 'nomLeftRing', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_protocol_nomLeftMiddle():

  db = Database()
  check_proto(db, 'nomLeftMiddle', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_protocol_nomLeftIndex():

  db = Database()
  check_proto(db, 'nomLeftIndex', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_protocol_nomRightRing():

  db = Database()
  check_proto(db, 'nomRightRing', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_protocol_nomRightMiddle():

  db = Database()
  check_proto(db, 'nomRightMiddle', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_protocol_nomRightIndex():

  db = Database()
  check_proto(db, 'nomRightIndex', 40,  72,  36,  36,  36, 128,  64,  64,  64)


@sql3_available
def test_driver_api():

  from bob.db.base.script.dbmanage import main

  nose.tools.eq_(main('utfvp dumplist --self-test'.split()), 0)
  nose.tools.eq_(main('utfvp dumplist --protocol=nom --group=dev --purpose=enroll --model=0011_1_2 --self-test'.split()), 0)
  nose.tools.eq_(main('utfvp checkfiles --self-test'.split()), 0)


@sql3_available
@db_available
def test_load():

  db = Database()

  for f in db.objects():

    # loads an image from the database
    image = f.load(DATABASE_PATH)
    assert isinstance(image, numpy.ndarray)
    nose.tools.eq_(len(image.shape), 2) #it is a 2D array
    nose.tools.eq_(image.dtype, numpy.uint8)


@sql3_available
@db_available
def test_annotations():

  db = Database()

  for f in db.objects():

    # loads an image from the database
    image = f.load(DATABASE_PATH)

    roi = f.roi()
    assert isinstance(roi, numpy.ndarray)
    nose.tools.eq_(len(roi.shape), 2) #it is a 2D array
    nose.tools.eq_(roi.shape[1], 2) #two columns
    nose.tools.eq_(roi.dtype, numpy.uint16)
    assert len(roi) > 10 #at least 10 points

    # ensures all annotation points are within image boundary
    Y,X = image.shape
    for y,x in roi:
      assert y < Y, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)
      assert x < X, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)


@sql3_available
def test_model_id_to_finger_name_conversion():

  db = Database()

  for f in db.objects():

    assert len(db.finger_name_from_model_id(f.model_id)) == 6
