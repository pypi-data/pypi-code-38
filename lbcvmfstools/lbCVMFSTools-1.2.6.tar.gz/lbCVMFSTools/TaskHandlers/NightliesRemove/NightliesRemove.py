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
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.Utils \
    import PathManager, LinkManager, InstalledManager
import shutil
import os

FREQ = 0


@inject(pathManager=PathManager)
class NightliesRemove(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True, overrideTodayCheck=False,
                 pathManager=None, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(NightliesRemove, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        logging.getLogger().setLevel(logging.INFO)
        self.overrideTodayCheck = overrideTodayCheck
        self.maxnbperslot = 9
        self.maxtodelete = 20
        if pathManager:
            self.pathManager = pathManager
        else:
            self.pathManager = PathManager()
        self.linkManager = LinkManager(pathManager=self.pathManager)
        self.installManager = InstalledManager(pathManager=self.pathManager)

    def listBuildsInDir(self, slotdir):
        """ List all the builds installed in a given dir
            and returns a triplet(buildId, date, isLinked) """
        buildIds = [f for f in os.listdir(slotdir)
                    if not os.path.islink(os.path.join(slotdir, f))]
        # List builds which are target of a loink therefore cannot be removed
        linkTargets = set()
        for f in os.listdir(slotdir):
            fp = os.path.join(slotdir, f)
            if os.path.islink(fp):
                linkTargets.add(os.readlink(fp))
        retinfo = [(f, os.path.join(slotdir, f),
                    os.path.getctime(os.path.join(slotdir, f)),
                    f in linkTargets)
                   for f in buildIds]

        # Returns a list of tuples containing:
        # (buildId, full path, creation time, is target of a link)
        def cast(tup):
            retval = 0
            try:
                retval = int(tup[0])
            except ValueError:
                pass
            return retval
        return sorted(retinfo, key=cast, reverse=True)

    def get_list_of_tasks(self):
        rootdir = self.pathManager._getRepoDir()
        allSlots = os.listdir(rootdir)
        toReturn = []
        for sname in allSlots:
            logging.info("Checking if %s need to be clean up" % sname)
            apath = os.path.join(rootdir, sname)
            allbuilds = self.listBuildsInDir(apath)
            nbTotal = len(allbuilds)
            nbForceKept = len([t for t in allbuilds if t[3]])
            potentialUnused = [t for t in allbuilds if not t[3]]
            nbavail = len(potentialUnused)
            logging.info(
                "There are %d builds in slot %s. %d are link targets "
                "and cannot be removed" % (nbTotal,
                                           sname, nbForceKept))
            nbwishtodelete = max(len(allbuilds) - self.maxnbperslot, 0)
            nbtodelete = min(nbwishtodelete, nbavail)
            logging.info(
                "We want a max of %d - Wish to delete %d slots - "
                "Can delete: %d" % (self.maxnbperslot,
                                    nbwishtodelete,
                                    nbavail))
            if nbtodelete > 0:
                toremove = potentialUnused[-nbtodelete:]
                toReturn.append({
                    'task_name': 'Cleanup %s' % sname,
                    'buildsIds': toremove
                })
        return toReturn

    def perform_task(self, task):
        toremove = task['buildsIds']
        logging.warning(
            "Found %d jobs to remove (will remove a"
            " max of %d as specified)" % (len(toremove), self.maxtodelete))
        for tup in list(toremove)[-1 * self.maxtodelete:]:
            try:
                logging.warning("Removing %s" % tup[1])
                shutil.rmtree(tup[1])
            except:
                logging.error("Problem removing: %s" % tup[1])




