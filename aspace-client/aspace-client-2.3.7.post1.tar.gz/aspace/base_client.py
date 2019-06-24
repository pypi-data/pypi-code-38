r"""
Contains the BaseASpaceClient class.
"""

import configparser
import requests
import time
import urllib

from aspace import constants


class BaseASpaceClient(requests.Session):
    """
    Extends the Session class from the requests Python library, adding
    methods that relate to 
    """

    def __init__(self, api_host: str = constants.DEFAULT_API_HOST,
                 username: str = constants.DEFAULT_USERNAME,
                 password: str = constants.DEFAULT_PASSWORD,
                 auto_auth=True):
        """
        Initializes a new ArchivesSpace client.

        :api_host: Url used to connect to the API of the ArchivesSpace 
        instance. Trailing slashes are not required.

        :username: Username of an ASpace user account that has access
        to the API.

        :password: Password of the ASpace user account.

        :auto_auth: Specifies whether the client automatically logs
        sends an authentication request to ArchivesSpace on initialization.
        This should be turned off in cases where the implementing program
        needs to wait for the ArchivesSpace instance to spin up.
        """

        super().__init__()

        self.aspace_api_host = api_host.strip()
        self.aspace_username = username
        self.aspace_password = password

        # In order to make sure that relative endpoints can be predictably
        # concatenated onto the end of the base url, the url needs to end in a
        # slash.
        if not self.aspace_api_host.endswith('/'):
            self.aspace_api_host += '/'

        self.headers['Accept'] = 'application/json'

        if auto_auth:
            self.authenticate()

    @classmethod
    def init_from_config(cls, config: configparser.ConfigParser, 
                         section='aspace_credentials', auto_auth=False):
        """
        Initializes an instance of any subclass of BaseASpaceClient from an
        instance of the `configparser.ConfigParser` builtin Python config
        parser. The following keys must be set under the specified `section`
        of the specified `config`. If any are not set, the initializer will
        use defaults from the `constants` module.

        `"api_host"`: Url used to connect to the API of the ArchivesSpace 
        instance. Trailing slashes are not required.

        `"username"`: Username of an ASpace user account that has access
        to the API.

        `"password"`: Password of the ASpace user account.
        """

        def aspace_credential(term, default=None):
            return config.get(section, term, fallback=default)

        _self = cls(
            api_host=aspace_credential(
                'api_host', constants.DEFAULT_API_HOST),

            username=aspace_credential(
                'username', constants.DEFAULT_USERNAME),

            password=aspace_credential(
                'password', constants.DEFAULT_PASSWORD),

            auto_auth=auto_auth,
        )

        return _self

    def prepare_request(self, request: requests.Request):
        """
        Overrides and extends the `prepare_request` function from
        `requests.sessions.Session`.
        """

        # In order to make sure that relative endpoints can be predictably
        # concatenated onto the end of the base url, the relative endpoint
        # needs to have no leading slashes.
        relative_uri = (
            request.url.lstrip(' /')
            if request.url else
            ''
        )

        request.url = urllib.parse.urljoin(self.aspace_api_host, relative_uri)
        return super().prepare_request(request)

    def send(self, request: requests.PreparedRequest, **kwargs):
        """
        Override of Session.send, adding the ability to reauthenticate and
        replay the request, in the event that a 412 error is reached. An HTTP
        response code of 412 from ArchivesSpace indicates either `SESSION_GONE`
        or `SESSION_EXPIRED`.
        """

        resp = super().send(request, **kwargs)

        # Catches any responses that have a code of 412, indicating either
        # SESSION_GONE or SESSION_EXPIRED
        if resp.status_code == 412:
            self.authenticate()
            request.headers[constants.X_AS_SESSION] = (
                self.headers[constants.X_AS_SESSION]
            )
            resp = super().send(request, **kwargs)

        return resp

    def wait_until_ready(self, check_interval=5.0, max_wait_time=None,
                         on_fail=None, authenticate_on_success=False):
        """
        Periodically checks the `/` endpoint of the base api host until the
        API becomes ready, or until the max_wait_time is reached.

        Returns a reference to self once finished.

        :check_interval: Specifies the number of seconds in between each 
        check. Can be a non-integer interval of seconds. Defaults to 5.

        :max_wait_time: Specifies the maximum number of seconds that the
        function will wait until raising a ValueError. Optional, if `None`,
        then the function will wait indefinitely.

        :on_fail: If callable, will execute after every attempt, before 
        initiating the wait. Intended to be used for writing to the 
        program's logs.

        :authenticate_on_success: If True, the client will attempt to
        authenticate after a successful connection. Please see the docs
        for the `authenticate` method.
        """

        timer = 0

        while True:
            try:
                if self.get('/').ok:
                    break
            except requests.exceptions.ConnectionError:
                pass

            if max_wait_time is not None and timer > max_wait_time:
                raise Exception(
                    "The API could not be reached within the maximum allowed "
                    "time."
                )

            if callable(on_fail):
                on_fail()

            time.sleep(check_interval)
            timer += check_interval

        if authenticate_on_success:
            self.authenticate()

        return self

    def authenticate(self):
        """
        Authenticates the ArchivesSpace API client and sets up the
        X-ArchivesSpace-Session header for future requests. Returns
        the JSON response if the login was valid. Raises an error
        if the HTTP status code was not in the 200 series.
        """

        if constants.X_AS_SESSION in self.headers:
            del self.headers[constants.X_AS_SESSION]

        resp = self.post(
            'users/' + self.aspace_username + '/login',
            {'password': self.aspace_password}
        )

        assert resp.ok, (
            'Received {} while attempting to authenticate: {}'.format(
                resp.status_code,
                resp.text,
            )
        )

        session = resp.json()['session']
        self.headers[constants.X_AS_SESSION] = session
        return resp
