# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages AmlCompute compute targets in Azure Machine Learning service."""

import copy
import json
import requests
import sys
import time
from azureml._compute._constants import MLC_COMPUTE_RESOURCE_ID_FMT
from azureml._compute._constants import MLC_ENDPOINT_FMT
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml._compute._util import amlcompute_payload_template
from azureml._compute._util import convert_duration_to_seconds
from azureml._compute._util import convert_seconds_to_duration
from azureml._compute._util import get_paginated_compute_nodes
from azureml._compute._util import get_paginated_compute_supported_vms
from azureml._compute._util import get_requests_session
from azureml.core.compute import ComputeTarget
from azureml.core.compute.compute import ComputeTargetProvisioningConfiguration
from azureml.exceptions import ComputeTargetException
from azureml._restclient.clientbase import ClientBase
from dateutil.parser import parse


class AmlCompute(ComputeTarget):
    """Class for managing AmlCompute compute target objects."""

    _compute_type = 'AmlCompute'

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
        vm_size = obj_dict['properties']['properties']['vmSize'] \
            if obj_dict['properties']['properties'] else None
        vm_priority = obj_dict['properties']['properties']['vmPriority'] \
            if obj_dict['properties']['properties'] else None
        scale_settings = obj_dict['properties']['properties']['scaleSettings'] \
            if obj_dict['properties']['properties'] else None
        scale_settings = ScaleSettings.deserialize(scale_settings) if scale_settings else None
        admin_username = obj_dict['properties']['properties']['userAccountCredentials']['adminUserName'] \
            if obj_dict['properties']['properties'] and \
            'userAccountCredentials' in obj_dict['properties']['properties'] and \
            'adminUserName' in obj_dict['properties']['properties']['userAccountCredentials'] else None
        admin_user_password = obj_dict['properties']['properties']['userAccountCredentials']['adminUserPassword'] \
            if obj_dict['properties']['properties'] and \
            'userAccountCredentials' in obj_dict['properties']['properties'] and \
            'adminUserPassword' in obj_dict['properties']['properties']['userAccountCredentials'] else None
        admin_user_ssh_key = obj_dict['properties']['properties']['userAccountCredentials']['adminUserSshPublicKey'] \
            if obj_dict['properties']['properties'] and \
            'userAccountCredentials' in obj_dict['properties']['properties'] and \
            'adminUserSshPublicKey' in obj_dict['properties']['properties']['userAccountCredentials'] else None
        vnet_resourcegroup_name = None
        vnet_name = None
        subnet_name = None
        subnet_id = obj_dict['properties']['properties']['subnet']['id'] \
            if obj_dict['properties']['properties'] and obj_dict['properties']['properties']['subnet'] else None
        if subnet_id:
            vnet_resourcegroup_name = subnet_id[subnet_id.index("/resourceGroups/") +
                                                len("/resourceGroups/"):subnet_id.index("/providers")]
            vnet_name = subnet_id[subnet_id.index("/virtualNetworks/") +
                                  len("/virtualNetworks/"):subnet_id.index("/subnets")]
            subnet_name = subnet_id[subnet_id.index("/subnets/") + len("/subnets/"):]
        status = AmlComputeStatus.deserialize(obj_dict['properties']) \
            if provisioning_state in ["Succeeded", "Updating"] else None
        super(AmlCompute, self)._initialize(compute_resource_id, name, location, compute_type, tags, description,
                                            created_on, modified_on, provisioning_state, provisioning_errors,
                                            cluster_resource_id, cluster_location, workspace, mlc_endpoint, None,
                                            workspace._auth, is_attached)
        self.vm_size = vm_size
        self.vm_priority = vm_priority
        self.scale_settings = scale_settings
        self.admin_username = admin_username
        self.admin_user_password = admin_user_password
        self.admin_user_ssh_key = admin_user_ssh_key
        self.vnet_resourcegroup_name = vnet_resourcegroup_name
        self.vnet_name = vnet_name
        self.subnet_name = subnet_name
        self.status = status

    @staticmethod
    def _create(workspace, name, provisioning_configuration):
        """Create implementation method.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param provisioning_configuration:
        :type provisioning_configuration: AmlComputeProvisioningConfiguration
        :return:
        :rtype: azureml.core.compute.amlcompute.AmlCompute
        """
        compute_create_payload = AmlCompute._build_create_payload(provisioning_configuration,
                                                                  workspace.location, workspace.subscription_id)
        return ComputeTarget._create_compute_target(workspace, name, compute_create_payload, AmlCompute)

    @staticmethod
    def provisioning_configuration(vm_size='', vm_priority="dedicated", min_nodes=0,
                                   max_nodes=None, idle_seconds_before_scaledown=None,
                                   admin_username=None, admin_user_password=None, admin_user_ssh_key=None,
                                   vnet_resourcegroup_name=None, vnet_name=None, subnet_name=None,
                                   tags=None, description=None):
        """Create a configuration object for provisioning an AmlCompute target.

        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as
            detailed in the previous link. Defaults to Standard_NC6
        :type vm_size: str
        :param vm_priority: dedicated or lowpriority VMs. If not specified, will default to dedicated.
        :type vm_priority: str
        :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
        :type min_nodes: int
        :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4
        :type max_nodes: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
            Defaults to 120
        :type idle_seconds_before_scaledown: int
        :param admin_username: Name of the administrator user account which can be used to SSH into nodes
        :type admin_username: str
        :param admin_user_password: Password of the administrator user account
        :type admin_user_password: str
        :param admin_user_ssh_key: SSH public key of the administrator user account
        :type admin_user_ssh_key: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet
        :type subnet_name: str
        :param tags: A dictionary of key value tags to provide to the compute object
        :type tags: dict[str, str]
        :param description: A description to provide to the compute object
        :type description: str
        :return: A configuration object to be used when creating a Compute object
        :rtype: AmlComputeProvisioningConfiguration
        :raises: ComputeTargetException
        """
        config = AmlComputeProvisioningConfiguration(vm_size, vm_priority, min_nodes,
                                                     max_nodes, idle_seconds_before_scaledown,
                                                     admin_username, admin_user_password, admin_user_ssh_key,
                                                     vnet_resourcegroup_name, vnet_name, subnet_name,
                                                     tags, description)
        return config

    @staticmethod
    def _build_create_payload(config, location, subscription_id):
        """Construct the payload needed to create an AmlCompute cluster.

        :param config:
        :type config: azureml.core.compute.AmlComputeProvisioningConfiguration
        :param location:
        :type location: str
        :param subscription_id:
        :type subscription_id:
        :return:
        :rtype: dict
        """
        json_payload = copy.deepcopy(amlcompute_payload_template)
        del(json_payload['properties']['resourceId'])
        del(json_payload['properties']['computeLocation'])
        json_payload['location'] = location
        if not config.vm_size and not config.vm_priority and not config.admin_username and not \
                config.vnet_resourcegroup_name and not config.vnet_name and not config.subnet_name:
            del(json_payload['properties']['properties'])
        else:
            if not config.vm_size:
                del(json_payload['properties']['properties']['vmSize'])
            else:
                json_payload['properties']['properties']['vmSize'] = config.vm_size
            if not config.vm_priority:
                del(json_payload['properties']['properties']['vmPriority'])
            else:
                json_payload['properties']['properties']['vmPriority'] = config.vm_priority
            json_payload['properties']['properties']['scaleSettings'] = config.scale_settings.serialize()
            if not config.admin_username:
                del(json_payload['properties']['properties']['userAccountCredentials'])
            else:
                json_payload['properties']['properties']['userAccountCredentials']['adminUserName'] = \
                    config.admin_username
                if config.admin_user_password:
                    json_payload['properties']['properties']['userAccountCredentials']['adminUserPassword'] = \
                        config.admin_user_password
                else:
                    del(json_payload['properties']['properties']['userAccountCredentials']['adminUserPassword'])
                if config.admin_user_ssh_key:
                    json_payload['properties']['properties']['userAccountCredentials']['adminUserSshPublicKey'] = \
                        config.admin_user_ssh_key
                else:
                    del(json_payload['properties']['properties']['userAccountCredentials']['adminUserSshPublicKey'])

            if not config.vnet_name:
                del(json_payload['properties']['properties']['subnet'])
            else:
                json_payload['properties']['properties']['subnet'] = \
                    {"id": "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/virtualNetworks"
                     "/{2}/subnets/{3}".format(subscription_id, config.vnet_resourcegroup_name,
                                               config.vnet_name, config.subnet_name)}
        if config.tags:
            json_payload['tags'] = config.tags
        else:
            del(json_payload['tags'])
        if config.description:
            json_payload['properties']['description'] = config.description
        else:
            del(json_payload['properties']['description'])
        return json_payload

    def wait_for_completion(self, show_output=False, min_node_count=None, timeout_in_minutes=20):
        """Wait for the AmlCompute cluster to finish provisioning.

        This can be configured to wait for a minimum number of nodes, and to timeout after a set period of time.

        :param show_output: Boolean to provide more verbose output. Defaults to False
        :type show_output: bool
        :param min_node_count: Minimum number of nodes to wait for before considering provisioning to be complete. This
            doesn't have to equal the minimum number of nodes that the compute was provisioned with, however it should
            not be greater than that.
        :type min_node_count: int
        :param timeout_in_minutes: The duration in minutes to wait before considering provisioning to have failed.
            Defaults to 20
        :type timeout_in_minutes: int
        :raises: ComputeTargetException
        """
        min_nodes_reached, timeout_reached, terminal_state_reached, status_errors_present = \
            self._wait_for_nodes(min_node_count, timeout_in_minutes, show_output)
        if show_output:
            print('AmlCompute wait for completion finished')
        if min_nodes_reached:
            if show_output:
                print('Minimum number of nodes requested have been provisioned')
        elif timeout_reached:
            if show_output:
                print('Wait timeout has been reached')
                if self.status:
                    print('Current provisioning state of AmlCompute is "{0}" and current node count is "{1}"'.
                          format(self.status.provisioning_state.capitalize(), self.status.current_node_count))
                else:
                    print('Current provisioning state of AmlCompute is "{}"'.
                          format(self.provisioning_state.capitalize()))
        elif terminal_state_reached:
            if self.status:
                state = self.status.provisioning_state.capitalize()
            else:
                state = self.provisioning_state.capitalize()
            if show_output:
                print('Terminal state of "{}" has been reached'.format(state))
                if state == 'Failed':
                    print('Provisioning errors: {}'.format(self.provisioning_errors))
        elif status_errors_present:
            if self.status:
                errors = self.status.errors
            else:
                errors = self.provisioning_errors
            if show_output:
                print('There were errors reported from AmlCompute:\n{}'.format(errors))

    def _wait_for_nodes(self, min_node_count, timeout_in_minutes, show_output):
        """Wait for nodes.

        :param min_node_count:
        :type min_node_count: int
        :param timeout_in_minutes:
        :type timeout_in_minutes: int
        :param show_output:
        :type show_output: bool
        :return:
        :rtype:
        """
        self.refresh_state()
        start_time = time.time()

        if self.status:
            current_state = self.status.provisioning_state
        else:
            current_state = self.provisioning_state
        if show_output and current_state:
            sys.stdout.write('{}'.format(current_state))
            sys.stdout.flush()

        min_nodes_reached = self._min_node_count_reached(min_node_count)
        timeout_reached = self._polling_timeout_reached(start_time, timeout_in_minutes)
        terminal_state_reached = self._terminal_state_reached()
        status_errors_present = self._status_errors_present()

        while not min_nodes_reached and not timeout_reached and not terminal_state_reached \
                and not status_errors_present:
            if show_output and not min_nodes_reached:
                if self.status and self.status.current_node_count:
                    sys.stdout.write("Waiting for cluster to scale. {0} out of {1} nodes ready.\n"
                                     .format(self.status.current_node_count, min_node_count))

            time.sleep(5)
            self.refresh_state()

            if self.status:
                state = self.status.provisioning_state
            else:
                state = None

            if show_output and state:
                if state != current_state and state != 'succeeded':
                    if current_state is None:
                        sys.stdout.write('{}'.format(state))
                    else:
                        sys.stdout.write('\n{}'.format(state))
                    current_state = state
                elif state:
                    sys.stdout.write('.')
                sys.stdout.flush()

            min_nodes_reached = self._min_node_count_reached(min_node_count)
            timeout_reached = self._polling_timeout_reached(start_time, timeout_in_minutes)
            terminal_state_reached = self._terminal_state_reached()
            status_errors_present = self._status_errors_present()

        if show_output:
            sys.stdout.write('\n')
            sys.stdout.flush()

        return min_nodes_reached, timeout_reached, terminal_state_reached, status_errors_present

    def _min_node_count_reached(self, min_node_count):
        """Return minimum node count reached.

        :param min_node_count:
        :type min_node_count: int
        :return:
        :rtype: bool
        """
        if not min_node_count:
            if self.status and self.status.scale_settings:
                min_node_count = self.status.scale_settings.minimum_node_count
        if min_node_count is not None and self.status and self.status.current_node_count >= min_node_count:
            return True
        return False

    def _polling_timeout_reached(self, start_time, timeout_in_minutes):
        """Poll timeout reached.

        :param start_time:
        :type start_time: datetime.datetime
        :param timeout_in_minutes:
        :type timeout_in_minutes: int
        :return:
        :rtype: bool
        """
        cur_time = time.time()
        if cur_time - start_time > timeout_in_minutes * 60:
            return True
        return False

    def _terminal_state_reached(self):
        """Terminal state reached.

        :param state:
        :type state: str
        :return:
        :rtype: bool
        """
        if self.status:
            state = self.status.provisioning_state.capitalize()
        else:
            state = self.provisioning_state.capitalize()
        if state == 'Failed' or state == 'Canceled':
            return True
        return False

    def _status_errors_present(self):
        """Return status error.

        :return:
        :rtype:
        """
        if (self.status and self.status.errors) or self.provisioning_errors:
            return True
        return False

    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state.
        """
        cluster = AmlCompute(self.workspace, self.name)
        self.modified_on = cluster.modified_on
        self.provisioning_state = cluster.provisioning_state
        self.provisioning_errors = cluster.provisioning_errors
        self.cluster_resource_id = cluster.cluster_resource_id
        self.cluster_location = cluster.cluster_location
        self.vm_size = cluster.vm_size
        self.vm_priority = cluster.vm_priority
        self.scale_settings = cluster.scale_settings
        self.status = cluster.status

    def get_status(self):
        """Retrieve the current detailed status for the AmlCompute cluster.

        :return: A detailed status object for the cluster
        :rtype: AmlComputeStatus
        """
        self.refresh_state()
        if not self.status:
            state = self.provisioning_state.capitalize()
            if state == 'Creating':
                print('AmlCompute is getting created. Consider calling wait_for_completion() first')
            elif state == 'Failed':
                print('AmlCompute is in a failed state, try deleting and recreating')
            else:
                print('Current provisioning state of AmlCompute is "{}"'.format(state))
            return None

        return self.status

    def delete(self):
        """Remove the AmlCompute object from its associated workspace.

        .. remarks::

            If this object was created through Azure ML,
            the corresponding cloud based objects will also be deleted. If this object was created externally and only
            attached to the workspace, it will raise exception and nothing will be changed.

        :raises: ComputeTargetException
        """
        self._delete_or_detach('delete')

    def detach(self):
        """Detach is not supported for AmlCompute object. Try to use delete instead.

        :raises: ComputeTargetException
        """
        raise ComputeTargetException('Detach is not supported for AmlCompute object. Try to use delete instead.')

    def serialize(self):
        """Convert this AmlCompute object into a json serialized dictionary.

        :return: The json representation of this AmlCompute object
        :rtype: dict
        """
        scale_settings = self.scale_settings.serialize() if self.scale_settings else None
        subnet_id = None
        if self.vnet_resourcegroup_name and self.vnet_name and self.subnet_name:
            subnet_id = "/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/virtualNetworks" \
                        "/{2}/subnets/{3}".format(self.workspace.subscription_id, self.vnet_resourcegroup_name,
                                                  self.vnet_name, self.subnet_name)

        amlcompute_properties = {'vmSize': self.vm_size, 'vmPriority': self.vm_priority,
                                 'scaleSettings': scale_settings,
                                 'userAccountCredentials': {'adminUserName': self.admin_username,
                                                            'adminUserPassword': self.admin_user_password,
                                                            'adminUserSshPublicKey': self.admin_user_ssh_key},
                                 'subnet': {'id': subnet_id}}
        amlcompute_status = self.status.serialize() if self.status else None
        cluster_properties = {'description': self.description, 'resourceId': self.cluster_resource_id,
                              'computeType': self.type, 'computeLocation': self.cluster_location,
                              'provisioningState': self.provisioning_state,
                              'provisioningErrors': self.provisioning_errors,
                              'properties': amlcompute_properties, 'status': amlcompute_status}
        return {'id': self.id, 'name': self.name, 'location': self.location, 'tags': self.tags,
                'properties': cluster_properties}

    @staticmethod
    def deserialize(workspace, object_dict):
        """Convert a json object into a AmlCompute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the AmlCompute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a AmlCompute object
        :type object_dict: dict
        :return: The AmlCompute representation of the provided json object
        :rtype: azureml.core.compute.amlcompute.AmlCompute
        :raises: ComputeTargetException
        """
        AmlCompute._validate_get_payload(object_dict)
        target = AmlCompute(None, None)
        target._initialize(workspace, object_dict)
        return target

    @staticmethod
    def _validate_get_payload(payload):
        if 'properties' not in payload or 'computeType' not in payload['properties']:
            raise ComputeTargetException('Invalid cluster payload:\n'
                                         '{}'.format(payload))
        if payload['properties']['computeType'] != AmlCompute._compute_type:
            raise ComputeTargetException('Invalid cluster payload, not "{}":\n'
                                         '{}'.format(AmlCompute._compute_type, payload))
        for arm_key in ['location', 'id', 'tags']:
            if arm_key not in payload:
                raise ComputeTargetException('Invalid cluster payload, missing ["{}"]:\n'
                                             '{}'.format(arm_key, payload))
        for key in ['properties', 'provisioningErrors', 'description', 'provisioningState', 'resourceId']:
            if key not in payload['properties']:
                raise ComputeTargetException('Invalid cluster payload, missing ["properties"]["{}"]:\n'
                                             '{}'.format(key, payload))
        if payload['properties']['properties']:
            for amlcompute_key in ['vmPriority', 'vmSize', 'scaleSettings']:
                if amlcompute_key not in payload['properties']['properties']:
                    raise ComputeTargetException('Invalid cluster payload, missing '
                                                 '["properties"]["properties"]["{}"]:\n'
                                                 '{}'.format(amlcompute_key, payload))

    def get(self):
        """Return compute object."""
        return ComputeTarget._get(self.workspace, self.name)

    def update(self, min_nodes=None, max_nodes=None, idle_seconds_before_scaledown=None):
        """Update Scale settings for AmlCompute target.

        :param min_nodes: Minimum number of nodes to use on the cluster.
        :type min_nodes: int
        :param max_nodes: Maximum number of nodes to use on the cluster
        :type max_nodes: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster
        :type idle_seconds_before_scaledown: int
        """
        if min_nodes is None and max_nodes is None and idle_seconds_before_scaledown is None:
            return
        else:
            self.refresh_state()
            if min_nodes is None:
                min_nodes = self.scale_settings.minimum_node_count
            if max_nodes is None:
                max_nodes = self.scale_settings.maximum_node_count
            if idle_seconds_before_scaledown is None:
                idle_seconds_before_scaledown = self.scale_settings.idle_seconds_before_scaledown
            self.scale_settings = ScaleSettings(min_nodes, max_nodes, idle_seconds_before_scaledown)

            compute_update_payload = {'properties': {'properties': {'scaleSettings': {}}}}
            compute_update_payload['properties']['properties']['scaleSettings'] = self.scale_settings.serialize()

            endpoint_fmt = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                           'Microsoft.MachineLearningServices/workspaces/{}/computes/{}'
            endpoint = endpoint_fmt.format(self.workspace.subscription_id, self.workspace.resource_group,
                                           self.workspace.name, self.name)
            headers = self.workspace._auth.get_authentication_header()
            params = {'api-version': MLC_WORKSPACE_API_VERSION}
            resp = ClientBase._execute_func(get_requests_session().patch, endpoint, params=params, headers=headers,
                                            json=compute_update_payload)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                             'Response Code: {}\n'
                                             'Headers: {}\n'
                                             'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    def list_nodes(self):
        """Get the details (e.g IP address, port etc) of all the compute nodes in the compute.

        :return: Details of all the compute nodes in the compute
        :rtype: :class:`list[dict]`
        """
        paginated_results = []
        endpoint_fmt = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                       'Microsoft.MachineLearningServices/workspaces/{}/computes/{}/listNodes'
        endpoint = endpoint_fmt.format(self.workspace.subscription_id, self.workspace.resource_group,
                                       self.workspace.name, self.name)
        headers = self.workspace._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().post, endpoint, params=params, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        result_list = json.loads(content)
        paginated_results = get_paginated_compute_nodes(result_list, headers)

        return paginated_results

    @staticmethod
    def supported_vmsizes(workspace, location=None):
        """List the supported VM sizes in a region.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param location: Location of cluster. If not specified, will default to workspace location.
        :type location: str
        :return: List of supported VM sizes in a region with name of the VM, VCPUs, RAM
        :rtype: :class:`list[dict]`
        """
        paginated_results = []
        if not workspace:
            return paginated_results

        if not location:
            location = workspace.location

        endpoint_fmt = 'https://management.azure.com/subscriptions/{}/providers/' \
                       'Microsoft.MachineLearningServices/locations/{}/vmSizes'
        endpoint = endpoint_fmt.format(workspace.subscription_id, location)
        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().get, endpoint, params=params, headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Error occurred retrieving targets:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        result_list = json.loads(content)
        paginated_results = get_paginated_compute_supported_vms(result_list, headers)

        return paginated_results


class AmlComputeProvisioningConfiguration(ComputeTargetProvisioningConfiguration):
    """Provisioning configuration object for AmlCompute targets.

    This objects is used to define the configuration parameters for provisioning AmlCompute objects.

    :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
        Note that not all sizes are available in all regions, as
        detailed in the previous link. Defaults to Standard_NC6
    :type vm_size: str
    :param vm_priority: dedicated or lowpriority VMs. If not specified, will default to dedicated.
    :type vm_priority: str
    :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
    :type min_nodes: int
    :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4
    :type max_nodes: int
    :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
        Defaults to 120
    :type idle_seconds_before_scaledown: int
    :param admin_username: Name of the administrator user account which can be used to SSH into nodes
    :type admin_username: str
    :param admin_user_password: Password of the administrator user account
    :type admin_user_password: str
    :param admin_user_ssh_key: SSH public key of the administrator user account
    :type admin_user_ssh_key: str
    :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
    :type vnet_resourcegroup_name: str
    :param vnet_name: Name of the virtual network
    :type vnet_name: str
    :param subnet_name: Name of the subnet inside the vnet
    :type subnet_name: str
    :param tags: A dictionary of key value tags to provide to the compute object
    :type tags: dict[str, str]
    :param description: A description to provide to the compute object
    :type description: str
    """

    def __init__(self, vm_size='', vm_priority="dedicated", min_nodes=0,
                 max_nodes=None, idle_seconds_before_scaledown=None,
                 admin_username=None, admin_user_password=None, admin_user_ssh_key=None,
                 vnet_resourcegroup_name=None, vnet_name=None, subnet_name=None,
                 tags=None, description=None):
        """Create a configuration object for provisioning a AmlCompute target.

        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as
            detailed in the previous link. Defaults to Standard_NC6
        :type vm_size: str
        :param vm_priority: dedicated or lowpriority VMs. If not specified, will default to dedicated.
        :type vm_priority: str
        :param min_nodes: Minimum number of nodes to use on the cluster. If not specified, will default to 0.
        :type min_nodes: int
        :param max_nodes: Maximum number of nodes to use on the cluster. Defaults to 4
        :type max_nodes: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster.
            Defaults to 120
        :type idle_seconds_before_scaledown: int
        :param admin_username: Name of the administrator user account which can be used to SSH into nodes
        :type admin_username: str
        :param admin_user_password: Password of the administrator user account
        :type admin_user_password: str
        :param admin_user_ssh_key: SSH public key of the administrator user account
        :type admin_user_ssh_key: str
        :param vnet_resourcegroup_name: Name of the resource group where the virtual network is located
        :type vnet_resourcegroup_name: str
        :param vnet_name: Name of the virtual network
        :type vnet_name: str
        :param subnet_name: Name of the subnet inside the vnet
        :type subnet_name: str
        :param tags: A dictionary of key value tags to provide to the compute object
        :type tags: dict[str, str]
        :param description: A description to provide to the compute object
        :type description: str
        :return: A configuration object to be used when creating a Compute object
        :rtype: AmlComputeProvisioningConfiguration
        :raises: ComputeTargetException
        """
        super(AmlComputeProvisioningConfiguration, self).__init__(AmlCompute, None)
        self.vm_size = vm_size
        self.vm_priority = vm_priority
        self.scale_settings = ScaleSettings(min_nodes, max_nodes, idle_seconds_before_scaledown)
        self.admin_username = admin_username
        self.admin_user_password = admin_user_password
        self.admin_user_ssh_key = admin_user_ssh_key
        self.vnet_resourcegroup_name = vnet_resourcegroup_name
        self.vnet_name = vnet_name
        self.subnet_name = subnet_name
        self.tags = tags
        self.description = description
        self.validate_configuration()

    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        if any([self.admin_username, self.admin_user_password, self.admin_user_ssh_key]) and \
                not self.admin_username:
                raise ComputeTargetException('Invalid user credentials, admin username must be provided along '
                                             'with either a password or SSH key information.')
        if self.admin_username:
            if not self.admin_user_password and not self.admin_user_ssh_key:
                raise ComputeTargetException('Invalid user credentials, no password or key information provided. '
                                             'Please provide either a password or SSH key information.')
        if any([self.vnet_name, self.vnet_resourcegroup_name, self.subnet_name]) and \
                not all([self.vnet_name, self.vnet_resourcegroup_name, self.subnet_name]):
                raise ComputeTargetException('Invalid configuration, not all virtual net information provided. '
                                             'To use a custom virtual net, please provide vnet name, vnet resource '
                                             'group and subnet name')
        elif self.scale_settings.maximum_node_count is None:
            raise ComputeTargetException('Invalid provisioning configuration, max nodes count is mandatory')


class ScaleSettings(object):
    """Requested scale settings object for a AmlCompute object."""

    def __init__(self, minimum_node_count, maximum_node_count, idle_seconds_before_scaledown):
        """Initialize the ScaleSettings object.

        :param minimum_node_count: Minimum number of nodes to use on the cluster.
        :type minimum_node_count: int
        :param maximum_node_count: Maximum number of nodes to use on the cluster
        :type maximum_node_count: int
        :param idle_seconds_before_scaledown: Node idle time in seconds before scaling down the cluster
        :type idle_seconds_before_scaledown: int
        """
        self.minimum_node_count = minimum_node_count
        self.maximum_node_count = maximum_node_count
        self.idle_seconds_before_scaledown = idle_seconds_before_scaledown

    def serialize(self):
        """Convert this ScaleSettings object into a json serialized dictionary.

        :return: The json representation of this ScaleSettings object
        :rtype: dict
        """
        duration = ""
        if self.idle_seconds_before_scaledown:
            duration = convert_seconds_to_duration(self.idle_seconds_before_scaledown)

        return {'minNodeCount': self.minimum_node_count,
                'maxNodeCount': self.maximum_node_count,
                'nodeIdleTimeBeforeScaleDown': duration}

    @staticmethod
    def deserialize(object_dict):
        """Convert a json object into a ScaleSettings object.

        :param object_dict: A json object to convert to a ScaleSettings object
        :type object_dict: dict
        :return: The ScaleSettings representation of the provided json object
        :rtype: ScaleSettings
        :raises: ComputeTargetException
        """
        if not object_dict:
            return None
        for key in ['minNodeCount', 'maxNodeCount', 'nodeIdleTimeBeforeScaleDown']:
            if key not in object_dict:
                raise ComputeTargetException('Invalid scale settings payload, missing "{}":\n'
                                             '{}'.format(key, object_dict))

        return ScaleSettings(object_dict['minNodeCount'],
                             object_dict['maxNodeCount'],
                             convert_duration_to_seconds(object_dict['nodeIdleTimeBeforeScaleDown']))


class AmlComputeStatus(object):
    """Detailed status for a AmlCompute object.

    .. remarks::

        Initialize a AmlComputeStatus object

    :param allocation_state: String description of the current allocation state
    :type allocation_state: str
    :param allocation_state_transition_time: Time of the most recent allocation state change
    :type allocation_state_transition_time: datetime.datetime
    :param creation_time: Cluster creation time
    :type creation_time: datetime.datetime
    :param current_node_count: The current number of nodes used by the cluster
    :type current_node_count: int
    :param errors: A list of error details, if any
    :type errors: :class:`list[dict]`
    :param modified_time: Cluster modification time
    :type modified_time: datetime.datetime
    :param node_state_counts: An object containing counts of the various current node states in the cluster
    :type node_state_counts: AmlComputeNodeStateCounts
    :param provisioning_state: Current provisioning state of the cluster
    :type provisioning_state: str
    :param provisioning_state_transition_time: Time of the most recent provisioning state change
    :type provisioning_state_transition_time: datetime.datetime
    :param scale_settings: An object containing the specified scale settings for the cluster
    :type scale_settings: ScaleSettings
    :param target_node_count: The target number of nodes for by the cluster
    :type target_node_count: int
    :param vm_priority: dedicated or lowpriority VMs.
    :type vm_priority: str
    :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
        Note that not all sizes are available in all regions, as
        detailed in the previous link.
    :type vm_size: str
    """

    def __init__(self, allocation_state, allocation_state_transition_time, creation_time, current_node_count,
                 errors, modified_time, node_state_counts, provisioning_state, provisioning_state_transition_time,
                 scale_settings, target_node_count, vm_priority, vm_size):
        """Initialize a AmlComputeStatus object.

        :param allocation_state: String description of the current allocation state
        :type allocation_state: str
        :param allocation_state_transition_time: Time of the most recent allocation state change
        :type allocation_state_transition_time: datetime.datetime
        :param creation_time: Cluster creation time
        :type creation_time: datetime.datetime
        :param current_node_count: The current number of nodes used by the cluster
        :type current_node_count: int
        :param errors: A list of error details, if any
        :type errors: :class:`list[dict]`
        :param modified_time: Cluster modification time
        :type modified_time: datetime.datetime
        :param node_state_counts: An object containing counts of the various current node states in the cluster
        :type node_state_counts: AmlComputeNodeStateCounts
        :param provisioning_state: Current provisioning state of the cluster
        :type provisioning_state: str
        :param provisioning_state_transition_time: Time of the most recent provisioning state change
        :type provisioning_state_transition_time: datetime.datetime
        :param scale_settings: An object containing the specified scale settings for the cluster
        :type scale_settings: ScaleSettings
        :param target_node_count: The target number of nodes for by the cluster
        :type target_node_count: int
        :param vm_priority: dedicated or lowpriority VMs.
        :type vm_priority: str
        :param vm_size: Size of agent VMs. More details can be found here: https://aka.ms/azureml-vm-details.
            Note that not all sizes are available in all regions, as
            detailed in the previous link.
        :type vm_size: str
        """
        self.allocation_state = allocation_state
        self.allocation_state_transition_time = allocation_state_transition_time
        self.creation_time = creation_time
        self.current_node_count = current_node_count
        self.errors = errors
        self.modified_time = modified_time
        self.node_state_counts = node_state_counts
        self.provisioning_state = provisioning_state
        self.provisioning_state_transition_time = provisioning_state_transition_time
        self.scale_settings = scale_settings
        self.target_node_count = target_node_count
        self.vm_priority = vm_priority
        self.vm_size = vm_size

    def serialize(self):
        """Convert this AmlComputeStatus object into a json serialized dictionary.

        :return: The json representation of this AmlComputeStatus object
        :rtype: dict
        """
        allocation_state_transition_time = self.allocation_state_transition_time.isoformat() \
            if self.allocation_state_transition_time else None
        creation_time = self.creation_time.isoformat() if self.creation_time else None
        modified_time = self.modified_time.isoformat() if self.modified_time else None
        node_state_counts = self.node_state_counts.serialize() if self.node_state_counts else None
        provisioning_state_transition_time = self.provisioning_state_transition_time.isoformat() \
            if self.provisioning_state_transition_time else None
        scale_settings = self.scale_settings.serialize() if self.scale_settings else None
        return {'currentNodeCount': self.current_node_count, 'targetNodeCount': self.target_node_count,
                'nodeStateCounts': node_state_counts, 'allocationState': self.allocation_state,
                'allocationStateTransitionTime': allocation_state_transition_time, 'errors': self.errors,
                'creationTime': creation_time, 'modifiedTime': modified_time,
                'provisioningState': self.provisioning_state,
                'provisioningStateTransitionTime': provisioning_state_transition_time,
                'scaleSettings': scale_settings,
                'vmPriority': self.vm_priority, 'vmSize': self.vm_size}

    @staticmethod
    def deserialize(object_dict):
        """Convert a json object into a AmlComputeStatus object.

        :param object_dict: A json object to convert to a AmlComputeStatus object
        :type object_dict: dict
        :return: The AmlComputeStatus representation of the provided json object
        :rtype: AmlComputeStatus
        :raises: ComputeTargetException
        """
        if not object_dict:
            return None
        allocation_state = object_dict['properties']['allocationState'] \
            if 'allocationState' in object_dict['properties'] else None
        allocation_state_transition_time = parse(object_dict['properties']['allocationStateTransitionTime']) \
            if 'allocationStateTransitionTime' in object_dict['properties'] else None
        creation_time = parse(object_dict['createdOn']) \
            if 'createdOn' in object_dict else None
        current_node_count = object_dict['properties']['currentNodeCount'] \
            if 'currentNodeCount' in object_dict['properties'] else None
        errors = object_dict['properties']['errors'] \
            if 'errors' in object_dict['properties'] else None
        modified_time = parse(object_dict['modifiedOn']) \
            if 'modifiedOn' in object_dict else None
        node_state_counts = AmlComputeNodeStateCounts.deserialize(object_dict['properties']['nodeStateCounts']) \
            if 'nodeStateCounts' in object_dict['properties'] else None
        provisioning_state = object_dict['provisioningState'] \
            if 'provisioningState' in object_dict else None
        provisioning_state_transition_time = parse(object_dict['provisioningStateTransitionTime']) \
            if 'provisioningStateTransitionTime' in object_dict else None
        scale_settings = ScaleSettings.deserialize(object_dict['properties']['scaleSettings']) \
            if 'scaleSettings' in object_dict['properties'] else None
        target_node_count = object_dict['properties']['targetNodeCount'] \
            if 'targetNodeCount' in object_dict['properties'] else None
        vm_priority = object_dict['properties']['vmPriority'] if 'vmPriority' in object_dict['properties'] else None
        vm_size = object_dict['properties']['vmSize'] if 'vmSize' in object_dict['properties'] else None

        return AmlComputeStatus(allocation_state, allocation_state_transition_time, creation_time, current_node_count,
                                errors, modified_time, node_state_counts, provisioning_state,
                                provisioning_state_transition_time, scale_settings, target_node_count, vm_priority,
                                vm_size)


class AmlComputeNodeStateCounts(object):
    """Detailed node counts for a AmlCompute object.

    :param idle_node_count: Current number of idle nodes
    :type idle_node_count: int
    :param leaving_node_count: Current number of nodes that are being deprovisioned
    :type leaving_node_count: int
    :param preempted_node_count: Current number of preempted nodes
    :type preempted_node_count: int
    :param preparing_node_count: Current number of nodes that are being provisioned
    :type preparing_node_count: int
    :param running_node_count: Current number of in use nodes
    :type running_node_count: int
    :param unusable_node_count: Current number of unusable nodes
    :type unusable_node_count: int
    """

    def __init__(self, idle_node_count, leaving_node_count, preempted_node_count, preparing_node_count,
                 running_node_count, unusable_node_count):
        """Initialize a AmlComputeNodeStateCounts object.

        :param idle_node_count: Current number of idle nodes
        :type idle_node_count: int
        :param leaving_node_count: Current number of nodes that are being deprovisioned
        :type leaving_node_count: int
        :param preempted_node_count: Current number of preempted nodes
        :type preempted_node_count: int
        :param preparing_node_count: Current number of nodes that are being provisioned
        :type preparing_node_count: int
        :param running_node_count: Current number of in use nodes
        :type running_node_count: int
        :param unusable_node_count: Current number of unusable nodes
        :type unusable_node_count: int
        """
        self.idle_node_count = idle_node_count
        self.leaving_node_count = leaving_node_count
        self.preempted_node_count = preempted_node_count
        self.preparing_node_count = preparing_node_count
        self.running_node_count = running_node_count
        self.unusable_node_count = unusable_node_count

    def serialize(self):
        """Convert this AmlComputeNodeStateCounts object into a json serialized dictionary.

        :return: The json representation of this AmlComputeNodeStateCounts object
        :rtype: dict
        """
        return {'preparingNodeCount': self.preparing_node_count, 'runningNodeCount': self.running_node_count,
                'idleNodeCount': self.idle_node_count, 'unusableNodeCount': self.unusable_node_count,
                'leavingNodeCount': self.leaving_node_count, 'preemptedNodeCount': self.preempted_node_count}

    @staticmethod
    def deserialize(object_dict):
        """Convert a json object into a AmlComputeNodeStateCounts object.

        :param object_dict: A json object to convert to a AmlComputeNodeStateCounts object
        :type object_dict: dict
        :return: The AmlComputeNodeStateCounts representation of the provided json object
        :rtype: AmlComputeNodeStateCounts
        :raises: ComputeTargetException
        """
        if not object_dict:
            return None
        idle_node_count = object_dict['idleNodeCount'] if 'idleNodeCount' in object_dict else None
        leaving_node_count = object_dict['leavingNodeCount'] if 'leavingNodeCount' in object_dict else None
        preempted_node_count = object_dict['preemptedNodeCount'] if 'preemptedNodeCount' in object_dict else None
        preparing_node_count = object_dict['preparingNodeCount'] if 'preparingNodeCount' in object_dict else None
        running_node_count = object_dict['runningNodeCount'] if 'runningNodeCount' in object_dict else None
        unusable_node_count = object_dict['unusableNodeCount'] if 'unusableNodeCount' in object_dict else None

        return AmlComputeNodeStateCounts(idle_node_count, leaving_node_count, preempted_node_count,
                                         preparing_node_count, running_node_count, unusable_node_count)
