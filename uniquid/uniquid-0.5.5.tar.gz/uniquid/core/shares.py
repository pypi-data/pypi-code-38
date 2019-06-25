# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import json
import requests
import jsonschema
import uniquid.core.constants as constants
import uniquid.core.schema as schema
import uniquid.core.helper as helper


class Shares:
    """Implements all commands related to device sharing across orgs.
    """

    def __init__(self, in_console, in_login_mgr):
        """Initialise an instance of the class."""
        self._console = in_console
        self._login_mgr = in_login_mgr

    def list_shares(self, in_direction, in_org):
        """List all shared devices.

        Function is complex because of the way the :orgId routing
        parameter can be used in the /api/v1/shares endpoint. Where possible,
        function trys to use the Orchestrator to filter based on orgId
        rather than filtering in the client.

        Arguments:
        in_direction -- Direction of sharing of the devices.
        in_org -- ID of a Organization to filter devices by.
        """
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # retrieve the device info from the server using HTTP API. if
        # possible, filter by org Id on server.
        org_string = ''
        if (in_direction == constants.SHARE_DIR_IN and
                in_org and
                len(in_org) > 0):
            org_string = in_org
        elif (in_direction == constants.SHARE_DIR_OUT):
            org_string = self._login_mgr.get_org_id()
        elif (in_direction == constants.SHARE_DIR_BOTH):
            pass
        # retrieve share objects from server
        try:
            url_string = 'http://{0}:{1}/api/v1/shares/{2}'
            url = url_string.format(self._login_mgr.get_api_ip(),
                                    self._login_mgr.get_api_port(),
                                    org_string)
            cookies = dict(JSESSIONID=session_key)
            response = requests.get(url, cookies=cookies)
            if (response.status_code == 200
                    and isinstance(response.json(), list)):
                # filter the items based on sharing direction
                filtered = list()
                if in_direction != constants.SHARE_DIR_BOTH:
                        filtered = helper.filter_list(response.json(),
                                                      'shareType',
                                                      in_direction)
                else:
                    filtered = response.json()
                # when listing devices which are shared both inwards and
                # outwards and filtering on org id, must filter both the
                # orgId and the ownerId.
                if (in_direction == constants.SHARE_DIR_BOTH and
                        in_org and
                        len(in_org) > 0):
                    filtered_in = helper.filter_list(filtered,
                                                     'ownerId',
                                                     in_org)
                    filtered_out = helper.filter_list(filtered,
                                                      constants.KEY_ORG_ID,
                                                      in_org)
                    filtered.clear()
                    filtered.extend(filtered_in)
                    filtered.extend(filtered_out)
                elif (in_direction == constants.SHARE_DIR_OUT and
                      in_org and
                      len(in_org) > 0):
                    filtered_out = helper.filter_list(filtered,
                                                      constants.KEY_ORG_ID,
                                                      in_org)
                    filtered.clear()
                    filtered.extend(filtered_out)
                self._console.print_objects(filtered)
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                        + str(response.status_code) + ']')
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)

    def create_shares(self, in_json):
        """Request that multiple devices are shared with another org.

            Arguments:
            in_json -- JSON sting describing a list of share object(s).
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
            jsonschema.validate(json_data, schema.NEW_SHARE_SCHEMA)
            assert isinstance(json_data, list)
        except (jsonschema.exceptions.ValidationError,
                json.decoder.JSONDecodeError) as e:
            self._console.exception(constants.ERR_INVALID_JSON + ': ' + str(e))
        # post json to server
        url_string = 'http://{0}:{1}/api/v1/shares'
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
                    self._console.error(constants.TXT_SHARE_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_LOGIN_REJECTED)
                elif response.status_code == 500:
                    self._console.error(constants.TXT_SHARE_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_SERVER_ERROR)
                else:
                    self._console.error(constants.TXT_SHARE_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                            + str(response.status_code) + ']')
            self._console.ok(constants.TXT_SHARE_CREATED + str(count))
        except requests.exceptions.ConnectionError:
            self._console.error(constants.TXT_SHARE_INTERRUPTED
                                + str(count))
            self._console.exception(constants.ERR_NO_RESPONSE)

    def delete_shares(self, in_json):
        """Request the removal of sharing of own devices with another org.

        Arguments:
        in_json -- JSON sting describing a list of share object(s).
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
            jsonschema.validate(json_data, schema.DELETE_SHARES_SCHEMA)
            assert isinstance(json_data, list)
        except (jsonschema.exceptions.ValidationError,
                json.decoder.JSONDecodeError) as e:
            self._console.exception(constants.ERR_INVALID_JSON + ': ' + str(e))
        # post json to server
        url_string = 'http://{0}:{1}/api/v1/shares/{2}'
        cookies = dict(JSESSIONID=session_key)
        count = 0
        try:
            for share_id in json_data:
                url = url_string.format(self._login_mgr.get_api_ip(),
                                        self._login_mgr.get_api_port(),
                                        str(share_id))
                response = requests.delete(url, cookies=cookies)
                if response.status_code == 200:
                    count = count + 1
                elif response.status_code == 401:
                    self._console.error(constants.TXT_SHARE_DEL_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_LOGIN_REJECTED)
                elif response.status_code == 404:
                    self._console.error(constants.TXT_SHARE_DEL_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_NO_SHARE + share_id)
                elif response.status_code == 500:
                    self._console.error(constants.TXT_SHARE_DEL_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_SERVER_ERROR)
                else:
                    self._console.error(constants.TXT_SHARE_DEL_INTERRUPTED
                                        + str(count))
                    self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                            + str(response.status_code) + ']')
            self._console.ok(constants.TXT_SHARE_DELETED + str(count))
        except requests.exceptions.ConnectionError:
            self._console.error(constants.TXT_SHARE_DEL_INTERRUPTED
                                + str(count))
            self._console.exception(constants.ERR_NO_RESPONSE)
