# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import ClientWithMLGatewaySupport
from .consts import AzureConsts


class AzureClient(ClientWithMLGatewaySupport):
    service_type = AzureConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, project_id=None):
        ClientWithMLGatewaySupport.__init__(self, ai_client, binding_uid)