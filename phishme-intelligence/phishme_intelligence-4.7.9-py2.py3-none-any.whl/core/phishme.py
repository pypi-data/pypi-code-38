# Copyright 2013-2016 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import argparse
import importlib
import json
import logging
import os
import random
import re
import six
import sys
import time
import traceback
from calendar import timegm
from datetime import datetime

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser

from . import config_check
from . import rest_api
from . import supported_integrations
from . import intelligence
from . import brand_intelligence

from phishme_intelligence import PmNotImplemented, PmSyncError, PmSearchTermError

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


__all__ = ['PhishMeIntelligence', 'read_args', 'read_config']


class PhishMeBase(object):
    """
    Contains helper methods for interacting with PhishMe Intelligence RESTful API, handling lock file to prevent concurrent execution, reading command line arguments, and reading a ConfigParser config file.

    """

    def __init__(self, config, config_file_location):
        """
        Initialize a PhishMe Intelligence object.

        :param ConfigParser config: ConfigParser object
        :param str config_file_location: Path to the config file location represented by :ref:`config`.
        """
        self.config = config
        self.config_file_location = config_file_location
        self.logger = logging.getLogger(__name__)

        # This dict holds instances of the integrations activated by this script.
        self.activated_integration_classes = {}
        self.activated_integrations = None
        self.imported_modules = {}

        self.updated_threat_intel = False

        # If jitter should be used AND an offset hasn't been generated, then generate.
        if self.config.getboolean('pm_jitter', 'use'):
            try:
                self.config.getint('pm_jitter', 'scheduler_offset')
            except ValueError as exception:
                self._generate_scheduler_offset()

        self.init_time_milliseconds = int(time.time())*1000
        self.position_original = self.config.get('pm_api', 'position')

        # Used to reduce the number of times a Threat ID is written to logs while processing CEF data.
        self.temp_cef_threat_id = 0

    def sync(self):
        """
        This will contact the PhishMe Intelligence API, retrieve any new or modified threat intelligence since the last successful check-in, process it into the output(s) designated by *config.ini*, and return.

        This method will update the *position* value in the [pm_api] section of the *config.ini* during each successful poll and subsequent processing of the returned threat intelligence. Any failure to process threat intelligence will cause the position value to not be updated. Subsequent executions will resume from the last successful execution, as controlled by the position value in *config.ini*.::

           [pm_api]
           base_url = https://www.threathq.com/apiv1
           user =
           pass =
           ssl_verify = True
           init_date = 2017-05-15
           position = 9d801cc1-d3ec-432b-a436-3eee186b1fff
           results_per_page = 100
           max_retries = 3
           expired_threat_days = 90

        :return: None
        """

        raise PmNotImplemented

    def search(self, product, description, action_domain=None, action_url_search=None, all_md5=None, begin_timestamp=None, brand=None,
               domain=None, drop_mail=None, end_timestamp=None, extracted_string=None, file=None, has_kit=None,
               ip=None, kit_file=None, kit_md5=None, language=None, malware_artifact_md5=None, malware_domain=None,
               malware_family=None, malware_file=None, malware_sender_ip=None, malware_sender_name=None,
               malware_subject=None, malware_watchlist_domain=None, malware_watchlist_ip=None,
               malware_watchlist_url_search=None, phishing_asn=None, phishing_asn_country_code=None,
               phishing_asn_organization=None, phishing_title=None, reported_domain=None, reported_url_search=None,
               threat_domain=None, threat_id=None, threat_ip=None, threat_type='all', threat_url_search=None,
               url_search=None, web_component_file=None, web_component_md5=None):
        """
        Use this method to search PhishMe Intelligence for one or more IOCs.

        :param product: The name of the product that PhishMe Intelligence will be sent to.
        :param description: A short description of the use case for this call.
        :param action_domain: (optional) List or string. The domain name associated with an action url of a phishing campaign.
        :param action_url_search: (optional) List or string. A specific url to search for, this supports exact matching if the url is enclosed in double quotes and partial matching otherwise.
        :param all_md5: (optional) List or string. Search for threats associated with the provided md5.
        :param int begin_timestamp: (optional) The seconds since epoch from which we should start returning data.
        :param brand: (optional) List or string. Search for brands associated with a threat. This search criteria must match the exact brand name used to categorize a threat within PhishMe.
        :param domain: (optional) List or string. The domain name associated with a phishing or malware campaign.
        :param str drop_mail: Search drop mail addresses associated with threats.
        :param int end_timestamp: (optional) The seconds since epoch from which we should end returning data.
        :param extracted_string: (optional) Search for extracted strings discovered within malware campaigns.
        :param file: (optional) List or string. The filename associated with a phishing or malware campaign.
        :param bool has_kit: (optional) Search for threats which have an associated kit.
        :param ip: (optional) List or string. The IP address associated with a phishing or malware campaign.
        :param kit_file: (optional) List or string. The filename associated with a phishing or malware campaign.
        :param kit_md5: (optional) List or string. Search for threats associated with the provided kit md5.
        :param language: (optional) List or string. The detected language of a phishing web page.
        :param malware_artifact_md5: (optional) List or string. Search for threats associated with the provided malware artifact md5.
        :param malware_domain: (optional) List or string. The domain name associated with a malware campaign.
        :param str malware_family: The malware family associated with a malware campaign.
        :param malware_file: (optional) List or string. The filename associated with a phishing or malware campaign.
        :param malware_sender_ip: (optional) List or string. The IP address of the sender of a malware campaign.
        :param str malware_sender_name: Search for the sender name of malware campaigns.
        :param str malware_subject: Search the message subject associated with malware campaigns.
        :param malware_watchlist_domain: (optional) List or string. The domain name of a watch list item associated with a malware campaign.
        :param malware_watchlist_ip: (optional) List or string. The IP address of a watch list item associated with a malware campaign.
        :param malware_watchlist_url_search: (optional) List or string. A specific url to search for, this supports exact matching if the url is enclosed in double quotes and partial matching otherwise.
        :param str phishing_asn: Search the ASN associated with a phishing threat.
        :param str phishing_asn_country_code: Search the country code associated with phishing threats.
        :param str phishing_asn_organization: Search the ASN organization associated with phishing threats.
        :param phishing_title: (optional) List or string. The title text of a phishing web page.
        :param reported_domain: (optional) List or string. The domain name associated with a reported url of a phishing threat.
        :param reported_url_search: (optional) List or string. A specific url to search for, this supports exact matching if the url is enclosed in double quotes and partial matching otherwise.
        :param threat_domain: (optional) List or string. The domain name associated with a phishing threat.
        :param threat_id: (optional) List or string. The unique identifier for a threat, the format of this value is a prefix of either a "p\_" for phish (PhishMe Brand Intelligence) or "m\_" for malware (PhishMe Intelligence) followed by the threatNativeId value.
        :param threat_ip: (optional) List or string. The IP address of the phishing threat.
        :param str threat_type: Choose whether to search for phishing attacks, malware campaigns, or both. If omitted, the default value is 'all'. Possible values are ['all', 'malware', 'phish'].
        :param threat_url_search: (optional) List or string. A specific url to search for, this supports exact matching if the url is enclosed in double quotes and partial matching otherwise.
        :param url_search: (optional) List or string. A specific url to search for, this supports exact matching if the url is enclosed in double quotes and partial matching otherwise.
        :param web_component_file: (optional) List or string. The filename associated with a phishing or malware campaign.
        :param web_component_md5: (optional) List or string. Search for threats associated with the provided web component md5.

        :return:
        """

        raise PmNotImplemented

    def test_connection(self):
        """
        This method will attempt to test the connection to the PhishMe Intelligence API by contacting the /feed/ endpoint.

        :return: An integer HTTP Status Code will be returned according to https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html.
        :rtype: int
        """

        raise PmNotImplemented

    def _run_integration(self):
        """
        This method manages all the retrieval and processing of threat intelligence from PhishMe's API.

        :return: None
        """

        # Do any required setup before contacting PhishMe's API.
        self._pre_run()

        # If there's no position marker, need to perform a backfill process. This will only happen if an integration is new or has been reset.
        end_timestamp = 0
        if not self.config.get('pm_api', 'position'):

            # Get time window parameters for backfill period.
            begin_timestamp, end_timestamp = self._date_to_epoch()

            # Retrieve older PhishMe threat intelligence for backfill phase using a Generator.
            for mrti, mrti_format in self._integration_backfill():
                self._process_threat(mrti=mrti, mrti_format=mrti_format, sync_phase='backfill')

        # Retrieve new/updated PhishMe threat intelligence for synchronization using a Generator.
        for list_to_retrieve in self._integration_updates(end_timestamp=end_timestamp):

            # Get the mrti in the correct format.
            for mrti, mrti_format in self._retrieve_threat(list_to_retrieve=list_to_retrieve):
                self._process_threat(mrti=mrti, mrti_format=mrti_format, sync_phase='updates')

        # If any post-processing needs to be done, this is where it is hooked.
        if self.updated_threat_intel:
            self._post_run()

        else:
            self.logger.info('No new threat intelligence processed.')

    def _pre_run(self):
        """
        Creates a class instance of any activated integration and executes `__init__` method.

        :return: None
        """

        # Loop through each integration that is active during this execution.
        for item in self.activated_integrations:

            # Get the Class name of the object to be instantiated.
            method_to_call = getattr(self.imported_modules[item.config_name], item.class_name)

            # Construct the Class. Any set-up needed is called from the __init__ method of the Class.
            class_instance = method_to_call(config=self.config, product=item.config_name)

            # Add this class instance to a dict so we can call methods on it later.
            self.activated_integration_classes[item.config_name] = class_instance

    def _process_threat(self, mrti, mrti_format, sync_phase):
        """
        Determines how the incoming threat intelligence should be processed, according to product and format.

        :param mrti: The machine readable threat intelligence, already formatted. One of [:class:`core.intelligence.Malware', :class:`core.intelligence.Phish', CEF, or STIX v1]
        :param str mrti_format: The data format of the mrti object. One of [cef, json, stix].
        :param str sync_phase: Phase of PhishMe Intelligence sync
        :return: None
        """

        # Record that new threat intelligence was processed.
        self.updated_threat_intel = True

        # Determine the Product and Threat ID being processed.
        product, threat_id, expired_threat = self._preprocess_threat(mrti, mrti_format)

        if sync_phase == 'backfill' or (sync_phase == 'updates' and not expired_threat):
            if mrti_format == 'json' and product == 'Intelligence':
                self._process_json_intelligence(mrti, threat_id)
            elif mrti_format == 'json' and product == 'Brand Intelligence':
                self._process_json_brand_intelligence(mrti, threat_id)
            elif mrti_format == 'stix':
                self._process_stix(mrti, threat_id)
            elif mrti_format == 'cef':
                self._process_cef(mrti, threat_id)

        else:
            self.logger.info('Skipping PhishMe ' + product + ' Threat ID ' + str(threat_id) + ' in ' + mrti_format.upper() + ' due to being originally published over ' + self.config.get('pm_api', 'expired_threat_days') + ' days ago.')

    def _process_cef(self, threat, threat_id):
        """
        Executes the `process` method of any activated integration expecting CEF.

        :param str threat: A CEF formatted message, representing a single IOC.
        :param int threat_id: The Threat ID.
        :return: None
        """

        if self.activated_integrations:
            # Loop through each integration that is active during this execution.
            for item in self.activated_integrations:

                # Only proceed if the integration uses JSON mrti.
                if item.mrti_format == 'cef':

                    # Get the object instance.
                    class_instance = self.activated_integration_classes[item.config_name]

                    # Call the process method on the instance.
                    class_instance.process(mrti=threat, threat_id=threat_id)

        else:
            self.process(threat, threat_id)

    def _process_stix(self, threat, threat_id):
        """
        Executes the `process` method of any activated integration expecting  STIX.

        :param str threat: A STIX formatted message, representing a single Threat ID.
        :param int threat_id: The Threat ID.
        :return: None
        """

        # Loop through each integration that is active during this execution.
        if self.activated_integrations:
            for item in self.activated_integrations:

                # Only proceed if the integration uses JSON mrti.
                if item.mrti_format == 'stix':

                    # Get the object instance.
                    class_instance = self.activated_integration_classes[item.config_name]

                    # Call the process method on the instance.
                    class_instance.process(mrti=threat, threat_id=threat_id)

        else:
            self.process(threat, threat_id)

    def _process_json_intelligence(self, threat, threat_id):
        """
        Executes the `process` method of any activated integration expecting JSON-formatted PhishMe Intelligence.

        :param json threat: A JSON formatted message, representing a single Threat ID.
        :param int threat_id:  The Threat ID.
        :return: None
        """

        # Create Intelligence object.
        intel = intelligence.Malware(threat, config=self.config)

        if self.activated_integrations:
            # Loop through each integration that is active during this execution.
            for item in self.activated_integrations:

                # Only proceed if the integration uses JSON mrti.
                if item.mrti_format == 'json':

                    # Get the object instance.
                    class_instance = self.activated_integration_classes[item.config_name]

                    # Call the process method on the instance.
                    class_instance.process(mrti=intel, threat_id=threat_id)

        else:
            self.process(intel, threat_id)

    def _process_json_brand_intelligence(self, threat, threat_id):
        """
        Executes the `process` method of any activated integration expecting JSON-formatted PhishMe Brand Intelligence.

        :param json threat: A JSON formatted message, representing a single Threat ID.
        :param int threat_id: The Threat ID.
        :return: None
        """

        # Create Brand Intelligence object.
        intel = brand_intelligence.Phish(threat)

        if self.activated_integrations:
            # Loop through each integration that is active during this execution.
            for item in self.activated_integrations:

                # Only proceed if the integration uses JSON mrti.
                if item.mrti_format == 'json':

                    # Get the object instance.
                    class_instance = self.activated_integration_classes[item.config_name]

                    # Call the process method on the instance.
                    class_instance.process(mrti=intel, threat_id=threat_id)

        else:
            self.process(intel, threat_id)

    def _post_run(self):
        """
        Executes the `post_run` method of any activated integration.

        :return: None
        """

        # Loop through each integration that is active during this execution.
        for item in self.activated_integrations:

            # Get the object instance.
            class_instance = self.activated_integration_classes[item.config_name]

            # Call the process method on the instance.
            class_instance.post_run(config_file_location=self.config_file_location)

    class _PhishMeConnectionType(object):
        """
        TODO: Not sure why we have this, Kevin?
        """

        THREAT_SEARCH = 1
        THREAT_UPDATES = 2
        T3_CEF = 3
        T3_STIX = 4
        FEED = 5

    def _select_mrti_formats(self):
        """
        TODO: Not sure why we have this, Josh?

        :return:
        """
        # TODO Remove this method.

        mrti_types = {
            'CEF': self.config.getboolean('pm_format', 'cef'),
            'JSON': self.config.getboolean('pm_format', 'json'),
            'STIX': self.config.getboolean('pm_format', 'stix')
        }

        return mrti_types

    def _integration_backfill(self):
        """
        Initializes an integration with a backfill according to the *init_date* from [pm_api] in *config.ini*. It's only meant to be run once, after that, new data is pulled from /threat/updates stream. To cause this method to execute again, simply clear the *position* value.::

           [pm_api]
           base_url = https://www.threathq.com/apiv1
           user =
           pass =
           ssl_verify = True
           init_date = 2017-05-15
           position = 9d801cc1-d3ec-432b-a436-3eee186b1fff
           results_per_page = 100
           max_retries = 3
           expired_threat_days = 90

        :return: An string representing mrti in one of the below formats. Returned via yield statement.
        :rtype: str
        :return: The format of the mrti. One of [cef, json, stix]. Returned via yield statement.
        :rtype: str
        """

        # This should only trigger when initializing an integration.
        self.logger.info('Initializing integration from ' + self.config.get('pm_api', 'init_date') + ' to now().')

        # Setting time window to cover full retention period of data.
        begin_timestamp, end_timestamp = self._date_to_epoch()

        if self.config.getboolean('pm_format', 'cef'):
            temp_begin_timestamp = begin_timestamp
            while temp_begin_timestamp < end_timestamp:

                # Chunks a long time window into 24 hour periods
                if(end_timestamp - temp_begin_timestamp) > 86400:
                    temp_end_timestamp = temp_begin_timestamp + 86400

                else:
                    temp_end_timestamp = end_timestamp

                payload = {
                    'beginTimestamp': temp_begin_timestamp,
                    'endTimestamp': temp_end_timestamp
                }
                cef_messages = self._retrieve_from_t3_cef(payload=payload)
                for index, cef_message in enumerate(cef_messages.splitlines()):
                    product = cef_message.split('|')[2].lower()
                    if product == 'intelligence' and self.config.getboolean('pm_product', 'intelligence'):
                        yield cef_message, 'cef'
                    elif product == 'brand intelligence' and self.config.getboolean('pm_product', 'brand_intelligence'):
                        yield cef_message, 'cef'

                # Increment the time window by 1 day for the next iteration.
                temp_begin_timestamp += 86400

        # Since STIX packages must be pulled one at a time, we have to start with JSON for both of them.
        if self.config.getboolean('pm_format', 'json') or self.config.getboolean('pm_format', 'stix'):

            # Set the threat_type to backfill.
            if self.config.getboolean('pm_product', 'intelligence') and self.config.getboolean('pm_product', 'brand_intelligence'):
                threat_type = 'all'
            elif self.config.getboolean('pm_product', 'intelligence'):
                threat_type = 'malware'
            elif self.config.getboolean('pm_product', 'brand_intelligence'):
                threat_type = 'phish'
            else:
                pass

            # Get backfill of data from PhishMe by using /threat/search. This will almost certainly involve multiple loops.
            cur_page_number = 0
            total_pages = 1
            while cur_page_number < total_pages:

                payload = {
                    'threatType': threat_type,
                    'beginTimestamp': begin_timestamp,
                    'endTimestamp': end_timestamp,
                    'resultsPerPage': self.config.get('pm_api', 'results_per_page'),
                    'page': cur_page_number
                }

                total_pages, threats = self._retrieve_from_threat_search(payload=payload)

                if self.config.getboolean('pm_format', 'json'):
                    # yield threats
                    for threat in threats:
                        yield threat, 'json'

                if self.config.getboolean('pm_format', 'stix'):
                    for threat in threats:
                        stix = self._retrieve_from_t3_stix(threat_type=threat.get('threatType').lower(), threat_id=str(threat.get('id')))
                        yield stix, 'stix'

                # Increment current page counter
                cur_page_number += 1

    def _integration_updates(self, end_timestamp):
        """
        Performs an update from the last successful communication with the PhishMe Intelligence API, using the *position* value as a starting point.
        This method will loop continue until less than 1000 entries are returned from the */threat/updates* endpoint.

           [pm_api]
           base_url = https://www.threathq.com/apiv1
           user =
           pass =
           ssl_verify = True
           init_date = 2017-05-15
           position = 9d801cc1-d3ec-432b-a436-3eee186b1fff
           results_per_page = 100
           max_retries = 3
           expired_threat_days = 90

        :param int end_timestamp: An epoch timestamp if the :func:`core.phishme.PhishMeIntelligence._integration_backfill` method was executed just prior to this call. Otherwise this value is 0.
        :return: A list of new or modified Threat IDs to be retrieved and processed.
        :rtype: list
        """

        # Set initial changelog_size to 1000, then continue requesting more data until less than 1000 Threat IDs received.
        changelog_size = 1000
        while changelog_size == 1000:

            # Request data from PhishMe's /threat/updates for new Threat IDs since last check.
            position_next, changelog_size, changelog = self._retrieve_from_threat_updates(end_timestamp=end_timestamp)

            self.logger.info('Retrieved ' + str(changelog_size) + ' updates.')

            # Lists to separate Threat IDs that are new/modified vs those that have been unpublished.
            list_to_retrieve = []
            # list_to_remove = []

            # Iterate through the changelog and categorize Threat IDs.
            for update in changelog:
                deleted = update.get('deleted')

                # These are new or modified items
                if not deleted:
                    list_to_retrieve.append(update)

            yield list_to_retrieve

            # Place new checkpoint in config file.
            self.config.set('pm_api', 'position', position_next)
            with open(self.config_file_location, 'w') as configfile:
                self.config.write(configfile)

    def _retrieve_threat(self, list_to_retrieve):
        """
        Retrieve a series of Threat IDs from /threat/search endpoint. The function will handle either intelligence product, with any data format.
        It will retrieve up to the number of records specified in *config.ini* by the *results_per_page* variable.

        :param list list_to_retrieve: A list of Threat IDs.
        :return: Yields a tuple of a single cef, json, or STIX message, along with the corresponding str: one of [cef, json, stix]
        :rtype: str, str
        """

        # Verify data should be processed.
        process_intelligence = self.config.getboolean('pm_product', 'intelligence')
        process_brand_intelligence = self.config.getboolean('pm_product', 'brand_intelligence')

        # Don't bother going further if neither of these formats will be retrieved.
        if self.config.getboolean('pm_format', 'cef') or self.config.getboolean('pm_format', 'stix'):

            # Cycling through these one at a time is ok because they can only be retrieved one at a time.
            for item in list_to_retrieve:

                if self.config.getboolean('pm_format', 'cef'):
                    # for item in list_to_retrieve:
                    if process_intelligence and item.get('threatType') == 'malware':
                        cef = self._retrieve_from_t3_cef(threat_type=item.get('threatType'), threat_id=str(item.get('threatId')))
                        for cef_single in cef.splitlines():
                            yield cef_single, 'cef'
                    elif process_brand_intelligence and item.get('threatType') == 'phish':
                        cef = self._retrieve_from_t3_cef(threat_type=item.get('threatType'), threat_id=str(item.get('threatId')))
                        for cef_single in cef.splitlines():
                            yield cef_single, 'cef'

                if self.config.getboolean('pm_format', 'stix'):
                    # for item in list_to_retrieve:
                        if process_intelligence and item.get('threatType') == 'malware':
                            stix = self._retrieve_from_t3_stix(threat_type=item.get('threatType'), threat_id=str(item.get('threatId')))
                            yield stix, 'stix'
                        elif process_brand_intelligence and item.get('threatType') == 'phish':
                            stix = self._retrieve_from_t3_stix(threat_type=item.get('threatType'), threat_id=str(item.get('threatId')))
                            yield stix, 'stix'

        # Need to decrement this list in chunks because multiple Threat IDs are retrieved in a single request.
        if self.config.getboolean('pm_format', 'json'):

            while list_to_retrieve:

                # Get the results_per_page number of Threat IDs at a time.
                results_per_page = self.config.getint('pm_api', 'results_per_page')
                payload = {'resultsPerPage': results_per_page}
                threat_list = []

                # Pull maximum Threat IDs
                for dummy in range(results_per_page):
                    # Only proceed if there are updates here.
                    if list_to_retrieve:
                        # Grab a single update.
                        item = list_to_retrieve.pop()
                        if process_intelligence and item.get('threatType') == 'malware':
                            threat_list.append('m_' + str(item.get('threatId')))
                        if process_brand_intelligence and item.get('threatType') == 'phish':
                            threat_list.append('p_' + str(item.get('threatId')))

                # Add the list of Threat IDs to the payload.
                payload.update({'threatId': threat_list})

                # Get threats from PhishMe.
                dummy, threats = self._retrieve_from_threat_search(payload=payload)

                # yield threats
                for threat in threats:
                    yield threat, 'json'

    def _preprocess_threat(self, mrti, mrti_format):
        """
        Determine the the PhishMe product and Threat ID, write them to the log, and return those values.

        :param mrti: A string or json representing a single threat.
        :param str mrti_format: The format or *mrti*. One of [cef, json, stix].
        :return: A tuple of the PhishMe product [Intelligence, Brand Intelligence], Threat ID, and a boolean representing whether this entry is new or deleted.
        :rtype: str, int, bool
        """
        # Set defaults for these values so nothing crashes if these values can't be discovered.
        product = 'unknown'
        threat_id = 0
        first_published = 0
        expired_threat = False
        write_to_log = True

        # Choose how to process this threat based on its format.
        if mrti_format == 'json':
            if mrti.get('threatType') == 'MALWARE':
                product = 'Intelligence'
            if mrti.get('threatType') == 'PHISH':
                product = 'Brand Intelligence'

            threat_id = mrti.get('id')

            # This value is 'firstPublished' in PhishMe Intelligence and 'firstDate' in PhishMe Brand Intelligence
            first_published = mrti.get('firstPublished') or mrti.get('firstDate')

        elif mrti_format == 'stix':
            product_temp = re.search('<stix:Title>Cofense\s(\w+)\sThreatID \d+</stix:Title>', mrti).group(1)
            if product_temp == 'Malware':
                product = 'Intelligence'
            if product_temp == 'Phish':
                product = 'Brand Intelligence'

            threat_id = re.search('<campaign:Title>(\d+)</campaign:Title>', mrti).group(1)

            # Extracting this timestamp takes some work.
            first_published_timestamp = re.search('<stix:Campaign\sid="Cofense:Campaign-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}"\stimestamp="(\S+)"\s', mrti).group(1)
            first_published_string = datetime.strptime(first_published_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            first_published = self._unix_time_millis(first_published_string)

        elif mrti_format == 'cef':
            product = mrti.split('|')[2]
            threat_id = re.search('externalId=(\d+)\s', mrti).group(1)

            # Prevent writing to the log when processing CEF because there could be multiple CEF events in the same Threat ID.
            if self.temp_cef_threat_id == threat_id:
                write_to_log = False
            self.temp_cef_threat_id = threat_id

            first_published = re.search('deviceCustomDate1=(\d+)\s', mrti).group(1)
            first_published = int(first_published)

        else:
            self.logger.warning('Unknown mrti_type: ' + mrti_format)

        # Check if this threat is expired.
        expired_threat_days = self.config.getint('pm_api', 'expired_threat_days')
        expired_threat_milliseconds = expired_threat_days*24*60*60*1000
        if first_published+expired_threat_milliseconds < self.init_time_milliseconds:
            expired_threat = True

        # This is a special case for CEF to write a single log entry for a CEF message rather than once per CEF message.
        if write_to_log:
            self.logger.info('Processing PhishMe ' + product + ' Threat ID ' + str(threat_id) + ' in ' + mrti_format.upper())

        return product, threat_id, expired_threat

    def _retrieve_from_feed(self, product='pm_api'):
        """
        Communicate with the /feed/ endpoint. Currently only implemented to assist with validating connections and returning the response. This may need to be modified in the future if this endpoint needs to be supported for the library.

        :return: A tuple of the HTTP Status code and the raw response text.
        :rtype: int, str
        """

        # Setup
        auth, url, proxies = self._setup_phishme_connection(self._PhishMeConnectionType.FEED)

        # Connect to PhishMe
        pm_rest_api = rest_api.RestApi(config=self.config, product=product)
        status_code, response = pm_rest_api.connect_to_api(verb='GET', url=url, auth=auth, proxies=proxies)

        return status_code, response

    def _retrieve_from_threat_updates(self, end_timestamp):
        """
        Communicate with the */threat/updates* endpoint, retrieving 1000 updates per request, and yielding them to be processed.

        :param int end_timestamp: Epoch timestamp.
        :return: A tuple of the next UUID position to retrieved if the current batch being processed completes successfully, the number of records to currently be processed, and a list of records to be retrieved for further processing.
        :rtype: str, int, list
        """

        # Setup
        auth, url, proxies = self._setup_phishme_connection(self._PhishMeConnectionType.THREAT_UPDATES)

        # If the position UUID does not exist, then the integration has been initialized during this execution and we need to provide that end_timestamp to
        # /threat/updates to receive back a position UUID. Otherwise, we provide the current position from the config file.
        if self.config.get('pm_api', 'position'):
            payload = {'position': self.config.get('pm_api', 'position')}
        else:
            payload = {'timestamp': end_timestamp}

        # Logging
        if self.config.get('pm_api', 'position'):
            self.logger.info('Retrieving ' + url + ' with position: ' + payload.get('position'))
        else:
            self.logger.info('Retrieving ' + url + ' with end_timestamp: ' + str(end_timestamp))

        # Connect to PhishMe
        pm_rest_api = rest_api.RestApi(config=self.config, product='pm_api')
        status_code, response = pm_rest_api.connect_to_api(verb='POST', url=url, auth=auth, params=payload, proxies=proxies)

        json_response = json.loads(response)

        # Extract and return appropriate response.
        changelog = json_response.get('data').get('changelog')
        changelog_size = len(changelog)
        next_position = json_response.get('data').get('nextPosition')

        # Verify data should be processed.
        process_intelligence = self.config.getboolean('pm_product', 'intelligence')
        process_brand_intelligence = self.config.getboolean('pm_product', 'brand_intelligence')

        # Remove updates for a PhishMe product we are not processing.
        proper_changelog = []
        for item in changelog:
            if item.get('threatType') == 'malware' and process_intelligence:
                proper_changelog.append(item)
            if item.get('threatType') == 'phish' and process_brand_intelligence:
                proper_changelog.append(item)

        return next_position, changelog_size, proper_changelog

    def _retrieve_from_t3_cef(self, payload=None, threat_type=None, threat_id=None):
        """
        Handle output from PhishMe's /t3/{threat_type}/{threat_id}/cef.

        :param dict payload: A pair of timestamps used for backfill.
        :param str threat_type: One of [malware, phish].
        :param int threat_id: The Threat ID to retrieve in CEF format.
        :return: A CEF-formatted string.
        :rtype: str
        """

        # Setup
        auth, url, proxies = self._setup_phishme_connection(self._PhishMeConnectionType.T3_CEF, threat_type, threat_id)

        # Logging
        self.logger.info('Retrieving ' + url)

        # Connect to PhishMe
        pm_rest_api = rest_api.RestApi(config=self.config, product='pm_api')
        if payload:
            status_code, response = pm_rest_api.connect_to_api(verb='POST', url=url, auth=auth, params=payload, proxies=proxies)
        else:
            status_code, response = pm_rest_api.connect_to_api(verb='GET', url=url, auth=auth, proxies=proxies)

        # Extract and return appropriate response.
        return response

    def _retrieve_from_t3_stix(self, threat_type=None, threat_id=None):
        """
        Handle output from PhishMe's /t3/{threat_type}/{threat_id}/stix.

        :param str threat_type: One of [malware, phish].
        :param int threat_id: The Threat ID to retrieve in STIX format.
        :return: A STIX-formatted XML string.
        :rtype: str
        """

        # Setup
        auth, url, proxies = self._setup_phishme_connection(self._PhishMeConnectionType.T3_STIX, threat_type, threat_id)

        # Logging
        self.logger.info('Retrieving ' + url)

        # Connect to PhishMe
        pm_rest_api = rest_api.RestApi(config=self.config, product='pm_api')
        status_code, response = pm_rest_api.connect_to_api(verb='GET', url=url, auth=auth, proxies=proxies)

        # Return appropriate response.
        return response

    def _retrieve_from_threat_search(self, payload, product='pm_api'):
        """
        Handle output from PhishMe's /threat/search

        :param dict payload: All search terms being sent to the /threat/search endpoint.
        :return: A set of Threat IDs in JSON.
        :rtype: dict
        :raises Exception: 'success' value in JSON returned from PhishMe Intelligence API is False
        """

        # Setup
        auth, url, proxies = self._setup_phishme_connection(self._PhishMeConnectionType.THREAT_SEARCH)

        # Logging
        if payload.get('page') and payload.get('beginTimestamp') and payload.get('endTimestamp'):
            self.logger.info('Retrieving ' + url + ' for window from ' + str(datetime.fromtimestamp(payload.get('beginTimestamp'))) + ' to ' + str(datetime.fromtimestamp(payload.get('endTimestamp'))) + '. Retrieving page ' + str(payload.get('page')) + '...')

        elif payload.get('beginTimestamp') and payload.get('endTimestamp'):
            self.logger.info('Retrieving ' + url + ' for window from ' + str(datetime.fromtimestamp(payload.get('beginTimestamp', ''))) + ' to ' + str(datetime.fromtimestamp(payload.get('endTimestamp', ''))))

        else:
            self.logger.info('Retrieving ' + url + ' for ' + str(payload) + '.')

        # Connect to PhishMe
        pm_rest_api = rest_api.RestApi(config=self.config, product=product)
        status_code, response = pm_rest_api.connect_to_api(verb='POST', url=url, auth=auth, params=payload, proxies=proxies)

        json_response = json.loads(response)

        # Extract and return appropriate response.
        if json_response.get('success'):
            # self.logger.info('Retrieved ' + str(len(json_response.get('data').get('threats'))) + ' threats, processing.')
            return json_response.get('data').get('page').get('totalPages'), json_response.get('data').get('threats')

        else:
            raise Exception
            # Need to raise an Exception here.
            # self.remove_lock_and_exit(1)

    def _setup_phishme_connection(self, connection_type, threat_type=None, threat_id=None):
        """
        This method will handle connection setup tasks for the various types of queries.

        :param PhishMeConnectionType connection_type:
        :param str threat_type: One of [malware, phish].
        :param int threat_id: Threat ID to search for (Threat Search and Threat Updates only)
        :return: A tuple of an authentication tuple, a URI, and a dict of proxy URIs.
        :rtype: tuple, str, dict
        :raises: Exception: Connection Type value not recognized
        """

        if connection_type is self._PhishMeConnectionType.THREAT_SEARCH:
                url_values = '/threat/search'
        elif connection_type is self._PhishMeConnectionType.THREAT_UPDATES:
                url_values = '/threat/updates'
        elif connection_type is self._PhishMeConnectionType.T3_CEF:
            if threat_type and threat_id:
                url_values = '/t3/' + threat_type + '/' + threat_id + '/cef'
            else:
                url_values = '/t3/cef'
        elif connection_type is self._PhishMeConnectionType.T3_STIX:
            if threat_type and threat_id:
                url_values = '/t3/' + threat_type + '/' + threat_id + '/stix'
        elif connection_type is self._PhishMeConnectionType.FEED:
            url_values = '/feed/'
        else:
            raise PmValidationError('Connection type not one of THREAT_SEARCH, THREAT_UPDATES, T3_CEF, or T3_STIX')

        url = self.config.get('pm_api', 'base_url') + url_values
        auth = (self.config.get('pm_api', 'user'), self.config.get('pm_api', 'pass'))

        # Configure proxy support if required.
        if self.config.getboolean('local_proxy', 'use') is True:
            proxy_url_http = self.config.get('local_proxy', 'http')
            proxy_url_https = self.config.get('local_proxy', 'https')

            # BASIC authentication.
            if self.config.getboolean('local_proxy', 'auth_basic_use'):

                proxy_basic_user = self.config.get('local_proxy', 'auth_basic_user')
                proxy_basic_pass = self.config.get('local_proxy', 'auth_basic_pass')

                proxy_basic_auth = proxy_basic_user + ':' + proxy_basic_pass + '@'

                index_http = proxy_url_http.find('//') + 2
                index_https = proxy_url_https.find('//') + 2

                proxy_url_http = proxy_url_http[:index_http] + proxy_basic_auth + proxy_url_http[index_http:]
                proxy_url_https = proxy_url_https[:index_https] + proxy_basic_auth + proxy_url_https[index_https:]

            proxies = {'http': proxy_url_http, 'https': proxy_url_https}

        else:
            proxies = {}

        return auth, url, proxies

    def _generate_scheduler_offset(self):
        """
        Determine the random offset used by an integration. This value is sent to the config file for use in subsequent executions.

        :return: None
        """

        # Generate
        value = random.randint(0, self.config.getint('pm_jitter', 'execution_frequency'))

        self.config.set('pm_jitter', 'scheduler_offset', str(value-1))

    def _date_to_epoch(self):
        """
        Converts a YYYY-MM-DD string into an epoch time.

        :return: A tuple of the converted epoch time from the config.ini file and the current time in epoch.
        :rtype: int, int
        """

        utc_time = time.strptime(self.config.get('pm_api', 'init_date'), '%Y-%m-%d')
        epoch_time = timegm(utc_time)
        return int(epoch_time), int(time.time())

    @staticmethod
    def _unix_time_millis(dt):
        """
        Convert a datetime object into milliseconds since epoch.

        :return: A timestamp in epoch milliseconds.
        :rtype: int
        """

        epoch = datetime.utcfromtimestamp(0)
        return int((dt - epoch).total_seconds()) * 1000

    def _add_lock(self):
        """
        Create lock file if it does not exit; exit if lock file already exists. The existence of this lock file prevents
        multiple simultaneous executions.

        :return: Returns True if the lock file was created or is not needed or returns False if the lock file exists or failed to be created.
        :rtype: bool
        """

        # Lock file is required for this execution
        if self.config.getboolean('local_file_lock', 'use') is True:
            lock_file_full_path = self.config.get('local_file_lock', 'lock_file')

            # Try to open the lock file. It probably won't exist, so an error will be thrown. This is normal.
            try:
                with open(lock_file_full_path, 'r+') as lock_file:

                    try:
                        # Check the lock file for current number of times it has been persistence
                        lock_file_value = lock_file.readline()
                        # If lock file is empty or a negative number default to 0
                        access_number = 0 if lock_file_value.strip() == "" or int(lock_file_value.strip()) < 0 \
                            else int(lock_file_value.strip())
                    except ValueError:
                        # If there is trash (non-integer value) in the file default to zero
                        access_number = 0

                    if access_number in range(0, 20):
                        access_number += 1
                        # on the 5th, 10th and 15th execution with a lock file in place ping Cofense so this status can
                        # be tracked (a /feed API call with a custom user agent)
                        if access_number in [5, 10, 15]:
                            self._retrieve_from_feed(product='custom_search_LOCK_FILE_{}'.format(access_number))
                        self._write_access_number_to_lock_file(access_number, lock_file)
                    else:
                        # if number greater than 20 we will allow execution of the integration and reset the number
                        self._write_access_number_to_lock_file(u'1', lock_file)
                        return True

                return self._lock_file_error(lock_file_full_path)

            # A lock file doesn't exist - create one.
            except (IOError, OSError):

                return self._create_lock_file(lock_file_full_path)

        # Lock file not required for this execution.
        else:
            return True

    def _write_access_number_to_lock_file(self, access_number, lock_file):
        """
        Handle writing the access number to the lock file

        :param access_number: access number to write to lock file(string)
        :param lock_file: path to lock file
        :return:
        """
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(six.u(str(access_number)))

    def _lock_file_error(self, lock_file_full_path):
        """
        Provides a meaningful error message to the user if lock file still exists

        :param lock_file_full_path: Full path to the lock file
        :return:
        """
        lock_file_error = 'Lock file exists at: ' + lock_file_full_path + '.\nIf no other instance of this script is ' \
                                                                          'currently running, you should delete the ' \
                                                                          'lock file.\nOtherwise, the lock file will ' \
                                                                          'be automatically removed when the script ' \
                                                                          'successfully exits.\nThe usage of this ' \
                                                                          'file is to prevent concurrent instances of '\
                                                                          'this script from executing. '
        self.logger.warning(lock_file_error)
        print(lock_file_error)
        return False

    def _create_lock_file(self, lock_file_full_path):
        """
        Actually create the lock file

        :param lock_file_full_path: Full path to the lock file
        :type str
        :return: Whether lock file has been created
        """
        # Create lock file.
        try:
            with open(lock_file_full_path, 'w+') as lock_file:
                lock_file.write(u'1')
                return True

        # Could not create a lock file. Likely a permissions error.
        except (IOError, OSError):
            self.logger.error(
                'Could not create lock file at: ' + lock_file_full_path + '. This is most likely a permissions issue.')
            return False

    def _remove_lock_and_exit(self, exit_code=0):
        """
        Remove lock file from the system.

        :param int exit_code: No longer in use and not particularly meaningful, an exit code can be passed in.
        :return: None
        """

        if self.config.getboolean('local_file_lock', 'use') is True:
            lock_file_full_path = self.config.get('local_file_lock', 'lock_file')
            os.remove(lock_file_full_path)

            # if exit_code == 0:
            #     self.logger.info('Exiting.\n\n')
            # else:
            #     self.logger.info('Exiting due to failure.\n\n')
            # sys.exit(exit_code)

    def process(self, mrti, threat_id):
        '''Use this method to process intelligence outside of a default module'''

        pass


class PhishMeIntelligence(PhishMeBase):
    """
    Contains helper methods for interacting with PhishMe Intelligence API and handling lock file.
    """

    def sync(self):
        """
        This will contact the PhishMe Intelligence API, retrieve any new or modified threat intelligence since the last successful check-in, process it into the output(s) designated by *config.ini*, and return.

        This method will update the *position* value in the [pm_api] section of the *config.ini* during each successful poll and subsequent processing of the returned threat intelligence. Any failure to process threat intelligence will cause the position value to not be updated. Subsequent executions will resume from the last successful execution, as controlled by the position value in *config.ini*.::

           [pm_api]
           base_url = https://www.threathq.com/apiv1
           user =
           pass =
           ssl_verify = True
           init_date = 2017-05-15
           position = 9d801cc1-d3ec-432b-a436-3eee186b1fff
           results_per_page = 100
           max_retries = 3
           expired_threat_days = 90

        :return: None
        """

        self.logger.info('PhishMe Intelligence sync starting.')

        # Check to ensure the config file is properly filled out.
        config_checker = config_check.ConfigCheck(config=self.config)

        # Validate the config file and call the lock if a lock is not being handled elsewhere.
        if config_checker.validate_config() and self._add_lock():

            try:

                # Observe jitter offset and sleep. Do not observe jitter when performing backfill (no position present).
                if self.config.getboolean('pm_jitter', 'use') and self.config.get('pm_api', 'position') != '':
                    minutes_to_sleep = self.config.getint('pm_jitter', 'scheduler_offset')
                    self.logger.info('Sleeping for ' + str(minutes_to_sleep) + ' minutes in observance of pm_jitter settings. Please do not adjust this value.')
                    time.sleep(60*minutes_to_sleep)

                # Perform necessary imports to support integrations specified in config.ini. Here be dragons.
                self.activated_integrations = supported_integrations.import_libraries(config=self.config)

                for activated_item in self.activated_integrations:
                    self.imported_modules[activated_item.config_name] = importlib.import_module(name=activated_item.output_product_module)

                # Proceed with getting data from PhishMe and performing (an) integration(s).
                self._run_integration()

                # Remove lock file and exit
                self._remove_lock_and_exit()

            except Exception as e:
                self.logger.error(traceback.format_exc())
                self.logger.error('PhishMe Intelligence sync completing due to exception.\n\n')

            else:
                self.logger.info('PhishMe Intelligence sync completing.\n\n')

        else:
            self.logger.error('PhishMe Intelligence sync completing due to error in config or acquiring lock.\n\n')

    def search(self, product, description, **kwargs):
        """
        Use this method to search PhishMe Intelligence for one or more IOCs.

        :param product: The name of the product that PhishMe Intelligence will be sent to.
        :param description: A short description of the use case for this call.
         param **kwargs: Any search parameter accepted by /threat/search

         See https://threathq.com/docs/rest_api_reference.html#threat for details

        :return:
        """

        self.logger.info('PhishMe Intelligence search starting.')

        try:

            # Creating a string to be included as part of User-Agent returned to PhishMe Intelligence API.
            product_description = product
            if description is not None:
                product_description += '/' + description
            product_description = product_description.lower().replace(' ', '_')

            payload = {
                'resultsPerPage': self.config.get('pm_api', 'results_per_page')
            }

            payload.update(kwargs)

            cur_page_number = 0
            total_pages = 1
            while cur_page_number < total_pages:

                payload.update({'page': cur_page_number})

                total_pages, threats = self._retrieve_from_threat_search(payload=payload, product='custom_search_'+product_description)

                for threat in threats:
                    if threat['threatType'] == 'PHISH':
                        yield brand_intelligence.Phish(threat)
                    elif threat['threatType'] == 'MALWARE':
                        yield intelligence.Malware(threat, config=self.config)
                    else:
                        self.logger.warning('Unknown data returned from /threat/search.')

                cur_page_number += 1

        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error('PhishMe Intelligence search completing due to exception.\n\n')
            raise e

        else:
            self.logger.info('PhishMe Intelligence search completing.\n\n')

    def test_connection(self):
        """
        This method will attempt to test the connection to the PhishMe Intelligence API by contacting the /feed/ endpoint.

        :return: An integer HTTP Status Code will be returned according to https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html.
        :rtype: int
        """

        return self._retrieve_from_feed()


def read_args(script_description):
    """
    Parse arguments from command line.

    Use the --conf flag to pass the path to the config file if it is not named *config.ini* or is not located in the current working directory.

    :param str script_description: Description of the package being executed.
    :return: Command line arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=script_description)

    # Arguments to parse.
    parser.add_argument('-conf', '--config_file', help='Config location. By default, config file is assumed to be in the same directory and named \'config.ini\'.', required=False, default='config.ini')

    return parser.parse_args()


def read_config(config_file):
    """
    Read configuration file. This file is typically named config.ini.

    :param str config_file: Path to config file.
    :return: Object containing all configuration items for using the phishme_intelligence library.
    :rtype: ConfigParser
    """

    if PYTHON_MAJOR_VERSION == 3:
        config = ConfigParser(interpolation=None)
    else:
        config = ConfigParser()

    config.read(config_file)

    return config
