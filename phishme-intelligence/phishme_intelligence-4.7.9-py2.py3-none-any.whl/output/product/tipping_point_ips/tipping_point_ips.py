#Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
#This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
#including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
#disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
#consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
#this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.

import logging
import sys
from datetime import datetime

from phishme_intelligence.core import rest_api
from phishme_intelligence.output.base_integration import BaseIntegration

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class TippingPointIps(BaseIntegration):
    """
    The PhishMe Intelligence TippingPoint IPS integration helper class
    """

    def __init__(self, config, product):
        """
        Initialize the PhishMe Intelligence TippingPoint IPS integration helper class

        :param ConfigParser config: PhishMe Intelligence integration configuration
        :param str product: Name of integration (section name from configuration e.g. integration_mcafee_siem)
        """

        super(TippingPointIps, self).__init__(config=config, product=product)

        self.logger = logging.getLogger(__name__)
        self.rest_api = rest_api.RestApi(config=self.config, product=self.product)

    def _quarantine(self, watchlist_ioc, watchlist_ioc_type, tag_data):
        """
        Add IOCs to TippingPoint IPS

        :param str watchlist_ioc: IOC value from PhishMe Intelligence
        :param str watchlist_ioc_type: Type of IOC value form PhishMe Intelligence (Domain Name or IPv4 Address)
        :param str tag_data: Tags to use for IOCs
        :return: None
        """

        url = 'https://' + self.config.get(self.product, 'host_with_protocol') + '/repEntries/add'
        params = {
            'smsuser': self.config.get(self.product, 'user'),
            'smspass': self.config.get(self.product, 'pass'),
            'TagData': tag_data
        }

        if watchlist_ioc_type == 'Domain Name':
            params.update(
                {
                    'dns': watchlist_ioc
                }
            )
        elif watchlist_ioc_type == 'IPv4 Address':
            params.update(
                {
                    'ip': watchlist_ioc
                }
            )

        else:
            self.logger.error('Incorrect watchlist type being sent to TippingPoint: ' + watchlist_ioc_type)

        status_code, response = self.rest_api.connect_to_api(verb='GET', url=url, params=params)
        if status_code != 200:
            print(response)

    def process(self, mrti, threat_id):
        """
        Select the correct IOCs to send to TippingPoint and format the correct context to go with them.

        :param str mrti: PhishMe Intelligence Threat ID information
        :param int threat_id: PhishMe Intelligence Threat ID number
        """

        threat_id = str(mrti.threat_id)
        last_published = datetime.fromtimestamp(mrti.last_published / 1e3).strftime('%Y-%m-%d')
        threat_details = mrti.threathq_url
        active_threat_report = mrti.active_threat_report

        # Loop through all BlockSet items.
        for item in mrti.block_set:

            # Only process these types of IOCs.
            if item.block_type == 'IPv4 Address' or item.block_type == 'Domain Name':

                impact_rating = item.impact

                # Build a string of context for this IOC
                tag_data = ''
                tag_data += 'PhishMeIntel_Threat-ID,' + threat_id + ','
                tag_data += 'PhishMeIntel_Malware-Family,' + item.malware_family + ','
                tag_data += 'PhishMeIntel_Impact-Rating,' + impact_rating + ','
                tag_data += 'PhishMeIntel_Role,' + item.role + ','
                tag_data += 'PhishMeIntel_Last-Published,' + last_published

                # Only push IOCs to TippingPoint if the Impact Rating is turned on.
                use_impact = 'impact_' + impact_rating.lower()
                if self.config.getboolean(self.product, use_impact):
                    self._quarantine(watchlist_ioc=item.watchlist_ioc, watchlist_ioc_type=item.block_type, tag_data=tag_data)
