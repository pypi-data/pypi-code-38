# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
import requests
import jsonschema
import uniquid.core.constants as constants
import uniquid.core.schema as schema


class Contracts:
    """Implements all commands related to contracts.
    """

    def __init__(self, in_console, in_login_mgr):
        """Initialise an instance of the class."""
        self._console = in_console
        self._login_mgr = in_login_mgr

    def create_contracts(self, in_json):
        """Create new contracts.

            Arguments:
            in_json -- JSON sting with a list of contract objects.
        """
        if in_json is None:
            self._console.exception(constants.exception('Internal. ' +
                                                        'Missing JSON.'))
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # validate json before bothering the backend
        json_data = None
        try:
            json_data = json.loads(in_json)
            jsonschema.validate(json_data, schema.NEW_CONTRACT_SCHEMA)
        except (jsonschema.exceptions.ValidationError,
                json.decoder.JSONDecodeError) as e:
            self._console.exception(constants.ERR_INVALID_JSON + ': ' + str(e))
        # post json to server
        url_string = 'http://{0}:{1}/api/v1/contracts'
        url = url_string.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port())
        cookies = dict(JSESSIONID=session_key)
        count = 0
        try:
            for obj in json_data:
                response = requests.post(url, cookies=cookies, json=obj)
                if response.status_code == 200:
                    count = count + 1
                elif response.status_code == 401:
                    self._console.ok(constants.TXT_CONTRACT_INTERRUPTED
                                          + str(count))
                    self._console.exception(constants.ERR_LOGIN_REJECTED)
                elif response.status_code == 500:
                    self._console.ok(constants.TXT_CONTRACT_INTERRUPTED
                                          + str(count))
                    self._console.exception(constants.ERR_SERVER_ERROR)
                else:
                    self._console.ok(constants.TXT_CONTRACT_INTERRUPTED
                                          + str(count))
                    self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                            + str(response.status_code) + ']')
            self._console.ok(constants.TXT_CONTRACT_CREATED + str(count))
        except requests.exceptions.ConnectionError:
            self._console.ok(constants.TXT_CONTRACT_INTERRUPTED
                                  + str(count))
            self._console.exception(constants.ERR_NO_RESPONSE)
        self._console.ok(constants.TXT_CONTRACT_CREATED_ALL)

    def list_contracts(self):
        """List all contracts.
        """
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # retrieve the device info from the server using HTTP API
        url_string = 'http://{0}:{1}/api/v1/contracts'
        url = url_string.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port())
        cookies = dict(JSESSIONID=session_key)
        try:
            response = requests.get(url, cookies=cookies)
            if (response.status_code == 200
                    and isinstance(response.json(), list)):
                self._console.print_objects(response.json())
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                        + str(response.status_code) + ']')
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)

    def show_contract(self, in_txid):
        """Show a single contract.

        Arguments:
        in_txid -- Transaction ID corresponding to the contract.
        """
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # retrieve the device info from the server using HTTP API
        url_string = 'http://{0}:{1}/api/v1/contracts'
        url = url_string.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port())
        cookies = dict(JSESSIONID=session_key)
        try:
            response = requests.get(url, cookies=cookies)
            if (response.status_code == 200
                    and response.json()):
                all_list = response.json()
                matched = None
                for contract in all_list:
                    if in_txid == contract.get('txid'):
                        matched = contract
                        break
                if matched:
                    self._console.print_objects(matched)
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                        + str(response.status_code) + ']')
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)

    def delete_contract(self, in_json):
        """Create a new contract.

            Arguments:
            in_json -- JSON sting with array of TXIDS.
        """
        if in_json is None:
            self._console.exception(constants.exception('Internal. ' +
                                                        'Missing JSON.'))
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # validate json before bothering the backend
        json_data = None
        try:
            json_data = json.loads(in_json)
            jsonschema.validate(json_data, schema.DELETE_CONTRACT_SCHEMA)
        except (jsonschema.exceptions.ValidationError,
                json.decoder.JSONDecodeError) as e:
            self._console.exception(constants.ERR_INVALID_JSON + ': ' + str(e))
        # post json to server, once per contract
        for txid in json_data:
            url_string = 'http://{0}:{1}/api/v1/contracts/{2}'
            url = url_string.format(self._login_mgr.get_api_ip(),
                                    self._login_mgr.get_api_port(),
                                    txid)
            cookies = dict(JSESSIONID=session_key)
            try:
                response = requests.delete(url,
                                           cookies=cookies,
                                           json=json_data)
                if response.status_code == 200:
                    self._console.ok(constants.TXT_CONTRACT_DELETED
                                     + str(txid))
                elif response.status_code == 401:
                    self._console.exception(constants.ERR_LOGIN_REJECTED)
                elif response.status_code == 404:
                    self._console.exception(constants.ERR_NO_CONTRACT)
                elif response.status_code == 500:
                    self._console.exception(constants.ERR_SERVER_ERROR)
                else:
                    self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                            + str(response.status_code) + ']')
            except requests.exceptions.ConnectionError:
                self._console.exception(constants.ERR_NO_RESPONSE)
        self._console.ok(constants.TXT_CONTRACT_DELETED_ALL)
