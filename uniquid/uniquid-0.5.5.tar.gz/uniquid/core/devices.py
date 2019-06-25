# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

import requests
import uniquid.core.constants as constants
import uniquid.core.helper as helper


class Devices:
    """Implements all commands related to devices.
    """

    def __init__(self, in_console, in_login_mgr):
        """Initialise an instance of the class."""
        self._console = in_console
        self._login_mgr = in_login_mgr

    def show_device(self, in_xpub):
        """Show detailed information for one device.

            Arguments:
            in_xpub -- Public key which uniquely identifies a device.
        """
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # retrieve the device info from the server using HTTP API
        url_string = 'http://{0}:{1}/api/v1/devices/{2}'
        url = url_string.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port(),
                                in_xpub)
        cookies = dict(JSESSIONID=session_key)
        try:
            response = requests.get(url, cookies=cookies)
            if (response.status_code == 200
                    and response.json()):
                self._console.print_objects(response.json())
            elif response.status_code == 404:
                # not an error to query a device which doesn't exist
                self._console.ok('')
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR
                                        + ' ['+str(response.status_code) + ']')
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)

    def list_devices(self, in_sort_by, in_is_sort_asc):
        """List all devices.

        Arguments:
        in_sort_by -- Key of field to sort list by.
        in_is_sort_asc -- Boolean. True if sort is ascending, otherwise False.
        """
        # check that user is logged in
        session_key = self._login_mgr.get_session_key()
        if not self._login_mgr.is_session_alive():
            self._console.exception(constants.ERR_LOGGED_OUT)
        # retrieve the device info from the server using HTTP API
        url_string = 'http://{0}:{1}/api/v1/devices'
        url = url_string.format(self._login_mgr.get_api_ip(),
                                self._login_mgr.get_api_port())
        cookies = dict(JSESSIONID=session_key)
        try:
            response = requests.get(url, cookies=cookies)
            if (response.status_code == 200
                    and isinstance(response.json(), list)):
                sorted = list()
                if in_sort_by:
                    sorted.extend(helper.sort_list(response.json(),
                                                   in_sort_by,
                                                   in_is_sort_asc,
                                                   True))
                else:
                    sorted.extend(response.json())
                self._console.print_objects(sorted)
            elif response.status_code == 401:
                self._console.exception(constants.ERR_LOGIN_REJECTED)
            elif response.status_code == 500:
                self._console.exception(constants.ERR_SERVER_ERROR)
            else:
                self._console.exception(constants.ERR_UNKNOWN_ERROR + ' ['
                                        + str(response.status_code) + ']')
        except requests.exceptions.ConnectionError:
            self._console.exception(constants.ERR_NO_RESPONSE)
