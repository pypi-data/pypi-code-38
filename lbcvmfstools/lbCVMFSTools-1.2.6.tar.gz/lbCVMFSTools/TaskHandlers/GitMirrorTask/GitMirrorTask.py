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
import threading
try:
    import Queue as queue
except:
    import queue as queue

from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface

FREQ = 10 * 60
TIMEOUT = 20 * 60


class GitMirrorTask(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True,
                 repodir='/cvmfs/lhcbdev.cern.ch/git-mirrors',
                 *args, **kwargs):
        if os.environ.get('CVMFS_REPO_NAME', None):
            repodir = "/cvmfs/%s/git-mirrors" % os.environ['CVMFS_REPO_NAME']
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(GitMirrorTask, self).__init__(FREQ, timeout=TIMEOUT,
                                            *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.repoDir = repodir
        logging.getLogger().setLevel(logging.INFO)

    def _md5(self, fname):
        hash_md5 = hashlib.md5()
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
            md5 = self._md5(path_head)
            todo.append({
                'path': path,
                'md5': md5
            })
        return [todo]

    def _mirrorRepo(self, task, queue):
        repo = task['path']
        needPublish = False
        try:
            logging.info("%sUpdating git repo: %s" % (self.log_prefix,
                                                      repo))
            subprocess.call(
                ["git", "--git-dir=%s" % repo, "remote", "update",
                 "--prune"])
            path_head = os.path.join(repo, 'FETCH_HEAD')
            md5 = self._md5(path_head)
            if md5 != task['md5']:
                logging.info("%sGit repo %s has changed" % (self.log_prefix,
                                                            repo))
                needPublish = True
        except Exception as e:
            logging.info(
                "%sGit update problem. Ignoring to avoid transaction"
                "rollback" % self.log_prefix)
            pass
        queue.put({
            'key': repo,
            'needPublish': needPublish
        })

    def perform_task(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        threads = []
        q = queue.Queue()
        for task in tasks:
            t = threading.Thread(target=self._mirrorRepo,
                                 args=(task, q))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        while not q.empty():
            q_obj = q.get()
            needPublish = needPublish or q_obj['needPublish']

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise UserWarning("No new files, aborting transaction")
