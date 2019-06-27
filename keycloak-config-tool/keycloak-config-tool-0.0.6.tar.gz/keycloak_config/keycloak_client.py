"""
Keycloak Client.
~~~~~~~~~~~~~~~~
"""

import re
import requests
import time


class NoSessionException(Exception):
    pass


class KeycloakClient(object):
    ADMIN_LOGIN_CLIENT_ID = 'admin-cli'
    RELATIVE_HEALTH_CHECK_ENDPOINT = '/realms/master'
    RELATIVE_TOKEN_ENDPOINT = '/realms/master/protocol/openid-connect/token'
    HEALTH_CHECK_INTERVAL = 5
    ACCESS_TOKEN_KEY = 'access_token'
    REFRESH_TOKEN_KEY = 'refresh_token'

    def __init__(self, base_url):
        """
        Constructor.
        :param base_url: The base URL of the Keycloak service.
        :return: The Keycloak client.
        """

        self.base_url = re.sub(r'/+$', '', base_url)
        self.health_check_endpoint = self.base_url + self.RELATIVE_HEALTH_CHECK_ENDPOINT
        self.token_endpoint = self.base_url + self.RELATIVE_TOKEN_ENDPOINT
        self.session_data = None

    # Wait for Keycloak to become available.
    def wait_for_availability(self, timeout):
        """
        Wait for Keycloak to become available.
        :param timeout: The maximum amount of time to wait for Keycloak to become available.
        :return: True if the Keycloak service became available, False otherwise.
        """

        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.check_availability():
                print('==== Keycloak is available.')
                return True
            else:
                print('==== Keycloak is not yet available.')
                sleep_duration = min(end_time - time.time(), self.HEALTH_CHECK_INTERVAL)
                time.sleep(sleep_duration)

        print('==== Keycloak never became available.')
        return False

    # Check Keycloak availability by requesting the master realm data.
    def check_availability(self):
        """
        Check Keycloak availability by requesting the master realm data.
        :return: True if the Keycloak service is available, False otherwise
        """

        available = False
        try:
            response = requests.get(self.health_check_endpoint)
            available = response.status_code == requests.codes.ok
        except Exception:
            pass

        return available

    def initialize_session(self, username, password):
        """
        Initialize the admin session by logging in with the provided username and password.
        :param username: The username to use when logging in
        :param password: The password to use when logging in
        :return: True if the login succeeds, False otherwise
        """

        login_data = {
            'grant_type': 'password',
            'client_id': self.ADMIN_LOGIN_CLIENT_ID,
            'username': username,
            'password': password
        }

        try:
            response = requests.post(self.token_endpoint, data=login_data)
            if response.status_code == requests.codes.ok:
                self.session_data = response.json()
                print('==== Login succeeded.')
                return True
            else:
                print('==== Login failed ({0}): {1}'.format(response.status_code, response.text))
                return False
        except Exception as err:
            print('==== Login failed: {0}'.format(err))
            return False

    def refresh_session(self):
        """
        Refresh the admin session by using the refresh token.
        :return: True if the session refresh succeeds, False otherwise
        """

        if not self.session_data:
            raise NoSessionException()

        login_data = {
            'grant_type': 'refresh_token',
            'client_id': self.ADMIN_LOGIN_CLIENT_ID,
            'refresh_token': self.session_data['refresh_token']
        }

        try:
            response = requests.post(self.token_endpoint, data=login_data)
            if response.status_code == requests.codes.ok:
                self.session_data = response.json()
                print('==== Session refresh succeeded.')
                return True
            else:
                print('==== Session refresh failed ({0}): {1}'.format(response.status_code, response.text))
                return False
        except Exception as err:
            print('==== Session refresh failed: {0}'.format(err))
            return False

    def get(self, path, params=None, **kwargs):
        """
        Performs a GET request.
        :param path: The request path, relative to the base URL.
        :param params: The query parameters.
        :param kwargs: Additional parameters.
        :return: The GET response.
        """

        kwargs.setdefault('allow_redirects', True)
        return self.execute_request('get', path, params=params, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        """
        Performs a POST request.
        :param path: The request path, relative to the base URL.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the request.
        :param json: (optional) JSON data to send in the body of the request.
        :param kwargs: Additional parameters.
        :return: The POST response.
        """

        return self.execute_request('post', path, data=data, json=json, **kwargs)

    def put(self, path, data=None, **kwargs):
        """
        Performs a PUT request.
        :param path: The request path, relative to the base URL.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the request.
        :param kwargs: Additional parameters.
        :return: The PUT response.
        """

        return self.execute_request('put', path, data=data, **kwargs)

    def delete(self, path, **kwargs):
        """
        Performs a DELETE request.
        :param path: The request path, relative to the base URL.
        :param kwargs: Additional parameters.
        :return: The DELETE response.
        """

        return self.execute_request('delete', path, **kwargs)

    def add_bearer_token(self, **kwargs):
        """
        Adds the "Bearer" token to the request parameters.
        :param kwargs: The request parameters.
        :return: The updated request parameters.
        """

        bearer = 'Bearer {0}'.format(self.session_data['access_token'])
        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = bearer
        else:
            kwargs['headers'] = {'Authorization': bearer}
        return kwargs

    def execute_request(self, method, path, **kwargs):
        """
        Generic method for performing requests.
        :param method: The request method.
        :param path: The request path, relative to the base URL.
        :param kwargs: The request parameters.
        :return: The resulting response.
        """

        new_kwargs = self.add_bearer_token(**kwargs)
        url = self.base_url + '/' + re.sub(r'^/+', '', path)
        response = requests.request(method, url, **new_kwargs)
        # We may need to perform a token refresh.
        if response.status_code == requests.codes.unauthorized and self.refresh_session():
            new_kwargs = self.add_bearer_token(**kwargs)
            response = requests.request(method, url, **new_kwargs)

        return response
