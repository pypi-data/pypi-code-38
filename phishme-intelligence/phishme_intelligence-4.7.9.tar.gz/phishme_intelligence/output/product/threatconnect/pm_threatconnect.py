#
# Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import requests
import datetime
from tcex import TcEx
from six.moves import configparser
from .pm_intel_processor import IntelligenceProcessor

from phishme_intelligence.output.base_integration import BaseIntegration


class PmThreatConnect(BaseIntegration):
    def __init__(self, config, product):
        """
        Initialize PmThreatConnect object

        :param config: Integration configuration values
        :type config: :class:`configparser.ConfigParser`
        :param logger: Logging mechanism for the integration
        :type logger: :class:`logging.Logger`
        """

        super(PmThreatConnect, self).__init__(config=config, product=product)

        # Set up ThreatConnect
        api_default_org = config.get('integration_threatconnect', 'api_default_org')
        api_base_url = config.get('integration_threatconnect', 'api_base_url')

        self.phishme_intel_auth = (config.get('pm_api', 'user'), config.get('pm_api', 'pass'))
        self.phishme_intel_proxy = self._set_phishme_intel_proxy(config)
        self.owner = api_default_org
        self.tcex = TcEx()
        self.pm_intel_processor = IntelligenceProcessor(self.owner, self.logger, self.tcex)
        self.source = 'Cofense Intelligence'
        self.max_threat_label_length = 90
        self.tc_group = config.get('integration_threatconnect', 'threatconnect_group')

    def _set_phishme_intel_proxy(self, config):
        """
        Setting PhishMe intel proxy values (that are used for getting the HTML Active Threat Report)

        :param config: The config values from the config.ini file
        :type: :class:`configparser.ConfigParser`
        :return: proxies dictionary (can be empty)
        :rtype: dict
        """
        # Configure proxy support if required.
        if config.getboolean('local_proxy', 'use') is True:
            proxy_url_http = config.get('local_proxy', 'http')
            proxy_url_https = config.get('local_proxy', 'https')

            # BASIC authentication.
            if config.getboolean('local_proxy', 'auth_basic_use'):
                proxy_basic_user = config.get('local_proxy', 'auth_basic_user')
                proxy_basic_pass = config.get('local_proxy', 'auth_basic_pass')

                proxy_basic_auth = proxy_basic_user + ':' + proxy_basic_pass + '@'

                index_http = proxy_url_http.find('//') + 2
                index_https = proxy_url_https.find('//') + 2

                proxy_url_http = proxy_url_http[:index_http] + proxy_basic_auth + proxy_url_http[index_http:]
                proxy_url_https = proxy_url_https[:index_https] + proxy_basic_auth + proxy_url_https[index_https:]

            proxies = {'http': proxy_url_http, 'https': proxy_url_https}

        else:
            proxies = {}

        return proxies

    def process(self, mrti, threat_id):
        """
        Main method called to begin processing of PhishMe Intelligence into ThreatConnect

        :param mrti: PhishMe Intelligence threat to process
        :type mrti: :class:`phishme_intelligence.core.intelligence.Malware`
        :type mrti: :class:`phishme_intelligence.core.intelligence.Phish`
        :param int threat_id: Threat ID of PhishMe Intelligence threat being processed
        :return: None
        """
        self.logger.debug('calling process')
        try:
            self.logger.debug('Threat type: ' + mrti.json.get('threatType'))
            threat_type = mrti.json.get('threatType').lower()
            if threat_type == 'malware':
                self.logger.debug('processing malware: {}'.format(mrti.threat_id))
                self.logger.debug('processing the group')
                self._process_group(mrti)
                self.logger.debug('processing documents')
                self._process_document(mrti)
                self.logger.debug('processing blocksets')
                self._process_blockset(mrti)
                self.logger.debug('processing executable sets')
                self._process_executableset(mrti)
                self.logger.debug('processing malware families')
                self._process_malware_family(mrti)
            elif threat_type == 'phish':
                self.logger.debug('processing phish: {}'.format(mrti.threat_id))
                self._process_phish_group(mrti)
                self.logger.debug('processing phish ip')
                self._process_phish_ip_details(mrti)
                self.logger.debug('processing phish urls')
                self._process_phish_url(mrti.phish_url, mrti.threat_id, mrti.threathq_url, 'phish')

                if mrti.action_url_list and len(mrti.action_url_list) > 0:
                    for action_url in mrti.action_url_list:
                        self.logger.debug('ActionURL {}'.format(str(action_url.url)))
                        self.logger.debug('query {}'.format(action_url.query))
                        self.logger.debug('test: {0}://{1}{2}'.format(action_url.protocol,
                                                                   action_url.host,
                                                                   action_url.path,
                                                                   action_url.query))
                        self._process_phish_url(action_url, mrti.threat_id, mrti.threathq_url, 'action')
                        self._process_phish_domain(action_url, mrti.threat_id, mrti.threathq_url)
                if mrti.reported_url_list and len(mrti.reported_url_list) > 0:
                    for reported_url in mrti.reported_url_list:
                        self._process_phish_url(reported_url, mrti.threat_id, mrti.threathq_url, 'reported')
                        self._process_phish_domain(reported_url, mrti.threat_id, mrti.threathq_url)
                #if mrti.web_components and len(mrti.web_components) > 0:
                #    for url in mrti.web_component_url_list:
                #        self._process_phish_url(url, mrti.threat_id, mrti.threathq_url, 'component')
                #        self._process_phish_domain(url, mrti.threat_id, mrti.threathq_url)

        except Exception as e:
            self.logger.debug(e)
            raise e

    def post_run(self, config_file_location):
        """
        Method called after sync of Threat Intelligence. Kicks off batch processing of indicators into ThreatConnect
        and saves position value

        :param str config_file_location: location of config.ini file (we don't use this value)
        :return:  None
        """
        self.logger.debug('calling post_run')
        self._commit_threat_intelligence()
        self.logger.debug('New position is {}'.format(self.config.get('pm_api', 'position')))
        self.tcex.results_tc('param.intel_position', self.config.get('pm_api', 'position'))

    def _commit_threat_intelligence(self):
        """
        Helper method for logging and beginning batch procesing of indicators into ThreatConnect
        """
        self.logger.debug('committing threat intelligence')
        # Batch process indicators
        self.logger.info("Begin Batch Processing of Indicators and their Group Associations to ThreatConnect...")
        self.pm_intel_processor.commit()
        self.logger.info("Indicators Successfully Processed!")

    # BEGIN PHISH

    def _process_phish_group(self, intel):
        """
        Generate Group that will correspond to a phishing campaign from Cofense Brand Intelligence

        :param intel: Machine readable threat intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Phish`
        """
        self.logger.debug('_process_phish_group called')

        # Make sure the name is less than the max length and make sure the id is
        # shown at the end of the group name
        id_label = '({})'.format(intel.threat_id)

        self.logger.debug('id_label is {}'.format(id_label))

        self.logger.debug('title is {}'.format(intel.title))
        if intel.title:
            group_name = intel.title[:self.max_threat_label_length - len(id_label)] + id_label
        else:
            group_name = intel.brand[:self.max_threat_label_length - len(id_label)] + id_label

        self.logger.debug('group_name is {}'.format(group_name))

        self.pm_intel_processor.add_group(group_type=self.tc_group, group_name=group_name,
                                          published_date=intel.first_published, threat_id=intel.threat_id)

        self.logger.debug('threathq_url is {}'.format(intel.threathq_url))
        self.logger.debug('Screenshot URL is {}'.format(intel.screenshot_url))
        self.logger.debug('Source is {}'.format(self.source))

        self.pm_intel_processor.add_group_attribute('Title', group_name)

        if intel.brand:
            self.pm_intel_processor.add_group_attribute('Description',
                                                        'Credential phish targeting brand{0} {1}'
                                                        .format('s' if len(intel.brand.split(',')) > 1 else ''
                                                                , intel.brand))

        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context', intel.threathq_url)
        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context', intel.screenshot_url)
        self.pm_intel_processor.add_group_attribute('Source', '{0} via Threat ID {1}'.format(self.source,
                                                                                            intel.threat_id))
        self.pm_intel_processor.group_ready()

    def _process_phish_ip_details(self, intel):
        """
        :param intel: Machine readable threat intelligence
        :type intel: :class:`phishme_intelligence.core.intelligence.Phish`
        """
        if not intel.ip:
            return

        self.logger.debug('processing ip: {}'.format(intel.ip.ip))

        infrastructure_details = []

        if intel.ip.asn:
            infrastructure_details.append('AS Number: {0}'.format(intel.ip.asn))
        if intel.ip.asn_organization:
            infrastructure_details.append('AS Organization: {0}'.format(intel.ip.asn_organization))
        if intel.ip.continent_code:
            infrastructure_details.append('Continent Code: {0}'.format(intel.ip.continent_code))
        if intel.ip.continent_name:
            infrastructure_details.append('Continent Name: {0}'.format(intel.ip.continent_name))
        if intel.ip.country_iso_code:
            infrastructure_details.append('Country Iso Code: {0}'.format(intel.ip.country_iso_code))
        if intel.ip.country_name:
            infrastructure_details.append('Country Name: {0}'.format(intel.ip.country_name))
        if intel.ip.isp:
            infrastructure_details.append('ISP: {0}'.format(intel.ip.isp))
        if intel.ip.latitude:
            infrastructure_details.append('Latitude: {0}'.format(intel.ip.latitude))
        if intel.ip.longitude:
            infrastructure_details.append('Longitude: {0}'.format(intel.ip.longitude))
        if intel.ip.metro_code:
            infrastructure_details.append('Metro Code: {0}'.format(intel.ip.metro_code))
        if intel.ip.organization:
            infrastructure_details.append('Organization: {0}'.format(intel.ip.organization))
        if intel.ip.postal_code:
            infrastructure_details.append('Postal Code: {0}'.format(intel.ip.postal_code))
        if intel.ip.subdivision_name:
            infrastructure_details.append('Subdivision Name: {0}'.format(intel.ip.subdivision_name))
        if intel.ip.subdivision_iso_code:
            infrastructure_details.append('Subdivision Iso Code: {0}'.format(intel.ip.subdivision_iso_code))
        if intel.ip.time_zone:
            infrastructure_details.append('Time zone: {0}'.format(intel.ip.time_zone))

        self.pm_intel_processor.add_ip_indicator(intel.ip.ip)
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                                        'ThreatHQ URL: ' + intel.threathq_url)
        self.pm_intel_processor.add_indicator_attribute('Source', '{0} via Threat ID {1}'.format(self.source,
                                                                                                intel.threat_id))

        for detail in infrastructure_details:
            self.pm_intel_processor.add_indicator_attribute('Infrastructure Ownership', detail)

        self.pm_intel_processor.add_indicator_tag(self.source)
        self.pm_intel_processor.add_indicator_rating(self._get_rating('None'))

        self.logger.debug('calling indicator_ready on {}'.format(intel.ip.ip))
        self.pm_intel_processor.indicator_ready(self.source, intel.threat_id)

    def _process_phish_url(self, incoming_url, threat_id, threathq_url, url_type):
        if isinstance(incoming_url, str):
            url = incoming_url
            severity = 'None'
        else:
            # Get the severity or default to none
            if incoming_url.json.get('urlSeverity'):
                severity = incoming_url.json.get('urlSeverity')
            else:
                severity = 'None'
            url = incoming_url.url

        # Sometimes we might get one that ends with a ? or a .
        # If so just cut that off
        if url.endswith('?') or url.endswith('.'):
            url = url[:-1]

        self.logger.debug('Processing url {}'.format(url))

        self.pm_intel_processor.add_url_indicator(self.tcex.s(url, errors='ignore'))

        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context', threathq_url)
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                                        'URL Type: {}'.format(url_type))

        self.pm_intel_processor.add_indicator_attribute('Source', '{0} via Threat ID {1}'.format(self.source,
                                                                                                threat_id))

        self.pm_intel_processor.add_indicator_tag(self.source)
        self.pm_intel_processor.add_indicator_rating(self._get_rating(severity))

        self.logger.debug('calling indicator_ready on {}'.format(url))
        self.pm_intel_processor.indicator_ready(self.source, threat_id)

    def _process_phish_domain(self, domain, threat_id, threathq_url):
        if not domain.domain:
            return
        self.logger.debug('processing domain {}'.format(domain.domain))
        # Get the severity or default to none
        if domain.json.get('domainSeverity'):
            severity = domain.json.get('domainSeverity')
        else:
            severity = 'None'

        self.pm_intel_processor.add_host_indicator(domain.domain)

        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context', threathq_url)

        self.pm_intel_processor.add_indicator_attribute('Source', '{0} via Threat ID {1}'.format(self.source,
                                                                                                threat_id))

        self.pm_intel_processor.add_indicator_tag(self.source)
        self.pm_intel_processor.add_indicator_rating(self._get_rating(severity))

        self.logger.debug('calling indicator_ready on {}'.format(domain.domain))
        self.pm_intel_processor.indicator_ready(self.source, threat_id)

    # END PHISH

    # BEGIN MALWARE

    def _set_blockset_indicator_value(self, block_set):
        """
        Set Indicator value based on type of BlockSet indicator

        :param block_set: BlockSet value
        :rtype block_set: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """
        if block_set.block_type == "Domain Name":
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                self.pm_intel_processor.add_host_indicator(block_set.watchlist_ioc[:-1])
            else:
                self.pm_intel_processor.add_host_indicator(block_set.watchlist_ioc)
        elif block_set.block_type == "IPv4 Address":
            self.pm_intel_processor.add_ip_indicator(block_set.watchlist_ioc)
        elif block_set.block_type == "URL":
            url = block_set.watchlist_ioc.replace("[.]", ".")
            if block_set.watchlist_ioc.endswith('?') or block_set.watchlist_ioc.endswith('.'):
                self.pm_intel_processor.add_url_indicator(self.tcex.s(url[:-1], errors='ignore'))
            else:
                self.pm_intel_processor.add_url_indicator(self.tcex.s(url, errors='ignore'))

        elif block_set.block_type == "Email":
            self.pm_intel_processor.add_email_indicator(block_set.watchlist_ioc)

    def _set_standard_indicator_attributes(self, intel):
        """
        Set attributes to indicators that are shared between Executable Set and Block Set types

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                              'Active Threat Report URL: ' + intel.active_threat_report)
        self.pm_intel_processor.add_indicator_attribute('Additional Analysis and Context',
                                              'Threat Detail Page URL: ' + intel.threathq_url)
        self.pm_intel_processor.add_indicator_attribute('Source', self.source + ' via Threat ID ' + str(intel.threat_id))
        self.pm_intel_processor.add_indicator_tag(self.source)

    def _set_blockset_attributes(self, intel, block_set):
        """
        Set attributes that are specific to Block Set indicators in ThreatConnect

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        :param block_set: specific BlockSet value to process
        :type block_set: :class:`phishme_intelligence.core.intelligence.Malware.BlockSet`
        """
        if block_set.malware_family_description is not None and block_set.malware_family is not None:
            self.pm_intel_processor.add_indicator_attribute("Description",
                                                            block_set.malware_family + ": " +
                                                            block_set.malware_family_description + ' (Threat ID ' +
                                                            str(intel.threat_id) + ')')

        self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", block_set.role + ': '
                                                        + block_set.role_description + ' (Threat ID ' +
                                                        str(intel.threat_id) + ')')

    def _set_executableset_attributes(self, executable_set, intel):
        """
        Set attributes specific to Executable Set PhishMe Intelligence value

        :param executable_set: The Executable Set value being processed
        :type executable_set: :class:`phishme_intelligence.core.intelligence.Malware.ExecutableSet`
        :param intel: Campaign intelligence data (full set)
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        self.pm_intel_processor.add_indicator_attribute("Description", executable_set.malware_family_description +
                                                        '( Threat ID ' + str(intel.threat_id) + ')')
        if executable_set.subtype is None:
            self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", executable_set.type +
                                                            '( Threat ID ' + str(intel.threat_id) + ')')
        else:
            self.pm_intel_processor.add_indicator_attribute("Additional Analysis and Context", executable_set.type +
                                                            ': ' + executable_set.subtype + '( Threat ID ' +
                                                            str(intel.threat_id) + ')')

    def _process_group(self, intel):
        """
        Generate Group that will correspond to campaign being processed from PhishMe Intelligence

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        self.logger.info('calling _process_group')

        self.logger.debug('setting the label')
        # Need to make sure Threat name is less than 100 characters...
        if len(intel.label) > self.max_threat_label_length:
            self.logger.info("Threat label longer than 90 characters so removing malware families from Threat name...")
            group_label_first_part = intel.label.split(" - ")[0]
            group_name = group_label_first_part + " - Multiple malware families (" + str(intel.threat_id) + ")"
        else:
            group_name = intel.label + " (" + str(intel.threat_id) + ")"

        self.logger.debug('adding the group')

        self.pm_intel_processor.add_group(group_type=self.tc_group, group_name=group_name,
                                          published_date=intel.first_published, threat_id=intel.threat_id)

        self.logger.debug('setting the description')
        if intel.executiveSummary is not None:
            self.pm_intel_processor.add_group_attribute('Description', self.tcex.s(intel.executiveSummary,
                                                                                   errors='ignore'))
        self.logger.debug('adding ATR URL')
        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context',
                                                    'Active Threat Report URL: ' + intel.active_threat_report)
        self.logger.debug('adding threat detail URL')
        self.pm_intel_processor.add_group_attribute('Additional Analysis and Context',
                                                    'Threat Detail Page URL: ' + intel.threathq_url)

        self.logger.debug('adding source')
        self.pm_intel_processor.add_group_attribute('Source', self.source + ' via Threat ID ' + str(intel.threat_id))

        self.logger.debug('adding tag')
        self.pm_intel_processor.add_group_tag(self.source)

        self.logger.debug('calling group_ready')
        self.pm_intel_processor.group_ready()

    def _process_executableset(self, intel):
        """
        Processing ExecutableSet values of current campaign being processed. These values are hashes of files
        observed on endpoints as a result of interacting with a phishing email

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        for executable_set in intel.executable_set:
            self.pm_intel_processor.add_file_indicator(executable_set.md5, executable_set.sha1, executable_set.sha256)
            self._set_executableset_attributes(executable_set, intel)
            self._set_standard_indicator_attributes(intel)

            self.pm_intel_processor.indicator_ready(self.source, intel.threat_id)
            self.logger.debug("Indicator " + executable_set.md5 + " Added to Processing List!")

    def _process_blockset(self, intel): 
        """
        Processing PhishMe Intelligence Block Set values related to current Threat being processed. These are network
        watch list items related to a particular threat ID

        :param intel: Campaign intelligence to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        for block_set in intel.block_set:
            self._set_blockset_indicator_value(block_set)
            self._set_blockset_attributes(intel, block_set)
            self._set_standard_indicator_attributes(intel)

            self.pm_intel_processor.add_indicator_rating(self._get_rating(block_set.impact))

            self.pm_intel_processor.indicator_ready(self.source, intel.threat_id)
            self.logger.debug("Indicator " + block_set.watchlist_ioc + " Added to Processing List!")

    def _process_document(self, intel):
        """
        Process Active Threat Report as ThreatConnect Document

        :param intel: PhishMe Intelligence campaign to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        """
        document_name = "Active Threat Report for Threat ID " + str(intel.threat_id)
        file_name = "Cofense_Intelligence_ATR_" + str(intel.threat_id) + ".html"

        if not intel.json['hasReport']:
            self.logger.info(
                "Threat with Threat ID " + str(intel.threat_id) + " does not have Active Threat Report so not "
                                                                  "creating document...")
            return
        else:
            try:
                report = requests.get(intel.active_threat_report_api, auth=self.phishme_intel_auth,
                                      proxies=self.phishme_intel_proxy)
            except Exception as e:
                self.logger.error("Unable to download Active Threat Report " + intel.active_threat_report +
                                  "! Skipping creation of Document...")
                return

            self.pm_intel_processor.add_document(document_name=document_name, file_name=file_name,
                                                 active_threat_report = report.content, group_type=self.tc_group, threat_id=intel.threat_id)
            self.pm_intel_processor.add_document_attribute('Source', self.source + ' via Threat ID '
                                                           + str(intel.threat_id))
            self.pm_intel_processor.add_document_tag(self.source)

            self.pm_intel_processor.document_ready()

    def _process_malware_family(self, intel):
        '''
        Adds malware family as a group 
        :param intel: PhishMe Intelligence campaign to process
        :type intel: :class:`phishme_intelligence.core.intelligence.Malware`
        '''
        if not intel.json.get('malwareFamilySet'):
            return
        
        for malware_family in intel.json.get('malwareFamilySet'):
            self.pm_intel_processor.add_malware_family(malware_family.get('familyName'), malware_family.get('description'))

    # END MALWARE

    # BEGIN UTILS

    @staticmethod
    def _get_rating(impact):
        """
        Return ThreatConnect rating that will correspond to our Impact scores (which are from the STIX standard)

        :param str impact: Impact value of BlockSet item
        :return: impact rating to set
        :rtype: int
        """
        if impact == "Minor":
            return 1
        elif impact == "Moderate":
            return 3
        elif impact == "Major":
            return 5

        return 0

    # END UTILS



