#!/usr/bin/env python

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
Command line client that interfaces to the Installer class

:author: Stefan-Gabriel CHITIC
'''
from __future__ import print_function

import logging
import optparse
import sys
import traceback

import os

from lbCVMFSTools.Injector import injector
from lbCVMFSTools.Scheduler import Scheduler
from lbCVMFSTools.TaskHandlerInterface import TaskHandlerInterface
from lbCVMFSTools.TransactionHandlerInterface import \
    TransactionHandlerInterface


# Class for known install exceptions
###############################################################################


class ClientException(Exception):
    """ Custom exception for cvmfs-install

    :param msg: the exception message
    """

    def __init__(self, msg):
        """ Constructor for the exception """
        # super(ClientException, self).__init__(msg)
        Exception.__init__(self, msg)


# Classes and method for command line parsing
###############################################################################


class ClientOptionParser(optparse.OptionParser):
    """ Custom OptionParser to intercept the errors and rethrow
    them as CVMFSDevManagerException """

    def error(self, msg):
        """
        Arguments parsing error message exception handler

        :param msg: the message of the exception
        :return: Raises CVMFSDevManagerException with the exception
        message
        """
        raise ClientException("Error parsing arguments: " + str(msg))

    def exit(self, status=0, msg=None):
        """
        Arguments parsing error message exception handler

        :param status: the status of the application
        :param msg: the message of the exception
        :return: Raises ClientException with the exception
        message
        """
        raise ClientException("Error parsing arguments: " + str(msg))


class GenericClient(object):
    """ Main class for the tool """

    def __init__(self, prog="", help=""):
        """ Common setup for both clients """
        logging.basicConfig(format="%(levelname)-8s: %(asctime)s %(message)s")
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.WARNING)
        self.prog = prog
        self.help = help
        self.dry_run = None

        parser = ClientOptionParser(usage=self.usage(self.prog, self.help))
        parser.add_option('--dry-run',
                          dest="dry_run",
                          default=False,
                          action="store_true",
                          help="Only print the command that will be run")
        parser.add_option('--admin-override',
                          dest="admin_override",
                          default=False,
                          action="store_true",
                          help="Admin override to ignore frequency of "
                               "executions")
        self.parser = parser

    def defineTaskHandler(self, args, opts):
        raise NotImplemented

    def defineTransitionHandler(self, args, opts):
        raise NotImplemented

    def configureClient(self, args, opts):
        raise NotImplemented

    def main(self):
        """ Main method for the ancestor:
        call parse and run in sequence

        :returns: the return code of the call
        """
        rc = 0
        try:
            opts, args = self.parser.parse_args()
            self.configureClient(args, opts)

            transactionHandler = self.defineTransitionHandler(args, opts)
            taskHandler = self.defineTaskHandler(args, opts)
            taskHandler.dry_run = opts.dry_run
            taskHandler.override = opts.admin_override
            injector.provide_instance(TransactionHandlerInterface,
                                      transactionHandler)
            injector.provide_instance(TaskHandlerInterface, taskHandler)

            # Getting the function to be invoked
            self.run()

        except ClientException as lie:
            print("ERROR: " + str(lie), file=sys.stderr)
            self.parser.print_help()
            rc = 1
        except:
            print("Exception:", file=sys.stderr)
            print('-'*60, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print('-'*60, file=sys.stderr)
            rc = 1
        return rc

    def run(self):
        """ Main method for the command"""
        Scheduler()

    def usage(self, cmd, help):
        """ Prints out how to use the script...
        """
        cmd = os.path.basename(cmd)
        return '''%s :%s ''' % (cmd, help)

