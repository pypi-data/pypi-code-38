'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''
from __future__ import unicode_literals, absolute_import

import logging
import sys
import socket

try:
    from configparser import NoOptionError
except ImportError:
    from ConfigParser import NoOptionError

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

        try:
            self.protocol = self.config.get(self.product, 'protocol')
        except NoOptionError:
            self.protocol = 'UDP'

    def send(self, mrti):
        """
        Send syslog message to configured endpoint

        :param str mrti: PhishMe intelligence to send via syslog

        :return: None
        """

        level = 5
        facility = 3
        if self.protocol.upper() == 'UDP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif self.protocol.upper() == 'TCP':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.logger.error('Incorrect protocol type. Set protocol in config file to either TCP or UDP')
            raise RuntimeError

        data = '<%d>%s' % (level + facility * 8, mrti)

        temp_mrti = data.encode('utf-8')

        sock.sendto(temp_mrti, (self.config.get(self.product, 'host_without_protocol'), self.config.getint(self.product, 'port')))
        sock.close()
