#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the Biosecurid database.
"""

import os, sys
import unittest
import bob.db.biosecurid.face

class BiosecuridDatabaseTest(unittest.TestCase):
  """Performs various tests on the Biosecurid database."""

  def test01_clients(self):
    db = bob.db.biosecurid.face.Database()
    self.assertEqual(len(db.groups()), 3)
    self.assertEqual(len(db.clients()), 400)
    self.assertEqual(len(db.clients(groups='dev')), 150)
    self.assertEqual(len(db.clients(groups='eval')), 100)
    self.assertEqual(len(db.clients(groups='world')), 150)
    self.assertEqual(len(db.clients(groups='impostorDev')), 12)
    self.assertEqual(len(db.clients(groups='impostorEval')), 10)
    self.assertEqual(len(db.models()), 228)
    self.assertEqual(len(db.models(groups='dev')), 138)
    self.assertEqual(len(db.models(groups='eval')), 90)


  def test02_objects(self):
    db = bob.db.biosecurid.face.Database()
    self.assertEqual(len(db.objects()), 6400)
    # A
    self.assertEqual(len(db.objects(protocol='A')), 6400)
    self.assertEqual(len(db.objects(protocol='A', groups='world')), 2400)
    self.assertEqual(len(db.objects(protocol='A', groups='dev')), 2400)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='enrol')), 1104)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe')), 1296)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', classes='client')), 1104)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', classes='impostor')), 192)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151])), 200)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151], classes='client')), 8)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151], classes='impostor')), 192)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151,1152])), 208)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151,1152], classes='client')), 16)
    self.assertEqual(len(db.objects(protocol='A', groups='dev', purposes='probe', model_ids=[1151,1152], classes='impostor')), 192)
    self.assertEqual(len(db.objects(protocol='A', groups='eval')), 1600)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='enrol')), 720)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe')), 880)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', classes='client')), 720)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', classes='impostor')), 160)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301])), 168)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301], classes='client')), 8)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301], classes='impostor')), 160)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301,1302])), 176)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301,1302], classes='client')), 16)
    self.assertEqual(len(db.objects(protocol='A', groups='eval', purposes='probe', model_ids=[1301,1302], classes='impostor')), 160)






  def test03_driver_api(self):

    from bob.db.base.script.dbmanage import main
    self.assertEqual(main('biosecurid.face dumplist --self-test'.split()), 0)
    self.assertEqual(main('biosecurid.face dumplist --protocol=A --class=client --group=dev --purpose=enrol --client=1151 --self-test'.split()), 0)
    self.assertEqual(main('biosecurid.face checkfiles --self-test'.split()), 0)
    self.assertEqual(main('biosecurid.face reverse user1001/session0001/u1001s0001_fa0001 --self-test'.split()), 0)
    self.assertEqual(main('biosecurid.face path 3011 --self-test'.split()), 0)

