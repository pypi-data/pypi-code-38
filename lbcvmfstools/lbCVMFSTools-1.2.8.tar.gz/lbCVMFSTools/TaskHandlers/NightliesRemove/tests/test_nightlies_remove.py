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
import logging
import shutil
import subprocess
import unittest

import os

from lbCVMFSTools.tests.MockLogger import MockLoggingHandler
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils \
    import PathManager
from lbCVMFSTools.TaskHandlers.NightliesRemove. \
    NightliesRemove import NightliesRemove


class TestGitMirror(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        if os.path.exists("/tmp/cvmfs/"):
            shutil.rmtree("/tmp/cvmfs")
        for j in range(10):
            for i in range(20):
                os.makedirs("/tmp/cvmfs/slot%s/%s" % (j, i))
            os.symlink('19',
                       '/tmp/cvmfs/slot%s/Today' % j)
        os.makedirs("/tmp/cvmfs/slot10/1")
        os.symlink('1',
                   '/tmp/cvmfs/slot10/Today')
        pathManager = PathManager(workspace=None,
                                  installArea='/tmp/cvmfs/')
        self.manager = NightliesRemove(pathManager=pathManager)

    def tearDown(self):
        if os.path.exists("/tmp/cvmfs/"):
            shutil.rmtree("/tmp/cvmfs")

    def mocked_call(self, *a, **kw):
        return 0

    def test_get_list_of_tasks(self):
        # Test with all slots not install
        todos = self.manager.get_list_of_tasks()
        self.assertEqual(len(todos), 10)
        l = [int(x['task_name']. replace('Cleanup slot', '')) for x in todos]
        self.assertEqual(sorted(l), list(range(10)))
        for l in todos:
            self.assertEqual(len(l['buildsIds']),
                             20 - self.manager.maxnbperslot)

    def test_perform_task(self):
        # Test with all slots not install
        todos = self.manager.get_list_of_tasks()
        for task in todos:
            self.manager.perform_task(task)
        info_output = [
            'Checking if slot0 need to be clean up',
            'There are 20 builds in slot slot0. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot1 need to be clean up',
            'There are 20 builds in slot slot1. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot2 need to be clean up',
            'There are 20 builds in slot slot2. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot3 need to be clean up',
            'There are 20 builds in slot slot3. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot4 need to be clean up',
            'There are 20 builds in slot slot4. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot5 need to be clean up',
            'There are 20 builds in slot slot5. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot6 need to be clean up',
            'There are 20 builds in slot slot6. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot7 need to be clean up',
            'There are 20 builds in slot slot7. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot8 need to be clean up',
            'There are 20 builds in slot slot8. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot9 need to be clean up',
            'There are 20 builds in slot slot9. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 11 slots - Can delete: 19',
            'Checking if slot10 need to be clean up',
            'There are 1 builds in slot slot10. 1 are link targets '
            'and cannot be removed',
            'We want a max of 9 - Wish to delete 0 slots - Can delete: 0'
        ]
        self.assertEqual(self.handler.messages['info'], info_output)
        warning_output = [
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot0/10',
            'Removing /tmp/cvmfs/slot0/9',
            'Removing /tmp/cvmfs/slot0/8',
            'Removing /tmp/cvmfs/slot0/7',
            'Removing /tmp/cvmfs/slot0/6',
            'Removing /tmp/cvmfs/slot0/5',
            'Removing /tmp/cvmfs/slot0/4',
            'Removing /tmp/cvmfs/slot0/3',
            'Removing /tmp/cvmfs/slot0/2',
            'Removing /tmp/cvmfs/slot0/1',
            'Removing /tmp/cvmfs/slot0/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot1/10',
            'Removing /tmp/cvmfs/slot1/9',
            'Removing /tmp/cvmfs/slot1/8',
            'Removing /tmp/cvmfs/slot1/7',
            'Removing /tmp/cvmfs/slot1/6',
            'Removing /tmp/cvmfs/slot1/5',
            'Removing /tmp/cvmfs/slot1/4',
            'Removing /tmp/cvmfs/slot1/3',
            'Removing /tmp/cvmfs/slot1/2',
            'Removing /tmp/cvmfs/slot1/1',
            'Removing /tmp/cvmfs/slot1/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot2/10',
            'Removing /tmp/cvmfs/slot2/9',
            'Removing /tmp/cvmfs/slot2/8',
            'Removing /tmp/cvmfs/slot2/7',
            'Removing /tmp/cvmfs/slot2/6',
            'Removing /tmp/cvmfs/slot2/5',
            'Removing /tmp/cvmfs/slot2/4',
            'Removing /tmp/cvmfs/slot2/3',
            'Removing /tmp/cvmfs/slot2/2',
            'Removing /tmp/cvmfs/slot2/1',
            'Removing /tmp/cvmfs/slot2/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot3/10',
            'Removing /tmp/cvmfs/slot3/9',
            'Removing /tmp/cvmfs/slot3/8',
            'Removing /tmp/cvmfs/slot3/7',
            'Removing /tmp/cvmfs/slot3/6',
            'Removing /tmp/cvmfs/slot3/5',
            'Removing /tmp/cvmfs/slot3/4',
            'Removing /tmp/cvmfs/slot3/3',
            'Removing /tmp/cvmfs/slot3/2',
            'Removing /tmp/cvmfs/slot3/1',
            'Removing /tmp/cvmfs/slot3/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot4/10',
            'Removing /tmp/cvmfs/slot4/9',
            'Removing /tmp/cvmfs/slot4/8',
            'Removing /tmp/cvmfs/slot4/7',
            'Removing /tmp/cvmfs/slot4/6',
            'Removing /tmp/cvmfs/slot4/5',
            'Removing /tmp/cvmfs/slot4/4',
            'Removing /tmp/cvmfs/slot4/3',
            'Removing /tmp/cvmfs/slot4/2',
            'Removing /tmp/cvmfs/slot4/1',
            'Removing /tmp/cvmfs/slot4/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot5/10',
            'Removing /tmp/cvmfs/slot5/9',
            'Removing /tmp/cvmfs/slot5/8',
            'Removing /tmp/cvmfs/slot5/7',
            'Removing /tmp/cvmfs/slot5/6',
            'Removing /tmp/cvmfs/slot5/5',
            'Removing /tmp/cvmfs/slot5/4',
            'Removing /tmp/cvmfs/slot5/3',
            'Removing /tmp/cvmfs/slot5/2',
            'Removing /tmp/cvmfs/slot5/1',
            'Removing /tmp/cvmfs/slot5/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot6/10',
            'Removing /tmp/cvmfs/slot6/9',
            'Removing /tmp/cvmfs/slot6/8',
            'Removing /tmp/cvmfs/slot6/7',
            'Removing /tmp/cvmfs/slot6/6',
            'Removing /tmp/cvmfs/slot6/5',
            'Removing /tmp/cvmfs/slot6/4',
            'Removing /tmp/cvmfs/slot6/3',
            'Removing /tmp/cvmfs/slot6/2',
            'Removing /tmp/cvmfs/slot6/1',
            'Removing /tmp/cvmfs/slot6/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot7/10',
            'Removing /tmp/cvmfs/slot7/9',
            'Removing /tmp/cvmfs/slot7/8',
            'Removing /tmp/cvmfs/slot7/7',
            'Removing /tmp/cvmfs/slot7/6',
            'Removing /tmp/cvmfs/slot7/5',
            'Removing /tmp/cvmfs/slot7/4',
            'Removing /tmp/cvmfs/slot7/3',
            'Removing /tmp/cvmfs/slot7/2',
            'Removing /tmp/cvmfs/slot7/1',
            'Removing /tmp/cvmfs/slot7/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot8/10',
            'Removing /tmp/cvmfs/slot8/9',
            'Removing /tmp/cvmfs/slot8/8',
            'Removing /tmp/cvmfs/slot8/7',
            'Removing /tmp/cvmfs/slot8/6',
            'Removing /tmp/cvmfs/slot8/5',
            'Removing /tmp/cvmfs/slot8/4',
            'Removing /tmp/cvmfs/slot8/3',
            'Removing /tmp/cvmfs/slot8/2',
            'Removing /tmp/cvmfs/slot8/1',
            'Removing /tmp/cvmfs/slot8/0',
            'Found 11 jobs to remove (will remove a max of 20 as specified)',
            'Removing /tmp/cvmfs/slot9/10',
            'Removing /tmp/cvmfs/slot9/9',
            'Removing /tmp/cvmfs/slot9/8',
            'Removing /tmp/cvmfs/slot9/7',
            'Removing /tmp/cvmfs/slot9/6',
            'Removing /tmp/cvmfs/slot9/5',
            'Removing /tmp/cvmfs/slot9/4',
            'Removing /tmp/cvmfs/slot9/3',
            'Removing /tmp/cvmfs/slot9/2',
            'Removing /tmp/cvmfs/slot9/1',
            'Removing /tmp/cvmfs/slot9/0']
        self.assertEqual(self.handler.messages['warning'], warning_output)
        for j in range(10):
            for i in range(20):
                if i < 11:
                    self.assertFalse(
                        os.path.exists("/tmp/cvmfs/slot%s/%s" % (j, i)))
                else:
                    self.assertTrue(
                        os.path.exists("/tmp/cvmfs/slot%s/%s" % (j, i)))
        self.assertTrue(os.path.exists("/tmp/cvmfs/slot10/1"))



if __name__ == "__main__":
    unittest.main()
