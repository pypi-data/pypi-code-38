# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import ClientWithMLGatewaySupport
from .consts import CustomConsts


class CustomClient(ClientWithMLGatewaySupport):
    service_type = CustomConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, project_id=None):
        ClientWithMLGatewaySupport.__init__(self, ai_client, binding_uid)
        self.url = ai_client._service_credentials['url']
        self.deployment_endpoint = self.url + '/v1/deployments'
        self.header = {}
        self.username = None
        self.password = None

        if 'username' in ai_client._service_credentials.keys():
            self.username = ai_client._service_credentials['username']

        if 'password' in ai_client._service_credentials.keys():
            self.password = ai_client._service_credentials['password']

        if 'header' in ai_client._service_credentials.keys():
            self.header = ai_client._service_credentials['header']