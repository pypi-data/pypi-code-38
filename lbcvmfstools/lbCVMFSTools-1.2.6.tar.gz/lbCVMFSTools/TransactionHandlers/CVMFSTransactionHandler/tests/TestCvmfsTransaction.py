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

import logging
import shutil
import unittest

import os

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface
from lbCVMFSTools.Injector import injector
from lbCVMFSTools.TransactionHandlers.CVMFSTransactionHandler.\
    CVMFSTranscationHandler import CVMFSTransactionHandler
from lbCVMFSTools.Scheduler import Scheduler
from lbCVMFSTools.tests.MockLogger import MockLoggingHandler
import subprocess


class WorkspaceImpl(TaskHandlerInterface):

    def __init__(self):
        self.no_auto_start = True

    def get_list_of_tasks(self):
        pass

    def perform_task(self, task):
        pass

    def preTransaction(self):
        pass

    def postTransaction(self):
        pass


class TestCVMFSTransaction(unittest.TestCase):

    def mocked_call(self, *a, **kw):
        l = a[0]
        if l == ['cvmfs_server', 'publish', 'cmvstest.cern.ch']:
            return 1
        return 0

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)

    def tearDown(self):
        pass

    def test_cvmfsTransaction(self):
        obj_to_inject = CVMFSTransactionHandler('cmvstest.cern.ch',
                                                dry_run=True)
        injector.provide_instance(TransactionHandlerInterface, obj_to_inject)
        injector.provide(TaskHandlerInterface, WorkspaceImpl)

        manager = Scheduler()
        try:
            with manager.transaction():
                pass
        except Exception as e:
            print(e)
            self.fail("cvmfsTransaction failed due to: %s" % e)

    def test_cvmfsTransactionFail(self):
        subprocess.call = self.mocked_call
        obj_to_inject = CVMFSTransactionHandler('cmvstest.cern.ch')
        injector.provide_instance(TransactionHandlerInterface, obj_to_inject)
        injector.provide(TaskHandlerInterface, WorkspaceImpl)

        try:
            with Scheduler().transaction():
                pass
            self.fail("The test should not arrive here")
        except Exception as e:
            # Check the flow of logs:
            should_see = ['Starting transaction',
                          'Called CVMFS Transaction start',
                          'Sending transaction',
                          'Called CVMFS Transaction publish',
                          'Aborting transaction',
                          'Called CVMFS Transaction abort']
            self.assertEqual(should_see,
                             self.handler.messages['info'])


if __name__ == "__main__":

    unittest.main()
