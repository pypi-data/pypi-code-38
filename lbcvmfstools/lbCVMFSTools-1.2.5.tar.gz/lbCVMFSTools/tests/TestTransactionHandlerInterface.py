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
@author: Stefan-Gabriel CHITIC
'''

import shutil
import unittest

import os

from lbCVMFSTools.TransactionHandlerInterface import TransactionHandlerInterface


class TestTransactionHandlerInterface(unittest.TestCase):

    def setUp(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        self.obj = TransactionHandlerInterface()

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def test_dry_run_mode(self):
        self.assertFalse(self.obj.dry_run)
        self.obj = TransactionHandlerInterface(dry_run=True)
        self.assertTrue(self.obj.dry_run)

    def test_transactionStart(self):
        self.assertRaises(NotImplementedError, self.obj.transactionStart)

    def test_transactionAbort(self):
        self.assertRaises(NotImplementedError,
                          self.obj.transactionAbort)

    def test_transactionPublish(self):
        self.assertRaises(NotImplementedError,
                          self.obj.transactionPublish)

if __name__ == "__main__":
    unittest.main()
