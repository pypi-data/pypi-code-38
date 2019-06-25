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

from lbCVMFSTools.TaskHandlers.GitMirrorTask.GitMirrorTask \
    import GitMirrorTask

from lbCVMFSTools.tests.MockLogger import MockLoggingHandler


class TestGitMirror(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/test1.git/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/test2.git/")
        os.mkdir("/tmp/toto/cvmfstest.cern.ch/test3.git/")
        with open(
                "/tmp/toto/cvmfstest.cern.ch/test1.git/FETCH_HEAD",
                'w') as f:
            f.write("1234\n")
        with open(
                "/tmp/toto/cvmfstest.cern.ch/test2.git/FETCH_HEAD",
                'w') as f:
            f.write("1234\n")
        with open(
                "/tmp/toto/cvmfstest.cern.ch/test3.git/FETCH_HEAD",
                'w') as f:
            f.write("1234\n")
        self.GitMirrorTaskI = GitMirrorTask(
            FREQ=1,
            repodir='/tmp/toto/cvmfstest.cern.ch/')
        self.args = None
        self.kwargs = None
        self.mocked_return_code = 0
        subprocess.call = self.mocked_call

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")

    def mocked_call(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.mocked_return_code

    def test_md5(self):
        md5 = self.GitMirrorTaskI._md5(
            '/tmp/toto/cvmfstest.cern.ch/test3.git/FETCH_HEAD')
        self.assertEqual('e7df7cd2ca07f4f1ab415d457a6e1c13', md5)

    def test_get_list_of_tasks(self):
        # Test with all slots not install
        todos = self.GitMirrorTaskI.get_list_of_tasks()
        parsed_slots = [[
            {'md5': 'e7df7cd2ca07f4f1ab415d457a6e1c13',
             'path': '/tmp/toto/cvmfstest.cern.ch/test1.git'},
            {'md5': 'e7df7cd2ca07f4f1ab415d457a6e1c13',
             'path': '/tmp/toto/cvmfstest.cern.ch/test2.git'},
            {'md5': 'e7df7cd2ca07f4f1ab415d457a6e1c13',
             'path': '/tmp/toto/cvmfstest.cern.ch/test3.git'}
        ]]
        self.assertEqual(todos, parsed_slots)

    def test_task_no_update(self):
        # Test with all slots not install
        todos = self.GitMirrorTaskI.get_list_of_tasks()
        try:
            self.GitMirrorTaskI.perform_task(todos[0])
            self.fail("Should returned with transaction abort")
        except Exception as e:
            pass

    def test_task_update(self):
        todos = self.GitMirrorTaskI.get_list_of_tasks()
        with open(
                "/tmp/toto/cvmfstest.cern.ch/test3.git/FETCH_HEAD",
                'w') as f:
            f.write("1244434\n")
        try:
            self.GitMirrorTaskI.perform_task(todos[0])
        except Exception as e:
            self.fail("Should publish the transaction %s " % str(e))

if __name__ == "__main__":
    unittest.main()
