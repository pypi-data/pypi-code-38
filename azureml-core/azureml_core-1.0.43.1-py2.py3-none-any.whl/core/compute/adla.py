# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages Azure Data Lake Analytics compute targets in Azure Machine Learning service."""

import copy
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._util import adla_payload_template
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetAttachConfiguration
from azureml.exceptions import ComputeTargetException


class AdlaCompute(ComputeTarget):
    """Manage Azure Data Lake Analytics compute target objects."""

    _compute_type = 'DataLakeAnalytics'

    def _initialize(self, workspace, obj_dict):
        """Class AdlaCompute constructor.

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
            if 'computeLocation' in obj_dict['properties'] else location
        provisioning_state = obj_dict['properties']['provisioningState']
        provisioning_errors = obj_dict['properties']['provisioningErrors']
        is_attached = obj_dict['properties']['isAttachedCompute']
        super(AdlaCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags,
                                             description, created_on, modified_on, provisioning_state,
                                             provisioning_errors, cluster_resource_id, cluster_location,
                                             workspace, mlc_endpoint, None, workspace._auth, is_attached)

    @staticmethod
    def attach(workspace, name, resource_id):
        """(Deprecated) Associate an already existing ADLA compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: An AdlaCompute object representation of the compute object
        :rtype: azureml.core.compute.adla.AdlaCompute
        :raises: ComputeTargetException
        """
        raise ComputeTargetException('This method is DEPRECATED. Please use the following code to attach a ADLA '
                                     'compute resource.\n'
                                     '# Attach ADLA\n'
                                     'attach_config = AdlaCompute.attach_configuration(resource_group='
                                     '"name_of_resource_group",\n'
                                     '                                                 account_name='
                                     '"name_of_adla_account")\n'
                                     'compute = ComputeTarget.attach(workspace, name, attach_config)')

    @staticmethod
    def _attach(workspace, name, config):
        """Associates an already existing ADLA compute resource with the provided workspace.

        :param workspace: The workspace object to associate the compute resource with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the compute resource inside the provided workspace. Does not have to
            match with the already given name of the compute resource
        :type name: str
        :param config: Attach configuration object
        :type config: DataLakeAnalyticsAttachConfiguration
        :return: An AdlaCompute object representation of the compute object
        :rtype: azureml.core.compute.adla.AdlaCompute
        :raises: ComputeTargetException
        """
        resource_id = config.resource_id
        if not resource_id:
            resource_id = AdlaCompute._build_resource_id(workspace._subscription_id, config.resource_group,
                                                         config.account_name)
        attach_payload = AdlaCompute._build_attach_payload(resource_id)
        return ComputeTarget._attach(workspace, name, attach_payload, AdlaCompute)

    @staticmethod
    def _build_resource_id(subscription_id, resource_group, account_name):
        """Build the Azure resource ID for the compute resource.

        :param subscription_id: The Azure subscription ID
        :type subscription_id: str
        :param resource_group: Name of the resource group in which the DataLakeAnalytics is located.
        :type resource_group: str
        :param account_name: The DataLakeAnalytics account name
        :type account_name: str
        :return: The Azure resource ID for the compute resource
        :rtype: str
        """
        ADLA_RESOURCE_ID_FMT = ('/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DataLakeAnalytics/'
                                'accounts/{}')
        return ADLA_RESOURCE_ID_FMT.format(subscription_id, resource_group, account_name)

    @staticmethod
    def attach_configuration(resource_group=None, account_name=None, resource_id=None):
        """Create a configuration object for attaching a DataLakeAnalytics compute target.

        :param resource_group: Name of the resource group in which the DataLakeAnalytics is located.
        :type resource_group: str
        :param account_name: The DataLakeAnalytics account name
        :type account_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: A configuration object to be used when attaching a Compute object
        :rtype: DataLakeAnalyticsAttachConfiguration
        """
        config = DataLakeAnalyticsAttachConfiguration(resource_group, account_name, resource_id)
        return config

    @staticmethod
    def _build_attach_payload(resource_id):
        """Build attach payload.

        :param resource_id:
        :type resource_id: str
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(adla_payload_template)
        json_payload['properties']['resourceId'] = resource_id
        del (json_payload['properties']['computeLocation'])
        return json_payload

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = AdlaCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location

    def delete(self):
        """Remove the ADLA object from its associated workspace.

        If this object was created through Azure ML, the corresponding cloud based objects will also be deleted.
        If this object was created externally and only attached to the workspace, it will raise exception and nothing
        will be changed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('delete')

    def detach(self):
        """Detach the ADLA object from its associated workspace.

        No underlying cloud object will be deleted, the association will just be removed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('detach')

    def serialize(self):
        """Convert this AdlaCompute object into a json serialized dictionary.

        :return: The json representation of this AdlaCompute object
        :rtype: dict
        """
        return {'id': self.id, 'name': self.name, 'tags': self.tags, 'location': self.location,
                'properties': {'computeType': self.type, 'computeLocation': self.cluster_location,
                               'description': self.description, 'resourceId': self.cluster_resource_id,
                               'provisioningErrors': self.provisioning_errors,
                               'provisioningState': self.provisioning_state}}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a json object into a AdlaCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the AdlaCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a AdlaCompute object
        :type object_dict: dict
        :return: The AdlaCompute representation of the provided json object
        :rtype: azureml.core.compute.adla.AdlaCompute
        :raises: ComputeTargetException
        """
        AdlaCompute._validate_get_payload(object_dict)
        target = AdlaCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != AdlaCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(AdlaCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))


class DataLakeAnalyticsAttachConfiguration(ComputeTargetAttachConfiguration):
    """Attach configuration object for DataLakeAnalytics compute targets.

    This objects is used to define the configuration parameters for attaching AdlaCompute objects.
    """

    def __init__(self, resource_group=None, account_name=None, resource_id=None):
        """Initialize the configuration object.

        :param resource_group: Name of the resource group in which the DataLakeAnalytics is located.
        :type resource_group: str
        :param account_name: The DataLakeAnalytics account name
        :type account_name: str
        :param resource_id: The Azure resource ID for the compute resource being attached
        :type resource_id: str
        :return: The configuration object
        :rtype: DataLakeAnalyticsAttachConfiguration
        """
        super(DataLakeAnalyticsAttachConfiguration, self).__init__(AdlaCompute)
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
            if resource_type != 'Microsoft.DataLakeAnalytics':
                raise ComputeTargetException('Invalid resource_id provided, resource type {} does not match for '
                                             'DataLakeAnalytics'.format(resource_type))
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
            raise ComputeTargetException('Please provide resource_group and account_name for the ADLA compute '
                                         'resource being attached. Or please provide resource_id for the resource '
                                         'being attached.')
