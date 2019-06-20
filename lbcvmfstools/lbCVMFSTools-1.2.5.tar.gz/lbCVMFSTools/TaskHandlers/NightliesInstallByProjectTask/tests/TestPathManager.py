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
Test of the version path manager functionality in the model classes.

@author: Stefan-Gabriel CHITIC
'''
import json
import shutil
import unittest

import os

from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils import\
    PathManager


class TestPathManager(unittest.TestCase):

    def setUp(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        self.pManager = PathManager(
            installArea="/tmp/toto/cvmfstest.cern.ch/nightlies",
            workspace="/tmp/foo/")

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def test_getRepoDir(self):
        self.assertEqual(self.pManager._getRepoDir(),
                         '/tmp/toto/cvmfstest.cern.ch/nightlies')

    def test_getVarDir(self):
        self.assertEqual(self.pManager.getVarDir(),
                         '/tmp/foo/var')

    def testgetConfDir(self):
        self.assertEqual(self.pManager.getConfDir(),
                         '/tmp/foo/conf')

    def testgetSlotDir(self):
        self.assertEqual(self.pManager.getSlotDir('slot1', 1234),
                         '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234')

    def test_getSlotTodayLink(self):
        self.assertEqual(self.pManager.getSlotTodayLink('slot1'),
                         '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Today')

    def testgetSlotInstalledFilename(self):
        self.assertEqual(self.pManager.getSlotInstalledFilename('slot1', 1234),
                         '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234/'
                         '.installed')

    def testgetVarInstalledFilename(self):
        self.assertEqual(self.pManager.getVarInstalledFilename('slot1', 1234),
                         '/tmp/foo/var/slot1.1234.installed')

    def testgetSlotDirDayLink(self):
        self.assertEqual(self.pManager.getSlotDirDayLink('slot1',
                                                         strdate='2017-05-31'),
                         '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/'
                         'Wed')

if __name__ == "__main__":
    unittest.main()
