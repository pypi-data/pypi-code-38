# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from requests.auth import HTTPBasicAuth
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.client.client import APIClientBase


'''
.. module:: APIClient4ICP
   :platform: Unix, Windows
   :synopsis: Watson OpenScale API Client.

.. moduleauthor:: IBM
'''


@logging_class
class APIClient4ICP(APIClientBase):
    """
    Watson OpenScale client.

    :var data_mart: Manage db connection
    :vartype data_mart: DataMart
    :var version: Returns version of the python library.
    :vartype version: str
    """
    def __init__(self, aios_credentials):
        """
        :param aios_credentials: credentials to Watson OpenScale instance including: url, instance_id or instance_guid, and apikey.
        :type aios_credentials: dict

        The way you might use me is:

        >>> aios_credentials = {
        >>>            "username": "***",
        >>>            "password": "***",
        >>>            "instance_guid": "***",
        >>>            "url": "https://***"
        >>>            }
        >>>
        >>> client = APIClient4ICP(self.aios_credentials)
        """
        validate_type(aios_credentials, "aios_credentials", dict, True)
        if 'iam_token' not in aios_credentials:
            validate_type(aios_credentials['username'], "aios_credentials.username", str, True)
            validate_type(aios_credentials['password'], "aios_credentials.password", str, True)

        if 'data_mart_id' not in aios_credentials and 'instance_guid' not in aios_credentials and 'instance_id' not in aios_credentials:
            aios_credentials['data_mart_id'] = '00000000-0000-0000-0000-000000000000'

        requests_session.verify = False
        APIClientBase.__init__(self, aios_credentials)

    def _create_token(self):
        header = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
        }

        response = requests_session.get(
            self._href_definitions.get_token_endpoint_href(),
            headers=header,
            auth=HTTPBasicAuth(
                self._service_credentials['username'],
                self._service_credentials['password']
            ),
            verify=False
        )

        response = handle_response(200, 'access token', response, True)
        token = response['accessToken']

        return token

    def __repr__(self):
        return 'APIClient4ICP(username=\'{}\', url=\'{}\')'.format(
            self._service_credentials['username'],
            self._service_credentials['url']
        )