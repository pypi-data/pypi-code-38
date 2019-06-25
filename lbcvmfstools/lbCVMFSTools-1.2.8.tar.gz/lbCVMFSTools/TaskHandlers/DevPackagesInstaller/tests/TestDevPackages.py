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
Test of the version build manager functionality in the model classes.

@author: Stefan-Gabriel CHITIC
'''
import json
import shutil
import unittest
from lbdevmanager.GitManager import GitManager
import os
from lbCVMFSTools.TaskHandlers.DevPackagesInstaller.DevPackagesInstaller \
    import DevPackagesInstaller
from lbdevmanager.LbInstallManager import LbInstallManager


class TestInstalledManager(unittest.TestCase):

    def __init__Mock(self, *args, **kwargs):
        pass

    def UpdateTagsMock(self):
        self.updatedTags = True

    def installFilesMock(self, task):
        print("Executing task: %s" % task)
        if task[0] == 'toto3':
            raise Exception("No install toto3")

    def setUp(self):
        self.updatedTags = False
        GitManager.__init__ = self.__init__Mock
        GitManager.UpdateTags = self.UpdateTagsMock
        LbInstallManager.installFiles = self.installFilesMock
        self.devPkgIns = DevPackagesInstaller(toInstall=['toto', 'toto2',
                                                         'toto3'],
                                              installed=[],
                                              priority=10,
                                              commitID='#commitID',
                                              maxretry=2,
                                              vhost='/lhcb-test'
                                              )
        self.devPkgIns.broker.receive_all('CVMFSDevActions')

    def tearDown(self):
        pass

    def test_get_list_of_tasks(self):
        self.assertEqual(['toto', 'toto2', 'toto3'],
                         self.devPkgIns.get_list_of_tasks())

    def test_perform_task(self):
        for task in ['toto', 'toto2', 'toto3']:
            print(task)
            self.devPkgIns.perform_task(task)
        self.assertEqual(['toto', 'toto2'], self.devPkgIns.installed)

    def test_postTransaction(self):
        for task in ['toto', 'toto2', 'toto3']:
            self.devPkgIns.perform_task(task)
        self.devPkgIns.postTransaction()
        res = self.devPkgIns.broker.receive_all('CVMFSDevActions')[0]
        self.assertEqual(res.body.arguments[0], '--toinstall="toto3"')
        self.assertEqual(res.header_frame.headers['max_retry'], 2)
        res = self.devPkgIns.broker.receive_all('CVMFSDevActions')
        self.assertEqual(len(res), 0)

    def test_postTransaction2(self):
        self.devPkgIns = DevPackagesInstaller(toInstall=['toto', 'toto2'],
                                              installed=[],
                                              priority=10,
                                              commitID='#commitID',
                                              maxretry=2,
                                              vhost='/lhcb-test'
                                              )
        print(self.devPkgIns.installed)
        for task in ['toto', 'toto2']:
            self.devPkgIns.perform_task(task)
        print(self.devPkgIns.installed)
        self.devPkgIns.postTransaction()
        self.assertEqual(self.updatedTags, True)
        res = self.devPkgIns.broker.receive_all('CVMFSDevActions')
        self.assertEqual(len(res), 0)

    def test_postTransaction3(self):
        self.updatedTags = False
        self.devPkgIns = DevPackagesInstaller(toInstall=['toto', 'toto2'],
                                              installed=['toto3'],
                                              priority=10,
                                              commitID='#commitID',
                                              maxretry=2,
                                              vhost='/lhcb-test'
                                              )
        print(self.devPkgIns.installed)
        for task in ['toto', 'toto2']:
            self.devPkgIns.perform_task(task)
        print(self.devPkgIns.installed)
        self.devPkgIns.postTransaction()
        self.assertEqual(['toto3','toto', 'toto2'], self.devPkgIns.installed)
        self.assertEqual(self.updatedTags, True)

        res = self.devPkgIns.broker.receive_all('CVMFSDevActions')
        self.assertEqual(len(res), 0)


if __name__ == "__main__":
    unittest.main()
