#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
# Nathaniel Watson
# nathanielwatson@stanfordhealthcare.org
# 2019-05-21
###

"""
Tests functions in the ``sruns_monitor.utils`` module.
"""

import hashlib
import json
import multiprocessing
import os
import psutil
import shutil
import tarfile
import time
import unittest

from sruns_monitor.tests import WATCH_DIR, TMP_DIR
from sruns_monitor import utils


class TestUtils(unittest.TestCase):
    """
    Tests functions in the ``sruns_monitor.utils`` module.
    """

    def setUp(self):
        self.test_rundir = os.path.join(WATCH_DIR, "CompletedRun1")
        self.test_delete_dirname = os.path.join(TMP_DIR, "DeleteTestDir")

    def tearDown(self):
        if os.path.exists(self.test_delete_dirname):
            shutil.rmtree(self.test_delete_dirname)

    def test_tar(self):
        """
        Tests that `utils.tar()` doesn't miss any files in the tarball. Tars the run directory at
        `self.test_rundir` and compares the list of files in the tarball with that which we expect
        to find. Removes the tarball it creates before exiting.
        """
        output_file = os.path.join(TMP_DIR, os.path.basename(self.test_rundir + ".tar.gz"))
        utils.tar(input_dir=self.test_rundir, tarball_name=output_file)
        t = tarfile.open(output_file)
        file_list = t.getnames()
        expected_file_list = [
            "CompletedRun1",
            "CompletedRun1/CopyComplete.txt"
        ]
        os.remove(output_file)
        self.assertEqual(file_list, expected_file_list)

    def test_running_too_long(self):
        """
        Tests that the method `monitor.Monitor.running_too_long` returns True when a child task
        runs for more than the configured amount of time.
        """

        def child_task():
            time.sleep(3)

        # Make process limit 1 second
        p = multiprocessing.Process(target=child_task)
        p.start()
        time.sleep(1)
        self.assertTrue(utils.running_too_long(process=psutil.Process(p.pid), limit_seconds=1))

    def test_not_running_too_long(self):
        """
        Tests that the method `monitor.Monitor.running_too_long` returns False when a child task
        runs for less than the configured amount of time.
        """

        def child_task():
            time.sleep(3)

        # Make process limit 1 second
        p = multiprocessing.Process(target=child_task)
        p.start()
        time.sleep(1)
        self.assertFalse(utils.running_too_long(process=psutil.Process(p.pid), limit_seconds=5))

    def test_delete_directory_if_too_old_1(self):
        """
        Creates a directory, waits 2 seconds, and tests that `utils.delete_directory_if_too_old`
        returns True when giving an age limit that has already been met. 
        """
        sleep_time = 2
        os.mkdir(self.test_delete_dirname)
        time.sleep(2)
        res = utils.delete_directory_if_too_old(dirpath=self.test_delete_dirname, age_seconds= sleep_time-1)
        self.assertEqual(res, True)

    def test_delete_directory_if_too_old_2(self):
        """
        Creates a directory and tests that `utils.delete_directory_if_too_old` returns False when 
        giving an age limit that hasn't been reached yet. 
        """
        os.mkdir(self.test_delete_dirname)
        res = utils.delete_directory_if_too_old(dirpath=self.test_delete_dirname, age_seconds=2)
        self.assertEqual(res, False)

    def test_delete_directory_if_too_old_3(self):
        """
        Creates a directory and tests that `utils.delete_directory_if_too_old` actually deletes
        the directory when we expect it to. 
        """
        os.mkdir(self.test_delete_dirname)
        time.sleep(1)
        res = utils.delete_directory_if_too_old(dirpath=self.test_delete_dirname, age_seconds=1)
        self.assertEqual(os.path.exists(self.test_delete_dirname), False)

    def test_delete_directory_if_too_old_4(self):
        """
        Creates a directory and tests that `utils.delete_directory_if_too_old` doesn't delete
        the directory when we don't expect it to. 
        """
        os.mkdir(self.test_delete_dirname)
        res = utils.delete_directory_if_too_old(dirpath=self.test_delete_dirname, age_seconds=2)
        self.assertEqual(os.path.exists(self.test_delete_dirname), True)

if __name__ == "__main__":
    unittest.main()
