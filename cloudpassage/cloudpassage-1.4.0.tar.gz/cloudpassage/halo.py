"""HaloSession class.

Manage session configuration for interacting with the CloudPassage Halo API.
"""

import base64
import json
import sys
import threading
import time
from .utility import Utility as utility
import cloudpassage.sanity as sanity
from .exceptions import CloudPassageAuthentication
from .exceptions import CloudPassageValidation
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests


class HaloSession(object):
    """ Create a Halo API connection object.

    On instantiation, it will attempt to authenticate against the Halo API
    using the apikey and apisecret provided, together with any overrides passed
    in through kwargs.

    Args:
        apikey (str): API key, retrieved from your CloudPassage Halo account
        apisecret (str): API key secret, found with your API key in your
            CloudPassage Halo account

    Keyword Args:
        api_host (str): Override the API endpoint hostname. Defaults to
            api.cloudpassage.com.
        api_port (str): Override the API HTTPS port. Defaults to 443.
        proxy_host (str): Hostname or IP address of proxy
        proxy_port (str): Port for proxy.  Ignored if proxy_host is not set
        user_agent (str): Override for UserAgent string.  We set this so that
            we can see what tools are being used in the field and set our
            development focus accordingly.  To override the default, feel free
            to pass this kwarg in.
        integration_string (str): If set, this will cause the user agent
            string to include an identifier for the integration being used.

    """
    # Max number of retries for any reason
    max_retries = 5
    # Always retry on these statuses, within the requests session.
    # We retry for auth failure (401) within the SDK code. See try_wrapper().
    retry_statuses = [429, 500, 502, 503, 504]

    # pylint: disable=too-many-instance-attributes

    def __init__(self, apikey, apisecret, **kwargs):
        self.auth_endpoint = 'oauth/access_token'
        self.api_host = 'api.cloudpassage.com'
        self.api_port = 443
        self.sdk_version = utility.get_sdk_version()
        self.sdk_version_string = "Halo-Python-SDK/%s" % self.sdk_version
        self.user_agent = ''
        self.integration_string = ''
        self.key_id = apikey
        self.secret = apisecret
        self.auth_token = None
        self.auth_scope = None
        self.proxy_host = None
        self.proxy_port = None
        self.lock = threading.RLock()
        # Override defaults for proxy
        if "proxy_host" in kwargs:
            self.proxy_host = kwargs["proxy_host"]
            if "proxy_port" in kwargs:
                self.proxy_port = kwargs["proxy_port"]
        # Override defaults for api host and port
        if "api_host" in kwargs:
            self.api_host = kwargs["api_host"]
        if "api_port" in kwargs:
            self.api_port = kwargs["api_port"]
        if "integration_string" in kwargs:
            self.integration_string = kwargs["integration_string"]
        if "user_agent" in kwargs:
            self.user_agent = kwargs["user_agent"]
        else:
            self.user_agent = self.sdk_version_string
        if self.integration_string != '':
            self.user_agent = "%s %s" % (self.integration_string,
                                         self.user_agent)
        # Set up session and connection pool
        self.build_client()
        return None

    def build_client(self):
        """Build client object for class instantiation."""
        self.client = requests.Session()
        self.retries = Retry(total=self.max_retries,
                             status_forcelist=self.retry_statuses,
                             backoff_factor=1)
        self.halo_http_adapter = HTTPAdapter(pool_connections=1,
                                             pool_maxsize=10,
                                             max_retries=self.retries)
        self.session_mount = "https://%s:%s" % (self.api_host, self.api_port)
        self.client.mount(self.session_mount, self.halo_http_adapter)
        return None

    @classmethod
    def build_proxy_struct(cls, host, port):
        """Return a structure describing the environment's HTTP proxy settings.

        It returns a dictionary object that can be passed to the requests
        module.
        """

        ret_struct = {"https": ""}
        if port is not None:
            ret_struct["https"] = "http://{host}:{port}".format(host=host,
                                                                port=port)
        else:
            ret_struct["https"] = "http://{host}:8080".format(host=host)
        return ret_struct

    def get_auth_token(self, endpoint, headers):
        """Returns the oauth token and scope.

        Args:
            endpoint (str): Full URL, including schema.
            headers (dict): Dictionary, containing header with encoded
                credentials.
                Example: {"Authorization": str("Basic " + encoded)}

        Returns:
            tuple: token, scope
        """

        token = None
        scope = None
        resp = self.client.post(endpoint, headers=headers)
        if resp.status_code == 200:
            auth_resp_json = resp.json()
            token = auth_resp_json["access_token"]
            try:
                scope = auth_resp_json["scope"]
            except KeyError:
                scope = None
        if resp.status_code == 401:
            token = "BAD"
        return token, scope

    def authenticate_client(self):
        """This method attempts to set an OAuth token

        Call this method and it will use the API key and secret
        as well as the proxy settings (if used) to authenticate
        this HaloSession instance.

        """

        success = False
        prefix = self.build_endpoint_prefix()
        endpoint = prefix + "/oauth/access_token?grant_type=client_credentials"
        combined = "{key_id}:{secret}".format(key_id=self.key_id,
                                              secret=self.secret)
        if sys.version_info < (3, 0):
            encoded = base64.b64encode(bytes(combined))
        else:
            encoded = base64.b64encode(bytes(combined, 'utf8')).decode()
        auth_header = "Basic {}".format(encoded)
        headers = {"Authorization": auth_header}
        max_tries = 5
        for _ in range(max_tries):
            token, scope = self.get_auth_token(endpoint, headers)
            if token == "BAD":
                # Add message for IP restrictions
                exc_msg = "Invalid credentials- can not obtain session token."
                raise CloudPassageAuthentication(exc_msg)
            if token is not None:
                self.auth_token = token
                self.auth_scope = scope
                success = True
                break
            else:
                time.sleep(1)
        self.client.headers.update(self.build_header())
        return success

    def build_endpoint_prefix(self):
        """This constructs everything to the left of the file path in the URL.

        """
        if not sanity.validate_api_hostname(self.api_host):
            error_message = "Bad API hostname: %s" % self.api_host
            raise CloudPassageValidation(error_message)
        prefix = "https://{host}:{port}".format(host=self.api_host,
                                                port=self.api_port)
        return prefix

    def build_header(self):
        """This constructs the auth header, required for all API interaction.

        """
        authstring = "Bearer " + self.auth_token
        header = {"Authorization": authstring,
                  "Content-Type": "application/json",
                  "User-Agent": self.user_agent,
                  "Accept-Encoding": "gzip"}
        return header

    def interact(self, verb, endpoint, params=None, reqbody=None):
        """This method allows us to wrap common Halo interaction functionality.

        Most exceptions will be caught and validated here, and if retries fail,
        those exceptions will be raised again for catching at a higher level.

        Args:
            verb (str): get, post, put, or delete.
            endpoint (str): URL- everything past api.cloudpassage.com.
            params (list of dict): This is a list of dictionary objects,
                represented like this: [{"k1": "two,too"}]
            reqbody (dict): Dictionary to be converted to JSON for insertion
                as payload for request.

        Returns:
            response object
        """
        # Build the complete URL
        url = "%s%s" % (self.build_endpoint_prefix(), endpoint)
        # Set up for try/retry
        success = False
        # If we've not authenticated the session, we do it now
        if self.auth_token is None:
            self.authenticate_client()
        success, response, exception = self.try_wrapper(verb, url, params,
                                                        reqbody)
        if success:
            return response
        raise exception

    def try_wrapper(self, verb, url, params, reqbody):
        """Wraps tries.

        Args:
            endpoint (str): Path part of URL.
            params (list of dict): URL params.
            reqbody (dict): Request body.

        Returns:
            success (bool)
            response (requests.response)
            exception (Exception)
        """
        verb_mapping = {'get': self.client.get,
                        'post': self.client.post,
                        'put': self.client.put,
                        'delete': self.client.delete}
        # Raise ValueError if invalid verb is used
        if verb not in verb_mapping:
            raise ValueError("Invalid HTTP verb for Halo API: %s" % verb)
        if self.auth_token is None:
            self.authenticate_client()
        success, response, exception = self.get_response(verb_mapping[verb],
                                                         verb, url, params,
                                                         reqbody)
        if response.status_code == 401:  # Try to reauth once.
            self.authenticate_client()
            success, response, exception = self.get_response(verb_mapping[verb],  # NOQA
                                                             verb, url, params,
                                                             reqbody)
        return success, response, exception

    def get_response(self, client_method, verb, url, params, reqbody):
        """Base method for getting response from Halo API.

        Args:
            client_method (requests.Session() method): This method is what
                performs the actual interaction with the Halo API. Example:
                ``self.connection.client.get``
            verb (str): The HTTP verb used in interacting with the Halo API.
            url (str): Complete URL for request.
            params (list): URL params in a list of dictionaries.
            reqbody (dict): Body of put/post request

        Returns:
            success (bool)
            response (requests.response)
            exception (Exception)
        """
        if verb in ['get', 'delete']:
            response = client_method(url, params=params)
        else:
            response = client_method(url, data=json.dumps(reqbody))
        success, exception = utility.parse_status(url, response.status_code,
                                                  response.text)
        return success, response, exception
