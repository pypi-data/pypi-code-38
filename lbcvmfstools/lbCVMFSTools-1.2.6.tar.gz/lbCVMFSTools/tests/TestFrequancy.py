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
import time
import os

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

class WorkspaceImplFrequancy(TaskHandlerInterface, object):

    def __init__(self):
        super(WorkspaceImplFrequancy, self).__init__(1)

    def get_list_of_tasks(self):
        return ['task1', 'task2', 'task3']

    def perform_task(self, task):
        pass

    def preTransaction(self):
        pass

    def postTransaction(self):
        pass

class TestTaskHandlerInterface(unittest.TestCase):

    def setUp(self):
        file = os.path.join(os.environ['HOME'], 'var', 'WorkspaceImplFrequancy')
        if os.path.exists(file):
            os.remove(file)
        self.obj = WorkspaceImplFrequancy()

    def tearDown(self):
        pass

    def test_metadatafile(self):
        self.assertTrue(self.obj.meta_filename == os.path.join(os.environ['HOME'], 'var', 'WorkspaceImplFrequancy'))

    def test_shouldRun(self):
        file = os.path.join(os.environ['HOME'], 'var', 'WorkspaceImplFrequancy')
        # File was not created yet
        self.assertTrue(self.obj.should_run())
        # File created, should not run
        self.obj.update_last_run()
        self.assertFalse(self.obj.should_run())
        # Sleep and test the run again:
        time.sleep(1)
        self.assertTrue(self.obj.should_run())



if __name__ == "__main__":

    unittest.main()
