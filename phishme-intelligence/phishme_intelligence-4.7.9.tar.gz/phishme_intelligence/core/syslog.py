# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import logging
import sys
import socket

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class Syslog(object):

    def __init__(self, config, product):
        """
        Initialize a Syslog object

        :param ConfigParser config: PhishMe Intelligence configuration
        :param product: Name of integration (section name from configuration e.g. integration_mcafee_siem)
        """

        self.logger = logging.getLogger(__name__)
        self.config = config
        self.product = product

    def send(self, mrti):
        """
        Send syslog message to configured endpoint

        :param str mrti: PhishMe intelligence to send via syslog

        :return: None
        """

        level = 5
        facility = 3
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = '<%d>%s' % (level + facility * 8, mrti)

        temp_mrti = data.encode('utf-8')

        sock.sendto(temp_mrti, (self.config.get(self.product, 'host_without_protocol'), self.config.getint(self.product, 'port')))
        sock.close()
