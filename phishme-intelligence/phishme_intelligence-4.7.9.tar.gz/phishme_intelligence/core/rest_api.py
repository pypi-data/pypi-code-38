# Copyright 2013-2017 PhishMe, Inc.  All rights reserved.
#
# This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
# including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
# disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
# consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
# this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
from __future__ import unicode_literals, absolute_import

import logging
import re
import sys
import time

import requests

from . import metadata

USER_AGENT_BASE = 'PhishMe Intelligence'


class RestApi(object):
    """

    """

    def __init__(self, config, product):
        """
        Initialize a RestApi object

        :param ConfigParser config: ConfigParser object
        :param str product: Name of section (integration) instantiating this object (or pm_api)
        """

        self.config = config
        self.product = product
        self.logger = logging.getLogger(__name__)
        self.version = metadata.__version__

    def connect_to_api(self, verb, url, auth=None, data=None, headers=None, params=None, proxies=None):
        """
        Method to send request the PhishMe Intelligence API and get back response

        :param str verb: Type of HTTP method (GET or POST)
        :param str url: HTTP URL to use for PhishMe Intelligence API connection
        :param tuple auth: (optional) Tuple for HTTP Basic Authentication credentials to use for PhishMe Intelligence API connection
        :param data: (optional) Dictionary or tuple values to send in body of request to PhishMe Intelligence API
        :type data: dict or tuple
        :param dict headers: (optional) HTTP headers to send with request to PhishMe Intelligence API
        :param dict params: (optional) Dictionary of query string data to send to PhishMe Intelligence API
        :param dict proxies: (optional) Dictionary of protocol and URL of proxy to use for PhishMe Intelligence API connection
        :return: Tuple of status code returned from PhishMe Intelligence API connection and JSON returned from PhishMe Intelligence API request
        :rtype: (int, str)
        """

        # Log that a proxy has been activated.
        if self.config.getboolean('local_proxy', 'use'):
            # Remove the username and password from a proxy URI so they aren't written to log file.
            sanitized_proxy = re.sub(pattern='https://(.*)@', repl='https://', string=self.config.get('local_proxy', 'https'))
            sanitized_proxy = re.sub(pattern='http://(.*)@', repl='http://', string=sanitized_proxy)
            sanitized_proxy = re.sub(pattern='(.*)@', repl='', string=sanitized_proxy)
            self.logger.info('Using proxy: ' + sanitized_proxy)

        # Determine whether the certificate should be verified. If not, suppress the warnings.
        if self.config.has_option(self.product, 'ssl_verify') and self.config.getboolean(self.product, 'ssl_verify'):
            verify_value = True

        else:
            requests.packages.urllib3.disable_warnings()
            verify_value = False

        # Try each request up to 3 times before failing.
        max_retries = self.config.getint('pm_api', 'max_retries')

        # Add custom headers.
        if headers is None:
            headers = {}
        if self.product == 'pm_api':
            headers['User-Agent'] = self._build_user_agent()
        elif self.product.startswith('custom_search_'):
            headers['User-Agent'] = self._build_user_agent(custom_product=self.product)
        else:
            headers['User-Agent'] = USER_AGENT_BASE

        # Attempt this API call up to a specified number of times. Exit if no success.
        for attempt in range(max_retries):
            try:
                if verb == 'GET':
                    response = requests.get(url=url, auth=auth, data=data, headers=headers, params=params, proxies=proxies, verify=verify_value)
                elif verb == 'POST':
                    response = requests.post(url=url, auth=auth, data=data, headers=headers, params=params, proxies=proxies, verify=verify_value)
                else:
                    pass

                # Verify an appropriate status code has been returned or skip this iteration.
                if not str(response.status_code).startswith('2'):
                    self.logger.warning('API call has failed: '
                                        'HTTP Status: ' + str(response.status_code) + ' '
                                        'URL: ' + str(url) + ' '
                                        'Data: ' + str(data) + ' '
                                        'Headers: ' + str(headers) + ' '
                                        'Parameters: ' + str(params) + ' '
                                        'Proxies: ' + str(proxies) + ' '
                                        'Verify: ' + str(verify_value) + ' '
                                        'Content: ' + str(response.content)
                                        )
                    continue

                # Return the status code and response content.
                return response.status_code, response.content.decode('utf-8')

            # Catch and log any exceptions thrown by requests package.
            except requests.exceptions.RequestException as exception:
                self.logger.error(exception)
                time.sleep(60)

        else:
            self.logger.error('An error occurred. Tried to complete request ' + str(max_retries) + ' times and all failed.')
            sys.exit(1)
            # Consider raising a custom error class here that will cause a clean exit. A lock file _should_ remain if an exit occurs here, because API connectivity was compromised, so all data was not properly sent to its destination.

    def _build_user_agent(self, custom_product=None):
        """
        Create a custom user agent for communicating with the PhishMe Intelligence API.

        :param str custom_product: suser agent for custom product (if applicable)
        :return: The custom user agent
        :rtype: str
        """

        # Begin with base.
        custom_user_agent = USER_AGENT_BASE

        # Build a list of the currently activated integrations.
        active_integrations = []

        if custom_product is not None:
            custom_product = custom_product.replace('custom_search_', '')
            active_integrations.append(custom_product)

        else:
            for section in self.config.sections():
                if section.startswith('integration_') and self.config.getboolean(section, 'use'):
                    # No need to keep this text, this will allow for shortened user-agent strings.
                    section = section.replace('integration_', '')

                    active_integrations.append(section)

        # Add the active integrations to the user-agent string.
        custom_user_agent += '/' + self.version + ' (' + ', '.join(active_integrations) + ')'

        return custom_user_agent
