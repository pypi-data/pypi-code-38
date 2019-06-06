from __future__ import unicode_literals, absolute_import

# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
try:
    from configparser import ConfigParser
    from io import StringIO
except ImportError:
    from ConfigParser import RawConfigParser as ConfigParser
    from StringIO import StringIO

import json
import logging
import os
import re
import sys
import time

from phishme_intelligence import PmValidationError


# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]

# Get the current logger object.
# LOGGER = logging.getLogger('phishme')

IS_VALID_CONFIG = True
"""
Global value that is used to track validity of configuration
"""


class ConfigCheck(object):
    """
    Contains methods related to validation of the config.ini file
    """
    
    def __init__(self, config):
        """
        Initialize a ConfigCheck object

        :param ConfigParser config: ConfigParser object (the loaded config.ini file)
        """

        self.config_copy = self._config_make_copy(config_old=config)
        self.logger = logging.getLogger(__name__)

        self.mandatory_sections = ['pm_api',
                                   'pm_jitter',
                                   'pm_product',
                                   'pm_format',
                                   'local_log',
                                   'local_file_lock',
                                   'local_proxy']
        
    def validate_config(self):
        """
        This method performs validation of the PhishMe Intelligence configuration file

        :return bool IS_VALID_CONFIG: Is the configuration valid?
        :rtype: bool
        """

        # Remove any deactivated sections since they don't need to be scanned.
        self._remove_unused_sections()
    
        # Validate any options that are standard across multiple sections.
        self._validate_standard_options()
    
        # Loop through all sections in config file and call a method to validate it.
        for section in self.config_copy.sections():

            if section not in self.mandatory_sections:
                if self.config_copy.has_option(section, 'check_config'):
                    if self.config_copy.getboolean(section, 'check_config'):

                        try:
                            validate_config_section = getattr(self, '_validate_config_section_'+section)

                            # Execute the correct validation method.
                            validate_config_section(section=section)

                        except PmValidationError as e:
                            self._log_warn(message='%s, non-validated section' % e, section=section)
                        except AttributeError as e:
                            self._log_error('Cannot find validation function: %s' % e)

        # Return the result if this config is acceptable.
        return IS_VALID_CONFIG

    def _validate_standard_options(self):
        """
        This method validates options across PhishMe Intelligence configuration sections that can be common across
        all sections:

        =====================  =====================================================  ==========
        Config Option          Usage                                                  Validation
        =====================  =====================================================  ==========
        host_with_protocol     URL with protocol provided (e.g. https://example.com)  Verifies values starts with 'http://' or 'https://'
        host_without_protocol  URL with protocol NOT provided (e.g. example.com       Verifies values does not start with 'http://' or 'https://'
        ssl_verify             Verify whether self-signed certificate is used         Value is boolean
        =====================  =====================================================  ==========

        :return: None
        """

        # Loop through all the sections.
        for section in self.config_copy.sections():

            if section in self.mandatory_sections:
                validate_mandatory_section = getattr(self, '_validate_config_section_' + section)
                validate_mandatory_section(section)
    
            # Look for a 'host_with_protocol' option.
            option = 'host_with_protocol'
            if self.config_copy.has_option(section, option):
    
                # Ensure that it has a protocol.
                if not (self.config_copy.get(section, option).startswith('https://') or self.config_copy.get(section, option).startswith('http://')):
                    self._log_warn(message='protocol is missing', section=section, option=option, value=self.config_copy.get(section, option))
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
            # Look for a 'host_without_protocol' option.
            option = 'host_without_protocol'
            if self.config_copy.has_option(section, option):
    
                # Ensure that it has a protocol.
                if self.config_copy.get(section, option).startswith('https://') or self.config_copy.get(section, option).startswith('http://'):
                    self._log_warn(message='Should not contain protocol.', section=section, option=option, value=self.config_copy.get(section, option))
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
            # Look for a 'ssl_verify' option.
            option = 'ssl_verify'
            if self.config_copy.has_option(section, option):
    
                # Validate boolean.
                self._validate_option_boolean(section=section, option=option)
    
                # Remove option so it won't be rechecked.
                self.config_copy.remove_option(section=section, option=option)
    
    def _remove_unused_sections(self):
        """
        This method removes sections of the PhishMe Intelligence configuration that are marked as not used.
        Those are sections that have a "use" value and that value is set to False.

        =====================  =====================================================
        Config Option          Usage
        =====================  =====================================================
        use                    Mark whether a section should be used in the configuration (True or False)
        =====================  =====================================================

        :return: None
        """
    
        # Loop through all the sections.
        for section in self.config_copy.sections():
    
            # If a section has a 'use' option.
            if self.config_copy.has_option(section, 'use'):
    
                # If the 'use' option is set to False.
                if not self.config_copy.getboolean(section, 'use'):
    
                    # Remove the entire section.
                    self.config_copy.remove_section(section)
    
                else:
                    # Remove the 'use' option only.
                    self.config_copy.remove_option(section=section, option='use')

    @staticmethod
    def _config_make_copy(config_old):
        """
        Helper method for performing deep copy of PhishMe Intelligence configuration

        :param ConfigParser config_old: ConfigParser to make copy of
        :return: deep copy of ConfigParser object
        :rtype: ConfigParser
        """
    
        # Make string from current ConfigParser object.
        config_string = StringIO()
        config_old.write(config_string)
    
        # We must reset the buffer ready for reading.
        config_string.seek(0)
    
        if PYTHON_MAJOR_VERSION == 3:
            config_new = ConfigParser(interpolation=None)
            config_new.read_file(config_string)
        else:
            config_new = ConfigParser()
            config_new.readfp(config_string)
    
        return config_new
    
    def _validate_config_section_pm_api(self, section):
        """
        This method validates the pm_api section of the PhishMe Intelligence configuration. This is general configuration
        relation to PhishMe API connection and authentication.

        ===================  ================================================================================  ==========
        Config Option        Usage                                                                             Validation
        ===================  ================================================================================  ==========
        base_url             PhishMe API URL                                                                   Value is not less than 10 characters long
        user                 PhishMe API credentials username                                                  Value is not less than 32 characters long
        pass                 PhishMe API credentials password                                                  Value is not less than 32 characters long
        init_date            Data to backfill intelligence from (if position isn't set)                        Value is in format YYYY-MM-DD
        position             "Marks place" in intelligence data (GUID)                                         Value is not less than 36 characters long (warning if blank)
        results_per_page     Number of results to return from /threat/search API endpoint                      Value is between 1 and 100
        max_retries          Number of times to retry PhishMe Intelligence connection                          Value is between 1 and 10
        expired_threat_days  Threat IDs with first published dates older than X days ignored (if republished)  Value is between 1 and 3650
        ===================  ================================================================================  ==========

        :return: None
        """
    
        for option in self.config_copy.options(section):
            value = self.config_copy.get(section, option)
    
            if option == 'base_url':
                self._validate_option_length(section, option, 10)
    
            elif option == 'user':
                self._validate_option_length(section, option, 32)
    
            elif option == 'pass':
                self._validate_option_length(section, option, 32)
    
            elif option == 'init_date':
                try:
                    time.strptime(self.config_copy.get(section, option), '%Y-%m-%d')
                except ValueError:
                    self._log_error(message='%s failed format check' % e, section=section, option=option)
    
            elif option == 'position':
                if len(value) == 0:
                    self._log_warn(message='is blank. This is normal during the initial execution of this script', section=section, option=option)
                else:
                    self._validate_option_length(section, option, 36)
    
            elif option == 'results_per_page':
                self._validate_option_number(section, option, minimum=1, maximum=100)
    
            elif option == 'max_retries':
                self._validate_option_number(section, option, minimum=1, maximum=10)

            elif option == 'expired_threat_days':
                self._validate_option_number(section, option, minimum=1, maximum=3650)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_pm_jitter(self, section):
        """
        This method validates the pm_jitter section of the PhishMe Intelligence configuration. Jitter is configured to
        stagger API connections in a way that will help prevent every integration hitting the API at exactly the same time.

        ===================  ===========================================================  ==========
        Config Option        Usage                                                        Validation
        ===================  ===========================================================  ==========
        execution_frequency  This is the possible range of execution frequency (minutes)  Value is between 5 and 1440
        scheduler_offset     Actual offset to use for jitter (generally generated)        Value is between 0 and execution_frequency value
        ===================  ===========================================================  ==========

        :return: None
        """

        # Loop through all the options.
        for option in self.config_copy.options(section):

            # Get the value for the option.
            value = self.config_copy.get(section, option)

            if option == 'execution_frequency':
                self._validate_option_number(section=section, option=option, minimum=5, maximum=1440)

            elif option == 'scheduler_offset':
                execution_frequency = self.config_copy.getint('pm_jitter', 'execution_frequency')
                self._validate_option_number(section=section, option=option, minimum=0, maximum=execution_frequency)

            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_product(self, section):
        """
        This method validates the pm_product section of the PhishMe Intelligence configuration. These entries specify whether
        to pull in PhishMe Intelligence, PhishMe Brand Intelligence, or both (customer must have access to specific product
        to be able to pull in)

        ===================  =================================================  ==========
        Config Option        Usage                                              Validation
        ===================  =================================================  ==========
        intelligence         Whether or not to pull PhishMe Intelligence        Value is True or False
        brand_intelligence   Whether or not to pull PhishMe Brand Intelligence  Value is True or False
        ===================  =================================================  ==========

        :return: None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            if option == 'intelligence':
                self._validate_option_boolean(section, option)
    
            elif option == 'brand_intelligence':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_format(self, section):
        """
        This method validates the pm_format section of the PhishMe Intelligence configuration. These entries specify whether
        to pull PhishMe Intelligence/PhishMe Brand Intelligence in CEF, JSON and/or STIX 1.1.1 formats. These values are
        configured by the integration based on which other sections are used.

        ===================  ===================================================================================  ==========
        Config Option        Usage                                                                                Validation
        ===================  ===================================================================================  ==========
        cef                  Whether or not to pull PhishMe Intelligence/Brand Intelligence in CEF format         Value is True or False
        json                 Whether or not to pull PhishMe Intelligence/Brand Intelligence in JSON format        Value is True or False
        stix                 Whether or not to pull PhishMe Intelligence/Brand Intelligence in STIX 1.1.1 format  Value is True or False
        ===================  ===================================================================================  ==========

        :return: None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            if option == 'cef':
                self._validate_option_boolean(section, option)
    
            elif option == 'json':
                self._validate_option_boolean(section, option)
    
            elif option == 'stix':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_pm_impact(self, section):
        """
    
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'major':
                self._validate_option_boolean(section, option)
    
            elif option == 'moderate':
                self._validate_option_boolean(section, option)
    
            elif option == 'minor':
                self._validate_option_boolean(section, option)
    
            elif option == 'none':
                self._validate_option_boolean(section, option)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_local_proxy(self, section):
        """
        This method validates the local_proxy section of the PhishMe Intelligence configuration. These are proxy
        configuration settings for PhishMe Intelligence integrations.

        ===================  =========================================================  ==========
        Config Option        Usage                                                      Validation
        ===================  =========================================================  ==========
        http                 HTTP URL for proxy                                         Value must be at least 10 characters log
        https                HTTPS URL for proxy                                        Value must be at least 10 characters log
        auth_basic_use       Whether or not to use Basic Authentication with the proxy  Value must be True or False
        auth_basic_user      HTTP Basic Authentication user name                        Value must exist if auth_basic_use is True
        auth_basic_pass      HTTP Basic Authentication password                         Value must exist if auth_basic_use is True
        ===================  =========================================================  ==========

        :return: None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'http':
                self._validate_option_length(section, option, 10)
    
            elif option == 'https':
                self._validate_option_length(section, option, 10)
    
            # Test BASIC auth settings.
            elif option == 'auth_basic_use':
                self._validate_option_boolean(section, option)
                if self.config_copy.getboolean(section, option):
                    auth_basic_user = self.config_copy.get(section, 'auth_basic_user')
                    auth_basic_pass = self.config_copy.get(section, 'auth_basic_pass')
                    self._validate_option_length(section, 'auth_basic_user', 1)
                    self._validate_option_length(section, 'auth_basic_pass', 1)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'auth_basic_user':
                pass
            elif option == 'auth_basic_pass':
                pass
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_local_file_lock(self, section):
        """
        This method validates the local_file_lock section of the PhishMe Intelligence configuration. These are settings
        related to the lock file used by the PhishMe Intelligence integration. NOTE: the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`

        ===================  ===========================================================  ==========
        Config Option        Usage                                                        Validation
        ===================  ===========================================================  ==========
        lock_file            Path to write lock file to (includes lock file name to use)  Verify that folder lock file is written to exists
        ===================  ===========================================================  ==========

        :return: None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'lock_file':
                # Just test whether parent dir is present. Lock file will not exist when this test is being run.
                self._validate_option_folder_exists(section, option, verify_file=False)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_local_log(self, section):
        """
        This method validates the local_log section of the PhishMe Intelligence configuration. These are configuration
        settings related to PhishMe Intelligence integration logging

        ===================  ===========================================  ==========
        Config Option        Usage                                        Validation
        ===================  ===========================================  ==========
        log_level            Logging level to perform (e.g. info, debug)  None
        log_name             Logging object to write to                   None
        log_file             File to log to                               Must be at least 6 characters and the directory & file must exist
        ===================  ===========================================  ==========

        :return: None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'log_file':
                self._validate_option_length(section, option, 6)
                self._validate_option_folder_exists(section, option, verify_file=True)

            elif option == 'log_level':
                # This is already validated when the logger is created, prior to executing the code in this class.
                pass

            elif option == 'log_name':
                # This is just a string to know what logger object to write or attach to.
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_local_sqlite(self, section):
        """
    
        
        :param section:
        :return:
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'use':
                pass
    
            elif option == 'db_location':
                self._validate_option_folder_exists(section, option, verify_file=False)
    
            elif option == 'data_retention_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
            elif option == 'data_retention_days':
                self._validate_option_number(section, option, minimum=1, maximum=365)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_raw_cef(self, section):
        """
        This method validates the integration_raw_cef section of the PhishMe Intelligence configuration. This is configuration
        related to writing CEF data to the filesystem. NOTE: the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`

        ===========================  ==================================================================  ==========
        Config Option                Usage                                                               Validation
        ===========================  ==================================================================  ==========
        append_file_use              Whether or not to append all CEF messages to a single file          Value is True or False
        append_file_location         Location to write single appended file of CEF messages to           Location exists
        multiple_file_use            Whether or not to (also) write all CEF messages to separate files   Value is True or False
        multiple_file_location       Location to write CEF messages to                                   Location exists
        multiple_file_split_by_date  Whether or not to create directories for CEF message files by date  Value is True or False
        ===========================  ==================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_integration_raw_json(self, section):
        """
        This method validates the integration_raw_json section of the PhishMe Intelligence configuration. This is configuration
        related to writing JSON data to the filesystem. NOTE: the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`

        ===========================  ===================================================================  ==========
        Config Option                Usage                                                                Validation
        ===========================  ===================================================================  ==========
        append_file_use              Whether or not to append all JSON messages to a single file          Value is True or False
        append_file_location         Location to write single appended file of JSON messages to           Location exists
        multiple_file_use            Whether or not to (also) write all JSON messages to separate files   Value is True or False
        multiple_file_location       Location to write JSON messages to                                   Location exists
        multiple_file_split_by_date  Whether or not to create directories for JSON message files by date  Value is True or False
        ===========================  ===================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_raw_stix(self, section):
        """
        This method validates the integration_raw_json section of the PhishMe Intelligence configuration. This is configuration
        related to writing STIX 1.1.1 data to the filesystem. NOTE: the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`

        ===========================  =========================================================================  ==========
        Config Option                Usage                                                                      Validation
        ===========================  =========================================================================  ==========
        append_file_use              Whether or not to append all STIX 1.1.1 messages to a single file          Value is True or False
        append_file_location         Location to write single appended file of STIX 1.1.1 messages to           Location exists
        multiple_file_use            Whether or not to (also) write all STIX 1.1.1 messages to separate files   Value is True or False
        multiple_file_location       Location to write STIX 1.1.1 messages to                                   Location exists
        multiple_file_split_by_date  Whether or not to create directories for STIX 1.1.1 message files by date  Value is True or False
        ===========================  =========================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'append_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_folder_exists(section, 'append_file_location', verify_file=False)
    
            elif option == 'multiple_file_use':
                if self.config_copy.getboolean(section, option):
                    self._validate_option_boolean(section, option)
    
                    self._validate_option_boolean(section, 'multiple_file_split_by_date')
    
                    self._validate_option_folder_exists(section, 'multiple_file_location', verify_file=False)
    
            # Ignore these, they will be screened if their respective sections are activated.
            elif option == 'append_file_location':
                pass
            elif option == 'multiple_file_location':
                pass
            elif option == 'multiple_file_split_by_date':
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_arcsight(self, section):
        """
        This method validates the integration_arcsight section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with the Arcsight SIEM. NOTE: host_without_protocol is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._validate_standard_options` and the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  =====================================================  ==========
        Config Option                Usage                                                  Validation
        ===========================  =====================================================  ==========
        port                         Port to use to to communicate to Arcsight              Value between 1 and 65536
        max_eps                      Maximum number of Events per Second (EPS) to generate  Value between 1 and 1000
        ===========================  =====================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'port':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=65536)
    
            elif option == 'max_eps':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=1000)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_carbon_black(self, section):
        """
        This method validates the integration_carbon_black section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with Carbon Black Response.  NOTE: host_with_protocol and ssl_verify validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._validate_standard_options` and the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  ==================================================================================  ==========
        Config Option                Usage                                                                               Validation
        ===========================  ==================================================================================  ==========
        api_token                    Token from Carbon Black to authenticate to Cb Response                              Value is at least 40 characters long
        feed_name                    Name of PhishMe Intelligence feed as it appears in Cb Response                      Value is alphanumeric characters
        feed_id                      Integer value designating PhishMe Intelligence feed in Cb Response                  Value between 0 and 1000 (warning if blank since it's populated by the script
        sqlite_location              Location to write SQLite database backing Cb Response integration to                Folder & file exist
        sqlite_data_retention_days   Number of days of PhishMe Intellignece to retain in SQLite database                 Value between 1 and 365
        cb_feed                      The full path including file name where PhishMe Intelligence data will be written.  Folder & file exist
        impact_major                 Integer representation of 'Major' impact rating                                     Value between 0 and 100
        impact_moderate              Integer representation of 'Moderate' impact rating                                  Value between 0 and 100
        impact_minor                 Integer representation of 'Minor' impact rating                                     Value between 0 and 100
        impact_none                  Integer representation of 'None' impact rating                                      Value between 0 and 100
        excluded_md5_use             Whether to exclude list of whitelisted hashes                                       Value is True or False
        excluded_md5                 List of whitelisted hashes                                                          Value is a JSON array
        ===========================  ==================================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'api_token':
                self._validate_option_length(section=section, option=option, min_length=40)
    
            elif option == 'feed_name':
                if not self._validate_option_alphanumeric(value):
                    self._log_warn(message='', section=section, option=option, value=value)
    
            elif option == 'feed_id':
                if len(value) == 0:
                    self._log_warn(message='is blank. This is normal during the initial execution of this script.', section=section, option=option)
                else:
                    self._validate_option_number(section=section, option=option, minimum=0, maximum=1000)
    
            elif option == 'sqlite_location':
                self._validate_option_folder_exists(section=section, option=option, verify_file=True)
    
            elif option == 'sqlite_data_retention_days':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=365)
    
            elif option == 'cb_feed':
                self._validate_option_folder_exists(section=section, option=option, verify_file=True)
    
            elif option == 'impact_major':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_moderate':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_minor':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'impact_none':
                self._validate_option_number(section=section, option=option, minimum=0, maximum=100)
    
            elif option == 'excluded_md5_use':
                self._validate_option_boolean(section=section, option=option)
    
                # Handle the excluded MD5s only if this section is turned on.
                if self.config_copy.getboolean(section, option):
                    try:
                        json.loads(self.config_copy.get(section, 'excluded_md5'))
                    except (json.JSONDecodeError, ValueError) as e:
                        self._log_warn(
                            message='%s: Excluded md5s are not formatted correctly. Ensure they are enclosed in [], double-quoted, and comma separated.' % e,
                            section=section,
                            option='excluded_md5'
                        )
    
            elif option == 'excluded_md5':
                # Handled conditionally above.
                pass
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_crits(self, section):
        """
        This method validates the integration_crits section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with CRITs.  NOTE: host_with_protocol and ssl_verify validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._validate_standard_options` and the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  =================================================================  ==========
        Config Option                Usage                                                              Validation
        ===========================  =================================================================  ==========
        user                         Username for account used to create API token for access to CRITs  Value is at least 3 characters
        api_token                    API token to use for REST API access to CRITs                      Value is at least 40 characters
        source                       Source to write PhishMe Intelligence data to in CRITs              Value is at least 3 characters
        ===========================  =================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'api_token':
                self._validate_option_length(section=section, option=option, min_length=40)
    
            elif option == 'source':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            elif option == 'user':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_logrhythm(self, section):
        """
        This method validates the integration_logrhythm section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with LogRhythm.  NOTE: The use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  ====================================================  ==========
        Config Option                Usage                                                 Validation
        ===========================  ====================================================  ==========
        output_dir                   Directory to output Indicator lists to for LogRhythm  Folder exists
        ===========================  ====================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'output_dir':
                self._validate_option_folder_exists(section=section, option=option, verify_file=False)
    
            else:
                self._non_valid_option_found(section, option)
    
    def _validate_config_section_integration_mcafee_siem(self, section):
        """
        This method validates the integration_mcafee_siem section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with the McAfee SIEM. NOTE: host_without_protocol is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._validate_standard_options` and the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  =====================================================  ==========
        Config Option                Usage                                                  Validation
        ===========================  =====================================================  ==========
        port                         Port to use to to communicate to McAfee SIEM           Value between 1 and 65536
        max_eps                      Maximum number of Events per Second (EPS) to generate  Value between 1 and 1000
        ===========================  =====================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'port':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=65536)
    
            elif option == 'max_eps':
                self._validate_option_number(section=section, option=option, minimum=1, maximum=1000)
    
            else:
                self._non_valid_option_found(section, option)

    def _validate_config_section_integration_tipping_point_ips(self, section):
        """
        This method validates the integration_tipping_point_ips section of the PhishMe Intelligence configuration. These are configuration
        options specific to using the standalone integration with Tipping Point.  NOTE: host_with_protocol and ssl_verify validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._validate_standard_options` and the use value is validated in
        :func:`phishme_intelligence.core.config_check.ConfigCheck._config_make_copy`.

        ===========================  ==================================================================================  ==========
        Config Option                Usage                                                                               Validation
        ===========================  ==================================================================================  ==========
        user                         Username used to access Tipping Point                                               Value is at least 3 characters
        pass                         Password used to access Tipping Point                                               Value is at least 8 characters
        impact_major                 Whether to send 'Major' impact rating items to Tipping Point                        Value is True or False
        impact_moderate              Whether to send 'Moderate' impact rating items to Tipping Point                     Value is True or False
        impact_minor                 Whether to send 'Minor' impact rating items to Tipping Point                        Value is True or False
        impact_none                  Whether to send 'None' impact rating items to Tipping Point                         Value is True or False
        ===========================  ==================================================================================  ==========

        :return None
        """
    
        # Loop through all the options.
        for option in self.config_copy.options(section):
    
            # Get the value for the option.
            value = self.config_copy.get(section, option)
    
            if option == 'user':
                self._validate_option_length(section=section, option=option, min_length=3)
    
            elif option == 'pass':
                self._validate_option_length(section=section, option=option, min_length=8)
    
            elif option == 'impact_major':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_moderate':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_minor':
                self._validate_option_boolean(section=section, option=option)
    
            elif option == 'impact_none':
                self._validate_option_boolean(section=section, option=option)
    
            else:
                self._non_valid_option_found(section, option)

    @staticmethod
    def _validate_option_alphanumeric(option):
        """
        Validates that value does NOT contain any non-alphanumeric character

        :param str option: Value to verify against regular expression
        :return: inverse of match against regular expression that matches any non-alphanumeric character
        :rtype: bool
        """
        return not bool(re.search(string=option, pattern=r'[^a-zA-Z\d]'))
    
    def _validate_option_length(self, section, option, min_length):
        """
        Validate that option is at least the length provided. Log error (see :class:`phishme_intelligence.core.config_check.ConfigCheck._log_error`)
        if not true.

        :param str section: Section of option to validate
        :param str option: Option to validate
        :param int min_length: Minimum length option should be
        :return: None
        """
    
        value = self.config_copy.get(section, option)
        if len(value) < min_length:
            self._log_error(message='failed length check', section=section, option=option)

    def _validate_option_boolean(self, section, option):
        """
        Validate that option is a boolean value (True or False). Log error (see :class:`phishme_intelligence.core.config_check.ConfigCheck._log_error`)
        if not true.

        :param str section: Section of option to validate
        :param str option: Option to validate
        :return: None
        """
    
        try:
            self.config_copy.getboolean(section, option)
        except ValueError as e:
            self._log_error(message='%s: should be a boolean value' % e, section=section, option=option)

    def _validate_option_max_one_true(self, error_message, *args):
        """
    
        :param error_message:
        :param args:
        :return:
        """
    
        if sum(bool(a) for a in args) > 1:
            self._log_error(message=error_message)
    
    def _validate_option_number(self, section, option, minimum, maximum):
        """
        Validate that option is an integer between an minimum and maximum (exclusive). Log error
        (see :class:`phishme_intelligence.core.config_check.ConfigCheck._log_error`) if not true.

        :param str section: Section of option to validate
        :param str option: Option to validate
        :param int minimum: Minimum integer value option should be
        :param int maximum: Maximum integer value option should be
        :return: None
        """
    
        try:
            value = self.config_copy.getint(section, option)
    
            if minimum:
                if value < minimum:
                    self._log_error(message='should be greater than or equal to ' + str(minimum) + '.', section=section, option=option)
    
            if maximum:
                if value > maximum:
                    self._log_error(message='should be less than or equal to ' + str(maximum) + '.', section=section, option=option)
    
        except ValueError as e:
            self._log_error(message='%s: should be an integer value.' % e, section=section, option=option)
    
    def _validate_option_folder_exists(self, section, option, verify_file=False):
        """
        Validate that option is a valid path to a folder or a file. Logs to
        :class:`phishme_intelligence.core.config_check.ConfigCheck._log_error` if no directory and
        :class:`phishme_intelligence.core.config_check.ConfigCheck._log_warn` if no file.

        :param str section: Section of option to validate
        :param str option: Option to validate
        :param bool verify_file: Whether to verify if path is to file and exists
        :return: None
        """
    
        value = self.config_copy.get(section, option)
    
        directory, file_name = os.path.split(value)
    
        if not os.path.isdir(directory):
            self._log_error(message='folder does not exist.', section=section, option=option)
    
        if verify_file:
            if not os.path.isfile(value):
                self._log_warn(message='file does not exist.', section=section, option=option)
        
    def _non_valid_option_found(self, section, option):
        """
        Validation passthru that that logs warning (see :class:`phishme_intelligence.core.config_check.ConfigCheck._log_warn`)

        :param str section: Section of option to validate
        :param str option: Option to validate
        :return: None
        """
    
        self._log_warn(message='non-validated option', section=section, option=option)

    def _log_warn(self, message, section=None, option=None, value=None):
        """
        Log warning level message related to configuration validation.

        :param str message: Message to log
        :param str section: Name of section to log
        :param str option: Name of option to log
        :param str value: Value of option to log
        :return: None
        """
    
        if section and option and value:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\' contains value \'' + value + '\': ' + message)
    
        elif section and option:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\': ' + message)
    
        elif section:
            self.logger.warning('Within config.ini, section \'' + section + '\': ' + message)
    
        else:
            self.logger.warning('Within config.ini: ' + message)

    def _log_error(self, message, section=None, option=None, value=None):
        """
        Log error level message related to configuration validation and set global IS_VALID_CONFIG value to False

        :param str message: Message to log
        :param str section: Name of section to log
        :param str option: Name of option to log
        :param str value: Value of option to log
        :return: None
        """
    
        global IS_VALID_CONFIG
        IS_VALID_CONFIG = False
    
        if section and option and value:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\' contains value \'' + value + '\': ' + message)
    
        elif section and option:
            self.logger.warning('Within config.ini, section \'' + section + '\' contains option \'' + option + '\': ' + message)
    
        elif section:
            self.logger.warning('Within config.ini, section \'' + section + '\': ' + message)
    
        else:
            self.logger.warning('Within config.ini: ' + message)
