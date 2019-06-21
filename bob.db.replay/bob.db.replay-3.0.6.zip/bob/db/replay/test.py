#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon Aug 8 12:40:24 2011 +0200
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

"""A few checks at the replay attack database.
"""

import os
import sys
import unittest
from .query import Database
from .models import *

authenticate_str = 'authenticate'
if sys.version_info[0] < 3:
  authenticate_str = authenticate_str.encode('utf8')

enroll_str = 'enroll'
if sys.version_info[0] < 3:
  enroll_str = enroll_str.encode('utf8')


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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'replay'))

  return wrapper


class ReplayDatabaseTest(unittest.TestCase):
  """Performs various tests on the replay attack database."""

  @db_available
  def test01_queryRealAccesses(self):

    db = Database()
    f = db.objects(cls='real')
    self.assertEqual(len(f), 200)  # 200 unique auth sessions
    for v in f[:10]:  # only the 10 first...
      self.assertTrue(isinstance(v.get_realaccess(), RealAccess))
      o = v.get_realaccess()
      self.assertEqual(o.purpose, authenticate_str)

    train = db.objects(cls='real', groups='train')
    self.assertEqual(len(train), 60)

    dev = db.objects(cls='real', groups='devel')
    self.assertEqual(len(dev), 60)

    test = db.objects(cls='real', groups='test')
    self.assertEqual(len(test), 80)

    # tests train, devel and test files are distinct
    s = set(train + dev + test)
    self.assertEqual(len(s), 200)

  @db_available
  def queryAttackType(self, protocol, N):

    db = Database()
    f = db.objects(cls='attack', protocol=protocol)

    self.assertEqual(len(f), N)
    for k in f[:10]:  # only the 10 first...
      k.get_attack()
      self.assertRaises(RuntimeError, k.get_realaccess)

    train = db.objects(cls='attack', groups='train', protocol=protocol)
    self.assertEqual(len(train), int(round(0.3 * N)))

    dev = db.objects(cls='attack', groups='devel', protocol=protocol)
    self.assertEqual(len(dev), int(round(0.3 * N)))

    test = db.objects(cls='attack', groups='test', protocol=protocol)
    self.assertEqual(len(test), int(round(0.4 * N)))

    # tests train, devel and test files are distinct
    s = set(train + dev + test)
    self.assertEqual(len(s), N)

  @db_available
  def test02_queryAttacks(self):

    self.queryAttackType('grandtest', 1000)

  @db_available
  def test03_queryPrintAttacks(self):

    self.queryAttackType('print', 200)

  @db_available
  def test04_queryMobileAttacks(self):

    self.queryAttackType('mobile', 400)

  @db_available
  def test05_queryHighDefAttacks(self):

    self.queryAttackType('highdef', 400)

  @db_available
  def test06_queryPhotoAttacks(self):

    self.queryAttackType('photo', 600)

  @db_available
  def test07_queryVideoAttacks(self):

    self.queryAttackType('video', 400)

  @db_available
  def test08_queryEnrollments(self):

    db = Database()
    f = db.objects(cls='enroll')
    self.assertEqual(len(f), 100)  # 50 clients, 2 conditions
    for v in f:
      self.assertEqual(v.get_realaccess().purpose, enroll_str)

  @db_available
  def test09_queryClients(self):

    db = Database()
    f = db.clients()
    self.assertEqual(len(f), 50)  # 50 clients
    self.assertTrue(db.has_client_id(3))
    self.assertFalse(db.has_client_id(0))
    self.assertTrue(db.has_client_id(21))
    self.assertFalse(db.has_client_id(32))
    self.assertFalse(db.has_client_id(100))
    self.assertTrue(db.has_client_id(101))
    self.assertTrue(db.has_client_id(119))
    self.assertFalse(db.has_client_id(120))

  @db_available
  def test10_queryfacefile(self):

    db = Database()
    o = db.objects(clients=(1,))[0]
    o.facefile()

  @db_available
  def test11_manage_files(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('replay files'.split()), 0)

  @db_available
  def test12_manage_dumplist_1(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('replay dumplist --self-test'.split()), 0)

  @db_available
  def test13_manage_dumplist_2(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('replay dumplist --class=attack --group=devel --support=hand --protocol=highdef --self-test'.split()), 0)

  @db_available
  def test14_manage_dumplist_client(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('replay dumplist --client=117 --self-test'.split()), 0)

  @db_available
  def test15_manage_checkfiles(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('replay checkfiles --self-test'.split()), 0)

  @db_available
  def test16_queryPrintVideoAttacks(self):

    self.queryAttackType(('print', 'video'), 600)

  @db_available
  def test17_queryPrintVideoAttacks(self):

    self.queryAttackType(('print', 'photo'), 600)

  @db_available
  def test18_queryPrintVideoAttacks(self):

    self.queryAttackType(('highdef', 'print'), 600)

  @db_available
  def test19_queryPrintVideoAttacks(self):

    self.queryAttackType(('highdef', 'video'), 600)

  @db_available
  def test20_queryPrintVideoAttacks(self):

    self.queryAttackType(('highdef', 'mobile', 'print'), 1000)

  @db_available
  def test21_queryDigitalPhotoAttacks(self):

    self.queryAttackType('digitalphoto', 400)

  @db_available
  def test22_queryPrintVideoAttacks(self):

    self.queryAttackType(('digitalphoto', 'photo'), 600)
