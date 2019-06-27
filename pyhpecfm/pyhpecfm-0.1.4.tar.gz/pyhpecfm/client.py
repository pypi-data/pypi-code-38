# -*- coding: utf-8 -*-
"""
This module provides helper functions and holds the main client object
for authenticating with an HPE Composable Fabric Manager.
"""
import time

import requests

# The following lines remove warnings for self-signed certificates
# noinspection PyUnresolvedReferences
from requests.packages.urllib3.exceptions import \
    InsecureRequestWarning  # pylint: disable=import-error
# noinspection PyUnresolvedReferences
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # pylint: disable=no-member


class CFMApiError(Exception):
    """Composable Fabric Manager API exception."""
    pass


class CFMClient(object):
    """Client class for the CFM REST API bindings."""

    def __init__(self, host, username, password, verify_ssl=False, timeout=30):
        """
        Initialize API instance.

        :param host: str FQDN or IPv4 Address of the target CFM host
        :param username: str valid username with sufficient permissions on the CFM host
        :param password: str valid password for username var
        :param verify_ssl: bool verify SSL certificate. Default value is False
        :param timeout: int timeout in seconds for API calls
        """
        self._host = host
        self._username = username
        self._password = password
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._session = None
        self._auth_token = None
        self._max_connection_retries = 3

    def __del__(self):
        """
        Disconnect from API on instance destruction.
        Explicitly expires token on CFM server instance.
        """
        self.disconnect()

    def connect(self, login=True):
        """
        Connect to CFM API and retrieve token.

        :param login: bool login and retrieve authentication token
        """
        self._session = None
        self._auth_token = None

        self._session = requests.session()
        self._session.headers.update({'Accept': 'application/json'})
        self._session.headers.update({'Content-Type': 'application/json'})

        if login:
            self._session.headers.update({'X-Auth-Username': '{}'.format(self._username)})
            self._session.headers.update({'X-Auth-Password': '{}'.format(self._password)})

            response = self._call_api('POST', 'v1/auth/token').json()
            self._auth_token = response.get('result')
            if self._auth_token:
                self._session = requests.session()
                self._session.headers.update({'Accept': 'application/json'})
                self._session.headers.update({'Authorization': 'Bearer {}'.format(self._auth_token)})
                self._session.headers.update({'X-Auth-Refresh-Token': 'true'})
            else:
                raise CFMApiError('Error retrieving authentication token')

    def disconnect(self):
        """Disconnect from CFM API session and delete token."""
        self._auth_token = None
        self._session = None

    def delete(self, path, params= None):
        """
        Helper function for HTTP DELETE commands

        :param path: str the requested path
        :return: requests.Response API call response
        :rtype: requests.Response
        """
        return self._call_api(method='DELETE', path=path, params= params)

    def get(self, path, params= None):
        """
        Helper function for HTTP GET commands

        :param path: str the requested path
        :return: requests.Response API call response
        :rtype: requests.Response
        """
        return self._call_api(method='GET', path=path, params=params)

    def patch(self, path, data):
        """
        Helper function for HTTP PATCH commands

        :param path: str the requested path
        :param data: dict the data to send
        :return: requests.Response API call response
        :rtype: requests.Response
        """
        return self._call_api(method='PATCH', path=path, json=data)

    def post(self, path, params=None, data=None):
        """
        Helper function for HTTP POST commands

        :param path: str the requested path
        :param json: dict the data to send
        :return: requests.Response API call response
        :rtype: requests.Response
        """
        return self._call_api(method='POST', path=path, params=params, json=data)

    def put(self, path, data):
        """
        Helper function for HTTP PUT commands

        :param path: str the requested path
        :param data: dict the data to send
        :return: requests.Response API call response
        :rtype: requests.Response
        """
        return self._call_api(method='PUT', path=path, json=data)

    def _call_api(self, method, path, params=None, headers=None, json=None,
                  timeout=None, stream=False):
        """Execute a CFM REST API request.

        Arguments:
            method (str): HTTP request type
            path (str): The request path of the REST API.
            params (dict): (Optional) query parameters.
            headers (dict): (Optional) HTTP Headers to send with the request.
            json (dict): (Optional) json to send in the body of the request.
            timeout (int): Optional timeout override.

        Returns:
            requests.Response (class): JSON representation of the response object from requests
        """
        request_headers = headers if headers else {'Content-Type': 'application/json;charset=UTF-8'}

        if self._auth_token:
            # Set Auth Token in Header
            request_headers.update(
                {'Authorization': 'Bearer {}'.format(self._auth_token),
                 'X-Auth-Refresh-Token': 'true'}
            )
        elif path != 'v1/auth/token':
            # If this is not a login request, then there is a problem with the auth token.
            print('{} {} Aborted: Failed to obtain auth token.'.format(method, path))
            return

        attempts = 0
        while attempts < self._max_connection_retries:
            try:
                attempts += 1
                if self._session:
                    return self._process_request(
                        self._session, method, path, params, request_headers, json, timeout,
                        verify=self._verify_ssl, stream=stream)
                else:
                    with requests.session() as session:
                        session.headers.update({'Accept': 'application/json'})
                        return self._process_request(
                            session, method, path, params, request_headers, json, timeout,
                            verify=self._verify_ssl, stream=stream)
            except requests.exceptions.ConnectionError as exception:
                print('Request failed with error %s', exception)
                if attempts >= self._max_connection_retries:
                    raise exception
                else:
                    print('Retrying Connect API request')
            except requests.exceptions.HTTPError as exception:
                error_code = int(exception.response.status_code)
                if error_code == 401:
                    print('API token no longer valid')
                    self.connect()
                    request_headers.update({'Authorization': 'Bearer {}'.format(self._auth_token)})
                    print('Retrying request %s:%s', method, path)
                elif error_code == 503:
                    print('Service Unavailable on  %s :%s ', method, path)
                    if attempts < self._max_connection_retries:
                        time.sleep(10)
                    else:
                        print('Raise exception retried %s times', attempts)
                        raise exception
                else:
                    print('Exception in API call: %s', exception)
                    raise exception
            except requests.exceptions.ReadTimeout as exception:
                print('ReadTimeout in API call attempt ( %s ) : %s', attempts,
                                   exception)
                if method in ['GET', 'get'] and attempts < self._max_connection_retries:
                    #  Sleep for 2 seconds before re-trying
                    #  Using native sleep method as opposed to eventlet.sleep as we are
                    #  dealing with requests module.
                    time.sleep(2)
                else:
                    print('Retry count ( %s )', attempts)
                    raise exception
                print('Retrying request %s : %s', method, path)
            except Exception as exception:
                print('Exception in API call: %s', exception)
                raise exception

    def _process_request(self, session, method, path, params, headers, json, timeout=None,
                         verify=False, cert=None, stream=False):
        """Execute a REST API request using the supplied session.

        Arguments:
            session (requests.Session): The session to use to issue the HTTP request.
            method (str): HTTP request type
            path (str): The request path of the Prism REST API.
            params (dict): Optional query parameters.
            headers (dict): Optional HTTP Headers to send with the request.
            json (dict): Optional json to send in the body of the request.
            timeout (int): Optional timeout override.
            verify (str): Optional path to trusted CA and/or server certificate(s).
            cert (tuple): Optional client private key and certificate (for two-way TLS).

        Raises (Exception):
            For any exception encountered.

        Returns:
            Response: The response object from requests
        """
        url = 'https://{}/api/{}'.format(self._host, path)
        request = {
            'method': method,
            'url': url,
            'timeout': timeout or self._timeout,
            'headers': headers,
            'params': params,
            'json': json,
            'verify': verify,
            'cert': cert,
            'stream': stream,
        }

        try:
            response = session.request(**request)
        except requests.exceptions.SSLError as exception:
            print('%s %s failed due to SSL handshake error; ensure %s contains a '
                               'certificate which can be used to validate HTTPS connections to %s',
                               method, path, verify, self._host)
            raise exception

        try:
            response.raise_for_status()
            return response
        except Exception as exception:
            print('%s %s failed with status %s',
                  method, path, response.status_code)
            raise exception
