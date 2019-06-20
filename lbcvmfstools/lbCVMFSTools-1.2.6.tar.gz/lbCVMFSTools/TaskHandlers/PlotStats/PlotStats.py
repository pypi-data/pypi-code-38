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
import os

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
import subprocess

FREQ = 3 * 60 * 60


class PlotStats(TaskHandlerInterface, object):

    def __init__(self, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(PlotStats, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''

    def get_list_of_tasks(self):
        return ['plotStats']

    def perform_task(self, task):
        home = os.environ['HOME']
        command = os.path.join(home, 'bin', 'plotstats.sh')
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed")
