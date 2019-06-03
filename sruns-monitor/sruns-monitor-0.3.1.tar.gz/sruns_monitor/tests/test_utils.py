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



if __name__ == "__main__":
    unittest.main()
