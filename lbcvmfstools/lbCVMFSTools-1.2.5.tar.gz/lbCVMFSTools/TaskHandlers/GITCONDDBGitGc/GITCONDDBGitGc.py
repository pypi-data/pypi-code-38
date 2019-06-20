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

FREQ = 7 * 24 * 60 * 60


class GITCONDDBGitGc(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True,
                 repodir='/cvmfs/lhcb.cern.ch/lib/lhcb/git-conddb',
                 *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(GITCONDDBGitGc, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repoDir = repodir
        logging.getLogger().setLevel(logging.INFO)

    def get_list_of_tasks(self):
        allrepos = os.listdir(self.repoDir)
        todo = []
        for r in allrepos:
            path = os.path.join(self.repoDir, r)
            todo.append(path)
        return todo

    def _comnunicate(self, command):
        command = command.split(' ')
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            raise Exception("Command %s failed")
        return out

    def perform_task(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        for repo in tasks:
            try:
                logging.info("%sRunning git gc: %s" % (self.log_prefix, repo))
                self._comnunicate("git --git-dir %s gc" % repo)
            except Exception as e:
                raise e
