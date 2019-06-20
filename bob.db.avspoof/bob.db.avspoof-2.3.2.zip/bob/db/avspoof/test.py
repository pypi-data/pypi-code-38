#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 19 Aug 13:43:50 2015
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

"""A few checks at the avspoof attack database.
"""

import unittest
from .query import Database
from .models import *

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
            raise SkipTest(
                "The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (
                dbfile, 'avspoof'))

    return wrapper


class AVSpoofDatabaseTest(unittest.TestCase):
    """Performs various tests on the AVspoof attack database."""

    @db_available
    def queryGroupsProtocolsTypes(self, protocol, cls, Ntrain, Ndevel, Ntest):

        db = Database()
        f = db.objects(cls=cls, protocol=protocol)

        self.assertEqual(len(f), Ntrain+Ndevel+Ntest)
        for k in f[:10]:  # only the 10 first...
            if cls == 'attack':
                attack_name = k.get_attack()
                self.assertNotEqual(attack_name, 'undefined_undefined')
                self.assertTrue(k.is_attack())
            else:
                self.assertTrue(k.is_real())

        train = db.objects(cls=cls, groups='train', protocol=protocol)
        self.assertEqual(len(train), Ntrain)

        dev = db.objects(cls=cls, groups='devel', protocol=protocol)
        self.assertEqual(len(dev), Ndevel)

        test = db.objects(cls=cls, groups='test', protocol=protocol)
        self.assertEqual(len(test), Ntest)

        # tests train, devel, and test files are distinct
        s = set(train + dev + test)
        self.assertEqual(len(s), Ntrain+Ndevel+Ntest)

    @db_available
    def test01_queryRealGrandtest(self):
        self.queryGroupsProtocolsTypes('grandtest',  'real', 4973, 4995, 5576)

    def test02_queryRealSmalltest(self):
        self.queryGroupsProtocolsTypes('smalltest',  'real', 741, 695, 680)

    @db_available
    def test03_queryAttacksGrandtest(self):
        self.queryGroupsProtocolsTypes('grandtest', 'attack', 56470, 56470, 63380)

    @db_available
    def test04_queryAttacksSmalltest(self):
        self.queryGroupsProtocolsTypes('smalltest', 'attack', 6910, 6910, 6910)

    @db_available
    def test05_queryRealPhysicalAccess(self):
        self.queryGroupsProtocolsTypes('physical_access',  'real', 4973, 4995, 5576)

    @db_available
    def test06_queryRealLogicalAccess(self):
        self.queryGroupsProtocolsTypes('logical_access',  'real', 4973, 4995, 5576)

    @db_available
    def test07_queryAttacksPhysicalAccess(self):
        self.queryGroupsProtocolsTypes('physical_access',  'attack', 38580, 38580, 43320)

    @db_available
    def test08_queryRealLogicalAccess(self):
        self.queryGroupsProtocolsTypes('logical_access',  'attack', 17890, 17890, 20060)


    @db_available
    def queryEnrollments(self, protocol, N):

        db = Database()
        f = db.objects(cls='enroll', protocol=protocol)
        self.assertEqual(len(f), N)
        for k in f[:10]:  # only the 10 first...
            self.assertTrue(k.is_real())

    @db_available
    def test09_queryEnrollmentsGrandtest(self):
        self.queryEnrollments('grandtest', 2418)

    @db_available
    def test10_queryEnrollmentsPhysicalAccess(self):
        self.queryEnrollments('physical_access', 2418)

    @db_available
    def test11_queryEnrollmentsLogicalAccess(self):
        self.queryEnrollments('logical_access', 2418)

    @db_available
    def test12_queryEnrollmentsSmalltest(self):
        self.queryEnrollments('smalltest', 334)

    @db_available
    def test13_queryClients(self):

        db = Database()
        f = db.clients()
        self.assertEqual(len(f), 44)  # 44 clients
        self.assertTrue(db.has_client_id(3))
        self.assertFalse(db.has_client_id(0))
        self.assertTrue(db.has_client_id(21))
        self.assertFalse(db.has_client_id(45))
        self.assertFalse(db.has_client_id(100))
        self.assertTrue(db.has_client_id(18))

        f = db.clients(gender='male')
        self.assertEqual(len(f), 31)  # 31 male clients
        clients = []
        for c in f:
            clients.append(c.id)
        self.assertIn(1, clients)
        self.assertNotIn(3, clients)
        self.assertIn(30, clients)
        self.assertNotIn(43, clients)

        f = db.clients(gender='female')
        self.assertEqual(len(f), 13)  # 13 female clients
        clients = []
        for c in f:
            clients.append(c.id)
        self.assertNotIn(1, clients)
        self.assertIn(3, clients)
        self.assertNotIn(30, clients)
        self.assertIn(43, clients)

    @db_available
    def test14_queryAudioFile(self):

        db = Database()
        o = db.objects(clients=(1,))[0]
        o.audiofile()

    @db_available
    def test15_manage_files(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('avspoof files'.split()), 0)

    @db_available
    def test16_manage_dumplist_1(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('avspoof dumplist --self-test'.split()), 0)

    @db_available
    def test17_manage_dumplist_2(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main(
            'avspoof dumplist --class=attack --group=devel --protocol=grandtest --self-test'.split()), 0)

    @db_available
    def test18_manage_dumplist_client(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('avspoof dumplist --client=23 --self-test'.split()), 0)

    @db_available
    def test19_manage_checkfiles(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('avspoof checkfiles --self-test'.split()), 0)

    @db_available
    def queryAttackType(self, protocol, attack, device, N):

        db = Database()
        f = db.objects(cls='attack', attack_type=attack, attack_devices=device, protocol=protocol)
        self.assertEqual(len(f), N)
        for k in f[:10]:  # only the 10 first...
            self.assertEqual(attack, k.attack_type)
            if device:
                k_attack = k.get_attack()
                self.assertEqual(attack+'_'+device, k_attack)


    @db_available
    def test20_queryReplayAttacks(self):
        self.queryAttackType('grandtest', 'replay', '', 8800)

    @db_available
    def test21_queryReplayAttacksLogicalAccess(self):
        self.queryAttackType('logical_access', 'replay', '', 0)

    @db_available
    def test22_queryLogicalAttacksPhysicalAccess(self):
        self.queryAttackType('physical_access', 'logical_access', '', 0)

    @db_available
    def test23_queryLogicalAttacks(self):
        self.queryAttackType('grandtest', 'logical_access', '', 55840)

    @db_available
    def test24_queryLogicalAttacksLogicalAccess(self):
        self.queryAttackType('logical_access', 'logical_access', '', 55840)

    @db_available
    def test25_queryReplayAttacksPhysicalAccess(self):
        self.queryAttackType('physical_access', 'replay', '', 8800)

    @db_available
    def test26_queryLaptopHQspeaker(self):
        self.queryAttackType('grandtest', 'replay', 'laptop_HQ_speaker', 2200)

    @db_available
    def test27_queryPhone1(self):
        self.queryAttackType('grandtest', 'replay', 'phone1', 2200)

    @db_available
    def test28_queryPhone2(self):
        self.queryAttackType('grandtest', 'replay', 'phone2', 2200)

    @db_available
    def test29_queryPhysicalAccess(self):
        self.queryAttackType('physical_access', 'physical_access', '', 55840)

    @db_available
    def test30_queryPhysicalAccessHQspeaker(self):
        self.queryAttackType('physical_access', 'physical_access_HQ_speaker', '', 55840)
