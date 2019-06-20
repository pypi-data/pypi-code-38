#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the KBOC16 database.
"""

import os, sys
import unittest
from .query import Database

class kboc16DatabaseTest(unittest.TestCase):

    def test_clients(self):
      db = Database()
      assert len(db.groups()) == 1
      assert len(db.clients()) == 300
      assert len(db.clients(groups='eval')) ==300
      assert len(db.clients(protocol = 'A', groups='eval')) == 300
      assert len(db.clients(protocol = 'A')) == 300
      assert len(db.clients(protocol = 'D', groups='eval')) == 100
      assert len(db.clients(protocol = 'D')) == 100
      assert len(db.models()) == 300
      assert len(db.models(groups='eval')) == 300
      assert len(db.models(protocol = 'A', groups='eval')) == 300
      assert len(db.models(protocol = 'A')) == 300
      assert len(db.models(protocol = 'D', groups='eval')) == 100
      assert len(db.models(protocol = 'D')) == 100
      assert not u'101' in [x.id for x in db.models(protocol = 'D', groups='eval')]
      assert u'1' in [x.id for x in db.models(protocol = 'D', groups='eval')]
      assert u'100' in [x.id for x in db.models(protocol = 'D', groups='eval')]



    def test_objects(self):
      db = Database()
      assert len(db.objects()) == 7200
      # A
      assert len(db.objects(protocol='A')) == 7200
      assert len(db.objects(protocol='A', groups='eval')) == 7200
      assert len(db.objects(protocol='A', groups='eval', purposes='enrol')) == 1200
      assert len(db.objects(protocol='A', groups='eval', purposes='probe')) == 6000
      assert len(db.objects(protocol='A', groups='eval', purposes='probe', classes='client')) == 6000
      assert len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1])) == 20
      assert len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1], classes='client')) == 20
      assert len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1,2])) == 40
      assert len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1,2], classes='client')) == 40

      # D
      assert len(db.objects(protocol='D')) == 2400
      assert len(db.objects(protocol='D', groups='eval')) == 2400
      assert len(db.objects(protocol='D', groups='eval', purposes='enrol')) == 400
      assert len(db.objects(protocol='D', groups='eval', purposes='probe')) == 2000
      assert len(db.objects(protocol='D', groups='eval', purposes='probe', classes='client')) == 2000
      assert len(db.objects(protocol='D', groups='eval', purposes='probe', model_ids=[1])) == 20
      assert len(db.objects(protocol='D', groups='eval', purposes='probe', model_ids=[1], classes='client')) == 20
      assert len(db.objects(protocol='D', groups='eval', purposes='probe', model_ids=[1,2])) == 40
      assert len(db.objects(protocol='D', groups='eval', purposes='probe', model_ids=[1,2], classes='client')) == 40


    def test_driver_api(self):

      from bob.db.base.script.dbmanage import main
      assert main('kboc16 dumplist --self-test'.split()) == 0
      assert main('kboc16 checkfiles --self-test'.split()) == 0
      assert main('kboc16 reverse T001_01 --self-test'.split()) == 0
      assert main('kboc16 path 37 --self-test'.split()) == 0
