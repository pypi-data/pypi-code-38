# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
import jsonschema
import requests
import tempfile
import os
import stat

import uniquid.core.constants as constants
import uniquid.core.helper as helper

# components of name and path of temporary session file
_TEMP_DIR = 'com.uniquid'
_TEMP_FILE_PREFIX = 'login_tempfile_v1'
_TEMP_FILE_SUFFIX = '.tmp'
# path of default credentials file
_DEFAULT_CRED_FILE = os.path.join('~', '.uniquid', 'credentials.json')


class LoginManager:
    """Controls the state of the login process and caches the session key
    between invocations.
    """

    def __init__(self, in_console):
        """Initialise the login manager instance."""
        self._console = in_console
        self._api_ip = None
        self._api_port = None
        self._session_key = None
        self._org_id = None
        self._login_ip = None

    def connect(self,
                in_org_id=None,
                in_access_key=None,
                in_user=None,
                in_login_url=None,
                in_org_url=None,
                in_cred_file=None):
        """Connect to the UniquID servers.

            Create a connection with the UniquID servers.

            Retrieve the temporary session key which must be used for
            HTTP calls to the Orchestrator API.

            Arguments:
            in_org_id -- Unique identifier of the Organization.
            in_access_key -- API Key to authenticate with Orchestrator
            HTTP API.
            in_user -- Username in the Orchestrator.
            in_login_url -- IP address and port number of the UniquID
            Onboarding HTTP API. Must be in the
            format <ip address>:<port number>.
            in_org_url -- IP address  and port number of the Orchestrator
            HTTP API. Must be in the format <ip address>:<port number>.
            in_cred_file -- Path to credentials file.
        """
        self._check_args(in_org_id, in_access_key, in_user, in_login_url,
                         in_org_url, in_cred_file)
        # access key and user may come from credentials file
        actual_access_key = in_access_key
        actual_user = in_user
        # check if a credential file exists
        cred_file = None
        credentials = None
        if in_cred_file:
            cred_file = self._get_user_cred_file(in_cred_file)
        else:
            cred_file = self._get_default_cred_file()
        if cred_file:
            self._fix_file_permissions(os.path.realpath(cred_file.name))
            credentials = self._read_cred_file(cred_file)
        # must specify user/key or credential file
        if (in_access_key is None and
                credentials is None):
            self._console.exception(constants.ERR_MISSING_API_KEY)
        elif (in_user is None and
                credentials is None):
            self._console.exception(constants.ERR_MISSING_USERNAME)
        # command line organization take precedence
        if in_org_id is not None:
            # user specified an org so start login from beginning
            self._api_ip = None
            self._api_port = None
            self._session_key = None
            self._org_id = in_org_id
            self._write_temp_file()
        else:
            # re-use last org login
            self._read_temp_file()
        # decide which organization to use
        if (in_org_id is None and
                credentials is not None):
            self._org_id = credentials['organization']
            self._write_temp_file()
        # decide which user to use
        if in_user is not None:
            actual_user = in_user
        else:
            actual_user = credentials['user']
        # decide which access key to use
        if in_access_key is not None:
            actual_access_key = in_access_key
        else:
            actual_access_key = credentials['accessKey']
        # address of HTTP API used to query the Orchestrator address
        login_address = None
        # address of orchestrator HTTP API for the organization
        orch_address = None
        try:
            # parse the IP address of the Onboarding HTTP API. Use the value
            # passed as an argument or use a default URL.
            login_address = helper.parse_url(in_login_url,
                                             constants.UNIQUID_LOGIN_IP,
                                             constants.UNIQUID_LOGIN_PORT)
            # save the ip address of login server
            if login_address['ip'] is not None:
                self._login_ip = login_address['ip']
            # retrieve IP address from Onboarding API. if user passes the
            # IP address and port of the Orchestrator, bypass the query to
            # the Onboarding API.
            if in_org_url is None:
                orch_address = self._get_orchestrator(
                                        in_org=self._org_id,
                                        in_login_ip=login_address['ip'],
                                        in_login_port=login_address['port'])
            if orch_address:
                self._api_ip = orch_address.get('publicIp')
                self._api_port = orch_address.get('port',
                                                  constants.ORCHESTRATOR_PORT)
                # check orchestrator is not being started
                if ('status' in orch_address and
                        orch_address['status'] != 'Ready'):
                    self._console.ok(constants.TXT_LOGIN_FAIL_ORCH_SPINUP)
                    self._write_temp_file()
                    self._console.exception(constants.ERR_ORCHESTRATOR_SPINUP)
            elif in_org_url:
                orch_address = helper.parse_url(in_org_url, '', '')
                self._api_ip = orch_address['ip']
                self._api_port = orch_address['port']
            else:
                self._console.exception(constants.ERR_QUERY_ERROR)
        except RuntimeError as e:
            self._console.exception(str(e.args))
        # have a valid orchestrator so try and login
        self._login_orchestrator(actual_user, actual_access_key)
        # store the session state in persistant storage i.e. temp file
        if (self._org_id is not None):
            self._write_temp_file()
            self.print_status(False)
        else:
            self._console.exception(constants.ERR_LOGIN_REJECTED)

    def disconnect(self):
        """Disconnect from the UniquID server and delete cached values."""
        self._read_temp_file()
        if(self._api_ip is None or
                self._api_port is None):
            self._console.exception(constants.ERR_LOGOUT_ERROR)
        # inform server we are diconnecting
        url = 'http://{0}:{1}/api/v1/logout'.format(self._api_ip,
                                                    self._api_port)
        cookies = dict(JSESSIONID=self._session_key)
        response = None
        try:
            response = requests.get(url, cookies=cookies)
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)
        if response.status_code == 200:
            self._api_ip = None
            self._api_port = None
            self._session_key = None
            self._login_ip = None
            # the Organization ID is kept for future use and not cleared.
            self._write_temp_file()
            self.print_status(False)
        elif response.status_code == 401:
            self._console.exception(constants.ERR_LOGOUT_REJECTED)
        elif response.status_code == 500:
            self._console.exception(constants.ERR_SERVER_ERROR)
        else:
            self._console.exception(constants.ERR_LOGOUT_REJECTED)

    def print_status(self, in_verbose=False):
        """Print connection status and Orchestrator information.

            Arguments:
            in_verbose -- True if verbose information should be printed,
            otherwise False if a summary of status should be printed.
        """
        self._console.ok(constants.TXT_CONF_STATUS + '\t' + self._get_configuration_state())
        self._console.ok(constants.TXT_SESSION_STATUS + '\t' + self._get_session_state())
        self._read_temp_file()
        if self._org_id is not None:
            self._console.ok(constants.TXT_ORG_ID + '\t' + self._org_id)
        # print verbose information only if configured
        if (in_verbose and
                self._get_configuration_state() == constants.TXT_CONFIGURED_YES and
                self._get_session_state() == constants.TXT_SESSION_ALIVE):
            if(self._api_ip is None or
                    self._api_port is None):
                self._console.exception(constants.ERR_LOGOUT_ERROR)
            # request info from server
            url = 'http://{0}:{1}/api/v1/info'.format(self._api_ip,
                                                      self._api_port)
            cookies = dict(JSESSIONID=self._session_key)
            response = None
            try:
                response = requests.get(url, cookies=cookies)
            except requests.exceptions.ConnectionError:
                self._console.exception(constants.ERR_NO_RESPONSE)
            if (response.status_code == 200 and
                    response.json()):
                self._console.print_objects(response.json(), True)
                # assemble orchestrator info
                orch_info = dict()
                orch_info['orgIp'] = self.get_api_ip()
                orch_info['orgPort'] = self.get_api_port()
                self._console.print_objects(orch_info, True)
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR)

    def _get_configuration_state(self):
        """Get whether the client is configured or not.  A configured client
           has a valid session key and the URL of the orchestrator.

            Returns:
            String describing the configuration state.
        """
        retval = constants.TXT_CONFIGURED_NO
        self._read_temp_file()
        if (self._session_key is not None
                and self._api_ip is not None
                and self._api_port is not None):
            retval = constants.TXT_CONFIGURED_YES
        return retval

    def _get_session_state(self):
        """Get whether the client has a valid session connected
           an orchestrator.

            Returns:
            String describing the session state.
        """
        retval = constants.TXT_SESSION_DEAD
        self._read_temp_file()
        if (self._session_key is not None
                and self._api_ip is not None
                and self._api_port is not None):
            # request info from orchestrator
            url_string = 'http://{0}:{1}/api/v1/properties'
            url = url_string.format(self._api_ip,
                                    self._api_port)
            cookies = dict(JSESSIONID=self._session_key)
            response = None
            try:
                response = requests.head(url, cookies=cookies)
                if (response.status_code == 200):
                    retval = constants.TXT_SESSION_ALIVE
            except requests.exceptions.ConnectionError:
                self._console.exception(constants.ERR_NO_RESPONSE)
        return retval

    def is_session_alive(self):
        """Check if the client is configured, the session key is valid and
            the client can connect to the orchestrator.
        """
        retval = False
        if self._get_session_state() == constants.TXT_SESSION_ALIVE:
            retval = True
        return retval

    def get_session_key(self):
        """Get the Orchestrator session key.

            Returns:
            String holding the current saved session key. None is returned
            if there is no valid session key.
        """
        if self._session_key is None:
                self._read_temp_file()
        return self._session_key

    def get_api_ip(self):
        """Get the IP address of the Orchestrator API.

            Returns:
            String with the IP address.
        """
        if self._api_ip is None:
            self._read_temp_file()
        return self._api_ip

    def get_api_port(self):
        """Get the port provided by the Orchestrator.

            Returns:
            String with the port number.
        """
        if self._api_port is None:
            self._read_temp_file()
        return self._api_port

    def get_login_ip(self):
        """Get the IP address of the Login server.

            Returns:
            String with the IP address.
        """
        retval = ''
        if self._login_ip is None:
            self._read_temp_file()
        if self._login_ip is not None:
            retval = self._login_ip
        return retval

    def get_org_id(self):
        """Get the ID of the user's Organization account.

            Returns:
            String with the Organization ID.
        """
        if self._org_id is None:
            self._read_temp_file()
        return self._org_id

    def _check_args(self,
                    in_org_id=None,
                    in_access_key=None,
                    in_user=None,
                    in_login_url=None,
                    in_org_url=None,
                    in_cred_file=None):
        """Check that the correct combination of arguments and options
            are passed to the function connect. Throws an exception if an
            incorrect argument or option combination is found.
            Arguments:
            Must be the exact same as the connect method.
            Throws:
            Exception if invalid argument combination is specified.
        """
        if (in_cred_file is not None and
                in_org_id is not None):
            self._console.exception(constants.ERR_CRED_ORG)
        elif (in_cred_file is not None and
              in_user is not None):
            self._console.exception(constants.ERR_CRED_USER)
        elif (in_cred_file is not None and
              in_access_key is not None):
            self._console.exception(constants.ERR_CRED_KEY)
        elif (in_org_id is not None and
              in_org_url is not None):
            self._console.exception(constants.ERR_ORG_ID_URL)
        elif (in_login_url is not None and
              in_org_url is not None):
            self._console.exception(constants.ERR_LOGIN_ORG_URL)

    def _get_orchestrator(self,
                          in_org=None,
                          in_login_ip=constants.UNIQUID_LOGIN_IP,
                          in_login_port=constants.UNIQUID_LOGIN_PORT):
        """Get the IP Address and the Port Number of the Orchestrator
            Public HTTP API.

            Arguments:
            in_org -- Organization ID.
            in_login_ip -- IP address of the Onboarding HTTP API. Uses a
            hardcoded IP Address if none is provided by the caller.
            in_login_port -- Port number of the Onboarding HTTP API. Uses a
            hardcoded Port Number if none is provided by the caller.
            Returns:
            JSON object describing IP address of the Orchestrator.
        """
        retval = None
        # must know Organization ID to get Orchestrator IP
        if in_org is None:
            self._console.exception(constants.ERR_MISSING_ORG_ID)
        elif in_login_ip is None:
            self._console.exception('Internal. Missing IP address.')
        elif in_login_port is None:
            self._console.exception('Internal. Missing port number.')
        headers = {'Content-Type': 'application/json'}
        # retrieve the orchestrator address from the server
        url_string = 'http://{0}:{1}/api/v1/instances/{2}'
        url = url_string.format(in_login_ip,
                                in_login_port,
                                in_org)
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if (constants.KEY_ORG_ID in data and
                            not data[constants.KEY_ORG_ID] is None):
                        retval = data
                except ValueError:
                    self._console.exception(constants.ERR_QUERY_ERROR)
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            else:
                self._console.exception(constants.ERR_ORG_NOT_FOUND
                                        + str(self._org_id))
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)
        return retval

    def _login_orchestrator(self, in_user, in_access_key):
        """Login to the orchestrator instance for the organization.
        """
        is_orch_resp_ok = False
        # login and retrieve session id
        headers = {'Content-Type': 'application/json'}
        # retrieve the session key from the server
        url = 'http://{0}:{1}/api/v1/login'.format(self._api_ip,
                                                   self._api_port)
        data = {'userId': in_user, 'password': in_access_key}
        response = None
        try:
            response = requests.post(url,
                                     data=json.dumps(data),
                                     headers=headers)
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)
        if response.status_code == 200:
            is_orch_resp_ok = True
        elif response.status_code == 401:
            self._console.exception(constants.ERR_LOGIN_REJECTED)
        elif response.status_code == 500:
            self._console.exception(constants.ERR_SERVER_ERROR)
        else:
            self._console.exception(constants.ERR_LOGIN_REJECTED)
        # server must return a valid session key
        if (is_orch_resp_ok
                and response is not None
                and response.headers is not None
                and 'Set-Cookie'in response.headers
                and response.headers['Set-Cookie'] is not None
                and response.cookies is not None):
                    self._session_key = response.cookies['JSESSIONID']
        else:
            self._console.exception(constants.ERR_LOGIN_REJECTED)

    def _fix_file_permissions(self, in_file_path):
        """Check and fix, if required, the permissions of the credentials
           file.
           Arguments:
           in_cred_file -- File path of the credentials file.
        """
        assert in_file_path != None
        if os.path.isfile(in_file_path):
            os.chmod(in_file_path, stat.S_IRUSR)
        else:
            self._console.error('Credentials file is missing from path: ' + in_file_path)

    def _read_temp_file(self):
        """Read the saved state from the temporary file.

        Function reads the saved state from the temporary file and
        writes values to data members of this object.
        """
        indata = None
        fd = self._get_temp_file('r')
        if fd is not None:
            with fd as infile:
                indata = json.load(infile)
                if 'session_key' in indata and indata['session_key']:
                    self._session_key = indata['session_key']
                if 'api_ip' in indata and indata['api_ip']:
                    self._api_ip = indata['api_ip']
                if 'api_port' in indata and indata['api_port']:
                    self._api_port = indata['api_port']
                if 'login_ip' in indata and indata['login_ip']:
                    self._login_ip = indata['login_ip']
                # don't overwrite org id if already in memory
                if (self._org_id is None and
                        'org' in indata and
                        indata['org']):
                    self._org_id = indata['org']
        else:
            # failed to open the temp file
            self._session_key = None
            self._api_ip = None
            self._api_key = None
            self._org_id = None
            self._login_ip = None

    def _write_temp_file(self):
        """Write the state of login to temporary file.
        """
        fd = self._get_temp_file('w')
        data = {}
        if self._session_key is not None:
            data['session_key'] = self._session_key
        if self._api_ip is not None:
            data['api_ip'] = self._api_ip
        if self._api_port is not None:
            data['api_port'] = self._api_port
        if self._org_id is not None:
            data['org'] = self._org_id
        if self._login_ip is not None:
            data['login_ip'] = self._login_ip
        with fd as outfile:
            json.dump(data, outfile)
            self._close_temp_file(outfile)

    def _get_temp_path(self):
        """Get the full path of the temporary file used to persist data.
            Returns:
            String with the full path to the temporary file."""
        retval = os.path.join(tempfile.gettempdir(),
                              _TEMP_DIR,
                              _TEMP_FILE_PREFIX + _TEMP_FILE_SUFFIX)
        return retval

    def _get_temp_file(self, in_mode='r'):
        """Get a handle to the temporary file that stores the session key.

            Arguments:
            in_mode -- 'r' to open in read mode. 'w' to open in write mode.
            Returns:
            A valid file handle or None.
        """
        retval = None
        if not (in_mode is 'r' or in_mode is 'w'):
            self._console.exception('Internal: Incorrect file mode specified.')
        # create temp dir if doesn't exist
        dir_path = os.path.dirname(self._get_temp_path())
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # if temp file already exists, use it.
        temp_path = self._get_temp_path()
        try:
            retval = open(temp_path, in_mode)
        except OSError:
            retval = None
        except (IOError, OSError):
            self._console.exception(constants.ERR_TEMP_FILE)
        return retval

    def _close_temp_file(self, in_fd):
        """Close the file handle for the temporary file.

            Arguments:
            in_fd -- File descriptor.
        """
        in_fd.close()

    def _get_default_cred_file(self):
        """Get a handle to the credential file, if one exists, in the
           configuration directory of the user's home directory.
           Returns:
           File handle or None if the file does not exist.
        """
        retval = None
        default_path = os.path.expanduser(_DEFAULT_CRED_FILE)
        try:
            retval = open(default_path, 'r')
        except (IOError, OSError):
            # it is ok for file to not exist on system
            retval = None
        except PermissionError:
            self._console.exception(constants.ERR_FILE_PERM+default_path)
        return retval

    def _get_user_cred_file(self, in_cred_path):
        """Get a handle to the credential file, if one exists, which the
           user specified as an option.
           Returns:
           File handle.
           Throws:
           Exception if file does not exist.
        """
        retval = None
        try:
            retval = open(in_cred_path, 'r')
        except (IOError, OSError):
            # file must exist and be readable
            self._console.exception(constants.ERR_FILE_OPEN + in_cred_path)
        except PermissionError:
            self._console.exception(constants.ERR_FILE_PERM + in_cred_path)
        return retval

    def _read_cred_file(self, in_file):
        """Read the credentials from a credentials file.

        Function reads the organization, access key and user from a saved
        file and returns a dictionary with the values.
        Arguments:
        in_file -- File descriptor of credentials file.
        Returns:
        A dictionary object with the organization, access key and user.
        """
        assert in_file is not None
        indata = None
        try:
            if in_file is not None:
                with in_file as infile:
                    indata = json.load(infile)
                    jsonschema.validate(indata, constants.CREDENTIALS_SCHEMA)
            else:
                self._console.exception('Internal: None passed to method.')
        except jsonschema.exceptions.ValidationError as e:
            self._console.exception(constants.ERR_BAD_CRED_FILE)
        if indata['version'] != constants.MAX_VERSION_CREDENTIALS:
            self._console.exception(constants.ERR_CRED_FILE_VERSION)
        assert indata is not None
        return indata
