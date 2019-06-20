###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Test of the version build manager functionality in the model classes.

@author: Stefan-Gabriel CHITIC
'''
import json
import shutil
import unittest

import os

from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils import \
    PathManager, InstalledManager


class TestInstalledManager(unittest.TestCase):

    def setUp(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234")
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        os.mkdir("/tmp/foo/var/")
        with open(
                "/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234/.installed",
                'w') as f:
            f.write("1234\n")
        self.pManager = PathManager(
            installArea="/tmp/toto/cvmfstest.cern.ch/nightlies",
            workspace="/tmp/foo/")
        self.wManager = InstalledManager(pathManager=self.pManager)

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def testgetFilenameForDate(self):
        self.assertEqual(self.wManager.getFilenameForDate('2017-05-31'),
                         '/tmp/foo/var/slots_proj_installed.2017-05-31')
        self.wManager = InstalledManager(pathManager=self.pManager)
        self.assertEqual(self.wManager.getFilenameForDate('2017-05-31'),
                         '/tmp/foo/var/slots_proj_installed.2017-05-31')

    def testsetInstalled(self):
        tuples = [("Slot1_set", 1234, "platform1", "Project1"),
                  ("Slot1_set", 1234, "platform1", "Project2"),
                  ("Slot2_set", 1235, "platform1", "Project1"),
                  ("Slot3_set", 1236, "platform1", "Project1")]
        tuples = set(tuples)
        self.wManager.setInstalled(tuples, "2017-05-31")
        res = self.wManager.getInstalled("2017-05-31")
        self.assertEqual(tuples, res)
        tuples_extra = [
            ("Slot1", 1234, "platform1", "Project1"),
            ("Slot2", 1235, "platform1", "Project1"),
            ("Slot2", 1236, "platform1", "Project1")]
        tuples_extra = set(tuples_extra)
        self.wManager.addInstalled(tuples_extra, "2017-05-31")
        res = self.wManager.getInstalled("2017-05-31")
        self.assertEqual(tuples.union(tuples_extra), res)

    def test_copyInstalledFile(self):
        self.wManager.copyInstalledFile('slot1', 1234)
        self.assertTrue(os.path.exists('/tmp/foo/var/slot1.1234.installed'))

    def test_installHasChanged(self):
        self.wManager.copyInstalledFile('slot1', 1234)
        with open(
                "/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234/.installed",
                'w') as f:
            f.write("1235\n")
        self.assertTrue(self.wManager.installHasChanged('slot1', 1234))

if __name__ == "__main__":
    unittest.main()
