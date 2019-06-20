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

FREQ = 20 * 60

class GITCONDDBSync(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True,
                 repodir='/cvmfs/lhcb.cern.ch/lib/lhcb/git-conddb',
                 *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(GITCONDDBSync, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repoDir = repodir
        logging.getLogger().setLevel(logging.INFO)

    def _md5(self, fname, inputOnly=False):
        hash_md5 = hashlib.md5()
        if inputOnly:
            hash_md5.update(fname)
            return hash_md5.hexdigest()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_list_of_tasks(self):
        allrepos = os.listdir(self.repoDir)
        todo = []
        for r in allrepos:
            path = os.path.join(self.repoDir, r)
            path_head = os.path.join(path, 'FETCH_HEAD')
            if os.path.exists(path_head):
                md5 = self._md5(path_head)
            else:
                md5 = None
            todo.append({
                'path': path,
                'md5': md5
            })
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
        for task in tasks:
            repo = task['path']
            try:
                logging.info("%sUpdating git repo: %s" % (self.log_prefix,
                                                          repo))

                before = self._md5(
                    self._comnunicate("git --git-dir %s for-each-ref" % repo),
                    inputOnly=True)

                master_old = self._comnunicate(
                    "git --git-dir %s rev-parse master" % repo).replace(
                    '\n', '')
                force_path = os.path.join(os.environ['HOME'],
                                          'force_git_conddb_update')

                self._comnunicate("git --git-dir %s fetch --prune" % repo)
                self._comnunicate("git --git-dir %s fetch --tags" % repo)

                after = self._md5(
                    self._comnunicate("git --git-dir %s for-each-ref" % repo),
                    inputOnly=True)
                if before != after:
                    needPublish = True
                if str(repo).endswith('ONLINE.git'):
                    if os.path.exists(force_path):
                        logging.info(
                            "%sONLINE update forced" % (self.log_prefix))
                        os.remove(force_path)
                    else:
                        res = self._comnunicate(
                            "git --git-dir %s log --decorate --stat %s.." % (repo, master_old))
                        needPublish = 'tick' in res or 'valid_runs' in res or 'fake' in res or 'onl-' in res
                path_head = os.path.join(repo, 'FETCH_HEAD')
                md5 = self._md5(path_head)
                if md5 != task['md5']:
                    logging.info("%sGit repo %s has changed" % (self.log_prefix,
                                                                repo))
                    needPublish = True
            except Exception as e:
                logging.info(
                    "%Git update problem. Ignoring to avoid transaction"
                    "rollback" % self.log_prefix)
                pass

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise UserWarning("No new files, aborting transaction")
