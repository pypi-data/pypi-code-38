# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages Databricks compute targets in Azure Machine Learning service."""

import copy
import json
import requests
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml._compute._util import databricks_compute_template
from azureml._compute._util import get_requests_session
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetAttachConfiguration
from azureml.exceptions import ComputeTargetException
from azureml._restclient.clientbase import ClientBase


class DatabricksCompute(ComputeTarget):
    """Manages Databricks compute target objects."""

    _compute_type = 'Databricks'

    def _initialize(self, workspace, obj_dict):
        """Initialize implementation method.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        name = obj_dict['name']
        compute_resource_id = MLC_COMPUTE_RESOURCE_ID_FMT.format(workspace.subscription_id, workspace.resource_group,
                                                                 workspace.name, name)
        mlc_endpoint = MLC_ENDPOINT_FMT.format(workspace.subscription_id, workspace.resource_group, workspace.name,
                                               name)
        location = obj_dict['location']
        compute_type = obj_dict['properties']['computeType']
        tags = obj_dict['tags']
        description = obj_dict['properties']['description']
        created_on = obj_dict['properties'].get('createdOn')
        modified_on = obj_dict['properties'].get('modifiedOn')
        cluster_resource_id = obj_dict['properties']['resourceId']
        cluster_location = obj_dict['properties']['computeLocation'] \
            if 'computeLocation' in obj_dict['properties'] else None
        provisioning_state = obj_dict['properties']['provisioningState']
        provisioning_errors = obj_dict['properties']['provisioningErrors']
        is_attached = obj_dict['properties']['isAttachedCompute']
        super(DatabricksCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags,
                                                   description, created_on, modified_on, provisioning_state,
                                                   provisioning_errors, cluster_resource_id, cluster_location,
                                                   workspace, mlc_endpoint, None, workspace._auth, is_attached)

    @staticmethod
    def attach(workspace, name, resource_id, access_token):
        """(Deprecated) Associate an already existing Databricks compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :param access_token: The access token for the resource being attached
        :type access_token: str
        :return: A DatabricksCompute object representation of the compute object
        :rtype: azureml.core.compute.databricks.DatabricksCompute
        :raises: ComputeTargetException
        """
        raise ComputeTargetException('This method is DEPRECATED. Please use the following code to attach a '
                                     'Databricks compute resource.\n'
                                     '# Attach Databricks\n'
                                     'attach_config = DatabricksCompute.attach_configuration(resource_group='
                                     '"name_of_resource_group",\n'
                                     '                                                       workspace_name='
                                     '"name_of_databricks_workspace",\n'
                                     '                                                       access_token='
                                     '"databricks_token")\n'
                                     'compute = ComputeTarget.attach(workspace, name, attach_config)')

    @staticmethod
    def _attach(workspace, name, config):
        """Associates an already existing Databricks compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param config: Attach configuration object
        :type config: DatabricksAttachConfiguration
        :return: A DatabricksCompute object representation of the compute object
        :rtype: azureml.core.compute.databricks.DatabricksCompute
        :raises: ComputeTargetException
        """
        resource_id = config.resource_id
        if not resource_id:
            resource_id = DatabricksCompute._build_resource_id(workspace._subscription_id, config.resource_group,
                                                               config.workspace_name)
        attach_payload = DatabricksCompute._build_attach_payload(resource_id, config.access_token)
        return ComputeTarget._attach(workspace, name, attach_payload, DatabricksCompute)

    @staticmethod
    def _build_resource_id(subscription_id, resource_group, workspace_name):
        """Build the Azure resource ID for the compute resource.

        :param subscription_id: The Azure subscription ID
        :type subscription_id: str
        :param resource_group: Name of the resource group in which the Databricks is located.
        :type resource_group: str
        :param workspace_name: The Databricks workspace name
        :type workspace_name: str
        :return: The Azure resource ID for the compute resource
        :rtype: str
        """
        DATABRICKS_RESOURCE_ID_FMT = ('/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Databricks/'
                                      'workspaces/{}')
        return DATABRICKS_RESOURCE_ID_FMT.format(subscription_id, resource_group, workspace_name)

    @staticmethod
    def attach_configuration(resource_group=None, workspace_name=None, resource_id=None, access_token=''):
        """Create a configuration object for attaching a Databricks compute target.

        :param resource_group: Name of the resource group in which the Databricks is located.
        :type resource_group: str
        :param workspace_name: The Databricks workspace name
        :type workspace_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :param access_token: The access token for the compute resource being attached
        :type access_token: str
        :return: A configuration object to be used when attaching a Compute object
        :rtype: DatabricksAttachConfiguration
        """
        config = DatabricksAttachConfiguration(resource_group, workspace_name, resource_id, access_token)
        return config

    @staticmethod
    def _build_attach_payload(resource_id, access_token):
        """Build attach payload.

        :param resource_id:
        :type resource_id: str
        :param access_token:
        :type access_token: str
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(databricks_compute_template)
        json_payload['properties']['resourceId'] = resource_id
        json_payload['properties']['properties']['databricksAccessToken'] = access_token
        del (json_payload['properties']['computeLocation'])
        return json_payload

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = DatabricksCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location

    def delete(self):
        """Delete is not supported for Databricks object. Try to use detach instead.

        :raises: ComputeTargetException
        """
        raise ComputeTargetException('Delete is not supported for Databricks object. Try to use detach instead.')

    def detach(self):
        """Detaches the Databricks object from its associated workspace.

        .. remarks::

            No underlying cloud object will be deleted, the
            association will just be removed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('detach')

    def get_credentials(self):
        """Retrieve the credentials for the Databricks target.

        :return: Credentials for the Databricks target
        :rtype: dict
        :raises: ComputeTargetException
        """
        endpoint = self._mlc_endpoint + '/listKeys'
        headers = self._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().post, endpoint, params=params, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from MLC:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        creds_content = json.loads(content)
        return creds_content

    def serialize(self):
        """Convert this DatabricksCompute object into a json serialized dictionary.

        :return: The json representation of this DatabricksCompute object
        :rtype: dict
        """
        return {'id': self.id, 'name': self.name, 'tags': self.tags, 'location': self.location,
                'properties': {'computeType': self.type, 'computeLocation': self.cluster_location,
                               'description': self.description,
                               'resourceId': self.cluster_resource_id,
                               'provisioningErrors': self.provisioning_errors,
                               'provisioningState': self.provisioning_state}}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a json object into a DatabricksCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the DatabricksCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a DatabricksCompute object
        :type object_dict: dict
        :return: The DatabricksCompute representation of the provided json object
        :rtype: azureml.core.compute.databricks.DatabricksCompute
        :raises: ComputeTargetException
        """
        DatabricksCompute._validate_get_payload(object_dict)
        target = DatabricksCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != DatabricksCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(DatabricksCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))


class DatabricksAttachConfiguration(ComputeTargetAttachConfiguration):
    """Attach configuration object for Databricks compute targets.

    This objects is used to define the configuration parameters for attaching DatabricksCompute objects.

    :param resource_group: Name of the resource group in which the Databricks is located.
    :type resource_group: str
    :param workspace_name: The Databricks workspace name
    :type workspace_name: str
    :param access_token: The access token for the resource being attached
    :type access_token: str
    :return: The configuration object
    :rtype: DatabricksAttachConfiguration
    """

    def __init__(self, resource_group=None, workspace_name=None, resource_id=None, access_token=''):
        """Initialize the configuration object.

        :param resource_group: Name of the resource group in which the Databricks is located.
        :type resource_group: str
        :param workspace_name: The Databricks workspace name
        :type workspace_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :param access_token: The access token for the compute resource being attached
        :type access_token: str
        :return: The configuration object
        :rtype: DatabricksAttachConfiguration
        """
        super(DatabricksAttachConfiguration, self).__init__(DatabricksCompute)
        self.resource_group = resource_group
        self.workspace_name = workspace_name
        self.resource_id = resource_id
        self.access_token = access_token
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        if self.resource_id:
            # resource_id is provided, validate resource_id
            resource_parts = self.resource_id.split('/')
            if len(resource_parts) != 9:
                raise ComputeTargetException('Invalid resource_id provided: {}'.format(self.resource_id))
            resource_type = resource_parts[6]
            if resource_type != 'Microsoft.Databricks':
                raise ComputeTargetException('Invalid resource_id provided, resource type {} does not match for '
                                             'Databricks'.format(resource_type))
            # make sure do not use other info
            if self.resource_group:
                raise ComputeTargetException('Since resource_id is provided, please do not provide resource_group.')
            if self.workspace_name:
                raise ComputeTargetException('Since resource_id is provided, please do not provide workspace_name.')
        elif self.resource_group or self.workspace_name:
            # resource_id is not provided, validate other info
            if not self.resource_group:
                raise ComputeTargetException('resource_group is not provided.')
            if not self.workspace_name:
                raise ComputeTargetException('workspace_name is not provided.')
        else:
            # neither resource_id nor other info is provided
            raise ComputeTargetException('Please provide resource_group and workspace_name for the Databricks '
                                         'compute resource being attached. Or please provide resource_id for the '
                                         'resource being attached.')
