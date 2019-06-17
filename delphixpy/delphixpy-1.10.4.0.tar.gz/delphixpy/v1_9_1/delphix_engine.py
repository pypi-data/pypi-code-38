# 
# Copyright 2014, 2019 by Delphix
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import time
from contextlib import contextmanager
from delphixpy.v1_9_1 import common
from delphixpy.v1_9_1 import exceptions
from delphixpy.v1_9_1 import http_client
from delphixpy.v1_9_1.job_context import JobMode
from delphixpy.v1_9_1.web import delphix as auth
from delphixpy.v1_9_1.web import session
from delphixpy.v1_9_1.web.vo import APISession, APIVersion, LoginRequest

REFRESH_LOGIN_TIMEOUT = 25  # Time before refreshing our login in minutes

API_LOCALE = 'en-US'
API_CLIENT = 'delphixpy'


def create_session(engine):
    """
    Create session.

    :param engine: DelphixEngine object
    """
    api_session = APISession()
    api_session.client = API_CLIENT
    api_session.locale = API_LOCALE
    api_version = APIVersion()
    api_version.major = 1
    api_version.minor = 9
    api_version.micro = 1
    api_session.version = api_version

    return session.set(engine, api_session)


class HttpMethod(object):
    """HTTP method enumeration"""
    POST = 'POST'
    GET = 'GET'


class HttpSession(object):
    """
    This class keeps a HTTP session
    """
    def __init__(self, host, client=http_client.HttpClient):
        """
        Create and initialize a new HttpSession

        :param host: The hostname of the engine
        :type host: str
        :param client: The class of the client used for perfoming HTTP requests
        """
        super(HttpSession, self).__init__()
        self._host = host
        self._cookie = None
        self._client = client(host)

    def _create_headers(self):
        """
        Return a list of headers to be sent to the engine
        """
        headers = {'Content-Type': 'application/json',
                   'User-Agent': "Delphix Python Agent"}
        if self._cookie:
            headers['Cookie'] = self._cookie
        return headers

    def _handle_response(self, request, request_method,
                         request_url, json_data=""):
        """
        Handle a response from a HTTP request

        :param request: Tuple (status, headers, data):
            status: HTTP status as an integer e.g. 404,
            headers: HTTP headers as a dictionary,
            data: HTTP data as raw data.
        :param request_method: A string describing the HTTP method used, e.g.
                              "POST".
        :param request_url: The URL to request as a string.
        """
        status, headers, data = request
        headers = dict((k.lower(), v) for k, v in headers.items())
        if status not in [http_client.OK, http_client.ACCEPTED]:
            msg = "HTTP status was %s when doing %s '%s' to '%s': %s"
            msg %= (status, request_method, json_data, request_url, data)
            raise exceptions.HttpError(value=msg, status=status, data=data)
        if headers and 'set-cookie' in headers:
            self._cookie = headers['set-cookie']
        return (status, headers, data)

    def post(self, path, data_to_post):
        """
        Perform a HTTP post request

        :param path: The path to the resource
        :type path: str
        :param data_to_post: The data_to_post to post as a dictionary
                             that can be transformed to a JSON object
        :type data_to_post: dict
        :returns: The response from the engine
        :rtype: dict
        """
        headers = self._create_headers()
        if data_to_post:
            jsondata = json.dumps(data_to_post)
        else:
            jsondata = ""
        response = self._client.post(path, jsondata, headers)
        return self._handle_response(response, HttpMethod.POST, path, jsondata)

    def get(self, path):
        """
        Perform a HTTP get request

        :param path: The path to the resource
        :type path: str
        :returns: The response from the engine
        :rtype: dict
        """
        headers = self._create_headers()
        response = self._client.get(path, headers)
        return self._handle_response(response, HttpMethod.GET, path)


class LoginHelper(object):
    """
    This class helps with logging in to the Delphix engine
    """
    def __init__(self, http_session, username, password, namespace):
        """
        Create and initialize new LoginHelper object

        :param http_session: The http_session session to use for performing
                             HTTP requests
        :type http_session: :class:`HttpSession`
        :param username: The username to use when logging in to the Delphix
                         engine
        :type username: str
        :param password: The password to use when logging in to the Delphix
                         engine
        :type password: str
        :param namespace: The namespace to use when logging in to the Delphix
                          engine
        :type namespace: str
        """
        super(LoginHelper, self).__init__()
        self._username = username
        self._password = password
        self._namespace = namespace
        self._http_session = http_session
        self._time_at_last_login = None

    API_VERSION = "1.9.1"

    def force_relogin(self):
        self._time_at_last_login = None

    def force_relogin_nonlazy(self):
        self.login()

    def login_if_needed(self):
        """
        Log in to the Delphix engine if it is needed. A login is needed
        if a domain has been created on the Delphix engine and there has been
        too long time since the last login.
        """
        if self._has_timed_out():
            self.login()

    def _parse_json(self, data):
        data = common.bytes_to_str(data)
        ret = json.loads(data)
        return ret

    def _has_timed_out(self):
        """
        Check if a login is needed because no requests have been made for a
        long time
        """
        if self._time_at_last_login is None:
            return True
        delta = (time.time() - self._time_at_last_login) / 60
        return delta >= REFRESH_LOGIN_TIMEOUT

    def login(self):
        """
        Perform the actual login
        """
        outer = self

        class EngineProxy():
            API_VERSION = outer.API_VERSION

            def post(self, url, data_to_post):
                _, _, body = outer._http_session.post(url, data_to_post)
                return outer._parse_json(body)
        login_request = LoginRequest()
        login_request.username = self._username
        login_request.password = self._password
        login_request.target = self._namespace
        auth.login(EngineProxy(), login_request)
        self._time_at_last_login = time.time()


class DelphixEngine(object):
    """
    This class represents the Delphix appliance
    """
    def __init__(self, address, user, password, namespace, use_https=False):
        self._address = address
        if use_https:
            self._http_session = HttpSession(
                address,
                client=http_client.HttpsClient
            )
        else:
            self._http_session = HttpSession(
                address
            )
        self._login_helper = LoginHelper(self._http_session, user, password, namespace)
        self._delphix_session = None

        self._default_login_helper = self._login_helper
        self._jobs = []
        self._job_contexts = []
        self._last_job = None

    API_VERSION = "1.9.1"

    def __repr__(self):
        return ("DelphixEngine(address='%s', delphix_session=%s)"
                % (self._address, self._delphix_session))

    @property
    def address(self):
        """
        Return the hostname or IP of the connected engine

        :rtype: str
        """
        return self._address

    def _create_session_if_needed(self):
        if not self._delphix_session:
            self._create_session()
            return True
        else:
            if self._login_helper._has_timed_out():
                self._create_session()
                return True
            return False

    def _create_session(self):
        outer = self

        class EngineProxy(object):
            API_VERSION = outer.API_VERSION

            def post(self, url, data_to_post):
                (_, _, body) = outer._http_session.post(url, data_to_post)
                return outer._parse_json(body)

        self._delphix_session = create_session(EngineProxy())

    def _parse_json(self, data):
        # Safely convert to str
        data = common.bytes_to_str(data)

        # Get rid of tabs since the Python JSON decoder cannot handle them
        data_without_tabs = data.replace('\t', '    ')
        return json.loads(data_without_tabs)

    def post(self, path, data_to_post):
        _, _, body = self._authenticate_and_perform(
            lambda: self._http_session.post(path, data_to_post))
        return self._parse_json(body)

    def get(self, path):
        _, _, body = self._authenticate_and_perform(
            lambda: self._http_session.get(path))
        return self._parse_json(body)

    def _authenticate_and_perform(self, action):
        self._create_session_if_needed()
        self._login_helper.login_if_needed()
        return action()

    def create_session(self):
        """
        Force creation of a new session
        """
        self._create_session()

    @contextmanager
    def authenticate_as(self, username, password, namespace):
        """
        Essentially performs a 'su' to a new domain- or system user.

        :param username: User to run under
        :type username: str
        :param password: Password of user to run under
        :type password: str
        :param namespace: Namespace to run under
        :type namespace: str
        """
        try:
            old_login_helper = self._login_helper
            self._login_helper = LoginHelper(self._http_session, username,
                                             password, namespace)
            yield
        finally:
            self._login_helper = old_login_helper

    def force_relogin(self):
        """
        Force the login helper to login again.
        """
        self._create_session()
        self._login_helper.force_relogin()

    def login(self):
        """
        Login to the Delphix engine.
        """
        self._create_session()
        self._login_helper.login()

    def clear_registered_job(self, job_ref_to_clear):
        """
        Take a list of job references to clear.
        """
        if self.is_async:
            while job_ref_to_clear in self.job_contexts[-1][1]:
                self.job_contexts[-1][1].remove(job_ref_to_clear)

    @property
    def is_async(self):
        if self.job_contexts:
            return self.job_contexts[-1][0] == JobMode.ASYNC
        return False

    @property
    def job_contexts(self):
        return self._job_contexts

    @property
    def last_job(self):
        return self._last_job

    @last_job.setter
    def last_job(self, new_val):
        self._last_job = new_val