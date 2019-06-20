#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Fri 3 Feb 13:43:22 2017
#


"""A few checks at the asvspoof2017 attack database.
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
                dbfile, 'asvspoof2017'))

    return wrapper


class ASVspoof2017DatabaseTest(unittest.TestCase):
    """Performs various tests on the AVspoof attack database."""

    @db_available
    def queryGroupsProtocolsTypes(self, protocol, purpose, Ntrain, Ndev, Neval):

        db = Database()
        f = db.objects(purposes=purpose, protocol=protocol)

        self.assertEqual(len(f), Ntrain+Ndev+Neval)
        for k in f[:10]:  # only the 10 first...
            if purpose == 'genuine':
                self.assertTrue(k.is_real())
            if purpose == 'spoof':
                self.assertTrue(k.is_attack())

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
        self.queryGroupsProtocolsTypes('competition',  'genuine', 1508, 760, 0)

    @db_available
    def test02_queryAttacksCM(self):
        self.queryGroupsProtocolsTypes('competition', 'spoof', 1508, 950, 0)

    @db_available
    def test12_queryClients(self):

        db = Database()
        f = db.clients()
        self.assertEqual(len(f), 18)  # 18 clients
        self.assertTrue(db.has_client_id('M0001'))
        self.assertFalse(db.has_client_id('M0019'))
        self.assertTrue(db.has_client_id('M0008'))
        self.assertFalse(db.has_client_id('M01'))
        self.assertFalse(db.has_client_id('M0100'))
        self.assertTrue(db.has_client_id('M0011'))

    @db_available
    def test13_queryAudioFile(self):

        db = Database()
        o = db.objects(clients=('M0001',))[0]
        o.audiofile()

    @db_available
    def test14_manage_files(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof2017 files'.split()), 0)

    @db_available
    def test15_manage_dumplist_1(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof2017 dumplist --self-test'.split()), 0)

    @db_available
    def test16_manage_dumplist_2(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main(
            'asvspoof2017 dumplist --purpose=spoof --group=dev --protocol=competition --self-test'.split()), 0)

    @db_available
    def test17_manage_dumplist_client(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof2017 dumplist --client=M0008 --self-test'.split()), 0)

    @db_available
    def test18_manage_checkfiles(self):

        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('asvspoof2017 checkfiles --self-test'.split()), 0)

    @db_available
    def queryAttackType(self, protocol, attack, N):

        db = Database()
        f = db.objects(purposes='spoof', attacks=attack, protocol=protocol)
        self.assertEqual(len(f), N)
        for k in f[:10]:  # only the 10 first...
            self.assertTrue(k.is_attack)

    @db_available
    def test19_queryS5AttacksCM(self):
        self.queryAttackType('competition', 'spoof', 2458)

    @db_available
    def test20_queryS1AttacksCM(self):
        self.queryAttackType('competition', 'undefined', 0)

