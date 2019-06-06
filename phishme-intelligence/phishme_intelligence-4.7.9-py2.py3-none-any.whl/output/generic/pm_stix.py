# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

from __future__ import unicode_literals, absolute_import

import os
import re
import sys

import defusedxml.ElementTree as etree

from phishme_intelligence.output.generic.generic_integration import GenericIntegration


class PmStix(GenericIntegration):
    """
    Class for generic processing of STIX 1.1.1 formatted PhishMe Intelligence data
    """

    def _file_append(self, mrti): 
        """
        Append STIX 1.1.1 formatted PhishMe Intelligence Threat ID information to a file.

        :param str mrti: PhishMe Intelligence in STIX 1.1.1 format
        :return: None
        """

        try:
            stix_xml = etree.fromstring(mrti.encode('utf-8'))
        except etree.XMLSyntaxError:
            self.logger.error('XML parse error of STIX package')
        else:
            with open(self.config.get(self.product, 'append_file_location'), 'ab+') as file_handle:
                file_handle.write(mrti.encode('utf-8') + b'\n')

    def _file_write(self, mrti, threat_id):
        """
        Write STIX 1.1.1 formatted PhishMe Intelligence Threat ID information to a file.

        :param str mrti: PhishMe Intelligence in STIX 1.1.1 format
        :return: None
        """
        # Extract the date of first publication from the Threat.
        year_month_day = re.search('<indicator:Start_Time precision=\"second\">(\d{4}-\d{2}-\d{2})T', mrti).group(1)

        # Appends the date to the base output directory path.
        if self.config.getboolean(self.product, 'multiple_file_split_by_date'):
            current_path = os.path.join(self.config.get(self.product, 'multiple_file_location'), year_month_day)
        else:
            current_path = self.config.get(self.product, 'multiple_file_location')

        # Make sure this directory exists and create it if needed.
        if not os.path.exists(current_path):
            os.makedirs(current_path)

        # Build the file path for the output file.
        cur_file = os.path.join(current_path, str(threat_id) + '.xml')

        try:
            stix_xml = etree.fromstring(mrti.encode('utf-8'))
        except etree.XMLSyntaxError:
            self.logger.error('XML parse error of STIX package for Threat ID: ' + threat_id + '.')
        else:
            with open(cur_file, 'wb+') as file_handle:
                file_handle.write(mrti.encode('utf-8') + b'\n')
