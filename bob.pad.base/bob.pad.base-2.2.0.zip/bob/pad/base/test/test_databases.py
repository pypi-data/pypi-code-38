#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#

import os
import unittest
import bob.pad.base
from bob.pad.base.test.dummy.database_sql import create_database

import pkg_resources

import tempfile
import shutil

dummy_dir = pkg_resources.resource_filename('bob.pad.base', 'test/dummy')

regenerate_database = False

class DummyDatabaseSqlTest(unittest.TestCase):

    def test01_database(self):
        # check that the database API works
        if regenerate_database:
            create_database()

        db = bob.pad.base.test.dummy.database_sql.TestDatabaseSql()

        def check_file(fs, l=1):
            assert len(fs) == l
            if l == 1:
                f = fs[0]
            else:
                f = fs[0][0]
            assert isinstance(f, bob.pad.base.test.dummy.database_sql.TestFileSql)
            assert f.id == 1
            assert f.client_id == 5
            assert f.path == "test/path"

        check_file(db.objects())
        check_file(db.all_files(), 2)
        check_file(db.training_files(), 2)
        check_file(db.files([1]))
        check_file(db.reverse(["test/path"]))
        # check if flat returns flat files
        assert len(db.all_files(flat=True)) == 2, db.all_files(flat=True)
        check_file(db.all_files(flat=True)[0:1])
        check_file(db.all_files(flat=True)[1:2])

        file = db.objects()[0]
        assert db.original_file_name(file) == "original/directory/test/path.orig"
        assert db.file_names([file], "another/directory", ".other")[0] == "another/directory/test/path.other"
        assert db.paths([1], "another/directory", ".other")[0] == "another/directory/test/path.other"

        # try file save
        temp_dir = tempfile.mkdtemp(prefix="bob_db_test_")
        data = [1., 2., 3.]
        file.save(data, temp_dir)
        assert os.path.exists(file.make_path(temp_dir, ".hdf5"))
        read_data = bob.io.base.load(file.make_path(temp_dir, ".hdf5"))
        for i in range(3):
            assert data[i] == read_data[i]
        shutil.rmtree(temp_dir)


class DummyDatabaseTest(unittest.TestCase):
    """Performs various tests on the AVspoof attack database."""

    def test00_db_available(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database',
                                            package_prefix='bob.pad.')
        self.assertTrue(db)

    def test01_trainFiles(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        files = db.training_files()
        self.assertEqual(len(files), 2)
        names = db.original_file_names(files)
        self.assertEqual(len(names), 2)
        self.assertTrue(('train_attack' in names[1]))
        self.assertTrue(('train_real' in names[0]))

    # @db_available
    def test02_devFiles(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        files = db.all_files('dev')
        self.assertEqual(len(files), 2)
        names = db.original_file_names(files)
        self.assertEqual(len(names), 2)
        self.assertTrue(('dev_attack' in names[1]))
        self.assertTrue(('dev_real' in names[0]))

    # @db_available
    def test03_evalFiles(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        files = db.all_files('eval')
        self.assertEqual(len(files), 2)
        names = db.original_file_names(files)
        self.assertEqual(len(names), 2)
        self.assertTrue(('eval_attack' in names[1]))
        self.assertTrue(('eval_real' in names[0]))

    # @db_available
    def test04_trainFiles4Test(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        files = db.all_files('train')
        self.assertEqual(len(files), 2)
        names = db.original_file_names(files)
        self.assertEqual(len(names), 2)
        self.assertTrue(('train_attack' in names[1]))
        self.assertTrue(('train_real' in names[0]))

    # @db_available
    def test05_scoreFiles(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        files = db.all_files('train')
        self.assertEqual(len(files), 2)
        names = db.original_file_names(files)
        self.assertEqual(len(names), 2)
        self.assertTrue(('train_attack' in names[1]))
        self.assertTrue(('train_real' in names[0]))

    # @db_available
    def test06_getAllData(self):
        db = bob.bio.base.load_resource(os.path.join(dummy_dir, 'database.py'), 'database', package_prefix='bob.pad.')
        self.assertEqual(len(db.all_files('train')), 2)
        self.assertEqual(len(db.all_files('dev')), 2)
        self.assertEqual(len(db.all_files('eval')), 2)
        self.assertEqual(len(db.all_files(('train, dev, eval'))[1]), 3)
        self.assertEqual(len(db.all_files(('train, dev, eval'))[0]), 3)

    # @db_available
    def test07_manage_files(self):
        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('spoof_test files'.split()), 0)

    # @db_available
    def test08_manage_dumplist(self):
        from bob.db.base.script.dbmanage import main

        self.assertEqual(main('spoof_test dumplist --self-test'.split()), 0)
