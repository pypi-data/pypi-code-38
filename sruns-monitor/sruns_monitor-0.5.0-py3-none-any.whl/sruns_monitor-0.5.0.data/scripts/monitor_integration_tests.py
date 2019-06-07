#!python
# -*- coding: utf-8 -*-

###
# Nathaniel Watson
# nathanielwatson@stanfordhealthcare.org
# 2019-05-21
###

"""
Tests functions in the ``sruns_monitor.monitor`` module. Because these are functional/integrational
tests, some user input is required in the form of a JSON configuration file. This should contain
a subset of the fields in the configuration file expected by the Monitor. Below is an example of
what is expected::

  {                                                                                                      
    "firestore_collectionection": "sequencing_runs",                                                           
    "gcp_bucket_name": "nathankw-testcgs",                                                               
    "gcp_bucket_basedir": "/",                                                                           
    "cycle_pause_sec": 60,                                                                               
    "task_runtime_limit_sec": 86400                                                                      
  }

This file must be named conf.json and must exist in the calling directory. 
"""

import hashlib
import json
import os
import unittest

from google.cloud import storage

import sruns_monitor as srm
from sruns_monitor.tests import WATCH_DIR, TMP_DIR
from sruns_monitor import utils
from sruns_monitor.monitor import Monitor
from sruns_monitor.sqlite_utils import Db 

#: The name of configuration file in JSON format that is used to instantiate the Monitor class. 
#: This file must exist in the calling directory.
CONF_FILE = "conf.json"

SQLITE_DB = os.path.join(os.path.dirname(__file__), "monitortest.db")

#: Flag that when set to True enables Firestore tests to run. This will be set to True automatically
#: when the user's conf.json file contains the firestore_collection parameter. 
FIRESTORE = False

def remove_test_db():
    if os.path.exists(SQLITE_DB):
        os.remove(SQLITE_DB)

def process_user_conf_file():
    """
    Because a user running the functional tests in this file needs to provide their own conf.json
    file in the calling directory in order to provide minimal configuration such as bucket name and
    Firestore collection, this function processes that file to add `sruns_monitor.C_WATCHDIR` and
    `sruns_monitor.C_SQLITE_DB` parameters that always point to test data within the 
    `sruns_monitor.tests`.  

    Additionally, sets the global variable FIRESTORE to True if the conf.json file contains the
    `sruns_monitor.C_FIRESTORE_COLLECTION` parameter, which will enable the Firestore tests to run.
    """
    global FIRESTORE
    fh = open(CONF_FILE)
    jconf = json.loads(fh.read())
    fh.close()
    firestore_coll = jconf.get(srm.C_FIRESTORE_COLLECTION)
    if firestore_coll and not firestore_coll.startswith("#"):
        FIRESTORE = True
    jconf[srm.C_WATCHDIR] = WATCH_DIR
    jconf[srm.C_SQLITE_DB] = SQLITE_DB
    fout = open(CONF_FILE, "w")
    fout.write(json.dumps(jconf, indent=4))
    fout.close()

def get_bucket(bucket_name):
    storage_client = storage.Client()
    return storage_client.get_bucket(bucket_name)

class TestTaskTar(unittest.TestCase):

    def setUp(self):
        """
        Creates a `Monitor` instance before each test runs.  The SQLite database specified by the
        conf file is created when the Monitor is instantiated, and a record is written with only
        its name attribute set. Then, the tar task executes. Once that completes, the SQLite
        record is stored as `self.rec` for inspection in the various test methods.
        """
        self.monitor = Monitor(conf_file=CONF_FILE)
        self.run_name = "CompletedRun1" # An actual test run directory
        self.monitor.sqlite_conn_mainthread.insert_run(name=self.run_name)
        self.monitor.task_tar(state=self.monitor.state, run_name=self.run_name, lock=self.monitor.lock, sqlite_conn=self.monitor.get_sqlite_conn())
        self.rec = self.monitor.sqlite_conn_mainthread.get_run(name=self.run_name)

    def test_scan(self):
        """
        Tests `Monitor.scan` for success. It should find only the completed run directories.
        """
        rundirs = self.monitor.scan()
        self.assertEqual(rundirs, ["CompletedRun1", "CompletedRun2", "TEST_RUN_DIR"])

    def tearDown(self):
        """
        Remove local SQLite database and tarfile after each test runs.
        """
        remove_test_db()
        os.remove(self.rec[Db.TASKS_TARFILE])


    def test_task_tar_pid_set(self):
        """
        Makes sure that when tarring a run directory, the pid of the child process is inserted into
        the SQLite record. Note in this case, the tarring method is run in the same thread, which
        is fine since this test is chiefly concerned with verifying that the pid attribute
        of the record is set.
        """
        pid = self.rec[Db.TASKS_PID]
        self.assertTrue(pid > 0)

    def test_task_tar_tarfile_set(self):
        """
        Makes sure that after tarring a run directory, the tarfile name is inserted into
        the SQLite record.
        """
        tarfile = self.rec[Db.TASKS_TARFILE]
        self.assertTrue(bool(tarfile))

    def test_task_tar_tarfile_exists(self):
        """
        Makes sure that after tarring a run directory, the tarfile referenced in the database
        record actually exists.
        """
        tarfile = self.rec[Db.TASKS_TARFILE]
        self.assertTrue(os.path.exists(tarfile))


class TestTaskUpload(unittest.TestCase):
    """
    Test's the monitor's upload-to-GCP-Storage application logic.
    """

    def setUp(self):
        """
        Create a `Monitor` instance before each test runs.  The SQLite database specified by the
        conf file is created when the Monitor is instantiated. A run record is inserted into
        the database with a value already set for the local tarfile path, which points to a tarfile
        that is also created each time before a test runs as `Monitor.task_upload` removes the local
        tarfile before exiting.  Then, the upload task executes. Once that completes, the SQLite
        record is stored as `self.rec` for inspection in the various test methods.
        """
        self.monitor = Monitor(conf_file=CONF_FILE)
        self.bucket = get_bucket(self.monitor.bucket_name)
        self.run_name = "CompletedRun1" # An actual test run directory
        self.tarfile = os.path.join(TMP_DIR, "rundir.tar.gz")
        fh = open(self.tarfile, 'w')
        fh.write("test line")
        fh.close()
        self.monitor.sqlite_conn_mainthread.insert_run(name=self.run_name, tarfile=self.tarfile)
        self.monitor.task_upload(state=self.monitor.state, run_name=self.run_name, lock=self.monitor.lock, sqlite_conn=self.monitor.get_sqlite_conn())
        self.rec = self.monitor.sqlite_conn_mainthread.get_run(name=self.run_name)

    def tearDown(self):
        """
        Remove local SQLite database after each test runs, as well as the blob object that is
        created in GCP Storage.
        """
        remove_test_db()
        blob = self.monitor.create_blob_name(run_name=self.run_name, filename=self.tarfile)
        self.bucket.delete_blob(blob) # raises google.api_core.exceptions.NotFound if blob doesn't exist.

    def test_task_upload_pid_set(self):
        """
        Makes sure that when uploading a tarball to GCP, the pid of the child process is inserted into
        the database record.
        """
        pid = self.rec[Db.TASKS_PID]
        self.assertTrue(pid > 0)

    def test_task_upload_tarfile_removed(self):
        """
        Makes sure that after uploading a tarball to GCP, the local tarfile is removed. Note that
        the local record's `Db.TASKS_TARFILE` attribute value is not changed, rather
        the file is just removed.
        """
        tarfile = self.rec[Db.TASKS_TARFILE]
        self.assertFalse(os.path.exists(tarfile))

    def test_task_upload_gcp_tarfile_set(self):
        """
        Makes sure that after uploading a tarred run directory to GCP, the SQLite database record's
        `Db.TASKS_GCP_TARFILE` attribute is set. Note that it should be set to the
        object's name in GCP, but this part of the logic isn't tested in this method.
        """
        gcp_tarfile = self.rec[Db.TASKS_GCP_TARFILE]
        self.assertTrue(bool(gcp_tarfile))

    def test_task_upload_gcp_tarfile_exists(self):
        """
        Makes sure that after uploading a tarred run directory to GCP, the GCP object referenced in
        the local database record's `Db.TASKS_GCP_TARFILE` attribute actually exists
        at the indicated location.
        """
        gcp_tarfile = self.rec[Db.TASKS_GCP_TARFILE]
        # gcp_tarfile has 'bucket_name/' at the beginnig of the path - need to remove that.
        gcp_tarfile = gcp_tarfile.split("/", 1)[-1]
        blob = self.bucket.get_blob(gcp_tarfile)
        # blob is None if file doesn't exist in GCP, otherwise it's a Blob instance.
        self.assertTrue(bool(blob))


class TestFirestore(unittest.TestCase):

    def setUp(self):
        """
        Create a `Monitor` instance before each test runs.  The SQLite database specified by the
        conf file is created when the Monitor is instantiated. A run record is inserted into
        the local SQLite database with a value set for the name only. Also, a Firestore record is
        created that initially sets the run name attribute, as well as the workflow status attribute
        to starting.
        """
        self.monitor = Monitor(conf_file=CONF_FILE)
        self.run_name = "CompletedRun1" # An actual test run directory
        self.monitor.sqlite_conn_mainthread.insert_run(name=self.run_name)
        # Create Firestore document
        firestore_payload = {
            srm.FIRESTORE_ATTR_WF_STATUS: Db.RUN_STATUS_STARTING
        }
        self.firestore_conn = self.monitor.get_firestore_conn()
        self.firestore_conn.document(self.run_name).set(firestore_payload)

    def tearDown(self):
        """
        Remove local SQLite database after each test runs, as well as the related Firestore record.
        """
        remove_test_db()
        self.firestore_conn.document(self.run_name).delete()

    def test_status_tar_complete(self):
        """
        Tests that after tarring is complete, the Firestore record's `sruns_monitor.FIRESTORE_ATTR_WF_STATUS`
        attribute is set to `Db.RUN_STATUS_TARRING_COMPLETE`.
        """
        self.monitor.task_tar(state=self.monitor.state, run_name=self.run_name, lock=self.monitor.lock, sqlite_conn=self.monitor.get_sqlite_conn())
        doc_ref = self.firestore_conn.document(self.run_name).get()
        doc = doc_ref.to_dict()
        self.assertEqual(doc[srm.FIRESTORE_ATTR_WF_STATUS], Db.RUN_STATUS_TARRING_COMPLETE)

    def test_status_upload_complete(self):
        """
        Tests that after uploading the tarfile to GCP is complete, the Firestore record's
        `sruns_monitor.FIRESTORE_ATTR_WF_STATUS` attribute is set to `Db.RUN_STATUS_UPLOADING_COMPLETE`.
        """
        self.monitor.task_tar(state=self.monitor.state, run_name=self.run_name, lock=self.monitor.lock, sqlite_conn=self.monitor.get_sqlite_conn())
        self.monitor.task_upload(state=self.monitor.state, run_name=self.run_name, lock=self.monitor.lock, sqlite_conn=self.monitor.get_sqlite_conn())
        doc_ref = self.firestore_conn.document(self.run_name).get()
        doc = doc_ref.to_dict()
        self.assertEqual(doc[srm.FIRESTORE_ATTR_WF_STATUS], Db.RUN_STATUS_UPLOADING_COMPLETE)

    def test_status_complete(self):
        """
        Tests that after running the entire workflow, the Firestore record's
        `sruns_monitor.FIRESTORE_ATTR_WF_STATUS` attribute is set to `Db.RUN_STATUS_COMPLETE`.

        Calls `monitor.Monitor.process_completed_run()`, which updates two attributes in Firestore:

          * `sruns_monitor.FIRESTORE_ATTR_WF_STATUS`
          * `sruns_monitor.FIRESTORE_ATTR_STORAGE`

        The first is set to completed status, and the latter is set to the value of the local database
        record's `sqlite_utils.Db.TASKS_GCP_TARFILE` attribute. This method tests that the first
        attribute's value is what we expect.
        """
        self.monitor.process_completed_run(run_name=self.run_name, archive=False)
        doc_ref = self.firestore_conn.document(self.run_name).get()
        doc = doc_ref.to_dict()
        self.assertEqual(doc[srm.FIRESTORE_ATTR_WF_STATUS], Db.RUN_STATUS_COMPLETE)

    def test_tarfile_path(self):
        """
        Tests that after running the entire workflow, the Firestore record's
        `sruns_monitor.FIRESTORE_ATTR_STORAGE` attribute is set to the same value as designated in
        the local SQLite record.

        Calls `monitor.Monitor.process_completed_run()`, which updates two attributes in Firestore:

          * `sruns_monitor.FIRESTORE_ATTR_WF_STATUS`
          * `sruns_monitor.FIRESTORE_ATTR_STORAGE`

        The first is set to completed status, and the latter is set to the value of the local database
        record's `sqlite_utils.Db.TASKS_GCP_TARFILE` attribute. This method tests that the second
        attribute's value is what we expect.
        """
        self.monitor.process_completed_run(run_name=self.run_name, archive=False)
        fs_doc_ref = self.firestore_conn.document(self.run_name).get()
        fs_doc = fs_doc_ref.to_dict()
        local_rec = self.monitor.sqlite_conn_mainthread.get_run(name=self.run_name)
        self.assertEqual(fs_doc[srm.FIRESTORE_ATTR_STORAGE], local_rec[Db.TASKS_GCP_TARFILE])


def get_suite():
    process_user_conf_file()
    test_classes = [TestTaskTar, TestTaskUpload]
    if FIRESTORE:
        test_classes.append(TestFirestore)
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for i in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(i))
    return suite
    

if __name__ == "__main__":
    suite = get_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
