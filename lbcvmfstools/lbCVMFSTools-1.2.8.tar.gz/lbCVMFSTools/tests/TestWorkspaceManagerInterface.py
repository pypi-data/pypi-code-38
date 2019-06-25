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


class TestTaskHandlerInterface(unittest.TestCase):

    def setUp(self):
        self.obj = TaskHandlerInterface(1)

    def tearDown(self):
        pass

    def test_dry_run_mode(self):
        self.assertFalse(self.obj.dry_run)
        self.obj = TaskHandlerInterface(1, dry_run=True)
        self.assertTrue(self.obj.dry_run)

    def test_get_list_of_tasks(self):
        self.assertRaises(NotImplementedError, self.obj.get_list_of_tasks)

    def test_perform_task(self):
        self.assertRaises(NotImplementedError,
                          self.obj.perform_task, None)

    def test_configure(self):
        self.assertRaises(NotImplementedError,
                          self.obj.configure)

if __name__ == "__main__":

    unittest.main()
