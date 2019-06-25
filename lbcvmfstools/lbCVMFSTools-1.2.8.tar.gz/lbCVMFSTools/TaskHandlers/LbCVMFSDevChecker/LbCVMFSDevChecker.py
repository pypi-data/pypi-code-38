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
CVMFS nightlies installer
@author: Stefan-Gabriel CHITIC, Ben Couturier
'''
import logging
import subprocess

from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSchecker.PluginManager import LbPluginManager

FREQ = 6 * 60


class LbCVMFSDevChecker(TaskHandlerInterface, object):

    def __init__(self, *args, **kwargs):
        logging.basicConfig(format="[%(asctime)s] "
                                   "%(levelname)-8s:"
                                   "%(message)s")
        logging.getLogger().setLevel(logging.INFO)
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(LbCVMFSDevChecker, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''

    def get_list_of_tasks(self):
        return ['monitor']

    def perform_task(self, task):
        l = LbPluginManager()
        l.executeAll()
