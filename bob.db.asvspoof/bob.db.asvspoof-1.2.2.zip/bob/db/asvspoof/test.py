#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Wed 2 Dec 15:19:22 2015
#


"""A few checks at the asvspoof attack database.
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
                dbfile, 'asvspoof'))

    return wrapper


class ASVspoofDatabaseTest(unittest.TestCase):
    """Performs various tests on the AVspoof attack database."""

    @db_available
    def queryGroupsProtocolsTypes(self, protocol, purpose, Ntrain, Ndev, Neval):

        db = Database()
        f = db.objects(purposes=purpose, protocol=protocol)

        self.assertEqual(len(f), Ntrain+Ndev+Neval)
        for k in f[:10]:  # only the 10 first...
            if purpose == 'real':
                self.assertTrue(k.is_real())
            if purpose == 'attack':
                self.assertTrue(k.is_attack())
            if purpose == 'impostor':
                self.assertTrue(k.is_impostor())
            if purpose == 'enroll':
                self.assertTrue(k.is_enroll())

        train = db.objects(purposes=purpose, groups='train', protocol=protocol)
        self.assertEqual(len(train), Ntrain)

        dev = db.objects(purposes=purpose, groups='dev', protocol=protocol)
        self.assertEqual(len(dev), Ndev)

        eval = db.objects(purposes=purpose, groups='eval', protocol=protocol)
        self.assertEqual(len(eval), Neval)

        # tests train, dev, and eval files are distinct
        s = set(train + dev + eval)
        self.assertEqual(len(s), Ntrain+Ndev+Neval)

    @db_available
    def test01_queryRealCM(self):
        self.queryGroupsProtocolsTypes('CM',  'real', 3750, 3497, 9404)

    @db_available
    def test02_queryAttacksCM(self):
        self.queryGroupsProtocolsTypes('CM', 'attack', 12625, 49875, 184000)

    @db_available
    def test03_queryRealASV(self):
        self.queryGroupsProtocolsTypes('ASV-male',  'real', 0, 1498, 4053)

    @db_available
    def test04_queryAttackASV(self):
        self.queryGroupsProtocolsTypes('ASV-male',  'attack', 0, 21375, 80000)

    @db_available
    def test05_queryImpostorASV(self):
        self.queryGroupsProtocolsTypes('ASV-male',  'impostor', 0, 4275, 8000)

    @db_available
    def test06_queryEnrollASV(self):
        self.queryGroupsProtocolsTypes('ASV-male',  'enroll', 0, 75, 100)
        self.queryGroupsProtocolsTypes('ASV-female',  'enroll', 0, 100, 130)

    @db_available
    def test07_queryRealASVFemale(self):
        self.queryGroupsProtocolsTypes('ASV-female',  'real', 0, 1999, 5351)

    @db_available
    def test08_queryAttackASVFemale(self):
        self.queryGroupsProtocolsTypes('ASV-female',  'attack', 0, 28500, 104000)

    @db_available
    def test09_queryImpostorASVFemale(self):
        self.queryGroupsProtocolsTypes('ASV-female',  'impostor', 0, 5700, 10400)

    @db_available
    def queryEnrollments(self, protocol, N):

        db = Database()
        f = db.objects(purposes='enroll', protocol=protocol)
        self.assertEqual(len(f), N)
        for k in f[:10]:  # only the 10 first...
            self.assertTrue(k.is_enroll())

    @db_available
    def test09_queryEnrollmentsCM(self):
        self.queryEnrollments('CM', 0)

    @db_available
    def test10_queryEnrollmentsASVFemale(self):
        self.queryEnrollments('ASV-female', 230)

    @db_available
    def test11_queryEnrollmentsASVMale(self):
        self.queryEnrollments('ASV-male', 175)

    @db_available
    def test12_queryClients(self):

        db = Database()
        f = db.clients()
        self.assertEqual(len(f), 107)  # 106 clients
        self.assertTrue(db.has_client_id('D19'))
        self.assertFalse(db.has_client_id('E50'))
        self.assertTrue(db.has_client_id('E27'))
        self.assertFalse(db.has_client_id('D105'))
        self.assertFalse(db.has_client_id('E0'))
        self.assertTrue(db.has_client_id('T2'))

        f = db.clients(gender='male')
        self.assertEqual(len(f), 35)  # 35 male clients
        clients = []
        for c in f:
            clients.append(c.id)
        self.assertIn('D7', clients)
        self.assertNotIn('D12', clients)
        self.assertIn('E44', clients)
        self.assertNotIn('E11', clients)

        f = db.clients(gender='female')
        self.assertEqual(len(f), 46)  # 46 female clients
        clients = []
        for c in f:
            clients.append(c.id)
        self.assertNotIn('D7', clients)
        self.assertIn('D12', clients)
        self.assertNotIn('E44', clients)
        self.assertIn('E11', clients)

    @db_available
    def test13_queryAudioFile(self):

        db = Database()
        o = db.objects(clients=('D1',))[0]
        o.audiofile()

    @db_available
    def test14_manage_files(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof files'.split()), 0)

    @db_available
    def test15_manage_dumplist_1(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof dumplist --self-test'.split()), 0)

    @db_available
    def test16_manage_dumplist_2(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main(
            'asvspoof dumplist --purpose=attack --group=dev --protocol=CM --self-test'.split()), 0)

    @db_available
    def test17_manage_dumplist_client(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof dumplist --client=E23 --self-test'.split()), 0)

    @db_available
    def test18_manage_checkfiles(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof checkfiles --self-test'.split()), 0)

    @db_available
    def queryAttackType(self, protocol, attack, N):

        db = Database()
        f = db.objects(purposes='attack', support=attack, protocol=protocol)
        self.assertEqual(len(f), N)
        for k in f[:10]:  # only the 10 first...
            self.assertTrue(k.is_attack)


    @db_available
    def test19_queryS5AttacksCM(self):
        self.queryAttackType('CM', 'S5', 30900)

    @db_available
    def test20_queryS1AttacksCM(self):
        self.queryAttackType('CM', 'S1', 30900)

    @db_available
    def test21_queryS10AttacksASVMale(self):
        self.queryAttackType('ASV-male', 'S10', 8000)

    @db_available
    def test22_queryS10AttacksCM(self):
        self.queryAttackType('CM', 'S10', 18400)

    @db_available
    def test23_queryS4AttacksASVFemale(self):
        self.queryAttackType('ASV-female', 'S4', 16100)
