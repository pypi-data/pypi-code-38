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
import os
from lbCVMFSTools.Injector import inject
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbdevmanager.GitManager import GitManager
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.Common import get_connection
from multiprocessing import Process

FREQ = 10 * 60 * 0


def install(siteroot, filesToInstall):
    from lbdevmanager.LbInstallManager import LbInstallManager
    installer = LbInstallManager(siteroot=siteroot)
    installer.installFiles(filesToInstall)


class DevPackagesInstaller(TaskHandlerInterface, object):

    def __init__(self, toInstall=[],
                 installed=[],
                 priority=0,
                 commitID=None,
                 maxretry=3,
                 installOnCvmfs=True,
                 vhost='/lhcb', *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(DevPackagesInstaller, self).__init__(FREQ, *args, **kwargs)
        self.toInstall = toInstall
        self.installed = installed
        self.priority = priority
        self.commitID = commitID
        self.max_retry = maxretry
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.siteroot = "/cvmfs/lhcbdev.cern.ch/lib"
        if os.environ.get('CVMFS_REPO_NAME', None):
            self.environ = "/cvmfs/%s/lib" % os.env['CVMFS_REPO_NAME']
        self.repo = os.path.expandvars("${HOME}/conf/cvmfsdev-sw")
        logging.getLogger().setLevel(logging.INFO)
        self.gitManager = None
        self.gitManager = GitManager(repo_path=self.repo)
        connection = get_connection(vhost=vhost)
        self.broker = CvmfsDevExchange(connection)

    def get_list_of_tasks(self):
        return self.toInstall

    def perform_task(self, task):
        try:
            p = Process(target=install, args=(self.siteroot, [task],))
            p.start()
            p.join()
            if p.exitcode == 0:
                self.installed.append(task)
        except Exception as e:
            print(e)
        finally:
            installer = None

    def postTransaction(self):
        all_good = True
        retryInstall = []
        for reqInstall in self.toInstall:
            if reqInstall not in self.installed:
                all_good = False
                retryInstall.append(reqInstall)
        if all_good:
            self.gitManager.UpdateTags()
        else:
            # Send re-list to RabbitMQ
            args = ['--toinstall="%s"' % ' '.join(retryInstall),
                    '--installed="%s"' % ' '.join(self.installed),
                    '--commitID=%s' % self.commitID, '--with_meta']
            self.broker.send_command('manager_dev',
                                     args,
                                     priority=self.priority,
                                     max_retry=self.max_retry)
