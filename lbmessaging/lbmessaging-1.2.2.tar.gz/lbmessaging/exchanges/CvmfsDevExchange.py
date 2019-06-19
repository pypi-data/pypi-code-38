###############################################################################
# (c) Copyright 2017 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Module in charge of dealing with sending and receiving commands for the
/cvmfs/lhcbdev.cern.ch
'''

from lbmessaging.exchanges.CommandExchange import CommandExchange
from lbmessaging.services.Common import ExposedIn
import os

__author__ = 'Ben Couturier <ben.couturier@cern.ch>'


CVMFSDEV_EXCHANGE = "cvmfsdev.action"


@ExposedIn('CVMFSNightliesService', mapping= {
        'dev_send': 'send_command',
        'dev_receive': 'receive_command'
    }
)
class CvmfsDevExchange(CommandExchange):
    """ Customized exchange for the cvmfsdev startum-0 server """

    def __init__(self, channel):
        """ Constructor that fixes the names of the exchanges
        :param channel: a pikaBlockingConnection channel that should be used in
                        the broker
        """

        super(CvmfsDevExchange, self).__init__(channel,
                                               CVMFSDEV_EXCHANGE)
