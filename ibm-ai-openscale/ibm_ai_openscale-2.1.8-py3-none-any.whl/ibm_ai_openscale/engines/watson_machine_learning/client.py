# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import ClientWithMLGatewaySupport
from .consts import WMLConsts
from ibm_ai_openscale.utils.client_errors import ClientError


class WMLClient(ClientWithMLGatewaySupport):
    service_type = WMLConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, service_credentials, project_id=None):
        ClientWithMLGatewaySupport.__init__(self, ai_client, binding_uid)
        self.service_credentials = service_credentials
        self.project_id = project_id

    def _get_native_client(self):
        try:
            from watson_machine_learning_client import WatsonMachineLearningAPIClient
        except Exception as e:
            raise ClientError("Error during import of 'watson_machine_learning_client' module.", e)
        return WatsonMachineLearningAPIClient(self.service_credentials, self.project_id)
