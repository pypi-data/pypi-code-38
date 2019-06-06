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
from datetime import datetime

from phishme_intelligence.output.generic.generic_integration import GenericIntegration


class PmCef(GenericIntegration):
    """
    Class for generic processing of CEF formatted PhishMe Intelligence data
    """

    def _file_append(self, mrti):
        """
        Append CEF formatted PhishMe Intelligence Threat ID information to a file.

        :param str mrti: PhishMe Intelligence in CEF format
        :return: None
        """

        temp_mrti = mrti.encode('utf-8')

        with open(self.config.get(self.product, 'append_file_location'), 'ab+') as file_handle:
            file_handle.write(temp_mrti + b'\n')

    def _file_write(self, mrti, threat_id):
        """
        Write CEF formatted PhishMe Intelligence Threat ID information to a file.

        :param str mrti: PhishMe Intelligence in CEF format
        :return: None
        """

        # Get date of first publication.
        first_published = re.search('deviceCustomDate1=(\d+)', mrti).group(1)

        # Extract the date of first publication from the Threat.
        year_month_day = datetime.fromtimestamp(int(first_published) / 1e3).strftime('%Y-%m-%d')

        # Appends the date to the base output directory path.
        if self.config.getboolean(self.product, 'multiple_file_split_by_date'):
            current_path = os.path.join(self.config.get(self.product, 'multiple_file_location'), year_month_day)
        else:
            current_path = self.config.get(self.product, 'multiple_file_location')

        # Make sure this directory exists and create it if needed.
        if not os.path.exists(current_path):
            os.makedirs(current_path)

        # Build the file path for the output file.
        cur_file = os.path.join(current_path, str(threat_id) + '.cef')

        temp_mrti = mrti.encode('utf-8')

        # Write the JSON to a file.
        with open(cur_file, 'wb+') as file_handle:
            file_handle.write(temp_mrti + b'\n')

