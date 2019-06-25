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
import os
from lbCVMFSTools.TaskHandlers.EnvKitInstaller.EnvKitInstaller \
    import EnvKitInstaller


class TestEnvKitInstaller(unittest.TestCase):

    def setUp(self):
        self.installer = EnvKitInstaller('dev', 'x86_64-slc5',
                                         '51da324634.2018-03-15',
                                         None)
        self.installer.root = './'

    def tearDown(self):
        pass

    #def test_get_list_of_tasks(self):
        #self.assertEqual([{
        #    'url': 'http://lhcb-rpm.web.cern.ch/lhcb-rpm/lbenv-kits/'
        #           'lbenv-kit.dev.x86_64-slc5.51da324634.2018-03-15.tar.bz2',
        #    'root': './',
        #    'prefix': '/cvmfs/lhcbdev.cern.ch/new-msr/var/'
        #              'lib/LbEnv/dev/x86_64-slc5/'
        #}], self.installer.get_list_of_tasks())

    #def test_perform_task(self):
        #task = self.installer.get_list_of_tasks()[0]
        #self.installer.perform_task(task)
        #self.assertTrue(os.path.exists('./cvmfs/lhcbdev.cern.ch/new-env/'
        #                              'dev/x86_64-slc5/pip.conf'))

if __name__ == "__main__":
    unittest.main()
