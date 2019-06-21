#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the VERA Fingervein database.
"""

import os
import numpy

from . import Database, PADDatabase
from .create import VERAFINGER_PATH

import nose.tools
from nose.plugins.skip import SkipTest


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


def db_available(path):
  """Decorator for detecting if the database files are available"""

  def decorator(test):
    from bob.io.base.test_utils import datafile
    from nose.plugins.skip import SkipTest
    import functools

    @functools.wraps(test)
    def wrapper(*args, **kwargs):
      if os.path.exists(path):
        return test(*args, **kwargs)
      else:
        raise SkipTest("The database path (%s) is not available" % (path,))

    return wrapper

  return decorator


@sql3_available
def test_counts_bio():

  # test whether the correct number of clients is returned
  db = Database()

  nose.tools.eq_(db.groups(), ('train', 'dev'))

  protocols = db.protocol_names()
  nose.tools.eq_(len(protocols), 8)
  assert 'Nom' in protocols
  assert 'Full' in protocols
  assert 'Fifty' in protocols
  assert 'B' in protocols
  assert 'Cropped-Nom' in protocols
  assert 'Cropped-Full' in protocols
  assert 'Cropped-Fifty' in protocols
  assert 'Cropped-B' in protocols

  nose.tools.eq_(db.purposes(), ('train', 'enroll', 'probe', 'attack'))
  nose.tools.eq_(db.genders(), ('M', 'F'))
  nose.tools.eq_(db.sides(), ('L', 'R'))

  # test model ids
  model_ids = db.model_ids()
  nose.tools.eq_(len(model_ids), 440)

  model_ids = db.model_ids(protocol='Nom')
  nose.tools.eq_(len(model_ids), 220)

  model_ids = db.model_ids(protocol='Fifty')
  nose.tools.eq_(len(model_ids), 100)

  model_ids = db.model_ids(protocol='B')
  nose.tools.eq_(len(model_ids), 216)

  model_ids = db.model_ids(protocol='Full')
  nose.tools.eq_(len(model_ids), 440)

  model_ids = db.model_ids(protocol='Cropped-Nom')
  nose.tools.eq_(len(model_ids), 220)

  model_ids = db.model_ids(protocol='Cropped-Fifty')
  nose.tools.eq_(len(model_ids), 100)

  model_ids = db.model_ids(protocol='Cropped-B')
  nose.tools.eq_(len(model_ids), 216)

  model_ids = db.model_ids(protocol='Cropped-Full')
  nose.tools.eq_(len(model_ids), 440)

  # test database sizes
  nose.tools.eq_(len(db.objects(protocol='Nom', groups='train')), 0)
  nose.tools.eq_(len(db.objects(protocol='Nom', groups='dev')), 660)
  nose.tools.eq_(len(db.objects(protocol='Nom', groups='dev',
    purposes='enroll')), 220)
  nose.tools.eq_(len(db.objects(protocol='Nom', groups='dev',
    purposes='probe')), 220)
  nose.tools.eq_(len(db.objects(protocol='Nom', groups='dev',
    purposes='attack')), 220)

  nose.tools.eq_(len(db.objects(protocol='Fifty', groups='train')), 240)
  nose.tools.eq_(len(db.objects(protocol='Fifty', groups='dev')), 300)
  nose.tools.eq_(len(db.objects(protocol='Fifty', groups='dev',
    purposes='enroll')), 100)
  nose.tools.eq_(len(db.objects(protocol='Fifty', groups='dev',
    purposes='probe')), 100)
  nose.tools.eq_(len(db.objects(protocol='Fifty', groups='dev',
    purposes='attack')), 100)

  nose.tools.eq_(len(db.objects(protocol='B', groups='train')), 224)
  nose.tools.eq_(len(db.objects(protocol='B', groups='dev')), 432)
  nose.tools.eq_(len(db.objects(protocol='B', groups='dev',
    purposes='enroll')), 216)
  nose.tools.eq_(len(db.objects(protocol='B', groups='dev',
    purposes='probe')), 216)
  nose.tools.eq_(len(db.objects(protocol='B', groups='dev',
    purposes='attack')), 216)

  nose.tools.eq_(len(db.objects(protocol='Full', groups='train')), 0)
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev')), 880)
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='enroll')), 440)
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='probe')), 440)
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='attack')), 440)

  nose.tools.eq_(len(db.objects(protocol='Cropped-Nom', groups='train')), 0)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Nom', groups='dev')), 660)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Nom', groups='dev',
    purposes='enroll')), 220)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Nom', groups='dev',
    purposes='probe')), 220)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Nom', groups='dev',
    purposes='attack')), 220)

  nose.tools.eq_(len(db.objects(protocol='Cropped-Fifty', groups='train')), 240)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Fifty', groups='dev')), 300)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Fifty', groups='dev',
    purposes='enroll')), 100)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Fifty', groups='dev',
    purposes='probe')), 100)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Fifty', groups='dev',
    purposes='attack')), 100)

  nose.tools.eq_(len(db.objects(protocol='Cropped-B', groups='train')), 224)
  nose.tools.eq_(len(db.objects(protocol='Cropped-B', groups='dev')), 432)
  nose.tools.eq_(len(db.objects(protocol='Cropped-B', groups='dev',
    purposes='enroll')), 216)
  nose.tools.eq_(len(db.objects(protocol='Cropped-B', groups='dev',
    purposes='probe')), 216)
  nose.tools.eq_(len(db.objects(protocol='Cropped-B', groups='dev',
    purposes='attack')), 216)

  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='train')), 0)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev')), 880)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='enroll')), 440)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='probe')), 440)
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='attack')), 440)

  # make sure that we can filter by model ids
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='probe', model_ids=model_ids[0])), 440)

  # filtering by model ids on attacks, returns all with matching finger
  nose.tools.eq_(len(db.objects(protocol='Full', groups='dev',
    purposes='attack', model_ids=model_ids[0])), 2)

  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='enroll', model_ids=model_ids[:10])), 10)

  # filtering by model ids on probes, returns all
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='probe', model_ids=model_ids[0])), 440)

  # filtering by model ids on attacks, returns all with matching finger
  nose.tools.eq_(len(db.objects(protocol='Cropped-Full', groups='dev',
    purposes='attack', model_ids=model_ids[0])), 2)


@sql3_available
@db_available(VERAFINGER_PATH)
def test_driver_api():

  from bob.db.base.script.dbmanage import main

  nose.tools.eq_(main('verafinger dumplist --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumplist --protocol=Full --group=dev --purpose=enroll --model=101_L_1 --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumplist --protocol=Cropped-Full --group=dev --purpose=attack --model=101_L_1 --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumplist --protocol=Full --group=dev --purpose=attack --model=101_L_1 --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumplist --protocol=Cropped-Full --group=dev --purpose=enroll --model=101_L_1 --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger checkfiles --self-test'.split()), 0)


@sql3_available
@db_available(VERAFINGER_PATH)
def test_load():

  db = Database()

  for f in db.objects():

    # loads an image from the database
    image = f.load(VERAFINGER_PATH)
    assert isinstance(image, numpy.ndarray)
    nose.tools.eq_(len(image.shape), 2) #it is a 2D array
    nose.tools.eq_(image.dtype, numpy.uint8)

    roi = f.roi(VERAFINGER_PATH)
    assert isinstance(roi, numpy.ndarray)
    nose.tools.eq_(len(roi.shape), 2) #it is a 2D array
    nose.tools.eq_(roi.shape[1], 2) #two columns
    nose.tools.eq_(roi.dtype, numpy.uint16)

    if f.size == 'full':
      assert len(roi) > 10 #at least 10 points
    else:
      assert len(roi) == 4

    # ensures all annotation points are within image boundary
    Y,X = image.shape
    for y,x in roi:
      assert y < Y, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)
      assert x < X, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)


@sql3_available
def test_model_id_to_finger_name_conversion():

  db = Database()

  for f in db.objects():

    assert len(db.finger_name_from_model_id(f.model_id)) == 5


@sql3_available
@db_available(VERAFINGER_PATH)
def test_load_pad():

  db = PADDatabase()

  for f in db.objects():

    # loads an image from the database
    image = f.load(VERAFINGER_PATH)
    assert isinstance(image, numpy.ndarray)
    nose.tools.eq_(len(image.shape), 2) #it is a 2D array
    nose.tools.eq_(image.dtype, numpy.uint8)

    roi = f.roi(VERAFINGER_PATH)
    assert isinstance(roi, numpy.ndarray)
    nose.tools.eq_(len(roi.shape), 2) #it is a 2D array
    nose.tools.eq_(roi.shape[1], 2) #two columns
    nose.tools.eq_(roi.dtype, numpy.uint16)

    if f.size == 'full':
      assert len(roi) > 10 #at least 10 points
    else:
      assert len(roi) == 4

    # ensures all annotation points are within image boundary
    Y,X = image.shape
    for y,x in roi:
      assert y < Y, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)
      assert x < X, 'Annotation (%d, %d) for %s surpasses the image size (%d, %d)' % (y, x, f.path, Y, X)


@sql3_available
@db_available(VERAFINGER_PATH)
def test_driver_api_pad():

  from bob.db.base.script.dbmanage import main

  nose.tools.eq_(main('verafinger dumppadlist --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumppadlist --protocol=full --group=dev --self-test'.split()), 0)
  nose.tools.eq_(main('verafinger dumppadlist --protocol=cropped --group=eval --self-test'.split()), 0)


@sql3_available
def test_counts_pad():

  # test whether the correct number of clients is returned
  db = PADDatabase()

  nose.tools.eq_(db.groups(), ('train', 'dev', 'eval'))

  protocols = db.protocol_names()
  nose.tools.eq_(len(protocols), 2)
  assert 'full' in protocols
  assert 'cropped' in protocols

  nose.tools.eq_(db.genders(), ('M', 'F'))
  nose.tools.eq_(db.sides(), ('L', 'R'))

  def _fingers_in_group(protocol, group):
    '''Returns a unique list of clients/fingers in the group as a set'''

    files = db.objects(protocol=protocol, groups=group)
    return set([k.finger.client.id for k in files]), \
        set([k.finger.unique_name for k in files])

  def _check_proto(name):
    '''Runs a full check on a given protocol'''

    # test database sizes
    nose.tools.eq_(len(db.objects(protocol=name, groups='train')), 240)
    nose.tools.eq_(len(db.objects(protocol=name, groups='train',
      purposes='real')), 120)
    nose.tools.eq_(len(db.objects(protocol=name, groups='train',
      purposes='attack')), 120)
    nose.tools.eq_(len(db.objects(protocol=name, groups='dev')), 240)
    nose.tools.eq_(len(db.objects(protocol=name, groups='dev',
      purposes='real')), 120)
    nose.tools.eq_(len(db.objects(protocol=name, groups='dev',
      purposes='attack')), 120)
    nose.tools.eq_(len(db.objects(protocol=name, groups='eval')), 400)
    nose.tools.eq_(len(db.objects(protocol=name, groups='eval',
      purposes='real')), 200)
    nose.tools.eq_(len(db.objects(protocol=name, groups='eval',
      purposes='attack')), 200)

    train_clients, train_fingers = _fingers_in_group(name, 'train')
    dev_clients, dev_fingers = _fingers_in_group(name, 'dev')
    eval_clients, eval_fingers = _fingers_in_group(name, 'eval')

    # Test individual counts on clients and fingers
    nose.tools.eq_(len(train_clients), 30)
    nose.tools.eq_(len(train_fingers), 60)
    nose.tools.eq_(len(dev_clients), 30)
    nose.tools.eq_(len(dev_fingers), 60)
    nose.tools.eq_(len(eval_clients), 50)
    nose.tools.eq_(len(eval_fingers), 100)

    nose.tools.eq_(train_clients.intersection(dev_clients), set())
    nose.tools.eq_(train_clients.intersection(eval_clients), set())
    nose.tools.eq_(dev_clients.intersection(eval_clients), set())
    nose.tools.eq_(train_fingers.intersection(dev_fingers), set())
    nose.tools.eq_(train_fingers.intersection(eval_fingers), set())
    nose.tools.eq_(dev_fingers.intersection(eval_clients), set())

  _check_proto('full')
  _check_proto('cropped')
