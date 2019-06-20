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
from datetime import datetime, timedelta
import os

FREQ = 0


@inject(pathManager=PathManager)
class NightliesRemoveLinks(TaskHandlerInterface, object):

    def __init__(self, installOnCvmfs=True, overrideTodayCheck=False,
                 pathManager=None, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(NightliesRemoveLinks, self).__init__(FREQ, *args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '
        self.installOnCvmfs = installOnCvmfs
        logging.getLogger().setLevel(logging.INFO)
        self.overrideTodayCheck = overrideTodayCheck
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
        retinfo = []
        # List builds which are target of a loink therefore cannot be removed
        for f in os.listdir(slotdir):
            fp = os.path.join(slotdir, f)
            if os.path.islink(fp):
                build_id = os.readlink(fp)
                retinfo.append((f, build_id,
                                datetime.fromtimestamp(
                                    os.path.getctime(fp)).date()))

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
        dates = [datetime.today() - timedelta(days=d)
                 for d in range(7)]
        date_dict = {str(d.strftime('%A'))[0:3]: d.date() for d in dates}
        date_dict['Today'] = datetime.today().date()
        date_dict['Yesterday'] = (datetime.today() - timedelta(days=1)).date()

        for sname in allSlots:
            logging.info("Checking if %s need to be clean up for symlinks" %
                         sname)
            apath = os.path.join(rootdir, sname)
            symLinks = self.listBuildsInDir(apath)
            logging.info(
                "There are %d are link targets in %s " % (len(symLinks),
                                                          sname))
            toDelete = []
            for link in symLinks:
                if link[0] not in date_dict.keys():
                    continue
                if date_dict[link[0]] != link[2]:
                    toDelete.append(os.path.join(apath, link[0]))
            logging.info(
                "We want to remove a number of %d invalid symlinks " % (
                    len(toDelete)))
            if toDelete:
                toReturn.append({
                    'task_name': 'Cleanup %s' % sname,
                    'buildsIds': toDelete
                })
        return toReturn

    def perform_task(self, task):
        toremove = task['buildsIds']
        logging.warning(
            "Found %d jobs to remove" % (len(toremove)))
        for tup in list(toremove):
            try:
                logging.warning("Removing %s" % tup)
                os.unlink(tup)
            except:
                logging.error("Problem removing: %s" % tup)




