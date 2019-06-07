#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides helped functions and holds the main auth object used for authenticating
against the desired HPE Composable Fabric Manager instance.
"""

from requests.models import PreparedRequest
import requests

# the following removes the warnings for self-signed certificates
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import \
    InsecureRequestWarning  # pylint: disable=import-error

# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint: disable=no-member


class CFMApiError(Exception):
    """Composable Fabric Manager API exception."""
    pass


class CFMClient(object):
    """Bindings for the CFM REST API."""

    def __init__(self, host, username, password, verify_ssl=False, timeout=30):
        """
        Initialize API instance.
        :param host: str FQDN or IPv4 Address of the target CFM host
        :param username: str valid username with sufficient permissions on the CFM host
        :param password: str valid password for username var
        :param verify_ssl: bool verifies SSL certificate when communicating over HTTPS. Default
        value of False
        :param timeout: int defines the timeout value for when a API call will be marked as
        unresponsive
        """
        self._host = host
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._session = None
        self._token = None

    def __del__(self):
        """Disconnect from API on instance destruction. Function
        Explicitly expires token on CFM server instance"""
        self.disconnect()

    def connect(self):
        """Connect to CFM API and retrieve token."""
        self._session = None
        self._token = None

        self._session = requests.session()
        self._session.headers.update({'Accept': 'application/json; version=1.0'})
        self._session.headers.update({'Content-Type': 'application/json'})
        self._session.headers.update({'X-Auth-Username': '{}'.format(self._username)})
        self._session.headers.update({'X-Auth-Password': '{}'.format(self._password)})

        response = self._call_api('POST', 'auth/token').json()
        self._token = response.get('result')
        if self._token:
            self._session = requests.session()
            self._session.headers.update({'Accept': 'application/json; version=1.0'})
            self._session.headers.update({'Authorization': 'Bearer {}'.format(self._token)})
            self._session.headers.update({'X-Auth-Refresh-Token': 'true'})
        else:
            print('Error getting authentication token')

    def disconnect(self):
        """Disconnect from CFM API and delete token."""
        # TODO (brian) add call to delete user token
        self._session = None
        self._token = None

    def get(self, path, params=None):
        """
        helper function used to issue HTTP get commands
        :param path: str which describes the desired path
        :return: requests.Response containing full response of API call
        :rtype: requests.Response
        """
        return self._call_api(method='GET', path=path, params=params)

    def patch(self, path, data):
        """Execute an API PATCH request.

        Arguments:
            path (str): API request path
            data (dict): Data to send

        Returns:
            Response: The requests response object
        """
        return self._call_api(method='PATCH', path=path, data=data)

    def post(self, path, data):
        """Execute an API POST request.

        Arguments:
            path (str): API request path
            data (dict): Data to send

        Returns:
            Response: The requests response object
        """
        return self._call_api(method='POST', path=path, data=data)

    def _call_api(self, method, path, params=None, data=None):
        """Execute an API request.

        Arguments:
            method (str): HTTP request type
            path (str): API request path
            data (dict): Data to send in dictionary format

        Returns:
            Response: The requests response object
        """
        url = 'https://{}/api/{}'.format(self._host, path)
        if params:
            req = PreparedRequest()
            req.prepare_url(url, params)
            url = req.url
        if self._session is None:
            self.connect()
        response = self._session.request(method=method,
                                         url=url,
                                         json=data,
                                         verify=self._verify_ssl,
                                         timeout=self._timeout)
        try:
            response.raise_for_status()
            return response
        # TODO CHECK FOR TOKEN EXPIRATION
        except Exception as exception:
            raise exception
