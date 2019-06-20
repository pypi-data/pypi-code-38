################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

import requests
import json
import base64
from datetime import datetime, timedelta
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided, ApiRequestFailure
from watson_machine_learning_client.href_definitions import HrefDefinitions


class ServiceInstance:
    """
        Connect, get details and check usage of your Watson Machine Learning service instance.
    """
    def __init__(self, client):
        self._logger = get_logger(__name__)
        self._client = client
        self._ICP = client.ICP
        self._wml_credentials = client.wml_credentials
        if self._ICP:
            self._wml_credentials[u'url'] = self.get_url() + ':31843'
            self._wml_credentials[u'instance_id'] = "999"
        self._href_definitions = HrefDefinitions(self._wml_credentials)
        self._client.wml_token = self._create_token()
        self._logger.info(u'Successfully prepared token: ' + self._client.wml_token)
        # ml_repository_client is initialized in repo
        self.details = None

    def get_instance_id(self):
        """
             Get instance id of your Watson Machine Learning service.
             
             **Output**
             
             .. important::
             
                **returns**: instance id\n
                **return type**: str
             
             **Example**
             
             >>> instance_details = client.service_instance.get_instance_id()
        """
        return self._wml_credentials['instance_id']

    def get_api_key(self):
        """
             Get api_key  of Watson Machine Learning service.
             :returns: api_key
             :rtype: str
             A way you might use me is:
             >>> instance_details = client.service_instance.get_api_key()
        """
        return self._wml_credentials['api_key']

    def get_url(self):
        """
             Get instance url of your Watson Machine Learning service.
             
             **Output**
             
             .. important::
             
                **returns**: instance url\n
                **return type**: str

             **Example**

             >>> instance_details = client.service_instance.get_url()
        """
        return self._wml_credentials['url']

    def get_username(self):
        """
             Get username for your Watson Machine Learning service.
             
             **Output**
             
             .. important::
             
                **returns**: username\n
                **return type**: str
             
             **Example**
             
             >>> instance_details = client.service_instance.get_username()
        """
        return self._wml_credentials['username']

    def get_password(self):
        """
             Get password for your Watson Machine Learning service.
             
             **Output**
             
             .. important::
             
                **returns**: password\n
                **return type**: str

             **Example**

             >>> instance_details = client.service_instance.get_password()
        """
        return self._wml_credentials['password']

    def get_details(self):
        """
             Get information about your Watson Machine Learning instance.
             
             **Output**
            
             .. important::

                **returns**: metadata of service instance\n
                **return type**: dict

             **Example**

             >>> instance_details = client.service_instance.get_details()
        """
        if not self._ICP:
            if self._wml_credentials is not None:
                response_get_instance = requests.get(
                    self._href_definitions.get_instance_by_id_endpoint_href(),
                    headers=self._client._get_headers()
                )

                if response_get_instance.status_code == 200:
                    return response_get_instance.json()
                else:
                    raise ApiRequestFailure(u'Getting instance details failed.', response_get_instance)
            else:
                raise NoWMLCredentialsProvided
        else:
            return {}

    def _get_token(self):
        if self._client.wml_token is None:
            self._create_token()
            self._client.repository._refresh_repo_client()

        else:
            if self._client._is_IAM():
                if self._get_expiration_datetime() - timedelta(minutes=50) < datetime.now():
                    self._client.wml_token = self._get_IAM_token()
                    self._client.repository._refresh_repo_client()

            elif self._get_expiration_datetime() - timedelta(minutes=30) < datetime.now():
                self._client.repository._refresh_repo_client()
                self._refresh_token()

        return self._client.wml_token

    def _create_token(self):

        if self._client.proceed is True:
            return self._wml_credentials["token"]
        if self._client._is_IAM():
            return self._get_IAM_token()
        else:
            if not self._ICP:
                response = requests.get(self._href_definitions.get_token_endpoint_href(),
                                        auth=(self.get_username(), self.get_password()))
                if response.status_code == 200:
                    token = response.json().get(u'token')
                else:
                    raise ApiRequestFailure(u'Error during getting ML Token.', response)
                return token
            else:
                token_url = self._wml_credentials['url'].replace(':31002', ':31843') + '/v1/preauth/validateAuth'
                response = requests.get(token_url, auth=(self.get_username(), self.get_password()), verify=False)

                if response.status_code == 200:
                    token = response.json().get(u'accessToken')
                else:
                    raise ApiRequestFailure(u'Error during getting ML Token.', response)
                return token

    def _refresh_token(self):
        import requests
        if self._client.proceed is True:
            self._client.wml_token = self._wml_credentials["token"]
        else:
            if not self._ICP:
                response = requests.put(
                    self._href_definitions.get_token_endpoint_href(),
                    json={'token': self._client.wml_token},
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'X-WML-User-Client': 'PythonClient'
                    }
                )

                if response.status_code == 200:
                    self._client.wml_token = response.json().get(u'token')
                else:
                    raise ApiRequestFailure(u'Error during refreshing ML Token.', response)
            else:
                token_url = self._wml_credentials['url'].replace(':31002', ':31843') + '/v1/preauth/validateAuth'
                response = requests.get(token_url, auth=(self.get_username(), self.get_password()), verify=False)

                if response.status_code == 200:
                    self._client.wml_token = response.json().get(u'accessToken')
                else:
                    raise ApiRequestFailure(u'Error during refreshing ICP Token.', response)

    def _get_expiration_datetime(self):
        token_parts = self._client.wml_token.split('.')
        token_padded = token_parts[1] + '=' * (len(token_parts[1]) % 4)
        token_info = json.loads(base64.b64decode(token_padded).decode('utf-8'))
        token_expire = token_info.get('exp')

        return datetime.fromtimestamp(token_expire)

    def _is_iam(self):
        token_parts = self._client.wml_token.split('.')
        token_padded = token_parts[1] + '=' * (len(token_parts[1]) % 4)
        token_info = json.loads(base64.b64decode(token_padded).decode('utf-8'))
        instanceId = token_info.get('instanceId')

        return instanceId

    def _get_IAM_token(self):
        if self._client.proceed is True:
            return self._wml_credentials["token"]
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic Yng6Yng='
        }

        mystr = 'apikey=' + self._href_definitions.get_iam_token_api()
        response = requests.post(
            self._href_definitions.get_iam_token_url(),
            data=mystr,
            headers=headers
        )

        if response.status_code == 200:
            token = response.json().get(u'access_token')
        else:
            raise ApiRequestFailure(u'Error during getting IAM Token.', response)
        return token