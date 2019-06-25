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
Sample task
@author: Stefan-Gabriel CHITIC
'''
import logging
import subprocess

from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface


FREQ = 1
TIMEOUT = 20 * 60


class LbCVMFSScriptRunner(TaskHandlerInterface, object):

    def __init__(self, command, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(LbCVMFSScriptRunner, self).__init__(
            FREQ, timeout=TIMEOUT, *args, **kwargs)
        self.script_command = command
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '

    def get_list_of_tasks(self):
        """ Logic to get the list of task to be executed
        """
        logging.info("%sGeting the list of tasks" % self.log_prefix)
        return [self.script_command]

    def _comnunicate(self, command):
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed: %s" % (command, err))
        print(out)

    def perform_task(self, tasks):
        """
        Executes a task(s)
        :param tasks:
        :return:
        """
        logging.info("%sExceuting task: %s" % (self.log_prefix, tasks))
        self._comnunicate(tasks)
