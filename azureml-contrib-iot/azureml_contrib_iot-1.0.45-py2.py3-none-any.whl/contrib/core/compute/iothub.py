# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages IotHub compute targets in Azure Machine Learning service."""

import copy
import json
import requests
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from ._util import iothub_compute_template
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetAttachConfiguration
from azureml.exceptions import ComputeTargetException


class IotHubCompute(ComputeTarget):
    """Manages IotHub compute target objects."""

    _compute_type = 'IotHub'

    def _initialize(self, workspace, obj_dict):
        """Class IotHubCompute constructor.

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
        mlc_endpoint = MLC_ENDPOINT_FMT.format(
            workspace.subscription_id,
            workspace.resource_group,
            workspace.name,
            name)
        location = obj_dict['location']
        compute_type = obj_dict['properties']['computeType']
        tags = obj_dict['tags']
        description = obj_dict['properties']['description']
        created_on = None
        modified_on = None
        cluster_resource_id = obj_dict['properties']['resourceId']
        cluster_location = obj_dict['properties']['computeLocation'] \
            if 'computeLocation' in obj_dict['properties'] else None
        provisioning_state = obj_dict['properties']['provisioningState']
        provisioning_errors = obj_dict['properties']['provisioningErrors']
        is_attached = obj_dict['properties']['isAttachedCompute']
        super(IotHubCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags,
                                               description, created_on, modified_on, provisioning_state,
                                               provisioning_errors, cluster_resource_id, cluster_location,
                                               workspace, mlc_endpoint, None, workspace._auth, is_attached)

    @staticmethod
    def _attach(workspace, name, config):
        """Associates an already existing IotHub compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param config: Attach configuration object
        :type config: IotHubAttachConfiguration
        :return: An IotHubCompute object representation of the compute object
        :rtype: azureml.contrib.core.compute.iothub.IotHubCompute
        :raises: ComputeTargetException
        """
        resource_id = config.resource_id
        if not resource_id:
            resource_id = IotHubCompute._build_resource_id(workspace._subscription_id, config.resource_group,
                                                           config.name)

        attach_payload = IotHubCompute._build_attach_payload(resource_id, config.connection_string)
        return ComputeTarget._attach(workspace, name, attach_payload, IotHubCompute)

    @staticmethod
    def _build_resource_id(subscription_id, resource_group, name):
        """Build the Azure resource Id for the compute resource.

        :param subscription_id: The Azure subscription Id
        :type subscription_id: str
        :param resource_group: Name of the resource group in which the IotHub is located
        :type resource_group: str
        :param name: The IotHub name
        :type name: str
        :return: The Azure resource Id for the compute resource
        :rtype: str
        """
        IOTHUB_RESOURCE_ID_FMT = ('/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Devices/IotHubs/{}')
        return IOTHUB_RESOURCE_ID_FMT.format(subscription_id, resource_group, name)

    @staticmethod
    def attach_configuration(resource_group=None, name=None, resource_id=None, connection_string=''):
        """Create a configuration object for attaching an IotHub compute target.

        :param resource_group: Name of the resource group in which the IotHub is located.
        :type resource_group: str
        :param name: The IotHub name
        :type name: str
        :param resource_id: The Azure resource Id for the compute resource being attached
        :type resource_id: str
        :param connection_string: The IotHub connection string for the comoute resource being attached
        :type connection_string: str
        :return: A configuration object to be used when attaching a Compute object
        :rtype: IotHubAttachConfiguration
        """
        config = IotHubAttachConfiguration(resource_group, name, resource_id, connection_string)
        return config

    @staticmethod
    def _build_attach_payload(resource_id, connection_string):
        """Build attach payload

        :param resource_id:
        :type resource_id: str
        :param connection_string: IotHub connection string
        :type connection_string: str
        :return: json payload object
        :rtype: dict
        """
        json_payload = copy.deepcopy(iothub_compute_template)
        json_payload['properties']['resourceId'] = resource_id
        json_payload['properties']['properties']['connectionString'] = connection_string
        del (json_payload['properties']['computeLocation'])
        return json_payload

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = IotHubCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location

    def delete(self):
        """Delete is not supported for IotHubCompute object. Try to use detach instead.

        :raises: ComputeTargetException
        """
        return ComputeTargetException('Delete is not supported for IotHubCompute object. Try to use detach instead')

    def detach(self):
        """Detaches the IotHubCompute object from its associated workspace.

        .. remarks::

            No underlying cloud object will be deleted. the association will just be removed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('detach')

    def get_credentials(self):
        """Retrieve the credentials for the IotHub target.

        :return: Credentials for the IotHub target
        :rtype: dict
        :raises: ComputeTargetException
        """
        endpoint = self._mlc_endpoint + '/listKeys'
        headers = self._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = requests.post(endpoint, params=params, headers=headers)

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
        """Convert this IotHubCompute object into a json serialized dictionary.

        :return: The json representation of this IotHubCompute object
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
        """Convert a json object into an IotHubCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the IotHubCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to an IotHubCompute object
        :type object_dict: dict
        :return: The IotHubCompute representation of the provided json object
        :rtype: azureml.contrib.core.compute.iothub.IotHubCompute
        :raises: ComputeTargetException
        """
        IotHubCompute._validate_get_payload(object_dict)
        target = IotHubCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != IotHubCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(IotHubCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))


class IotHubAttachConfiguration(ComputeTargetAttachConfiguration):
    """Attach configuration object for IotHub compute targets.

    This object is used to define the configuration parameters for attaching IotHubCompute object.

    :param resource_group: Name of the resource group in which the IotHub is located.
    :type: resource_group: str
    :param name: The IotHub name
    :type: name: str
    :param resource_id: The Azure resource Id for the compute resource being attached.
    :type resource_id: str
    :param connection_string: The IotHub connection string for the compute resource being attached.
    :type connection_string: str
    :return: The configuraiton object
    :rtype: IotHubAttachConfiguration
    """

    def __init__(self, resource_group=None, name=None, resource_id=None, connection_string=''):

        """Initialize the configuration object.

        :param resource_group: Name of the resource group in which the IotHub is located.
        :type resource_group: str
        :param name: The IotHub name
        :type name: str
        :param resource_id: The Azure resource Id for the compute resource being attached.
        :type resource_id: str
        :param connection_string: The IotHub connection string for the compute resource being attached.
        :type connection_string: str
        :return: The configuraiton object
        :rtype: IotHubAttachConfiguration
        """
        super(IotHubAttachConfiguration, self).__init__(IotHubCompute)
        self.resource_group = resource_group
        self.name = name
        self.resource_id = resource_id
        self.connection_string = connection_string
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
            if resource_type != 'Microsoft.Devices':
                raise ComputeTargetException('Invalid resource_id provided, resource type {} does not match for '
                                             'IotHub'.format(resource_type))
            # make sure do not use other info
            if self.resource_group:
                raise ComputeTargetException('Since resource_id is provided, please do not provide resource_group.')
            if self.name:
                raise ComputeTargetException('Since resource_id is provided, please do not provide name.')
        elif self.resource_group or self.name:
            # resource_id is not provided, validate other info
            if not self.resource_group:
                raise ComputeTargetException('resource_group is not provided.')
            if not self.name:
                raise ComputeTargetException('name is not provided.')
        else:
            # neither resource_id nor other info is provided.
            raise ComputeTargetException('Please provide resource_group and name for the IotHub '
                                         'compute resource being attached. Or please provide resource_id for the '
                                         'resource being attached.')
