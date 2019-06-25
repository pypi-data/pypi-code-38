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
import subprocess
import unittest

import os

from lbCVMFSTools.Injector import injector
from lbCVMFSTools.TransactionHandlers.CVMFSTransactionHandler.\
    CVMFSTranscationHandler import CVMFSTransactionHandler


class TestCVMFSTransactionHandler(unittest.TestCase):

    def setUp(self):
        self.args = None
        self.kwargs = None
        self.mocked_return_code = 0

    def mocked_call(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.mocked_return_code

    def tearDown(self):
        pass

    def test_Constructor(self):
        # test with reponame, no injection
        self.manager = CVMFSTransactionHandler('cvmfstest-no_injection.cern.ch')
        self.assertEqual('cvmfstest-no_injection.cern.ch',
                         self.manager.reponame)

    def test_cvmfsStart(self):
        self.manager = CVMFSTransactionHandler('cvmfstest.cern.ch')

        # Mock Suprocess :
        subprocess.call = self.mocked_call
        # No error
        self.manager.transactionStart()
        # with erros
        self.mocked_return_code = 1
        self.assertRaises(RuntimeError,
                          self.manager.transactionStart)
        self.assertEqual(self.args, (["cvmfs_server", "abort", "-f",
                                     'cvmfstest.cern.ch'],))

    def test_cvmfsAbort(self):
        self.manager = CVMFSTransactionHandler('cvmfstest.cern.ch')

        # Mock Suprocess :
        subprocess.call = self.mocked_call
        # No error
        self.manager.transactionAbort()
        # with erros
        self.mocked_return_code = 1
        self.assertRaises(RuntimeError,
                          self.manager.transactionAbort)
        self.assertEqual(self.args, (["cvmfs_server", "abort", "-f",
                                     'cvmfstest.cern.ch'],))

    def test_cvmfsPublish(self):
        self.manager = CVMFSTransactionHandler('cvmfstest.cern.ch')

        # Mock Suprocess :
        subprocess.call = self.mocked_call
        # No error
        self.manager.transactionPublish()

        # with erros
        self.mocked_return_code = 1
        self.assertRaises(RuntimeError,
                          self.manager.transactionPublish)

if __name__ == "__main__":
    unittest.main()
