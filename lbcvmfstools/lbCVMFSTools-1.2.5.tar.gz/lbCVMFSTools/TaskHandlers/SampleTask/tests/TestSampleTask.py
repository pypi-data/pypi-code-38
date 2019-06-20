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
import logging
import shutil
import subprocess
import unittest

import os

from lbCVMFSTools.TaskHandlers.SampleTask.SampleTask \
    import SampleTask
from lbCVMFSTools.TransactionHandlers.DefaultTransactionHandler. \
    DefaultTransactionHandler import DefaultTransactionHandler
from lbCVMFSTools.tests.MockLogger import MockLoggingHandler
from lbCVMFSTools.Scheduler import Scheduler
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface
from lbCVMFSTools.Injector import injector


class TestManager(unittest.TestCase):

    def setUp(self):
        self.task = SampleTask(FREQ=1)
        injector.provide(TransactionHandlerInterface, DefaultTransactionHandler)
        injector.provide(TaskHandlerInterface, SampleTask)
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)

    def tearDown(self):
        pass

    def test_get_list_of_tasks(self):
        Scheduler()
        should_see = [
            'Geting the list of tasks',
            'Starting executing: task1',
            'Starting transaction',
            'Noting to do for transaction start',
            'Process finished before timeout',
            'Sending transaction',
            'Noting to do for transaction publish',
            'Successfully executed: task1',
            'Starting executing: task2',
            'Starting transaction',
            'Noting to do for transaction start',
            'Process finished before timeout',
            'Sending transaction',
            'Noting to do for transaction publish',
            'Successfully executed: task2',
            'Starting executing: task3',
            'Starting transaction',
            'Noting to do for transaction start',
            'Process finished before timeout',
            'Sending transaction',
            'Noting to do for transaction publish',
            'Successfully executed: task3']
        self.assertEqual(self.handler.messages['info'], should_see)

if __name__ == "__main__":
    unittest.main()
