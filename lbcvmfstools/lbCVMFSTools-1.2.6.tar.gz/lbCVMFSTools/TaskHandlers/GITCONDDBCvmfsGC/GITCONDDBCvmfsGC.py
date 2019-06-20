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
@author: Stefan-Gabriel CHITIC
'''
import logging
import subprocess
import os
import hashlib

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

FREQ = 24 * 60 * 60


class GITCONDDBCvmfsGC(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True,
                 repo='/cvmfs/lhcb-condb.cern.ch/',
                 *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(GITCONDDBCvmfsGC, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repo = repo
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_tasks(self):
        return ['gc']

    def _comnunicate(self, command):
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        if err:
            logging.error("%s" % err)
        logging.info("%s" % out)
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed" % command)
        return out

    def perform_task(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        # BY default we consider all is there
        # Now installing and checking the difference
        for _ in tasks:
            try:
                logging.info("%sRunning gc: %s" % (self.log_prefix, self.repo))
                command = ["cvmfs_server", "gc", "-t", "3 days ago", "-f",
                           self.repo]
                self._comnunicate(command)
            except Exception as e:
                raise e
