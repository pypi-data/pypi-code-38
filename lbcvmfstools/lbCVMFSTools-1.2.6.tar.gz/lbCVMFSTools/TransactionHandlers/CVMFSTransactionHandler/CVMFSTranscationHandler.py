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
Slot manager for CVMFS Tools
@author: Stefan-Gabriel CHITIC, Ben Couturier
'''

import subprocess
import logging
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface


class CVMFSTransactionHandler(TransactionHandlerInterface):

    def __init__(self, reponame, *args, **kwargs):
        self.reponame = reponame
        super(CVMFSTransactionHandler, self).__init__(*args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '

    def transactionStart(self):
        """ Start a CVMFS transaction """
        logging.info("%sCalled CVMFS Transaction start" % self.log_prefix)
        if self.dry_run is True:
            return
        rc = subprocess.call(["cvmfs_server", "transaction", self.reponame])
        if rc != 0:
            self.transactionAbort()
            raise(RuntimeError("Could not start CVMFS transaction"))

    def transactionPublish(self):
        """ Publish a CVMFS transaction """
        logging.info("%sCalled CVMFS Transaction publish" % self.log_prefix)

        if self.dry_run is True:
            return
        # subprocess.call(["checkfds"])
        newenv = dict()
        newenv["PATH"] = "/home/cvlhcbdev/bin:/usr/sue/bin" \
                         ":/sbin:/bin:/usr/sbin:/usr/bin:" \
                         "/usr/local/sbin:/home/cvlhcbdev/bin"
        rc = subprocess.call(["cvmfs_server", "publish", self.reponame],
                             env=newenv)

        if rc != 0:
            # subprocess.call(["checkfds"])
            raise(RuntimeError("Could not publish CVMFS transaction"))

    def transactionAbort(self):
        """ Abort a CVMFS transaction """
        logging.info("%sCalled CVMFS Transaction abort" % self.log_prefix)
        if self.dry_run is True:
            return
        rc = subprocess.call(["cvmfs_server", "abort", "-f", self.reponame])
        if rc != 0:
            raise(RuntimeError("Could not abort CVMFS transaction"))
