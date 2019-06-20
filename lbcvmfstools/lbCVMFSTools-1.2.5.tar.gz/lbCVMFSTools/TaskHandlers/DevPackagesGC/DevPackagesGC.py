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
from lbdevmanager.LbInstallManager import LbInstallManager

FREQ = 10 * 60 * 24


class DevPackagesGC(TaskHandlerInterface, object):

    def __init__(self, siteroot="/cvmfs/lhcbdev.cern.ch/lib",
                 repo=None,
                 installOnCvmfs=True, *args, **kwargs):
        if os.environ.get('CVMFS_REPO_NAME', None):
            siteroot = "/cvmfs/%s/lib" % os.environ['CVMFS_REPO_NAME']
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(DevPackagesGC, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        self.siteroot = siteroot
        if repo:
            self.repo = repo
        else:
            self.repo = os.path.expandvars("${HOME}/conf/cvmfsdev-sw")
        logging.getLogger().setLevel(logging.INFO)
        self.gitManager = GitManager(repo_path=self.repo)
        self.installer = LbInstallManager(siteroot=self.siteroot)

    def get_list_of_tasks(self):
        installedPkgs = self.gitManager.GetInstalledPkg()
        currentRequestedPrefixes = self.gitManager.GetYamlContent()
        currentRequestedPkgs = []
        toReturn = []
        for prefixWithExclusions in currentRequestedPrefixes:
            prefix = prefixWithExclusions['prefix']
            prefixWithExclusions['prefix'] = prefix.replace('+', '\+')
            pkgList = self.installer.checkPackagesInRemoteDatabase(
                prefixWithExclusions)
            for pkg in pkgList:
                currentRequestedPkgs.append(pkg.rpmName())
        for pkg in installedPkgs:
            if pkg not in currentRequestedPkgs:
                toReturn.append(pkg)
        return toReturn

    def perform_task(self, task):
        self.installer.removeFiles([task])

    def postTransaction(self):
        self.gitManager.RemoveFromListOfFiles(self.installer.removedPacakges)
