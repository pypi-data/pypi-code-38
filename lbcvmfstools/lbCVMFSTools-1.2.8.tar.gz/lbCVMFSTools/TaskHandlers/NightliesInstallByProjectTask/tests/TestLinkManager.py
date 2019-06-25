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
Test of the version path link functionality in the model classes.

@author: Stefan-Gabriel CHITICTestLinkManager
'''
import json
import shutil
import unittest

import os

from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils import \
    PathManager, LinkManager


class TestLinkManager(unittest.TestCase):

    def setUp(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1232")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1233")
        with open('/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1234/'
                  'slot-config.json', 'w') as f:
            json.dump({'build_id': '1234', 'date': '2017-05-31'}, f)
        with open('/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1233/'
                  'slot-config.json', 'w') as f:
            json.dump({'build_id': '1233', 'date': '2017-05-30'}, f)
        with open('/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/1232/'
                  'slot-config.json', 'w') as f:
            json.dump({'build_id': '1232', 'date': '2017-05-29'}, f)
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        self.pManager = PathManager(
            installArea="/tmp/toto/cvmfstest.cern.ch/nightlies",
            workspace="/tmp/foo/")
        self.lManager = LinkManager(pathManager=self.pManager)

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def testcheckLinks(self):
        os.symlink('1234',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Today')
        os.symlink('1233',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Yesterday')
        os.symlink('1234',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/latest')
        os.symlink('1234',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Wed')
        self.assertTrue(self.lManager.checkLinks('slot1', 1234, '2017-05-31'))
        try:
            # The cvmfs path dose not exists, so it should return Fail
            self.lManager = LinkManager()
            self.assertFalse(
                self.lManager.checkLinks('slot1', 1234, '2017-05-31'))
        except Exception as e:
            pass

    def testfixLinks(self):
        os.symlink('1233',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Today')
        os.symlink('1233',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Wed')
        os.symlink('1232',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/Yesterday')
        os.symlink('1233',
                   '/tmp/toto/cvmfstest.cern.ch/nightlies/slot1/latest')
        self.lManager.fixLinks('slot1', 1234, '2017-05-31')
        self.assertTrue(self.lManager.checkLinks('slot1', 1234, '2017-05-31'))

    def testfixLinks2(self):
        self.lManager.fixLinks('slot1', 1234, '2017-05-31')
        self.assertTrue(self.lManager.checkLinks('slot1', 1234, '2017-05-31'))

if __name__ == "__main__":
    unittest.main()
