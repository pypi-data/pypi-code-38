# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.


import logging


class BaseIntegration(object):
    """
    Base Class of all PhishMe Integration classes
    """
    def __init__(self, config, product):
        """
        Initialize BaseIntegration class

        :param ConfigParser config: PhishMe Intelligence integration configuration
        :param str product: Name of integration (section name from configuration e.g. integration_mcafee_siem)
        """

        self.config = config
        self.logger = logging.getLogger(__name__)
        self.product = product

        self.logger.info('Initialized %s integration' % self.product)

    def process(self, mrti, threat_id):
        """
        Method stub for process; this will be overridden by child integration classes

        :param str mrti: PhishMe Intelligence Threat ID data
        :param int threat_id: PhishMe Intelligence threat id
        :return: None
        """

        pass

    def post_run(self, config_file_location):
        """
        Method stub for post_run; this will be overridden by child integration classes as needed

        :param str config_file_location: Path to configuration file
        :return: None
        """

        pass
