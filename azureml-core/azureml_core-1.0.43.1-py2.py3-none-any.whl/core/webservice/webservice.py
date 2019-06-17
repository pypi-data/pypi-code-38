# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing the abstract parent class for Webservices in Azure Machine Learning service."""

try:
    from abc import ABCMeta

    ABC = ABCMeta('ABC', (), {})
except ImportError:
    from abc import ABC
from abc import abstractmethod
import copy
import json
import logging
import os
import requests
import sys
import time
from dateutil.parser import parse
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.exceptions import WebserviceException
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import CLOUD_DEPLOYABLE_IMAGE_FLAVORS
from azureml._model_management._constants import ACI_WEBSERVICE_TYPE, AKS_WEBSERVICE_TYPE, FPGA_WEBSERVICE_TYPE, \
    IOT_WEBSERVICE_TYPE
from azureml._model_management._constants import LOCAL_WEBSERVICE_TYPE, UNKNOWN_WEBSERVICE_TYPE
from azureml._model_management._util import get_paginated_results
from azureml._model_management._util import get_requests_session
from azureml._model_management._util import webservice_name_validation
from azureml._model_management._util import _get_mms_url
from azureml._restclient.clientbase import ClientBase

module_logger = logging.getLogger(__name__)


class Webservice(ABC):
    """
    Class for Azure Machine Learning Webservices.

    Webservice constructor is used to retrieve a cloud representation of a Webservice object associated with the
    provided Workspace. Returns an instance of a child class corresponding to the specific type of the retrieved
    Webservice object. Class allows for deploying machine learning models from either a Model or Image object. See
    the following how-to for code
    examples: https://docs.microsoft.com/azure/machine-learning/service/how-to-deploy-and-where

    :param workspace: The workspace object containing the Webservice object to retrieve
    :type workspace: azureml.core.workspace.Workspace
    :param name: The name of the Webservice object to retrieve
    :type name: str
    """

    _expected_payload_keys = ['computeType', 'createdTime', 'description', 'imageId', 'kvTags', 'name', 'properties']
    _webservice_type = None

    def __new__(cls, workspace, name):
        """Webservice constructor.

        Webservice constructor is used to retrieve a cloud representation of a Webservice object associated with the
        provided workspace. Will return an instance of a child class corresponding to the specific type of the
        retrieved Webservice object.

        :param workspace: The workspace object containing the Webservice object to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the of the Webservice object to retrieve
        :type name: str
        :return: An instance of a child of Webservice corresponding to the specific type of the retrieved
            Webservice object
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        if workspace and name:
            service_payload = cls._get(workspace, name)
            if service_payload:
                service_type = service_payload['computeType']
                child_class = None
                for child in Webservice.__subclasses__():
                    if service_type == child._webservice_type:
                        child_class = child
                        break
                    elif child._webservice_type == UNKNOWN_WEBSERVICE_TYPE:
                        child_class = child

                if child_class:
                    service = super(Webservice, cls).__new__(child_class)
                    service._initialize(workspace, service_payload)
                    return service
            else:
                raise WebserviceException('WebserviceNotFound: Webservice with name {} not found in provided '
                                          'workspace'.format(name))
        else:
            return super(Webservice, cls).__new__(cls)

    def __init__(self, workspace, name):
        """Webservice constructor.

        Webservice constructor is used to retrieve a cloud representation of a Webservice object associated with the
        provided workspace. Will return an instance of a child class corresponding to the specific type of the
        retrieved Webservice object.

        :param workspace: The workspace object containing the Webservice object to retrieve
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the of the Webservice object to retrieve
        :type name: str
        :return: An instance of a child of Webservice corresponding to the specific type of the retrieved
            Webservice object
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        pass

    @property
    def _webservice_session(self):
        if not self._session:
            self._session = requests.Session()
            self._session.headers.update({'Content-Type': 'application/json'})

            if self.auth_enabled:
                service_keys = self.get_keys()
                self._session.headers.update({'Authorization': 'Bearer ' + service_keys[0]})

        return self._session

    def _initialize(self, workspace, obj_dict):
        """Initialize the Webservice instance.

        This is used because the constructor is used as a getter.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param obj_dict:
        :type obj_dict: dict
        :return:
        :rtype: None
        """
        # Expected payload keys
        self.auth_enabled = obj_dict['authEnabled']
        self.compute_type = obj_dict['computeType']
        self.created_time = parse(obj_dict['createdTime'])
        self.description = obj_dict['description']
        self.image_id = obj_dict['imageId']
        self.tags = obj_dict['kvTags']
        self.name = obj_dict['name']
        self.properties = obj_dict['properties']

        # Common amongst Webservice classes but optional payload keys
        self.error = obj_dict['error'] if 'error' in obj_dict else None
        self.image = Image.deserialize(workspace, obj_dict['imageDetails']) if 'imageDetails' in obj_dict else None
        self.state = obj_dict['state'] if 'state' in obj_dict else None
        self.updated_time = parse(obj_dict['updatedTime']) if 'updatedTime' in obj_dict else None

        # Utility payload keys
        self._auth = workspace._auth
        self._operation_endpoint = None
        self._mms_endpoint = _get_mms_url(workspace) + '/services/{}'.format(self.name)
        self.workspace = workspace
        self._session = None

    @staticmethod
    def _get(workspace, name=None):
        """Get the Webservice with the corresponding name.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :return:
        :rtype: dict
        """
        if not name:
            raise WebserviceException('Name must be provided', logger=module_logger)

        base_url = _get_mms_url(workspace)
        mms_url = base_url + '/services'

        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'expand': 'true'}

        service_url = mms_url + '/{}'.format(name)

        resp = ClientBase._execute_func(get_requests_session().get, service_url, headers=headers, params=params)
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            service_payload = json.loads(content)
            return service_payload
        elif resp.status_code == 404:
            return None
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    @staticmethod
    def deploy(workspace, name, model_paths, image_config, deployment_config=None, deployment_target=None):
        """
        Deploy a Webservice from zero or more model files.

        This will register any models files provided and create an image in the process,
        all associated with the specified Workspace. Use this function when you have a directory of
        models to deploy that haven't been previously registered.

        :param workspace: A Workspace object to associate the Webservice with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to give the deployed service. Must be unique to the workspace, only consist of lowercase
            letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param model_paths: A list of on-disk paths to model files or folder. Can be an empty list.
        :type model_paths: :class:`list[str]`
        :param image_config: An ImageConfig object used to determine required Image properties.
        :type image_config: azureml.core.image.image.ImageConfig
        :param deployment_config: A WebserviceDeploymentConfiguration used to configure the webservice. If one is not
            provided, an empty configuration object will be used based on the desired target.
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target: A ComputeTarget to deploy the Webservice to. As Azure Container Instances
            has no associated ComputeTarget, leave this parameter as None to deploy to Azure Container
            Instances.
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return: A Webservice object corresponding to the deployed webservice
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        webservice_name_validation(name)
        Webservice._check_for_local_deployment(deployment_config)
        Webservice._check_for_existing_webservice(workspace, name)
        models = []
        for model_path in model_paths:
            model_name = os.path.basename(model_path.rstrip(os.sep))[:30]
            models.append(Model.register(workspace, model_path, model_name))
        return Webservice.deploy_from_model(workspace, name, models, image_config, deployment_config,
                                            deployment_target)

    @staticmethod
    def deploy_from_model(workspace, name, models, image_config, deployment_config=None, deployment_target=None):
        """
        Deploy a Webservice from zero or more model objects.

        This function is similar to :func:`deploy`, but does not :func:`azureml.core.model.Model.register` the
        models. Use this function if you have model objects that are already registered. This will create an image
        in the process, associated with the specified Workspace.

        :param workspace: A Workspace object to associate the Webservice with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to give the deployed service. Must be unique to the workspace, only consist of lowercase
            letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param models: A list of model objects. Can be an empty list.
        :type models: :class:`list[azureml.core.model.Model]`
        :param image_config: An ImageConfig object used to determine required Image properties.
        :type image_config: azureml.core.image.image.ImageConfig
        :param deployment_config: A WebserviceDeploymentConfiguration used to configure the webservice. If one is not
            provided, an empty configuration object will be used based on the desired target.
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target: A ComputeTarget to deploy the Webservice to. As ACI has no associated ComputeTarget,
            leave this parameter as None to deploy to ACI.
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return: A Webservice object corresponding to the deployed webservice
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        webservice_name_validation(name)
        Webservice._check_for_local_deployment(deployment_config)
        Webservice._check_for_existing_webservice(workspace, name)

        image = Image.create(workspace, name, models, image_config)
        image.wait_for_creation(True)
        if image.creation_state != 'Succeeded':
            raise WebserviceException('Error occurred creating image {} for service. More information can be found '
                                      'here: {}\n Generated DockerFile can be found here: {}'.format(
                                          image.id,
                                          image.image_build_log_uri,
                                          image.generated_dockerfile_uri), logger=module_logger)
        return Webservice.deploy_from_image(workspace, name, image, deployment_config, deployment_target)

    @staticmethod
    def deploy_from_image(workspace, name, image, deployment_config=None, deployment_target=None):
        """
        Deploy a Webservice from an Image object.

        Use this function if you already have an :class:`azureml.core.image.image.Image` object created
        for a model.

        :param workspace: A Workspace object to associate the Webservice with
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to give the deployed service. Must be unique to the workspace, only consist of lowercase
            letters, numbers, or dashes, start with a letter, and be between 3 and 32 characters long.
        :type name: str
        :param image: An :class:`azureml.core.image.image.Image` object to deploy.
        :type image: azureml.core.image.image.Image
        :param deployment_config: A WebserviceDeploymentConfiguration used to configure the webservice. If one is not
            provided, an empty configuration object will be used based on the desired target.
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target: A ComputeTarget to deploy the Webservice to. As Azure Container Instances has
            no associated ComputeTarget, leave this parameter as None to deploy to Azure Container Instances.
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return: A Webservice object corresponding to the deployed webservice
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        webservice_name_validation(name)
        Webservice._check_for_local_deployment(deployment_config)
        Webservice._check_for_existing_webservice(workspace, name)
        if deployment_target is None:
            if deployment_config is None:
                for child in Webservice.__subclasses__():  # This is a hack to avoid recursive imports
                    if child._webservice_type == ACI_WEBSERVICE_TYPE:
                        return child._deploy(workspace, name, image, deployment_config)
            return deployment_config._webservice_type._deploy(workspace, name, image, deployment_config)

        else:
            if deployment_config is None:
                for child in Webservice.__subclasses__():  # This is a hack to avoid recursive imports
                    if child._webservice_type == AKS_WEBSERVICE_TYPE:
                        return child._deploy(workspace, name, image, deployment_config, deployment_target)

        return deployment_config._webservice_type._deploy(workspace, name, image, deployment_config, deployment_target)

    @staticmethod
    def _check_for_existing_webservice(workspace, name):
        try:
            Webservice(workspace, name=name)
            raise WebserviceException('Error, there is already a service with name {} found in '
                                      'workspace {}'.format(name, workspace._workspace_name))
        except WebserviceException as e:
            if 'WebserviceNotFound' in e.message:
                pass
            else:
                raise WebserviceException(e.message, logger=module_logger)

    @staticmethod
    def _check_for_local_deployment(deployment_config):
        from azureml.core.webservice.local import LocalWebserviceDeploymentConfiguration
        if deployment_config and (type(deployment_config) is LocalWebserviceDeploymentConfiguration):
            raise WebserviceException('This method does not support local deployment configuration. Please use '
                                      'deploy_local_from_model for local deployment.')

    @staticmethod
    def deploy_local_from_model(workspace, name, models, image_config, deployment_config=None, wait=False):
        """
        Build and deploy a LocalWebservice for testing. Requires Docker to be installed and configured.

        :param workspace: A Workspace object with which to associate the Webservice.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name to give the deployed service. Must be unique on the local machine.
        :type name: str
        :param models: A list of model objects. Can be an empty list.
        :type models: :class:`list[azureml.core.model.Model]`
        :param image_config: An ImageConfig object used to determine required service image properties.
        :type image_config: azureml.core.image.image.ImageConfig
        :param deployment_config: A LocalWebserviceDeploymentConfiguration used to configure the webservice. If one is
            not provided, an empty configuration object will be used.
        :type deployment_config: LocalWebserviceDeploymentConfiguration
        :param wait: Wait for the LocalWebservice's Docker container to report as healthy. Throws an exception if the
            container crashes. (Default: False)
        :type wait: bool
        :rtype: azureml.core.webservice.LocalWebservice
        :raises: WebserviceException
        """
        webservice_name_validation(name)

        for child in Webservice.__subclasses__():  # This is a hack to avoid recursive imports
            if child._webservice_type == LOCAL_WEBSERVICE_TYPE:
                return child._deploy(workspace, name, models, image_config, deployment_config, wait)

    @staticmethod
    @abstractmethod
    def _deploy(workspace, name, image, deployment_config, deployment_target):
        """Deploy the Webservice to the cloud.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param image:
        :type image: azureml.core.image.image.Image
        :param deployment_config:
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target:
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return:
        :rtype: azureml.core.webservice.webservice.Webservice
        """
        pass

    @staticmethod
    def _deploy_webservice(workspace, name, webservice_payload, webservice_class):
        """Deploy the Webservice to the cloud.

        :param workspace:
        :type workspace: azureml.core.workspace.Workspace
        :param name:
        :type name: str
        :param webservice_payload:
        :type webservice_payload: dict
        :param webservice_class:
        :type webservice_class: azureml.core.webservice.webservice.Webservice
        :return:
        :rtype: azureml.core.webservice.webservice.Webservice
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        base_url = _get_mms_url(workspace)
        mms_endpoint = base_url + '/services'

        print('Creating service')
        try:
            resp = ClientBase._execute_func(get_requests_session().post, mms_endpoint, params=params, headers=headers,
                                            json=webservice_payload)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)
        if resp.status_code >= 400:
            raise WebserviceException('Error occurred creating service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        if 'Operation-Location' in resp.headers:
            operation_location = resp.headers['Operation-Location']
        else:
            raise WebserviceException('Missing response header key: Operation-Location', resp.status_code,
                                      logger=module_logger)
        create_operation_status_id = operation_location.split('/')[-1]
        operation_url = base_url + '/operations/{}'.format(create_operation_status_id)

        service = webservice_class(workspace, name=name)
        service._operation_endpoint = operation_url
        return service

    def wait_for_deployment(self, show_output=False):
        """Automatically poll on the running Webservice deployment.

        Wait for the Webservice to reach a terminal state. Will throw a WebserviceException if it reaches a
        non-successful terminal state.

        :param show_output: Option to print more verbose output (Default: False)
        :type show_output: bool
        :raises: WebserviceException
        """
        try:
            operation_state, error = self._wait_for_operation_to_complete(show_output)
            self.update_deployment_state()
            if operation_state != 'Succeeded':
                if error:  # Operation response error
                    error_response = json.dumps(error, indent=2)
                elif self.error:  # Service response error
                    error_response = json.dumps(self.error, indent=2)
                else:
                    error_response = 'No error message received from server.'

                raise WebserviceException('Service deployment polling reached non-successful terminal state, current '
                                          'service state: {}\n'
                                          'Error:\n'
                                          '{}'.format(self.state, error_response), logger=module_logger)
            print('{} service creation operation finished, operation "{}"'.format(self._webservice_type,
                                                                                  operation_state))
        except WebserviceException as e:
            if e.message == 'No operation endpoint':
                self.update_deployment_state()
                raise WebserviceException('Long running operation information not known, unable to poll. '
                                          'Current state is {}'.format(self.state), logger=module_logger)
            else:
                raise WebserviceException(e.message, logger=module_logger)

    def _wait_for_operation_to_complete(self, show_output):
        """Poll on the async operation for this Webservice.

        :param show_output:
        :type show_output: bool
        :return:
        :rtype: (str, str)
        """
        if not self._operation_endpoint:
            raise WebserviceException('No operation endpoint', logger=module_logger)
        state, error = self._get_operation_state()
        current_state = state
        if show_output:
            sys.stdout.write('{}'.format(current_state))
            sys.stdout.flush()
        while state != 'Succeeded' and state != 'Failed' and state != 'Cancelled' and state != 'TimedOut':
            time.sleep(5)
            state, error = self._get_operation_state()
            if show_output:
                sys.stdout.write('.')
                if state != current_state:
                    sys.stdout.write('\n{}'.format(state))
                    current_state = state
                sys.stdout.flush()
        return state, error

    def _get_operation_state(self):
        """Get the current async operation state for the Webservice.

        :return:
        :rtype: str, str
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        resp = ClientBase._execute_func(get_requests_session().get, self._operation_endpoint, headers=headers,
                                        params=params, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Resource Provider:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)
        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        content = json.loads(content)
        state = content['state']
        error = content['error'] if 'error' in content else None
        return state, error

    def update_deployment_state(self):
        """
        Refresh the current state of the in-memory object.

        Perform an in-place update of the properties of the object based on the current state of the corresponding
        cloud object. Primarily useful for manual polling of creation state.
        """
        service = Webservice(self.workspace, name=self.name)
        for key in self.__dict__.keys():
            if key is not "_operation_endpoint":
                self.__dict__[key] = service.__dict__[key]

    @staticmethod
    def list(workspace, compute_type=None, image_name=None, image_id=None, model_name=None, model_id=None, tags=None,
             properties=None):
        """List the Webservices associated with the corresponding Workspace. Can be filtered with specific parameters.

        :param workspace: The Workspace object to list the Webservices in.
        :type workspace: azureml.core.workspace.Workspace
        :param compute_type: Filter to list only specific Webservice types. Options are 'ACI', 'AKS'.
        :type compute_type: str
        :param image_name: Filter list to only include Webservices deployed with the specific image name
        :type image_name: str
        :param image_id: Filter list to only include Webservices deployed with the specific image id
        :type image_id: str
        :param model_name: Filter list to only include Webservices deployed with the specific model name
        :type model_name: str
        :param model_id: Filter list to only include Webservices deployed with the specific model id
        :type model_id: str
        :param tags: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type tags: :class:`list`
        :param properties: Will filter based on the provided list, by either 'key' or '[key, value]'.
            Ex. ['key', ['key2', 'key2 value']]
        :type properties: :class:`list`
        :return: A filtered list of Webservices in the provided Workspace
        :rtype: :class:`list[Webservice]`
        :raises: WebserviceException
        """
        webservices = []
        headers = {'Content-Type': 'application/json'}
        headers.update(workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'expand': 'true'}

        base_url = _get_mms_url(workspace)
        mms_workspace_url = base_url + '/services'

        if compute_type:
            if compute_type.upper() != ACI_WEBSERVICE_TYPE and \
               compute_type.upper() != AKS_WEBSERVICE_TYPE and \
               compute_type.upper() != FPGA_WEBSERVICE_TYPE and \
               compute_type.upper() != IOT_WEBSERVICE_TYPE:
                raise WebserviceException('Invalid compute type "{}". Valid options are "ACI", '
                                          '"AKS", "FPGA", "IOT"'.format(compute_type), logger=module_logger)
            params['computeType'] = compute_type
        if image_name:
            params['imageName'] = image_name
        if image_id:
            params['imageId'] = image_id
        if model_name:
            params['modelName'] = model_name
        if model_id:
            params['modelId'] = model_id
        if tags:
            tags_query = ""
            for tag in tags:
                if type(tag) is list:
                    tags_query = tags_query + tag[0] + "=" + tag[1] + ","
                else:
                    tags_query = tags_query + tag + ","
            tags_query = tags_query[:-1]
            params['tags'] = tags_query
        if properties:
            properties_query = ""
            for prop in properties:
                if type(prop) is list:
                    properties_query = properties_query + prop[0] + "=" + prop[1] + ","
                else:
                    properties_query = properties_query + prop + ","
            properties_query = properties_query[:-1]
            params['properties'] = properties_query

        try:
            resp = ClientBase._execute_func(get_requests_session().get, mms_workspace_url, headers=headers,
                                            params=params, timeout=MMS_SYNC_TIMEOUT_SECONDS)
            resp.raise_for_status()
        except requests.Timeout:
            raise WebserviceException('Error, request to MMS timed out to URL: {}'.format(mms_workspace_url),
                                      logger=module_logger)
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        services_payload = json.loads(content)
        paginated_results = get_paginated_results(services_payload, headers)
        for service_dict in paginated_results:
            service_type = service_dict['computeType']
            child_class = None

            for child in Webservice.__subclasses__():
                if service_type == child._webservice_type:
                    child_class = child
                    break
                elif child._webservice_type == UNKNOWN_WEBSERVICE_TYPE:
                    child_class = child

            if child_class:
                service_obj = child_class.deserialize(workspace, service_dict)
                webservices.append(service_obj)
        return webservices

    def _add_tags(self, tags):
        """Add tags to this Webservice.

        :param tags:
        :type tags: dict[str, str]
        :return:
        :rtype: dict[str, str]
        """
        updated_tags = self.tags
        if updated_tags is None:
            return copy.deepcopy(tags)
        else:
            for key in tags:
                if key in updated_tags:
                    print("Replacing tag {} -> {} with {} -> {}".format(key, updated_tags[key], key, tags[key]))
                updated_tags[key] = tags[key]

        return updated_tags

    def _remove_tags(self, tags):
        """Remove tags from this Webservice.

        :param tags:
        :type tags: :class:`list[str]`
        :return:
        :rtype: :class:`list[str]`
        """
        updated_tags = self.tags
        if updated_tags is None:
            print('Model has no tags to remove.')
            return updated_tags
        else:
            if type(tags) is not list:
                tags = [tags]
            for key in tags:
                if key in updated_tags:
                    del updated_tags[key]
                else:
                    print('Tag with key {} not found.'.format(key))

        return updated_tags

    def _add_properties(self, properties):
        """Add properties to this Webservice.

        :param properties:
        :type properties: dict[str, str]
        :return:
        :rtype: dict[str, str]
        """
        updated_properties = self.properties
        if updated_properties is None:
            return copy.deepcopy(properties)
        else:
            for key in properties:
                if key in updated_properties:
                    print("Replacing tag {} -> {} with {} -> {}".format(key, updated_properties[key],
                                                                        key, properties[key]))
                updated_properties[key] = properties[key]

        return updated_properties

    def get_logs(self, num_lines=5000):
        """Retrieve logs for this Webservice.

        :param num_lines: The maximum number of log lines to retrieve (Default: 5000)
        :type num_lines: int
        :return: The logs for this Webservice
        :rtype: str
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(self.workspace._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION, 'tail': num_lines}
        service_logs_url = self._mms_endpoint + '/logs'

        resp = ClientBase._execute_func(get_requests_session().get, service_logs_url, headers=headers, params=params)
        if resp.status_code >= 400:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)
        else:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            service_payload = json.loads(content)
            if 'content' not in service_payload:
                raise WebserviceException('Invalid response, missing "content":\n'
                                          '{}'.format(service_payload), logger=module_logger)
            else:
                return service_payload['content']

    @abstractmethod
    def run(self, input):
        """
        Call this Webservice with the provided input.

        Abstract method implemented by child classes of :class:`azureml.core.webservice.Webservice`.

        :param input: The input data to call the Webservice with. This is the data your machine learning model expects
            as an input to run predictions.
        :type input: varies
        :return: The result of calling the Webservice. This will return predictions run from your machine
            learning model.
        :rtype: dict
        :raises: WebserviceException
        """
        pass

    def get_keys(self):
        """Retrieve auth keys for this Webservice.

        :return: The auth keys for this Webservice
        :rtype: (str, str)
        :raises: WebserviceException
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}
        list_keys_url = self._mms_endpoint + '/listkeys'

        try:
            resp = ClientBase._execute_func(get_requests_session().post, list_keys_url, params=params, headers=headers)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        content = resp.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        keys_content = json.loads(content)
        if 'primaryKey' not in keys_content:
            raise WebserviceException('Invalid response key: primaryKey', logger=module_logger)
        if 'secondaryKey' not in keys_content:
            raise WebserviceException('Invalid response key: secondaryKey', logger=module_logger)
        primary_key = keys_content['primaryKey']
        secondary_key = keys_content['secondaryKey']

        return primary_key, secondary_key

    def regen_key(self, key):
        """Regenerate one of the Webservice's keys. Must specify either 'Primary' or 'Secondary' key.

        :param key: Which key to regenerate. Options are 'Primary' or 'Secondary'
        :type key: str
        :raises: WebserviceException
        """
        headers = {'Content-Type': 'application/json'}
        headers.update(self._auth.get_authentication_header())
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        if not key:
            raise WebserviceException('Error, must specify which key with be regenerated: Primary, Secondary',
                                      logger=module_logger)
        key = key.capitalize()
        if key != 'Primary' and key != 'Secondary':
            raise WebserviceException('Error, invalid value provided for key: {}.\n'
                                      'Valid options are: Primary, Secondary'.format(key), logger=module_logger)
        keys_url = self._mms_endpoint + '/regenerateKeys'
        body = {'keyType': key}
        try:
            resp = ClientBase._execute_func(get_requests_session().post, keys_url, params=params, headers=headers,
                                            json=body)
            resp.raise_for_status()
        except requests.ConnectionError:
            raise WebserviceException('Error connecting to {}.'.format(keys_url), logger=module_logger)
        except requests.exceptions.HTTPError:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

        if 'Operation-Location' in resp.headers:
            operation_location = resp.headers['Operation-Location']
        else:
            raise WebserviceException('Missing operation location from response header, unable to determine status.',
                                      logger=module_logger)
        create_operation_status_id = operation_location.split('/')[-1]
        operation_endpoint = _get_mms_url(self.workspace) + '/operations/{}'.format(create_operation_status_id)
        operation_state = 'Running'
        while operation_state != 'Cancelled' and operation_state != 'Succeeded' and operation_state != 'Failed' \
                and operation_state != 'TimedOut':
            try:
                operation_resp = ClientBase._execute_func(get_requests_session().get, operation_endpoint,
                                                          params=params, headers=headers,
                                                          timeout=MMS_SYNC_TIMEOUT_SECONDS)
                operation_resp.raise_for_status()
            except requests.ConnectionError:
                raise WebserviceException('Error connecting to {}.'.format(operation_endpoint), logger=module_logger)
            except requests.Timeout:
                raise WebserviceException('Error, request to {} timed out.'.format(operation_endpoint),
                                          logger=module_logger)
            except requests.exceptions.HTTPError:
                raise WebserviceException('Received bad response from Model Management Service:\n'
                                          'Response Code: {}\n'
                                          'Headers: {}\n'
                                          'Content: {}'.format(operation_resp.status_code, operation_resp.headers,
                                                               operation_resp.content), logger=module_logger)
            content = operation_resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            content = json.loads(content)
            if 'state' in content:
                operation_state = content['state']
            else:
                raise WebserviceException('Missing state from operation response, unable to determine status',
                                          logger=module_logger)
            error = content['error'] if 'error' in content else None
        if operation_state != 'Succeeded':
            raise WebserviceException('Error, key regeneration operation "{}" with message '
                                      '"{}"'.format(operation_state, error), logger=module_logger)

    @abstractmethod
    def update(self, *args):
        """
        Update the Webservice parameters.

        Abstract method implemented by child classes of :class:`azureml.core.webservice.Webservice`.
        Possible parameters to update vary based on Webservice child type. For Azure Container Instances
        webservices, see :func:`azureml.core.webservice.aci.AciWebservice.update` for specific parameters.

        :param args: Values to update
        :type args: varies
        :raises: WebserviceException
        """
        pass

    def delete(self):
        """
        Delete this Webservice from its associated workspace.

        This function call is not asynchronous; it runs until the resource is deleted.

        :raises: WebserviceException
        """
        headers = self._auth.get_authentication_header()
        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        resp = ClientBase._execute_func(get_requests_session().delete, self._mms_endpoint, headers=headers,
                                        params=params, timeout=MMS_SYNC_TIMEOUT_SECONDS)

        if resp.status_code == 200:
            self.state = 'Deleting'
        elif resp.status_code == 202:
            self.state = 'Deleting'
            if 'Operation-Location' in resp.headers:
                operation_location = resp.headers['Operation-Location']
            else:
                raise WebserviceException('Missing response header key: Operation-Location', resp.status_code,
                                          logger=module_logger)
            create_operation_status_id = operation_location.split('/')[-1]
            operation_url = _get_mms_url(self.workspace) + '/operations/{}'.format(create_operation_status_id)

            self._operation_endpoint = operation_url
            self._wait_for_operation_to_complete(True)
        elif resp.status_code == 204:
            print('No service with name {} found to delete.'.format(self.name))
        else:
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content),
                                      logger=module_logger)

    def serialize(self):
        """
        Convert this Webservice into a json serialized dictionary.

        Use :func:`deserialize` to convert back into a Webservice object.

        :return: The json representation of this Webservice
        :rtype: dict
        """
        created_time = self.created_time.isoformat() if self.created_time else None
        updated_time = self.updated_time.isoformat() if self.updated_time else None
        image_details = self.image.serialize()
        return {'name': self.name, 'description': self.description, 'tags': self.tags,
                'properties': self.properties, 'state': self.state, 'createdTime': created_time,
                'updatedTime': updated_time, 'error': self.error, 'computeType': self.compute_type,
                'workspaceName': self.workspace.name, 'imageId': self.image_id, 'imageDetails': image_details,
                'scoringUri': self.scoring_uri}

    @classmethod
    def deserialize(cls, workspace, webservice_payload):
        """
        Convert a json object generated from :func:`azureml.core.Webservice.serialize` into a Webservice object.

        Will fail if the provided workspace is not the workspace the Webservice is registered under.

        :param cls:
        :type cls:
        :param workspace: The workspace object the Webservice is registered under
        :type workspace: azureml.core.workspace.Workspace
        :param webservice_payload: A json object to convert to a Webservice object
        :type webservice_payload: dict
        :return: The Webservice representation of the provided json object
        :rtype: azureml.core.webservice.webservice.Webservice
        """
        cls._validate_get_payload(webservice_payload)
        webservice = cls(None, None)
        webservice._initialize(workspace, webservice_payload)
        return webservice

    @classmethod
    def _validate_get_payload(cls, payload):
        """Validate the payload for this Webservice.

        :param payload:
        :type payload: dict
        :return:
        :rtype:
        """
        if 'computeType' not in payload:
            raise WebserviceException('Invalid payload for {} webservice, missing computeType:\n'
                                      '{}'.format(cls._webservice_type, payload), logger=module_logger)
        if payload['computeType'] != cls._webservice_type and cls._webservice_type != UNKNOWN_WEBSERVICE_TYPE:
            raise WebserviceException('Invalid payload for {} webservice, computeType is not {}":\n'
                                      '{}'.format(cls._webservice_type, cls._webservice_type, payload),
                                      logger=module_logger)
        for service_key in cls._expected_payload_keys:
            if service_key not in payload:
                raise WebserviceException('Invalid {} Webservice payload, missing "{}":\n'
                                          '{}'.format(cls._webservice_type, service_key, payload),
                                          logger=module_logger)


class WebserviceDeploymentConfiguration(ABC):
    """Parent class for all Webservice deployment configuration objects.

    These objects will be used to define the configuration parameters for deploying a Webservice on a specific target.
    """

    def __init__(self, type):
        """Initialize the configuration object.

        :param type: The type of Webservice associated with this object
        :type type: class[Webservice]
        """
        self._webservice_type = type

    @abstractmethod
    def validate_configuration(self):
        """Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        pass

    @classmethod
    def validate_image(cls, image):
        """Check that the image that is being deployed to the webservice is valid.

        Will raise a WebserviceException if validation fails.

        :param cls:
        :type cls:
        :param image: The image that will be deployed to the webservice.
        :type image: azureml.core.image.image.Image
        :raises: WebserviceException
        """
        if image is None:
            raise WebserviceException("Image is None", logger=module_logger)
        if image.creation_state != 'Succeeded':
            raise WebserviceException('Unable to create service with image {} in non "Succeeded" '
                                      'creation state.'.format(image.id), logger=module_logger)
        if image.image_flavor not in CLOUD_DEPLOYABLE_IMAGE_FLAVORS:
            raise WebserviceException('Deployment of {} images is not supported'.format(image.image_flavor),
                                      logger=module_logger)
