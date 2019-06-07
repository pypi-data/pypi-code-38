#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# Nathaniel Watson
# nathanielwatson@stanfordhealthcare.org
# 2019-05-21
###

"""
Tests functions in the ``sruns_monitor.sqlite_utils`` module.
"""

import hashlib
import json
import os
import unittest

from sruns_monitor.tests import WATCH_DIR, TMP_DIR
from sruns_monitor.sqlite_utils import Db


class TestStatus(unittest.TestCase):
    """
    Tests `Db.get_run_status` for returning the correct workflow status value based on 
    varying conditions in a database record. 
    """

    def setUp(self):
        """
        Creates a `Db` instance and associates that to the `self.db` attribute. 
        The database name is referenced by `self.dbname`. The SQLite database will be created in the
        temporary directory specified by `sqlite_utils.tests.TMP_DIR`. 
        """
        self.dbname = os.path.join(TMP_DIR, "test_sqlite_utils.db")
        self.db = Db(dbname=self.dbname)

    def tearDown(self):
        """
        Remove local SQLite database after each test runs.
        """
        os.remove(self.dbname)

    def test_status_new_run(self):
        """
        When we don't have a record for a given run in the database, we should get the status
        `sqlite_utis.Db.RUN_STATUS_NEW`.
        """
        status = self.db.get_run_status("CompletedRun1")
        self.assertEqual(status, Db.RUN_STATUS_NEW)

    def test_status_run_complete(self):
        """
        When a record has a value set for each attribute that represents a workflow step result,
        i.e. the tarfile path and the GCP Storage object path, `Db.get_run_status` 
        should return the status `Db.RUN_STATUS_COMPLETE`.
        """
        run_name = "testrun"
        self.db.insert_run(name=run_name, tarfile="run.tar.gz", gcp_tarfile="/bucket/obj.tar.gz")
        status = self.db.get_run_status(run_name)
        self.assertEqual(status, Db.RUN_STATUS_COMPLETE)

    def test_status_not_running_1(self):
        """
        When a record has a partially completed workflow and the PID value is not set,
        `Db.get_run_status` should return the status `Db.RUN_STATUS_NOT_RUNNING`.
        """
        run_name = "testrun"
        self.db.insert_run(name=run_name, tarfile="run.tar.gz", gcp_tarfile="", pid=0)
        status = self.db.get_run_status(run_name)
        self.assertEqual(status, Db.RUN_STATUS_NOT_RUNNING)

    def test_status_not_running_2(self):
        """
        When a record has a partially completed workflow and the PID value is set but
        that process doesn't actually exist, `Db.get_run_status` should return the
        status `Db.RUN_STATUS_NOT_RUNNING`.
        """
        run_name = "testrun"
        self.db.insert_run(name=run_name, tarfile="run.tar.gz", gcp_tarfile="", pid=1010101010)
        status = self.db.get_run_status(run_name)
        self.assertEqual(status, Db.RUN_STATUS_NOT_RUNNING)

    def test_status_running(self):
        """
        When a record has a partially completed workflow and the PID value is set and
        that process exists, `Db.get_run_status` should return the status
        `Db.RUN_STATUS_STARTING`.
        """
        run_name = "testrun"
        self.db.insert_run(name=run_name, tarfile="run.tar.gz", gcp_tarfile="", pid=os.getpid())
        status = self.db.get_run_status(run_name)
        self.assertEqual(status, Db.RUN_STATUS_RUNNING)



class TestDb(unittest.TestCase):
    """
    Tests the record creation/modification methods in the class `sruns_monitor.Db`.
    """

    def setUp(self):
        self.dbfile = "test.db"
        # Instantiating the Db class should create the database and a tasks table.
        self.db = Db(self.dbfile)


    def tearDown(self):
        self.db.conn.close() # Prevent 'sqlite3.OperationalError: database is locked' errors.
        os.remove(self.dbfile)

    def test_db_exists(self):
        """
        Tests that the database file gets created when instantiating the `sruns_monitor.Db` class.
        """
        self.assertTrue(os.path.exists(self.dbfile))

    def test_db_table_exists(self):
        """
        Tests that the database contains the table specified by the class variable
        `Db.TASKS_TABLE_NAME`.
        """
        tables = self.db.get_tables()
        self.assertTrue(Db.TASKS_TABLE_NAME in tables)

    def test_insert_run_attr_name(self):
        """
        Tests `sqlite_utls.Db.insert_run` for success when creating a new record with only the name
        attribute set.
        """
        run_name = "first_run"
        self.db.insert_run(name=run_name)
        rec = self.db.get_run(run_name)
        expected = {
            Db.TASKS_NAME: run_name,
            Db.TASKS_PID: 0,
            Db.TASKS_TARFILE: '',
            Db.TASKS_GCP_TARFILE: ''
        }
        self.assertTrue(rec == expected)

    def test_insert_run_attrs_name_pid(self):
        """
        Tests `sqlite_utls.Db.insert_run` for success when creating a new record with only the name
        and pid attributes set.
        """
        run_name = "first_run"
        pid = 77103
        self.db.insert_run(name=run_name, pid=pid)
        rec = self.db.get_run(run_name)
        expected = {
            Db.TASKS_NAME: run_name,
            Db.TASKS_PID: pid,
            Db.TASKS_TARFILE: '',
            Db.TASKS_GCP_TARFILE: ''
        }
        self.assertTrue(rec == expected)

    def test_update_run_attr_tarfile(self):
        """
        Tests `sqlite_utls.Db.update_run` for success when updating an existing record to add a value
        for the local tarfile path.
        """
        run_name = "first_run"
        pid = 77103
        self.db.insert_run(name=run_name, pid=pid)
        tarfile = run_name + ".tar.gz"
        self.db.update_run(name=run_name, payload={Db.TASKS_TARFILE: tarfile})
        rec = self.db.get_run(run_name)
        expected = {
            Db.TASKS_NAME: run_name,
            Db.TASKS_PID: pid,
            Db.TASKS_TARFILE: tarfile,
            Db.TASKS_GCP_TARFILE: ''
        }
        self.assertTrue(rec == expected)

    def test_update_run_attr_gcptarfile(self):
        """
        Tests `sqlite_utls.Db.update_run` for success when updating an existing record to add a value
        for the gcp_tarfile path.
        """
        run_name = "first_run"
        pid = 77103
        tarfile = run_name + ".tar.gz"
        self.db.insert_run(name=run_name, pid=pid, tarfile=tarfile)
        gcp_tarfile = "run_name/run_name.tar.gz"
        self.db.update_run(name=run_name, payload={Db.TASKS_GCP_TARFILE: gcp_tarfile})
        rec = self.db.get_run(run_name)
        print(rec)
        expected = {
            Db.TASKS_NAME: run_name,
            Db.TASKS_PID: pid,
            Db.TASKS_TARFILE: tarfile,
            Db.TASKS_GCP_TARFILE: gcp_tarfile
        }
        self.assertTrue(rec == expected)


if __name__ == "__main__":
    unittest.main()
