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

import unittest

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.Scheduler import Scheduler
from lbCVMFSTools.Injector import injector
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface


class WorkspaceImpl(TaskHandlerInterface, object):

    def __init__(self):
        super(WorkspaceImpl, self).__init__(1)
        self.perform_task_ok = False
        self.perform_task_ko = False

    def get_list_of_tasks(self):
        return ['task1', 'task2', 'task3']

    def perform_task(self, task):
        if task == 'task3':
            self.perform_task_ko = True
            raise Exception("Exception test")
        self.perform_task_ok = True

    def preTransaction(self):
        pass

    def postTransaction(self):
        pass


class TransactionImpl(TransactionHandlerInterface):

    def __init__(self, *args, **kwargs):
        self.perform_task_rollback = False

    def transactionPublish(self):
        pass

    def transactionStart(self):
        pass

    def transactionAbort(self):
        self.perform_task_rollback = True


class TestScheduler(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_schedulerAutoRun(self):
        injector.provide(TaskHandlerInterface, WorkspaceImpl)
        injector.provide(TransactionHandlerInterface, TransactionImpl)
        try:
            s = Scheduler()
            self.fail("Should have failed")
        except:
            pass

    def test_schedulerNoAutoRun(self):
        w = WorkspaceImpl()
        setattr(w, 'no_auto_start', True)
        injector.provide_instance(TaskHandlerInterface, w)
        s = Scheduler()
        impls = s.taskHandler
        implTrans = s.transactionHandler
        # the schedulers shoun't have run
        self.assertFalse(impls.perform_task_ok)
        try:
            s.start()
        except:
            pass
        # check if at least one task was performed ok
        self.assertTrue(impls.perform_task_ok)
        # check if at least one task was performed ko
        self.assertTrue(impls.perform_task_ko)
        # check if at a rollback was performed
        self.assertTrue(implTrans.perform_task_rollback)

if __name__ == "__main__":

    unittest.main()
