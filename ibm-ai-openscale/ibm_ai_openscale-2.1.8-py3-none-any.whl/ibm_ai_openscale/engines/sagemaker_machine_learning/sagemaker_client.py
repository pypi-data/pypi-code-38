# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.clients import KnownServiceClient, ClientWithMLGatewaySupport
from .consts import SageMakerConsts


class SageMakerClient(KnownServiceClient, ClientWithMLGatewaySupport):
    service_type = SageMakerConsts.SERVICE_TYPE

    def __init__(self, binding_uid, ai_client, project_id=None):
        ClientWithMLGatewaySupport.__init__(self, ai_client, binding_uid)

    def prepare_artifact(self, asset, add_all_deployments=True, deployment_uids=None):
        artifact = super(SageMakerClient, self).prepare_artifact(asset, add_all_deployments, deployment_uids)

        if 'predicted_target_field' in artifact.properties:
            artifact.properties['prediction_field'] = artifact.properties['predicted_target_field']
            del artifact.properties['predicted_target_field']

        return artifact
