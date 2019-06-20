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
import time
import os

TRANSACTION_START = 'TRANSACTION_START'
TRANSACTION_END = 'TRANSACTION_END'
COMMAND_START = 'COMMAND_START'
COMMAND_END = 'COMMAND_END'
LBNINSTALL_START = 'LBNINSTALL_START'
LBNINSTALL_END = 'LBNINSTALL_END'

current_command = None


def write(flag, command=None):
    global current_command
    if command:
        current_command = command
    filename = "%s/audit.log" % (
        os.environ.get('LOGDIR', os.environ.get('HOME', ''))
    )
    str_time = int(round(time.time() * 1000))
    file_line = '%s\t%s\t%s\n' % (str_time, current_command, flag)
    f = open(filename, 'a+')
    f.write(file_line)
    f.close()


