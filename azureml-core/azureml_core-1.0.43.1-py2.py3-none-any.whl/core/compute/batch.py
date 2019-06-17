# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages Batch Compute Targets in Azure ML."""

import copy
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._util import batch_compute_template
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetAttachConfiguration
from azureml.exceptions import ComputeTargetException


class BatchCompute(ComputeTarget):
    """Manages Batch target objects."""

    _compute_type = 'Batch'

    def _initialize(self, workspace, obj_dict):
        """
        Initialize abstract method.

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
        created_on = None
        modified_on = None
        cluster_resource_id = obj_dict['properties']['resourceId']
        cluster_location = obj_dict['properties']['computeLocation'] \
            if 'computeLocation' in obj_dict['properties'] else location
        provisioning_state = obj_dict['properties']['provisioningState']
        provisioning_errors = obj_dict['properties']['provisioningErrors']
        is_attached = obj_dict['properties']['isAttachedCompute']
        super(BatchCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags,
                                              description, created_on, modified_on, provisioning_state,
                                              provisioning_errors, cluster_resource_id, cluster_location,
                                              workspace, mlc_endpoint, None, workspace._auth, is_attached)

    @staticmethod
    def _attach(workspace, name, config):
        """
        Associates an already existing Batch compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param config: Attach configuration object
        :type config: BatchAttachConfiguration
        :return: A BatchCompute object representation of the compute object
        :rtype: azureml.core.compute.batch.BatchCompute
        :raises: ComputeTargetException
        """
        resource_id = config.resource_id
        if not resource_id:
            resource_id = BatchCompute._build_resource_id(workspace._subscription_id, config.resource_group,
                                                          config.account_name)
        attach_payload = BatchCompute._build_attach_payload(resource_id)
        return ComputeTarget._attach(workspace, name, attach_payload, BatchCompute)

    @staticmethod
    def _build_resource_id(subscription_id, resource_group, account_name):
        """
        Build the Azure resource ID for the compute resource.

        :param subscription_id: The Azure subscription ID
        :type subscription_id: str
        :param resource_group: Name of the resource group in which the Batch account is located.
        :type resource_group: str
        :param account_name: The Batch account name
        :type account_name: str
        :return: The Azure resource ID for the compute resource
        :rtype: str
        """
        BATCH_RESOURCE_ID_FMT = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Batch/batchAccounts/{}'
        return BATCH_RESOURCE_ID_FMT.format(subscription_id, resource_group, account_name)

    @staticmethod
    def attach_configuration(resource_group=None, account_name=None, resource_id=None):
        """
        Create a configuration object for attaching a Batch compute target.

        :param resource_group: Name of the resource group in which the Batch account is located.
        :type resource_group: str
        :param account_name: The Batch account name
        :type account_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: A configuration object to be used when attaching a Compute object
        :rtype: BatchAttachConfiguration
        """
        config = BatchAttachConfiguration(resource_group, account_name, resource_id)
        return config

    @staticmethod
    def _build_attach_payload(resource_id):
        """Build attach payload.

        :param resource_id:
        :type resource_id: str
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(batch_compute_template)
        json_payload['properties']['resourceId'] = resource_id
        return json_payload

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = BatchCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location

    def delete(self):
        """
        Delete is not supported for Batch object. Try to use detach instead.

        :raises: ComputeTargetException
        """
        raise ComputeTargetException('Delete is not supported for Batch object. Try to use detach instead.')

    def detach(self):
        """
        Detaches the Batch object from its associated workspace.

        .. remarks::
            No underlying cloud object will be deleted, the
            association will just be removed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('detach')

    def serialize(self):
        """
        Convert this BatchCompute object into a json serialized dictionary.

        :return: The json representation of this BatchCompute object
        :rtype: dict
        """
        return {'id': self.id, 'name': self.name, 'tags': self.tags, 'location': self.location,
                'properties': {'computeType': 'Batch', 'computeLocation': self.cluster_location,
                               'description': self.description,
                               'resourceId': self.cluster_resource_id,
                               'provisioningErrors': self.provisioning_errors,
                               'provisioningState': self.provisioning_state}}

    @staticmethod
    def deserialize(workspace, object_dict):
        """
        Convert a json object into a BatchCompute object.

        .. remarks::
            Will fail if the provided workspace is not the
            workspace the Compute is associated with.

        :param workspace: The workspace object the BatchCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a BatchCompute object
        :type object_dict: dict
        :return: The BatchCompute representation of the provided json object
        :rtype: azureml.core.compute.batch.BatchCompute
        :raises: ComputeTargetException
        """
        BatchCompute._validate_get_payload(object_dict)
        target = BatchCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != BatchCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(BatchCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))


class BatchAttachConfiguration(ComputeTargetAttachConfiguration):
    """Attach configuration object for Batch compute targets.

    This objects is used to define the configuration parameters for attaching BatchCompute objects.

    :param resource_group: Name of the resource group in which the Batch account is located.
    :type resource_group: str
    :param account_name: The Batch account name
    :type account_name: str
    :param resource_id: The Azure resource ID for the compute resource being attached
    :type resource_id: str
    :return: The configuration object
    :rtype: BatchAttachConfiguration
    """

    def __init__(self, resource_group=None, account_name=None, resource_id=None):
        """Initialize the configuration object.

        :param resource_group: Name of the resource group in which the Batch account is located.
        :type resource_group: str
        :param account_name: The Batch account name
        :type account_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: The configuration object
        :rtype: BatchAttachConfiguration
        """
        super(BatchAttachConfiguration, self).__init__(BatchCompute)
        self.resource_group = resource_group
        self.account_name = account_name
        self.resource_id = resource_id
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
            if resource_type != 'Microsoft.Batch':
                raise ComputeTargetException('Invalid resource_id provided, resource type {} does not match for '
                                             'Batch'.format(resource_type))
            # make sure do not use other info
            if self.resource_group:
                raise ComputeTargetException('Since resource_id is provided, please do not provide resource_group.')
            if self.account_name:
                raise ComputeTargetException('Since resource_id is provided, please do not provide account_name.')
        elif self.resource_group or self.account_name:
            # resource_id is not provided, validate other info
            if not self.resource_group:
                raise ComputeTargetException('resource_group is not provided.')
            if not self.account_name:
                raise ComputeTargetException('account_name is not provided.')
        else:
            # neither resource_id nor other info is provided
            raise ComputeTargetException('Please provide resource_group and account_name for the Batch compute '
                                         'resource being attached. Or please provide resource_id for the resource '
                                         'being attached.')
