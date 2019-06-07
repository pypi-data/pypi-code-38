# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.utils import *
from ibm_ai_openscale.base_classes.clients import Client
from ibm_ai_openscale.base_classes import Artifact, SourceDeployment


class ClientWithMLGatewaySupport(Client):

    def __init__(self, ai_client, binding_uid):
        Client.__init__(self, binding_uid)
        self._ai_client = ai_client

    def _get_deployments_details(self):

        response = requests_session.get(self._ai_client._href_definitions.get_ml_gateway_discovery_href(binding_uid=self.binding_uid),
                                headers=self._ai_client._get_headers())

        deployments_details = handle_response(200, 'get deployments', response, True)

        return deployments_details['resources']

    def _make_artifact_from_details(self, all_details, add_all_deployments=True, deployment_uids=None):
        # TODO created_at - if SPSS will be returning it, default can be removed
        try:
            details = all_details[0]
        except Exception:
            raise ClientError('Unable to get asset details. Details: {}'.format(all_details))

        return Artifact(
            source_uid=details['entity']['asset']['asset_id'],
            source_url=details['entity']['asset']['url'] if 'url' in details['entity']['asset'] else details['entity']['scoring_endpoint']['url'], # custom special case
            binding_uid=self.binding_uid,
            name=details['entity']['asset']['name'],
            type=details['entity']['asset']['asset_type'] if 'asset_type' in details['entity']['asset'] else 'model',
            created=details['entity']['asset']['created_at'] if 'created_at' in details['entity']['asset'] else details['metadata']['created_at'] if 'created_at' in details['metadata'] else '0000-01-01T00:00:00.0Z',
            frameworks=[details['entity']['asset_properties']['model_type']] if 'model_type' in details['entity']['asset_properties'] else [],
            input_data_schema=details['entity']['asset_properties']['input_data_schema'] if 'input_data_schema' in details['entity']['asset_properties'] else None,
            training_data_schema=details['entity']['asset_properties']['training_data_schema'] if 'training_data_schema' in details['entity']['asset_properties'] else None,
            output_data_schema=details['entity']['asset_properties']['output_data_schema'] if 'output_data_schema' in details['entity']['asset_properties'] else None,
            label_column=details['entity']['asset_properties']['label_column'] if 'label_column' in details['entity']['asset_properties'] else None,
            source_entry=details,
            properties=details['entity']['asset_properties'],
            source_rn=details['entity']['asset']['asset_rn'] if 'asset_rn' in details['entity']['asset'] else '',
            deployments=self._prepare_deployments(all_details, add_all_deployments, deployment_uids)
        )

    def get_artifact(self, source_uid, add_all_deployments=True, deployment_uids=None):
        deployment_details = self._get_deployments_details()
        asset_details = [detail for detail in deployment_details if detail['entity']['asset']['asset_id'] == source_uid]

        if asset_details is not None:
            return self._make_artifact_from_details(asset_details, add_all_deployments, deployment_uids)
        else:
            raise IncorrectValue(source_uid)

    def get_artifacts(self):
        models = {}
        deployment_details = self._get_deployments_details()

        for model in deployment_details:
            model_uid = model['entity']['asset']['asset_id']
            if model_uid not in models.keys():
                models[model_uid] = []
            models[model_uid].append(model)

        return [self._make_artifact_from_details(details) for details in models.values()]

    def _prepare_deployments(self, deployment_details, add_all_deployments=True, deployment_uids=None):
        if deployment_uids is None and add_all_deployments:
            prepared_deployments = deployment_details
        elif deployment_uids is not None:
            prepared_deployments = [ deployment for deployment in deployment_details if deployment['metadata']['guid'] in deployment_uids]
        else:
            prepared_deployments = []

        return [
            # TODO created_at - if SPSS will be returning it, default can be removed
            SourceDeployment(
                deployment['metadata']['guid'],
                deployment['metadata']['url'] if 'url' in deployment['metadata'] else '',
                deployment['entity']['name'],
                deployment['entity']['type'],
                deployment['metadata']['created_at'] if 'created_at' in deployment['metadata'] else '0000-01-01T00:00:00.0Z',
                scoring_endpoint=deployment['entity']['scoring_endpoint'],
                rn=deployment['entity']['deployment_rn'] if 'deployment_rn' in deployment['entity'] else None
            ) for deployment in prepared_deployments
        ]