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


class DefaultTransactionHandler(TransactionHandlerInterface):

    def __init__(self, *args, **kwargs):
        super(DefaultTransactionHandler, self).__init__(*args, **kwargs)
        self.log_prefix = ''
        if self.dry_run:
            self.log_prefix = 'IN DRY-RUN MODE: '

    def transactionStart(self):
        """ Start a CVMFS transaction """
        logging.info("%sNoting to do for transaction start" % self.log_prefix)

    def transactionPublish(self):
        """ Publish a CVMFS transaction """
        logging.info("%sNoting to do for transaction publish" %
                     self.log_prefix)

    def transactionAbort(self):
        """ Abort a CVMFS transaction """
        logging.info("%sNoting to do for transaction abort" %
                     self.log_prefix)
