#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A few checks at the AT&T/ORL Face database.
"""

import os, sys
import unittest
from . import Database

class ATNTDatabaseTest(unittest.TestCase):
  """Performs various tests on the AT&T/ORL Face database."""

  def test01_query(self):
    db = Database()

    f = db.groups()
    self.assertEqual(len(f), 2) # number of groups

    f = db.objects()
    self.assertEqual(len(f), 400) # number of all files in the database

    f = db.objects(groups='world')
    self.assertEqual(len(f), 200) # number of all training files

    f = db.objects(groups='dev')
    self.assertEqual(len(f), 200) # number of all test files

    f = db.objects(groups='dev', purposes = 'enroll')
    self.assertEqual(len(f), 100) # number of enroll files

    f = db.objects(groups='dev', purposes = 'probe')
    self.assertEqual(len(f), 100) # number of probe files

    f = db.clients()
    self.assertEqual(len(f), 40) # number of clients

    f = db.clients(groups = 'world')
    self.assertEqual(len(f), 20) # number of training clients

    f = db.clients(groups = 'dev')
    self.assertEqual(len(f), 20) # number of test clients

    f = db.objects(groups = 'dev', purposes = 'enroll', model_ids = [3])
    self.assertEqual(len(f), 5)

    files = sorted(f, key=lambda x: x.id)
    values = sorted(list(db.m_enroll_files))
    for i in range(5):
      self.assertEqual(files[i].path, os.path.join("s3", str(values[i])))
      self.assertEqual(db.get_client_id_from_file_id(files[i].id), 3)

    # when querying a probe file, the model id must be ignored.
    f  = db.objects(groups = 'dev', purposes = 'probe', model_ids = [3])
    f2 = db.objects(groups = 'dev', purposes = 'probe')
    self.assertEqual(set([x.id for x in f]),set([x.id for x in f2]))

    # test the path function
    f = db.objects(groups='dev', purposes = 'enroll', model_ids = [7])
    ids = [x.id for x in f]
    paths = db.paths(ids, 'test', '.tmp')
    self.assertEqual(len(f), len(paths))
    for path in paths:
      parts = os.path.split(path)
      self.assertEqual(parts[0], os.path.join('test', 's7'))
      self.assertEqual(os.path.splitext(parts[1])[1], '.tmp')

    # test the reverse function
    tested_ids = [f.id for f in db.reverse(paths)]
    self.assertEqual(ids, tested_ids)


  def test02_driver_api(self):

    from bob.db.base.script.dbmanage import main

    self.assertEqual(main('atnt dumplist --self-test'.split()), 0)
    self.assertEqual(main('atnt checkfiles -d "." --self-test'.split()), 0)
    self.assertEqual(main('atnt reverse s34/1 --self-test'.split()), 0)
    self.assertEqual(main('atnt path 331 --self-test'.split()), 0)


