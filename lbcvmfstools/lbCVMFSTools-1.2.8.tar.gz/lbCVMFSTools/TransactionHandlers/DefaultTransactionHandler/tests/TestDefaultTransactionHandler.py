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
import subprocess
import unittest
import logging

from lbCVMFSTools.TransactionHandlers.DefaultTransactionHandler. \
    DefaultTransactionHandler import DefaultTransactionHandler
from lbCVMFSTools.tests.MockLogger import MockLoggingHandler


class TestDefaultTransactionHandler(unittest.TestCase):

    def setUp(self):
        self.manager = DefaultTransactionHandler()
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)

    def tearDown(self):
        pass

    def test_Start(self):
        self.manager.transactionStart()
        self.manager = DefaultTransactionHandler(dry_run=True)
        self.manager.transactionStart()
        should_see = ['Noting to do for transaction start',
                      'IN DRY-RUN MODE: Noting to do for transaction start']
        self.assertEqual(should_see,
                         self.handler.messages['info'])

    def test_Abort(self):
        self.manager.transactionAbort()
        self.manager = DefaultTransactionHandler(dry_run=True)
        self.manager.transactionAbort()

        should_see = ['Noting to do for transaction abort',
                      'IN DRY-RUN MODE: Noting to do for transaction abort']
        self.assertEqual(should_see,
                         self.handler.messages['info'])

    def test_Publish(self):
        self.manager.transactionPublish()
        self.manager = DefaultTransactionHandler(dry_run=True)
        self.manager.transactionPublish()
        should_see = ['Noting to do for transaction publish',
                      'IN DRY-RUN MODE: Noting to do for transaction publish']
        self.assertEqual(should_see,
                         self.handler.messages['info'])


if __name__ == "__main__":
    unittest.main()
