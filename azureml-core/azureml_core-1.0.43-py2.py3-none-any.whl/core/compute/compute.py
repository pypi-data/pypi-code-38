# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages the abstract parent class for compute targets in Azure Machine Learning service."""

try:
    from abc import ABCMeta
    ABC = ABCMeta('ABC', (), {})
except ImportError:
    from abc import ABC
from abc import abstractmethod
import json
import requests
import sys
import time
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml._compute._util import WORKSPACE_API_VERSION
from azureml._compute._util import get_paginated_compute_results
from azureml._compute._util import get_requests_session
from azureml.exceptions import ComputeTargetException, UserErrorException
from azureml._restclient.clientbase import ClientBase
from dateutil.parser import parse


class ComputeTarget(ABC):
    """Abstract parent class for all compute targets managed by Azure Machine Learning.

    .. remarks::

        ComputeTarget constructor retrieves
        the cloud representation of a Compute object associated with the provided workspace. Returns an
        instance of a child class corresponding to the specific type of the retrieved Compute object.

    :param workspace: The workspace object containing the Compute object to retrieve
    :type workspace: azureml.core.workspace.Workspace
    :param name: The name of the of the Compute object to retrieve
    :type name: str
    """

    _compute_type = None

    def __new__(cls, workspace, name):
        """Return an instance of a compute target.

        ComputeTarget constructor is used to retrieve a cloud representation of a Compute object associated with the
        provided workspace. Will return an instance of a child class corresponding to the specific type of the
        retrieved Compute object.

        :param workspace: The workspace object containing the Compute object to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the of the Compute object to retrieve
        :type name: str
        :return: An instance of a child of ComputeTarget corresponding to the specific type of the retrieved
            Compute object
        :rtype: azureml.core.compute.compute.ComputeTarget
        :raises: ComputeTargetException
        """
        if workspace and name:
            compute_payload = cls._get(workspace, name)
            if compute_payload:
                compute_type = compute_payload['properties']['computeType']
                is_attached = compute_payload['properties']['isAttachedCompute']
                for child in ComputeTarget.__subclasses__():
                    if is_attached and compute_type == 'VirtualMachine' and child.__name__ == 'DsvmCompute':
                        # Cannot attach DsvmCompute
                        continue
                    elif not is_attached and compute_type == 'VirtualMachine' and child.__name__ == 'RemoteCompute':
                        # Cannot create RemoteCompute
                        continue
                    elif compute_type == child._compute_type:
                        compute_target = super(ComputeTarget, cls).__new__(child)
                        compute_target._initialize(workspace, compute_payload)
                        return compute_target
            else:
                raise ComputeTargetException('ComputeTargetNotFound: Compute Target with name {} not found in '
                                             'provided workspace'.format(name))
        else:
            return super(ComputeTarget, cls).__new__(cls)

    def __init__(self, workspace, name):
        """Class ComputeTarget constructor.

        Retrieve a cloud representation of a Compute object associated with the provided workspace. Returns an
        instance of a child class corresponding to the specific type of the retrieved Compute object.

        :param workspace: The workspace object containing the Compute object to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the of the Compute object to retrieve
        :type name: str
        :return: An instance of a child of ComputeTarget corresponding to the specific type of the retrieved
            Compute object
        :rtype: azureml.core.compute.compute.ComputeTarget
        :raises: ComputeTargetException
        """
        pass

    @abstractmethod
    def _initialize(self, compute_resource_id, name, location, compute_type, tags, description, created_on,
                    modified_on, provisioning_state, provisioning_errors, cluster_resource_id, cluster_location,
                    workspace, mlc_endpoint, operation_endpoint, auth, is_attached):
        """Initilize abstract method.

        :param compute_resource_id:
        :type compute_resource_id: str
        :param name:
        :type name: str
        :param location:
        :type location: str
        :param compute_type:
        :type compute_type: str
        :param tags:
        :type tags: :class:`list[str]`
        :param description:
        :type description: str
        :param created_on:
        :type created_on: datetime.datetime
        :param modified_on:
        :type modified_on: datetime.datetime
        :param provisioning_state:
        :type provisioning_state: str
        :param provisioning_errors:
        :type provisioning_errors: :class:`list[dict]`
        :param cluster_resource_id:
        :type cluster_resource_id: str
        :param cluster_location:
        :type cluster_location: str
        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param mlc_endpoint:
        :type mlc_endpoint: str
        :param operation_endpoint:
        :type operation_endpoint: str
        :param auth:
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param is_attached:
        :type is_attached: boolean
        :return:
        :rtype: None
        """
        self.id = compute_resource_id
        self.name = name
        self.location = location
        self.type = compute_type
        self.tags = tags
        self.description = description
        self.created_on = parse(created_on) if created_on else None
        self.modified_on = parse(modified_on) if modified_on else None
        self.provisioning_state = provisioning_state
        self.provisioning_errors = provisioning_errors
        self.cluster_resource_id = cluster_resource_id
        self.cluster_location = cluster_location
        self.workspace = workspace
        self._mlc_endpoint = mlc_endpoint
        self._operation_endpoint = operation_endpoint
        self._auth = auth
        self.is_attached = is_attached

    @staticmethod
    def _get(workspace, name):
        """Return web response content for the compute.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :return:
        :rtype: dict
        """
        compute_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/' \
                     'workspaces/{}/computes/{}'.format(workspace.subscription_id, workspace.resource_group,
                                                        workspace.name, name)
        endpoint = 'https://management.azure.com{}'.format(compute_id)
        headers = workspace._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().get, endpoint, params=params, headers=headers)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            get_content = json.loads(content)
            return get_content
        elif resp.status_code == 404:
            return None
        else:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))

    @staticmethod
    def create(workspace, name, provisioning_configuration):
        """Provision a Compute object.

        This creates a new compute target rather than attaching an existing one.
        See https://docs.microsoft.com/azure/machine-learning/service/how-to-auto-train-remote#create-resource
        for an example of creating a resource using a provisioning_configuration.

        .. remarks::

            The type of object provisioned is
            determined based on the provided provisioning configuration.

        :param workspace: The workspace object to create the Compute object under.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the Compute object
        :type name: str
        :param provisioning_configuration: A ComputeTargetProvisioningConfiguration object that is used to determine
            the type of Compute object to provision, and how to configure it.
        :type provisioning_configuration: ComputeTargetProvisioningConfiguration
        :return: An instance of a child of ComputeTarget corresponding to the type of object provisioned
        :rtype: azureml.core.compute.compute.ComputeTarget
        :raises: ComputeTargetException
        """
        if name in ["amlcompute", "local", "containerinstance"]:
            raise UserErrorException("Please specify a different target name."
                                     " {} is a reserved name.".format(name))
        compute_type = provisioning_configuration._compute_type
        return compute_type._create(workspace, name, provisioning_configuration)

    @staticmethod
    def _create_compute_target(workspace, name, compute_payload, target_class):
        """Create compute target.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param compute_payload:
        :type compute_payload: dict
        :param target_class:
        :type target_class:
        :return:
        :rtype: azureml.core.compute.compute.ComputeTarget
        """
        endpoint_fmt = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                       'Microsoft.MachineLearningServices/workspaces/{}/computes/{}'
        endpoint = endpoint_fmt.format(workspace.subscription_id, workspace.resource_group, workspace.name, name)
        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().put, endpoint, params=params, headers=headers,
                                        json=compute_payload)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        if 'Azure-AsyncOperation' not in resp.headers:
            raise ComputeTargetException('Error, missing operation location from resp headers:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        compute_target = target_class(workspace, name)
        compute_target._operation_endpoint = resp.headers['Azure-AsyncOperation']
        return compute_target

    @staticmethod
    def attach(workspace, name, attach_configuration):
        """Attach a Compute object.

        The type of object to pass to attach_configuration is a
        :class:`azureml.core.compute.compute.ComputeTargetAttachConfiguration`
        object built using the attach_configuration function on any of the child classes of
        :class:`azureml.core.compute.compute.ComputeTarget`.

        :param workspace: The workspace object to attach the Compute object to.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to associate with the Compute object
        :type name: str
        :param attach_configuration: A ComputeTargetAttachConfiguration object that is used to determine
            the type of Compute object to attach, and how to configure it.
        :type attach_configuration: azureml.core.compute.compute.ComputeTargetAttachConfiguration
        :return: An instance of a child of ComputeTarget corresponding to the type of object attached
        :rtype: azureml.core.compute.compute.ComputeTarget
        :raises: ComputeTargetException
        """
        compute_type = attach_configuration._compute_type
        return compute_type._attach(workspace, name, attach_configuration)

    @staticmethod
    def _attach(workspace, name, attach_payload, target_class):
        """Attach implementation method.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param attach_payload:
        :type attach_payload: dict
        :param target_class:
        :type target_class:
        :return:
        :rtype:
        """
        attach_payload['location'] = workspace.location
        endpoint_fmt = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                       'Microsoft.MachineLearningServices/workspaces/{}/computes/{}'
        endpoint = endpoint_fmt.format(workspace.subscription_id, workspace.resource_group, workspace.name, name)
        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MLC_WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().put, endpoint, params=params, headers=headers,
                                        json=attach_payload)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        if 'Azure-AsyncOperation' not in resp.headers:
            raise ComputeTargetException('Error, missing operation location from resp headers:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        compute_target = target_class(workspace, name)
        compute_target._operation_endpoint = resp.headers['Azure-AsyncOperation']
        return compute_target

    @staticmethod
    def list(workspace):
        """List all ComputeTarget objects within the workspace.

        Return a list of instantiated child objects corresponding to the specific type of Compute. Objects are
        cildren of :class:`azureml.core.compute.compute.ComputeTarget`.

        :param workspace: The workspace object containing the objects to list
        :type workspace: azureml.core.workspace.Workspace
        :return: List of compute targets within the workspace
        :rtype: :class:`list[azureml.core.compute.ComputeTarget]`
        :raises: ComputeTargetException
        """
        envs = []
        endpoint = 'https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/' \
                   'Microsoft.MachineLearningServices/workspaces/{}/computes'.format(workspace.subscription_id,
                                                                                     workspace.resource_group,
                                                                                     workspace.name)
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
        paginated_results = get_paginated_compute_results(result_list, headers)
        for env in paginated_results:
            if 'properties' in env and 'computeType' in env['properties']:
                compute_type = env['properties']['computeType']
                is_attached = env['properties']['isAttachedCompute']
                env_obj = None
                for child in ComputeTarget.__subclasses__():
                    if is_attached and compute_type == 'VirtualMachine' and child.__name__ == 'DsvmCompute':
                        # Cannot attach DsvmCompute
                        continue
                    elif not is_attached and compute_type == 'VirtualMachine' and child.__name__ == 'RemoteCompute':
                        # Cannot create RemoteCompute
                        continue
                    elif compute_type == child._compute_type:
                        env_obj = child.deserialize(workspace, env)
                        break
                if env_obj:
                    envs.append(env_obj)
        return envs

    def wait_for_completion(self, show_output=False):
        """Wait for the current provisioning operation to finish on the cluster.

        :param show_output: Boolean to provide more verbose output. Defaults to False
        :type show_output: bool
        :raises: ComputeTargetException
        """
        try:
            operation_state, error = self._wait_for_completion(show_output)
            print('Provisioning operation finished, operation "{}"'.format(operation_state))
            self.refresh_state()
            if operation_state != 'Succeeded':
                if error and 'statusCode' in error and 'message' in error:
                    error_response = ('StatusCode: {}\n'
                                      'Message: {}'.format(error['statusCode'], error['message']))
                else:
                    error_response = error

                raise ComputeTargetException('Compute object provisioning polling reached non-successful terminal '
                                             'state, current provisioning state: {}\n'
                                             'Provisioning operation error:\n'
                                             '{}'.format(self.provisioning_state, error_response))
        except ComputeTargetException as e:
            if e.message == 'No operation endpoint':
                self.refresh_state()
                raise ComputeTargetException('Long running operation information not known, unable to poll. '
                                             'Current state is {}'.format(self.provisioning_state))
            else:
                raise e

    def _wait_for_completion(self, show_output):
        """Wait for completion implementation.

        :param show_output:
        :type show_output: bool
        :return:
        :rtype: (str, dict)
        """
        if not self._operation_endpoint:
            raise ComputeTargetException('No operation endpoint')
        operation_state, error = self._get_operation_state()
        current_state = operation_state
        if show_output:
            sys.stdout.write('{}'.format(current_state))
            sys.stdout.flush()
        while operation_state != 'Succeeded' and operation_state != 'Failed' and operation_state != 'Canceled':
            time.sleep(5)
            operation_state, error = self._get_operation_state()
            if show_output:
                sys.stdout.write('.')
                if operation_state != current_state:
                    sys.stdout.write('\n{}'.format(operation_state))
                    current_state = operation_state
                sys.stdout.flush()
        return operation_state, error

    def _get_operation_state(self):
        """Retrun operation state.

        :return:
        :rtype: (str, dict)
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': WORKSPACE_API_VERSION}
        resp = ClientBase._execute_func(get_requests_session().get, self._operation_endpoint, params=params,
                                        headers=headers)

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
        content = json.loads(content)
        status = content['status']
        error = content['error']['error'] if 'error' in content else None
        return status, error

    @abstractmethod
    def refresh_state(self):
        """Perform an in-place update of the properties of the object.

        Update properties based on the current state of the corresponding cloud object.

        Primarily useful for manual polling of compute state. Abstract
        method implemented by child classes of :class:`azureml.core.compute.compute.ComputeTarget`.
        """
        pass

    def get_status(self):
        """Retrieve the current provisioning state of the Compute object.

        :return: Current provisioning_state
        :rtype: str
        """
        self.refresh_state()
        return self.provisioning_state

    @abstractmethod
    def delete(self):
        """Remove the Compute object from its associated workspace.

        Abstract method implemented by child classes of :class:`azureml.core.compute.compute.ComputeTarget`.

        .. remarks::

            If this object was created through Azure Machine Learning service, the corresponding cloud based objects
            will also be deleted. If this object was created externally and only attached to the workspace, it will
            raise exception and nothing will be changed.
        """
        pass

    @abstractmethod
    def detach(self):
        """Detach the Compute object from its associated workspace.

        Abstract method implemented by child classes of :class:`azureml.core.compute.compute.ComputeTarget`.

        .. remarks::

            Underlying cloud objects are not deleted, only the association is removed.
        """
        pass

    def _delete_or_detach(self, underlying_resource_action):
        """Remove the Compute object from its associated workspace.

        If underlying_resource_action is 'delete', the corresponding cloud based objects will also be deleted.
        If underlying_resource_action is 'detach', no underlying cloud object will be deleted, the association
        will just be removed.

        :param underlying_resource_action: whether delete or detach the underlying cloud object
        :type underlying_resource_action: str
        :raises: ComputeTargetException
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MLC_WORKSPACE_API_VERSION, 'underlyingResourceAction': underlying_resource_action}
        resp = ClientBase._execute_func(get_requests_session().delete, self._mlc_endpoint, params=params,
                                        headers=headers)

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ComputeTargetException('Received bad response from Resource Provider:\n'
                                         'Response Code: {}\n'
                                         'Headers: {}\n'
                                         'Content: {}'.format(resp.status_code, resp.headers, resp.content))

        self.provisioning_state = 'Deleting'

    @abstractmethod
    def serialize(self):
        """Convert this Compute object into a json serialized dictionary.

        :return: The json representation of this Compute object
        :rtype: dict
        """
        created_on = self.created_on.isoformat() if self.created_on else None
        modified_on = self.modified_on.isoformat() if self.modified_on else None
        compute = {'id': self.id, 'name': self.name, 'location': self.location, 'type': self.type, 'tags': self.tags,
                   'description': self.description, 'created_on': created_on, 'modified_on': modified_on,
                   'provisioning_state': self.provisioning_state, 'provisioning_errors': self.provisioning_errors}
        return compute

    @staticmethod
    @abstractmethod
    def deserialize(workspace, object_dict):
        """Convert a json object into a Compute object.

        Will fail if the provided workspace is not the workspace the Compute is associated with.

        :param workspace: The workspace object the Compute object is associated with
        :type workspace: azureml.core.workspace.Workspace
        :param object_dict: A json object to convert to a Compute object
        :type object_dict: dict
        :return: The Compute representation of the provided json object
        :rtype: azureml.core.compute.compute.ComputeTarget
        """
        pass

    @staticmethod
    @abstractmethod
    def _validate_get_payload(payload):
        pass


class ComputeTargetProvisioningConfiguration(ABC):
    """Abstract parent class for all ComputeTarget provisioning configuration objects.

    These objects are used to define the configuration parameters for provisioning Compute objects.

    :param type: The type of ComputeTarget this object is associated with
    :type type: azureml.core.compute.compute.ComputeTarget
    :param location: The Azure region to provision the Compute object in.
    :type location: str
    """

    def __init__(self, type, location):
        """Initialize the ProvisioningConfiguration object.

        :param type: The type of ComputeTarget this object is associated with
        :type type: azureml.core.compute.compute.ComputeTarget
        :param location: The Azure region to provision the Compute object in.
        :type location: str
        :return: The ProvisioningConfiguration object
        :rtype: ComputeTargetProvisioningConfiguration
        """
        self._compute_type = type
        self.location = location

    @abstractmethod
    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        pass


class ComputeTargetAttachConfiguration(ABC):
    """Abstract parent class for all ComputeTarget attach configuration objects.

    These objects are used to define the configuration parameters for attaching Compute objects.
    """

    def __init__(self, type):
        """Initialize the AttachConfiguration object.

        :param type: The type of ComputeTarget this object is associated with
        :type type: azureml.core.compute.compute.ComputeTarget
        :return: The AttachConfiguration object
        :rtype: ComputeTargetAttachConfiguration
        """
        self._compute_type = type

    @abstractmethod
    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a ComputeTargetException if validation fails.

        :raises: ComputeTargetException
        """
        pass
