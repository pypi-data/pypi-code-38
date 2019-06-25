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

from lbCVMFSTools.Injector import injector
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask. \
    NightliesInstallByProjectTask import NightliesInstallByProjectTask
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils import \
    PathManager, InstalledManager
from lbCVMFSTools.tests.MockLogger import MockLoggingHandler


class TestManager(unittest.TestCase):

    def setUp(self):
        self.handler = MockLoggingHandler()
        logging.getLogger().addHandler(self.handler)
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")
        os.mkdir("/tmp/toto/")
        os.mkdir("/tmp/toto/slot1")
        os.mkdir("/tmp/toto/slot1/1235")
        os.mkdir("/tmp/toto/slot1/12345")
        os.mkdir("/tmp/foo/")
        os.mkdir("/tmp/foo/conf/")
        os.mkdir("/tmp/foo/var/")
        with open(
                "/tmp/toto/slot1/1235/.installed",
                'w') as f:
            f.write("\n")
        with open(
                "/tmp/toto/slot1/12345/.installed",
                'w') as f:
            f.write("\n")
        self.pManager = PathManager(
            installArea="/tmp/toto/",
            workspace="/tmp/foo/")
        injector.provide_instance(PathManager, self.pManager)
        self.iManager = InstalledManager(pathManager=self.pManager)
        self.manager = NightliesInstallByProjectTask('slot1', '12345',
                                                     'centos7_x64_opt',
                                                     'project1',
                                                     FREQ=1,
                                                     installOnCvmfs=False)
        self.manager.overrideTodayCheck = True
        self.args = None
        self.kwargs = None
        self.mocked_return_code = 0
        self.return_data_slots = {
            'cvmfs': [],
            'afs': [
                 {'slot': 'slot1',
                  'build_id': 1235,
                  'platform': 'centos7_x64_opt',
                  'completed': True},
                 {'slot': 'slot2',
                  'build_id': 1243,
                  'platform': 'centos7_x64_opt',
                  'completed': False},
                 {'slot': 'slot1',
                  'build_id': 1235,
                  'platform': 'centos7_x86_opt',
                  'completed': False},
             ]}
        # Mock Suprocess :
        subprocess.call = self.mocked_call

    def tearDown(self):
        if os.path.exists("/tmp/toto"):
            shutil.rmtree("/tmp/toto")
        if os.path.exists("/tmp/foo"):
            shutil.rmtree("/tmp/foo/")

    def mocked_call(self, *a, **kw):
        self.args = a
        self.kwargs = kw
        return self.mocked_return_code

    def test_get_list_of_tasks(self):
        # Test with all slots not install
        todos = self.manager.get_list_of_tasks()
        parsed_slots = [('slot1', '12345', 'centos7_x64_opt', 'project1')]
        self.assertEqual(todos, parsed_slots)

        # Mark 1 slot as installed
        self.iManager.addInstalled(parsed_slots)
        todos = self.manager.get_list_of_tasks()
        self.assertEqual(todos, [])

        logs = []
        logs.append("%s, %s, %s, %s is already installed for today, "
                    "skipping" % ('slot1', '12345', 'centos7_x64_opt',
                                  'project1'))
        self.assertEqual(sorted(logs),
                         sorted(self.handler.messages['info']))

    def test_postTransaction(self):
        installed = self.manager.installManager.getInstalled()
        self.assertEqual(len(installed), 0)
        self.manager.postTransaction(success=True)
        installed = self.manager.installManager.getInstalled()
        self.assertEqual(len(installed), 1)

    def test_perform_task(self):
        todos = self.manager.get_list_of_tasks()
        # Perform 1 installation
        self.manager.perform_task(todos[0])
        logs = [
            'Need to fix the links for slot1 12345',
            'Updating slot1 12345 centos7_x64_opt project1',
            'Invoking: lbn-install --no-git --dest=/tmp/toto/'
            'slot1/12345 --platforms=centos7_x64_opt --projects=project1 '
            'slot1 12345',
            'Install has changed - copying list of installed tars']
        self.assertEqual(logs, self.handler.messages['info'])

    def test_lbn_install_call(self):
        todos = self.manager.get_list_of_tasks()

        # Perform 1 installation with error
        self.mocked_return_code = 1
        self.assertRaises(RuntimeError, self.manager.perform_task, todos[0])
        logs = [
            'Need to fix the links for slot1 12345',
            'Updating slot1 12345 centos7_x64_opt project1',
            'Invoking: lbn-install --no-git --dest=/tmp/toto/'
            'slot1/12345 --platforms=centos7_x64_opt --projects=project1 '
            'slot1 12345']
        self.assertEqual(sorted(logs),
                         sorted(self.handler.messages['info']))
        values = " ".join(str(v) for v in self.args[0])
        self.assertEqual(values,
                         'lbn-install --no-git --dest=/tmp/toto/'
                         'slot1/12345 --platforms=centos7_x64_opt '
                         '--projects=project1 '
                         'slot1 12345')

if __name__ == "__main__":
    unittest.main()
