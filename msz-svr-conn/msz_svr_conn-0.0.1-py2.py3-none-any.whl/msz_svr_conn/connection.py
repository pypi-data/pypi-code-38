import copy
import decimal
import json
import logging
import requests
import time
import uuid
import warnings

from requests.exceptions import ConnectionError

from . import exceptions


LOGGER = logging.getLogger(__name__)


class ApiConnection(object):

    """Handles authenticating and accessing a resource server.

    Parameters:
        host (str): resource server location in the format ``host[:port]``
        oauth_id (str): OAuth client ID
        oauth_secret (str): OAuth client secret
        user_email (str): User's email
        user_password (str): User's password
        scheme (str): ``http`` or ``https`` defaults to ``http``
        token_url (str): Endpoint to get tokens from the auth_server
        scopes (list(str)): an array of strings describing the scopes.
        auth_retries (int or None): number of times to retry/reauthenticate
            a request if authentication failed. Use -1 for infinite retries.
        auth_retry_delay (float): (seconds) how long to wait before
            retrying auth failures. Use 0.0 to mean no delay.
        timeout_retries (int or None): number of times to retry
            a request if it timed out. Use -1 for infinite retries.
        timeout_retry_delay (float): (seconds) how long to wait before
            retrying timeout failures. Use 0.0 to mean no delay.
        connect_retries (int or None): number of times to retry a request
            if there's a connection error. Use -1 for infinite retries.
        connect_retry_delay (float): (seconds) how long to wait before
            retrying a request that failed on a connection error.
            Use 0.0 to mean no delay.
    """

    RequestFailure = exceptions.RequestFailure
    AuthFailure = exceptions.AuthFailure

    def __init__(self, host, oauth_id, oauth_secret, user_email,
                 user_password, scheme='https', token_url=None, scopes=None,
                 auth_retries=3, auth_retry_delay=1, timeout_retries=3,
                 timeout_retry_delay=1, connect_retries=3,
                 connect_retry_delay=1):
        """Authenticate the connection with the edgeserver."""
        LOGGER.debug(
            'Init connection: host={} oauth_id={} user_email={} \
            scheme={} token_url={} scopes={} auth_retries={} \
            auth_retry_delay={} timeout_retries={} \
            timeout_retry_delay={} connect_retries={} \
            connect_retry_delay={}'.format(
                host, oauth_id, oauth_secret, user_email, user_password,
                scheme, token_url, scopes, auth_retries, auth_retry_delay,
                timeout_retries, timeout_retry_delay, connect_retries,
                connect_retry_delay))
        assert scheme in ['http', 'https']
        self.host = host
        self.oauth_id = oauth_id
        self.oauth_secret = oauth_secret
        self.user_email = user_email
        self.user_password = user_password
        self.scheme = '{}://'.format(scheme)
        self.base_url = ApiConnection.urljoin(self.scheme, self.host)
        self.token_url = token_url
        self.auth_retries = auth_retries
        self.auth_retry_delay = auth_retry_delay
        self.timeout_retries = timeout_retries
        self.timeout_retry_delay = timeout_retry_delay
        self.connect_retries = connect_retries
        self.connect_retry_delay = connect_retry_delay

        self.base_headers = {
            'Accept': 'application/json, */*'
        }

        if self.token_url is not None:
            self.authenticate(self.token_url, scopes=scopes)

    def _get_token(self, token_url=None, refresh=False, scopes=None):
        """Retrieve access tokens from the authserver.

        Parameters:
            token_url (str): Location of the oauth2 provider's token endpoint
            refresh (bool): Whether to refresh an access token or get a new one
            scopes (list or None): Scopes required

        Returns:
            dict: A dictionary containing the access token, expiry,
                refresh token (optional), scopes(optional)

        Raises:
            exceptions.AuthFailure: if the authentication fails
            AssertionError: if scopes is not ``None`` or ``list``
            ValueError: if ``refresh`` is called before ``authenticate``
        """
        LOGGER.debug('Get token: token_url={} refresh={} scopes={}'.format(token_url, refresh, scopes))  # noqa

        assert (isinstance(scopes, (list, tuple))) or (scopes is None)

        if (not hasattr(self, 'credentials')) and (refresh is True):
            raise ValueError("authenticate not yet called")

        tk = self.token_url if token_url is None else token_url
        payload = {
            'client_id': self.oauth_id,
            'client_secret': self.oauth_secret,
        }
        if scopes is not None:
            payload['scope'] = " ".join(scopes)

        extra = (
            {
                'refresh_token': self.credentials['refresh_token'],
                'grant_type': 'refresh_token'
            }
            if refresh else
            {
                'username': self.user_email,
                'password': self.user_password,
                'grant_type': 'password',
            }
        )
        payload.update(extra)
        response = self.make_request(method="POST", url=tk, data=payload)

        if response.status_code != 200:
            errors = {
                'status_code': response.status_code,
                'response': response.text
            }
            msg = "Failed to authenticate. Error code {}: {}"
            msg = msg.format(response.status_code, response.text)
            raise self.__class__.AuthFailure(msg, errors)

        self.credentials = response.json()
        self.base_headers['Authorization'] = "{} {}".format(
            self.credentials['token_type'], self.credentials['access_token']
        )
        self.credentials['token_acquired'] = time.time()
        LOGGER.debug('Get token: credentials={}'.format(self.credentials))
        return self.credentials

    def authenticate(self, token_url=None, scopes=None):
        """Authenticate the client with the auth server.

        Parameters:
            token_url (str): Location of the oauth2 provider's token endpoint
            scopes (list or None): Scopes required

        Returns:
            dict: A dictionary containing the access token, expiry,
                refresh token (optional), scopes(optional)

        Raises:
            exceptions.AuthFailure: if the authentication fails
            AssertionError: if scopes is not ``None`` or ``list``
        """
        LOGGER.debug('Authenticate: token_url={} scopes={}'.format(token_url, scopes))  # noqa
        return self._get_token(token_url, refresh=False, scopes=scopes)

    def refresh(self, token_url=None, scopes=None):
        """Refresh the access token

        Parameters:
            token_url (str): Location of the oauth2 provider's token endpoint
            scopes (list or None): Scopes required

        Returns:
            dict: A dictionary containing the access token, expiry,
                refresh token (optional), scopes(optional)

        Raises:
            exceptions.AuthFailure: if the authentication fails
            AssertionError: if scopes is not ``None`` or ``list``
            ValueError: if ``refresh`` is called before ``authenticate``
        """
        LOGGER.debug('Refresh token: token_url={} scopes={}'.format(token_url, scopes))  # noqa
        return self._get_token(token_url, refresh=True, scopes=scopes)

    def serialize_dict_to_json(self, dictionary):
        """Serialize a dictionary to it's JSON equivalent.

        Parameters:
            dictionary (dict): a dictionary of serializable items

        Returns:
            str: JSON string

        Raises:
            TypeError: if the dictionary has an item that is not serializable
        """
        LOGGER.debug('Serialize dict to json: {}'.format(dictionary))

        def json_default(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()

            if isinstance(obj, uuid.UUID) or isinstance(obj, decimal.Decimal):
                return str(obj)

            msg = "Obj {} of Type {} is not serializable"
            msg = msg.format(obj, type(obj))
            raise TypeError(msg)

        return json.dumps(dictionary, default=json_default)

    def call_stub(self, url, method='GET', params=None, payload=None,
                  files=None, extra_headers=None, disable_json_parsing=False):
        """Make HTTP calls using URL stubs to the base_url"""
        LOGGER.debug(
            'Call Stub: url={} method={} params={} payload={} extra_headers={} disable_json_parsing={}'.format(  # noqa
                url, method, params, payload, extra_headers,
                disable_json_parsing
            )
        )
        full_url = ApiConnection.urljoin(self.base_url, url)
        return self.call(
            full_url, method, params=params, payload=payload, files=files,
            extra_headers=extra_headers,
            disable_json_parsing=disable_json_parsing,
            is_stub=False
        )

    def call(self, url, method='GET', params=None, payload=None, files=None,
             extra_headers=None, disable_json_parsing=False, is_stub=True):
        """Make HTTP call.

        Uses the HTTP client to make a HTTP request to the provided
        url with the provided data. also handles filling in of the
        HTTP headers

        Parameters:
            url (str): the uri fragment to make the call to
            method (str): HTTP method to call
            params (dict): a dict to be sent as query parameters
            payload (dict): dict with the data to send with the call
                This will be serialized to json before being sent over.
            files (dict): dict with file data to send with the call
                e.g. {'model_file_field': open('path/file.pdf', 'rb')}
            extra_headers (dict): dict with any additional HTTP headers
                These will update the base headers.
            disable_json_parsing (bool): parse the response as json or not.
                If False, response will be returned as JSON object.
                If True, response will be returned as a different Content-Type.
            is_stub (bool): whether the url passed is a stub (to be
                concatenated with the base url) or a fully qualified url

        Returns:
            dict: dict if the response returned any json response

        Returns:
            None: None if nothing was returned by the response

        Raises:
            exceptions.RequestFailure: if response has a status code >= 400.
                These include server errors (500 and above).
        """
        LOGGER.debug(
            'Call: url={} method={} params={} payload={} extra_headers={} disable_json_parsing={} is_stub={}'.format(  # noqa
                url, method, params, payload, extra_headers,
                disable_json_parsing, is_stub
            )
        )
        headers = copy.deepcopy(self.base_headers)
        if extra_headers:
            headers.update(extra_headers)

        # let requests populate the Content-Type when uploading files with
        # multipart/form-data and boundary.
        if files:
            headers.pop('Content-Type', None)

        # don't serialize payload to dict when POSTing a file and data and set
        # Content-Type header to application/json
        if payload and not files:
            headers.update({
                'Content-Type': 'application/json'
            })
            payload = self.serialize_dict_to_json(payload)

        if is_stub:
            msg = (
                "use of url stubs will be removed from the (call) method "
                "in favour of the (call_stub) method"
            )
            warnings.warn(msg, PendingDeprecationWarning)
            url = ApiConnection.urljoin(self.base_url, url)

        response = self.make_request(
            method=method, url=url, params=params, data=payload, files=files,
            headers=headers)

        if self.auth_retries is not None:
            current_retries = self.auth_retries
            infinite_retries = self.auth_retries == -1
            while current_retries > 0 or infinite_retries:
                # auth HTTP status codes
                # 401 - Unauthorized
                # 403 - Forbidden
                if response.status_code in [401, 403]:
                    time.sleep(self.auth_retry_delay)
                    LOGGER.debug('Retrying on auth error')
                    if hasattr(self, 'credentials'):
                        # get new access token from refresh token
                        self.refresh()
                    else:
                        # authenticate using email and password
                        self.authenticate()
                    # update headers with the new Authorization header
                    headers.update(self.base_headers)
                    response = self.make_request(
                        method=method, url=url, params=params, data=payload,
                        files=files, headers=headers)
                    current_retries -= 1
                else:
                    break

        if self.timeout_retries is not None:
            current_retries = self.timeout_retries
            infinite_retries = self.timeout_retries == -1
            while current_retries > 0 or infinite_retries:
                # timeout HTTP status codes
                # 502 - Bad Gateway
                # 503 - Service Unavailable
                # 504 - Gateway Timeout
                if response.status_code in [502, 503, 504]:
                    time.sleep(self.timeout_retry_delay)
                    LOGGER.debug('Retrying on timeout error')
                    # send the request again
                    response = self.make_request(
                        method=method, url=url, params=params, data=payload,
                        files=files, headers=headers)
                    current_retries -= 1
                else:
                    break

        if response.status_code >= 400 or response.status_code >= 500:
            # raise custom exception to encapsulate our API
            errors = {
                'method': method,
                'url': url,
                'status_code': response.status_code,
                'response': response.text,
                'payload': payload,
                'request': response.request
            }
            msg = "API request {} {} failed, Error Code {}: {}, Payload: {}"
            msg = msg.format(
                method, url, response.status_code, response.text, payload)
            raise self.__class__.RequestFailure(msg, errors)

        if disable_json_parsing:
            resp = response.content
            LOGGER.debug('Call: content={}'.format(resp))
        else:
            resp = response.json()
            LOGGER.debug('Call: json={}'.format(resp))

        return resp

    def make_request(self, *args, **kwargs):
        """Logic of making a request to a server

        All requests made by ApiConnection are done through this method
        """
        # take advantage of requests request method
        LOGGER.debug('Make request: args={} kwargs={}'.format(args, kwargs))
        current_retries = self.connect_retries
        infinite_retries = self.connect_retries == -1
        while True:
            try:
                response = requests.request(*args, **kwargs)
                break
            except ConnectionError:
                if self.connect_retries is None:
                    raise
                if current_retries <= 0 and not infinite_retries:
                    raise
                current_retries -= 1
                time.sleep(self.connect_retry_delay)
        LOGGER.debug(
            'Make request: status_code={} headers={} content={}'.format(
                response.status_code, response.headers, response.content))
        return response

    @staticmethod
    def urljoin(*urlparts):
        """Join url segments.

        A uniform way to concatenate urls

        For example::

            url = urljoin('http://', 'google.com', 'mail')
            print url
            # prints 'http://google.com/mail'

        Parameters:
            *urlparts (str): url segments to join

        Return:
            str: the full (combined) url
        """
        LOGGER.debug('Urljoin: urlparts={}'.format(urlparts))
        url = ''

        for part in urlparts:
            if part in ('', None):
                pass
            elif part == '/':
                if not url.endswith('/'):
                    url = "{}/".format(url)
            else:
                prt = str(part).strip().lstrip('/')
                if not url.endswith('/'):
                    f = '/' if url != '' or part[0] == '/' else ''
                    prt = "{}{}".format(f, prt)
                url = "{}{}".format(url, prt)
        return url
