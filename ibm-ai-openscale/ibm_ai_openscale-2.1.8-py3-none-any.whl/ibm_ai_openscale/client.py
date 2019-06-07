# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.client.client import APIClientBase


'''
.. module:: APIClient
   :platform: Unix, Windows
   :synopsis: Watson OpenScale API Client.

.. moduleauthor:: IBM
'''


@logging_class
class APIClient(APIClientBase):
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
        >>>            "apikey": "***",
        >>>            "instance_guid": "***",
        >>>            "url": "https://api.aiopenscale.cloud.ibm.com"
        >>>            }
        >>>
        >>> client = APIClient(self.aios_credentials)
        """
        validate_type(aios_credentials, "aios_credentials", dict, True)

        if 'username' in aios_credentials:
            print("Warning: If you intend to work on ICP use APIClient4ICP instead. APIClient is configured to be connected to cloud.")

        if 'iam_token' not in aios_credentials:
            validate_type(aios_credentials['apikey'], "aios_credentials.apikey", str, True)
        APIClientBase.__init__(self, aios_credentials)

    def _create_token(self):
        header = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
        }

        response = requests_session.post(
            self._href_definitions.get_token_endpoint_href(),
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self._service_credentials['apikey']
            },
            headers=header
        )
        response = handle_response(200, 'access token', response, True)
        token = response['access_token']

        return token

    def __repr__(self):
        return 'APIClient(data_mart_id=\'{}\', url=\'{}\')'.format(
            self._service_credentials['data_mart_id'],
            self._service_credentials['url']
        )