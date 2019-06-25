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
from lbCVMFSTools.TaskHandlers.NightliesInstallByProjectTask.\
    LbInfluxDBConnector import getConnector
from lbCVMFSTools import Audit
import datetime
import requests
from threading import Thread


FREQ = 0


@inject(pathManager=PathManager)
class NightliesInstallByProjectTask(TaskHandlerInterface, object):

    def __init__(self, slot, build, platform, project,
                 installOnCvmfs=True, overrideTodayCheck=False,
                 pathManager=None, *args, **kwargs):
        if kwargs.get('FREQ', None):
            global FREQ
            FREQ = kwargs.get('FREQ')
        super(NightliesInstallByProjectTask, self).__init__(FREQ, *args,
                                                            **kwargs)
        self.slot = slot
        self.build = build
        self.platform = platform
        self.project = project
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

    def get_list_of_tasks(self):
        alreadyInstalled = self.installManager.getInstalled()
        tuple_slot = (self.slot, self.build, self.platform,  self.project)
        if tuple_slot in alreadyInstalled:
            logging.info("%s%s, %s, %s, %s is already installed for today, "
                         "skipping" % (self.log_prefix, self.slot, self.build,
                                       self.platform, self.project))
            return []
        if not self.overrideTodayCheck and not self._shouldInstall():
            logging.info("%s%s, %s, %s, %s is not a slot for today, "
                         "skipping" % (self.log_prefix, self.slot, self.build,
                                       self.platform, self.project))
            return []
        return [tuple_slot]

    def _shouldInstall(self):
        from LbNightlyTools import Dashboard
        dash = Dashboard()
        strdate = self.installManager.getTodayStr(None)
        rows = [(row.doc['slot'], row.doc['build_id']) for row in
                dash.db.view('summaries/byDay', key=strdate, include_docs=True)]
        # First sort in revers by slot and by build id.
        # If same slot has multiple builds, first will come the higher (most
        # recent) build.
        rows.sort(reverse=True)
        # Convert the list of tuples in a dictionary. The key will be slot name
        # and its value it will be the last element in the list of builds id
        # from the same slot, i.e the first build of the day. This will be the
        # one that needs to be installed on CVMFS.
        rows = dict(rows)
        return str(rows.get(self.slot)) == self.build

    def postTransaction(self, success=False):
        if success and not self.dry_run:
            self.installManager.addInstalled(
                    [(self.slot, self.build, self.platform, self.project)])

    def perform_task(self, task):
        current_time = datetime.datetime.utcnow()
        slot = task[0]
        build = task[1]
        platform = task[2]
        project = task[3]
        # BY default we consider all is there
        needPublish = False
        # Now installing and checking the difference
        # making sure we haev the appropriate links for the builds
        try:
            if not self.linkManager.checkLinks(slot, build):
                logging.info("%sNeed to fix the links for %s %s" %
                             (self.log_prefix, slot, build))
                needPublish = True
                if not self.dry_run:
                    self.linkManager.fixLinks(slot, build)
        except Exception as e:
            pass

        # performing the install
        logging.info("%sUpdating %s %s %s %s" % (self.log_prefix,
                                                 slot, build, platform,
                                                 project))
        if self.installOnCvmfs:
            try:
                self.lbnInstall(slot, build, platform, project)
                try:
                    self._sendToInflux(current_time, slot, platform,
                                       project, build)
                except:
                    pass
            except:
                raise
        else:
            self.lbnInstall(slot, build, platform, project)

        # Comparing the list of tar files
        try:
            if self.installManager.installHasChanged(slot, build):
                logging.info(
                    "%sInstall has changed - copying list of "
                    "installed tars" % self.log_prefix)
                if not self.dry_run:
                    self.installManager.copyInstalledFile(slot, build)
                needPublish = True
        except Exception as e:
            print(e)
            # We just ignore and will not publish
            logging.info(
                "%sError checking whether the install has changed" %
                self.log_prefix)
        # Mark the platform as installed

        if not needPublish and self.installOnCvmfs:
            logging.info(
                "%sNo new files to install - aborting transaction" %
                self.log_prefix)
            raise UserWarning("No new files, aborting transaction")

    def _sendToInflux(self, started_time, slot, platform, project, buildId):
        current_time = datetime.datetime.utcnow()
        install_time = (current_time - started_time).total_seconds()
        started_time = started_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        db_entries = []
        db_entry = {
            'measurement': "cvmfs-nightlies",
            'tags': {
                'slot': str(slot),
                'platform': str(platform),
                'project': str(project)
                },
            "time": started_time,
            'fields': {
                'build_id': buildId,
                'install_time': install_time
                }
            }
        db_entries.append(db_entry)
        getConnector().write_points(db_entries)

    def updateMatterMost(self, slotname, buildId, platform, project):
        try:
            hook = "https://mattermost.web.cern.ch/" \
                   "hooks/q6wwxruzpbfs7bnc13wbege4hh"
            message = "Just finish deploying slot: %s, " \
                      "build: %s, project: %s, platform: " \
                      "%s to CVMFSDev Stratum-0" % (slotname,
                                                    buildId, project,
                                                    platform)
            payload = {"text": message}
            r = requests.post(hook, json=payload)
        except:
            pass

    def lbnInstall(self, slotname, buildId, platform, project):
        """ Actually call the lbn install command"""
        targetDir = self.pathManager.getSlotDir(slotname, buildId)
        args = ["lbn-install", "--no-git", "--dest=%s" % targetDir,
                "--platforms=%s" % platform, '--projects=%s' % project,
                slotname, str(buildId)]
        logging.info("%sInvoking: %s" % (self.log_prefix, " ".join(args)))
        if self.dry_run:
            return
        Audit.write(Audit.LBNINSTALL_START)
        rc = subprocess.call(args)
        Audit.write(Audit.LBNINSTALL_END)
        if rc != 0:
            raise RuntimeError("Could not perform lbn-install")
        thread = Thread(target=self.updateMatterMost, args=(slotname, buildId,
                                                            platform, project,))
        thread.start()

if __name__ == '__main__':
    a = NightliesInstallByProjectTask('lhcb-head', '1881', None, None)
