#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

import logging
import sys

from phishme_intelligence.output.base_integration import BaseIntegration
from phishme_intelligence.core.syslog import Syslog

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class McAfeeSiem(BaseIntegration):

    def __init__(self, config, product):
        """

        :param config:
        :param product:
        :return:
        """

        super(McAfeeSiem, self).__init__(config=config, product=product)

        self.logger = logging.getLogger(__name__)
        self.syslog = Syslog(config=config, product=product)

    def process(self, mrti, threat_id):
        """

        :param mrti:
        :param threat_id:
        :return:
        """

        # Send CEF via syslog.
        self.syslog.send(mrti=mrti)
