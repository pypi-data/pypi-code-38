from __future__ import unicode_literals

"""
Copyright 2013-2016 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

PhishMe QRadar SIEM Module
Author: Josh Larkins
Support: support@phishme.com
ChangesetID: CHANGESETID_VERSION_STRING

"""

import sys
import json

from phishme_intelligence.output.base_integration import BaseIntegration

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class QRadarSiem(BaseIntegration):

    def write_file(self, indicator_json, indicator_type):

        output_dir = self.config.get(self.product, 'json_output_dir')

        try:
            with open(output_dir + '%s.json' % indicator_type, 'a') as indicator_file:
                indicator_file.write(json.dumps(indicator_json) + '\n')
        except OSError as e:
            self.logger.error('Could not write indicator file to %s: %s' % (output_dir, e))

    def process(self, mrti, threat_id):
        """

        :param mrti:
        :param threat_id:
        :return:
        """

        self.logger.info('Processing Threat ID: %s' % threat_id)
        self.logger.info('Building Collection Data for %s' % threat_id)

        threathq_url = mrti.threathq_url
        active_threat_report_url = mrti.active_threat_report
        brand = mrti.brand
        first_published = mrti.first_published
        last_published = mrti.last_published

        self.logger.info('Writing %s indicators to JSON files' % threat_id)
        for artifact in mrti.executable_set:
            md5 = {artifact.md5: {'Identifier': threat_id,
                                  'First Seen Date': first_published,
                                  'Last Seen Date': last_published,
                                  'Malware Family': artifact.malware_family,
                                  'Threat Details': threathq_url,
                                  'Active Threat Report': active_threat_report_url,
                                  'Brand': brand,
                                  'Infrastructure Type': artifact.type,
                                  'Provider': 'Cofense Intelligence'}}
            sha256 = {artifact.sha256: {'Identifier': threat_id,
                                        'First Seen Date': first_published,
                                        'Last Seen Date': last_published,
                                        'Malware Family': artifact.malware_family,
                                        'Threat Details': threathq_url,
                                        'Active Threat Report': active_threat_report_url,
                                        'Brand': brand,
                                        'Infrastructure Type': artifact.type,
                                        'Provider': 'Cofense Intelligence'}}

            self.write_file(md5, 'MD5')
            self.write_file(sha256, 'SHA256')

        for ioc in mrti.block_set:

            indicator = {ioc.watchlist_ioc: {'Identifier': threat_id,
                                             'Impact Rating': ioc.impact,
                                             'First Seen Date': first_published,
                                             'Last Seen Date': last_published,
                                             'Malware Family': ioc.malware_family,
                                             'Threat Details': threathq_url,
                                             'Active Threat Report': active_threat_report_url,
                                             'Brand': brand,
                                             'Infrastructure Type': ioc.role,
                                             'Provider': 'Cofense Intelligence'}}

            if ioc.block_type == 'URL':
                self.write_file(indicator, 'URL')

            if ioc.block_type == 'IPv4 Address':
                self.write_file(indicator, 'IPv4')

            if ioc.block_type == 'Domain Name':
                self.write_file(indicator, 'Hostname')





