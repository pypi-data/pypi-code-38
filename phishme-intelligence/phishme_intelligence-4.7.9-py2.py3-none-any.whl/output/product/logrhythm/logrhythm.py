#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

import logging
import os

from phishme_intelligence.output.base_integration import BaseIntegration


class LogRhythm(BaseIntegration):

    def __init__(self, config, product):
        """

        :param config:
        :param logger:
        :param product:
        :return:
        """

        super(LogRhythm, self).__init__(config=config, product=product)

        self.logger = logging.getLogger(__name__)

        # Make the directory if it doesn't exist.
        self.output_dir = self.config.get(self.product, 'output_dir')
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    @staticmethod
    def _file_write(ioc, file_path):
        """

        :param ioc:
        :param file_path:
        :return:
        """

        # Write the JSON to a file.
        with open(file_path, 'ab+') as file_handle:
            file_handle.write(ioc.encode('utf8') + '\n'.encode('utf8'))

    def process(self, mrti, threat_id):
        """

        :param mrti:
        :param threat_id:
        :return:
        """

        for item in mrti.block_set:
            file_name = 'phishme_intelligence' + '_' + item.block_type + '_' + item.impact + '.txt'
            file_name = file_name.replace(' ', '').lower()
            destination_dir = os.path.join(self.output_dir, file_name)

            self._file_write(ioc=item.watchlist_ioc, file_path=destination_dir)

        for item in mrti.subject_set:
            file_name = 'phishme_intelligence_subjects_none.txt'
            destination_dir = os.path.join(self.output_dir, file_name)
            self._file_write(ioc=item.subject, file_path=destination_dir)

        for item in mrti.executable_set:

            file_name = 'phishme_intelligence' + '_' + 'md5' + '.txt'
            destination_dir = os.path.join(self.output_dir, file_name)
            self._file_write(ioc=item.md5, file_path=destination_dir)
