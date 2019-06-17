# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for managing local debug Webservices in Azure Machine Learning service."""

import datetime
import logging
import os
import pickle
import posixpath
import shutil
import tempfile
import requests

from azureml.exceptions import WebserviceException
from azureml.core.image.container import ContainerImageConfig
from azureml.core.model import Model
from azureml.core.model import InferenceConfig
from azureml.core.webservice import Webservice
from azureml.core.webservice.webservice import WebserviceDeploymentConfiguration
from azureml._model_management._constants import DOCKER_IMAGE_HTTP_PORT
from azureml._model_management._constants import LOCAL_WEBSERVICE_TYPE
from azureml._model_management._constants import MMS_WORKSPACE_API_VERSION
from azureml._model_management._constants import WEBSERVICE_SCORE_PATH
from azureml._model_management._constants import WEBSERVICE_SWAGGER_PATH
from azureml._model_management._util import _get_mms_url
from azureml._model_management._util import add_sdk_to_requirements
from azureml._model_management._util import build_docker_image
from azureml._model_management._util import cleanup_container
from azureml._model_management._util import cleanup_docker_image
from azureml._model_management._util import connect_docker_network
from azureml._model_management._util import container_health_check
from azureml._model_management._util import container_scoring_call
from azureml._model_management._util import create_docker_container
from azureml._model_management._util import create_docker_volume
from azureml._model_management._util import create_tar_in_memory
from azureml._model_management._util import get_docker_client
from azureml._model_management._util import get_docker_container
from azureml._model_management._util import get_docker_containers
from azureml._model_management._util import get_docker_host_container
from azureml._model_management._util import get_docker_logs
from azureml._model_management._util import get_docker_network
from azureml._model_management._util import get_docker_port
from azureml._model_management._util import get_docker_volume
from azureml._model_management._util import login_to_docker_registry
from azureml._model_management._util import start_docker_container
from azureml._model_management._util import write_dir_in_container
from azureml._model_management._util import write_file_in_container
from azureml._model_management._util import get_requests_session
from azureml._restclient.clientbase import ClientBase
from base64 import b64decode, b64encode

module_logger = logging.getLogger(__name__)


def _in_state(states):
    states = states if isinstance(states, (list, tuple)) else [states]

    def decorator(func):
        def decorated(self, *args, **kwargs):
            if self.state not in states:
                raise WebserviceException('Cannot call {}() when service is {}.'.format(func.__name__, self.state),
                                          logger=module_logger)

            return func(self, *args, **kwargs)

        return decorated

    return decorator


class LocalWebservice(Webservice):
    """
    Class for local debug Webservices.

    :param workspace: The workspace object containing any Model objects that will be retrieved.
    :type workspace: azureml.core.workspace.Workspace
    :param name: The name of the Webservice object to retrieve.
    :type name: str
    """

    APP_ROOT_DIR = '/var/azureml-app'  # Default

    CONTAINER_LABEL_DEPLOYMENT_CONFIG = 'amlDeploymentConfig'
    CONTAINER_LABEL_IMAGE_CONFIG = 'amlImageConfig'
    CONTAINER_LABEL_IS_SERVICE = 'amlIsService'
    CONTAINER_LABEL_MODELS_DIR = 'amlModelsDir'
    CONTAINER_LABEL_MODELS_LOCAL = 'amlModelsLocal'
    CONTAINER_LABEL_MODELS_REMOTE = 'amlModelsRemote'
    CONTAINER_LABEL_SERVICE_NAME = 'amlServiceName'

    MODELS_DIR = 'azureml-models'  # For inside the image
    MODELS_DIR_TEMP_PREFIX = 'azureml_models_'  # For the temp directory to be mounted

    NETWORK_NAME = 'azureml-local'

    STATE_DELETED = 'deleted'
    STATE_DEPLOYING = 'deploying'
    STATE_FAILED = 'failed'
    STATE_RUNNING = 'running'
    STATE_UNKNOWN = 'unknown'

    _webservice_type = LOCAL_WEBSERVICE_TYPE

    # Ignore Webservice's magic __new__(), which assumes there is a cloud
    # representation of the service.
    def __new__(cls, *args, **kwargs):
        """
        Local webservice constructor.

        LocalWebservice constructor is used to retrieve a local representation of a LocalWebservice object associated
        with the provided workspace.

        :param workspace: The workspace object containing any Model objects that will be retrieved.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the LocalWebservice object to retrieve.
        :type name: str
        :return: An instance of LocalWebservice.
        :rtype: azureml.core.webservice.LocalWebservice
        :raises: WebserviceException
        """
        return super(Webservice, cls).__new__(cls)

    def __init__(self, workspace, name, must_exist=True):
        """
        Local webservice constructor.

        LocalWebservice constructor is used to retrieve a local representation of a LocalWebservice object associated
        with the provided workspace.

        :param workspace: The workspace object containing any Model objects that will be retrieved.
        :type workspace: azureml.core.workspace.Workspace
        :param name: The name of the LocalWebservice object to retrieve.
        :type name: str
        :param must_exist: Boolean for if there must be a service deployed in order to get the object.
            Defaults to True
        :type must_exist: bool
        :return: An instance of LocalWebservice.
        :rtype: azureml.core.webservice.LocalWebservice
        :raises: WebserviceException
        """
        self.name = name
        self.compute_type = LOCAL_WEBSERVICE_TYPE
        self._workspace = workspace
        self.error = None
        self.state = None
        self.image_id = None
        self.tags = None
        self.properties = None
        self.created_time = datetime.datetime.now()
        self.updated_time = datetime.datetime.now()

        self._docker_client = get_docker_client()

        self._host_container = get_docker_host_container(self._docker_client)

        if self._host_container is not None:
            self._host_network = get_docker_network(self._docker_client, LocalWebservice.NETWORK_NAME)

        self.update_deployment_state(must_exist=must_exist)

    @_in_state([STATE_DEPLOYING, STATE_FAILED, STATE_RUNNING])
    def delete(self, delete_cache=True, delete_image=False, delete_volume=True):
        """
        Delete this LocalWebservice from the local machine.

        This function call is not asynchronous; it runs until the service is deleted.

        :param delete_cache: Delete temporary files cached for the service. (Default: True)
        :type delete_cache: bool
        :param delete_image: Delete the service's Docker image. (Default: False)
        :type delete_image: bool
        :param delete_volume: Delete the service's Docker volume. (Default: True)
        :type delete_volume: bool
        :raises: WebserviceException
        """
        cleanup_container(self._container)

        if delete_cache and self._models_dir:
            # We're recursively deleting a directory, so be a little paranoid.
            if LocalWebservice.MODELS_DIR_TEMP_PREFIX in self._models_dir:
                shutil.rmtree(self._models_dir, ignore_errors=True)

        if delete_image:
            cleanup_docker_image(self._docker_client, self._container.image.id)

        if delete_volume and self._volume:
            self._volume.remove()

        self.state = LocalWebservice.STATE_DELETED

    @staticmethod
    def deploy_configuration(port=None):
        """
        Create a configuration object for deploying a local Webservice.

        :param port: The local port on which to expose the service's HTTP endpoint.
        :type port: int
        :return: A configuration object to use when deploying a Webservice object
        :rtype: LocalWebserviceDeploymentConfiguration
        :raises: WebserviceException
        """
        return LocalWebserviceDeploymentConfiguration(port)

    def deploy_to_cloud(self, name=None, deployment_config=None, deployment_target=None):
        """
        Deploy a Webservice based on the LocalWebservice's configuration.

        :param name: The name to give the deployed service. Must be unique to the workspace.
        :type name: str
        :param deployment_config: A WebserviceDeploymentConfiguration used to configure the webservice. If one is not
            provided, an empty configuration object will be used based on the desired target.
        :type deployment_config: WebserviceDeploymentConfiguration
        :param deployment_target: A ComputeTarget to which to deploy the Webservice. As ACI has no associated
            ComputeTarget, leave this parameter as None to deploy to ACI.
        :type deployment_target: azureml.core.compute.ComputeTarget
        :return: A Webservice object corresponding to the deployed webservice.
        :rtype: azureml.core.webservice.webservice.Webservice
        :raises: WebserviceException
        """
        if not self._deployable:
            raise WebserviceException('The LocalWebservice is not in a deployable state. Recreate it, or use '
                                      'the Webservice.deploy() or Webservice.deploy_from_model() methods directly.',
                                      logger=module_logger)

        models = [model['local_path'] for model in self._models_local] + self._models_remote

        return Webservice.deploy_from_model(workspace=self._workspace,
                                            name=name or self.name,
                                            models=models,
                                            image_config=self._image_config,
                                            deployment_config=deployment_config,
                                            deployment_target=deployment_target)

    @classmethod
    def deserialize(cls, workspace, webservice_payload):
        """
        Convert a json object generated from :func:`azureml.core.Webservice.serialize` into a Webservice object.

        Not supported for LocalWebservice.

        :param cls:
        :type cls:
        :param workspace: The workspace object the Webservice is registered under
        :type workspace: azureml.core.workspace.Workspace
        :param webservice_payload: A json object to convert to a Webservice object
        :type webservice_payload: dict
        :raises: NotImplementedError
        """
        raise NotImplementedError('Local web services cannot be deserialized.')

    def get_keys(self):
        """
        Retrieve auth keys for this Webservice.

        Not supported for LocalWebservice.

        :return: The auth keys for this Webservice
        :raises: NotImplementedError
        """
        raise NotImplementedError('Local web services do not support auth keys.')

    @_in_state([STATE_DEPLOYING, STATE_FAILED, STATE_RUNNING])
    def get_logs(self, num_lines=5000, raw=False):
        """
        Retrieve logs for this LocalWebservice.

        :param num_lines: The maximum number of log lines to retrieve. (Default: 5000)
        :type num_lines: int
        :param raw: Return the raw Docker container output without attempting to format it. (Default: False)
        :type raw: bool
        :return: The logs for this LocalWebservice.
        :rtype: str
        :raises: WebserviceException
        """
        return get_docker_logs(self._container, num_lines=num_lines, raw=raw)

    @staticmethod
    def list(workspace, model_name=None, model_id=None):
        """
        List the LocalWebservices associated with the corresponding Workspace. Can be filtered using parameters.

        Not supported for LocalWebservice.

        :param workspace: The Workspace object associated with the LocalWebservices.
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Filter list to only include LocalWebservices deployed with the specific model name.
        :type model_name: str
        :param model_id: Filter list to only include LocalWebservices deployed with the specific model ID.
        :type model_id: str
        :return: A filtered list of LocalWebservices associated with the provided Workspace.
        :rtype: :class:`list[LocalWebservice]`
        :raises: WebserviceException
        """
        services = []

        for container in get_docker_containers(get_docker_client(),
                                               label_name=LocalWebservice.CONTAINER_LABEL_IS_SERVICE,
                                               label_value=str(True)):
            try:
                name = container.labels[LocalWebservice.CONTAINER_LABEL_SERVICE_NAME]
            except KeyError:
                continue

            service = LocalWebservice(workspace, name)

            try:
                if (model_name is None or
                        any(model['name'] == model_name for model in service._models_local) or
                        any(model.name == model_name for model in service._models_remote)) \
                        and (model_id is None or any(model.id == model_id for model in service._models_remote)):
                    services.append(service)
            except AttributeError:
                continue

        return services

    @property
    def port(self):
        """
        Get the local webservice port.

        :return: Port number.
        :rtype: int
        """
        return getattr(self, '_port', None)

    def regen_key(self, key):
        """
        Regenerate one of the Webservice's keys.

        Not supported for LocalWebservice.

        :param key: Which key to regenerate. Options are 'Primary' or 'Secondary'
        :type key: str
        :raises: NotImplementedError
        """
        raise NotImplementedError('Local web services do not support auth keys.')

    @_in_state([STATE_DEPLOYING, STATE_FAILED, STATE_RUNNING])
    def reload(self, wait=False):
        """
        Reload the LocalWebservice's execution script and dependencies.

        This restarts the service's container with copies of updated assets, including the execution script and local
        dependencies, but it does not rebuild the underlying image. Accordingly, changes to Conda/pip dependencies or
        custom Docker steps will not be reflected in the reloaded LocalWebservice. To handle those changes call
        LocalWebservice.update(), instead.

        :param wait: Wait for the service's container to reach a healthy state. (Default: False)
        :type wait: bool
        :raises: WebserviceException
        """
        self._run_container(wait=wait)

    @_in_state([STATE_DEPLOYING, STATE_RUNNING])
    def run(self, input_data):
        """
        Call this LocalWebservice with the provided input.

        :param input_data: The input with which to call the LocalWebservice.
        :type input_data: varies
        :return: The result of calling the LocalWebservice.
        :rtype: varies
        :raises: WebserviceException
        """
        if self.state == LocalWebservice.STATE_DEPLOYING:
            self.wait_for_deployment()

        container_scoring_call(self._port, input_data, self._container, self._internal_base_url,
                               cleanup_on_failure=False)

    @property
    def scoring_uri(self):
        """
        Get the local webservice scoring URI.

        :return: Scoring URI.
        :rtype: str
        """
        if hasattr(self, '_base_url'):
            return self._base_url + WEBSERVICE_SCORE_PATH
        else:
            return None

    def serialize(self):
        """
        Convert this Webservice into a JSON-serialized dictionary.

        :return: Serialized representation of the Webservice.
        :rtype: dict
        """
        created_time = self.created_time.isoformat() if self.created_time else None
        updated_time = self.updated_time.isoformat() if self.updated_time else None
        return {'name': self.name, 'tags': self.tags, 'properties': self.properties, 'state': self.state,
                'createdTime': created_time, 'updatedTime': updated_time, 'error': self.error,
                'computeType': self.compute_type, 'workspaceName': self._workspace.name, 'imageId': self.image_id,
                'scoringUri': self.scoring_uri, 'swaggerUri': self.swagger_uri, 'port': self.port}

    @property
    def swagger_uri(self):
        """
        Get the local webservice Swagger URI.

        :return: Swagger URI.
        :rtype: str
        """
        if hasattr(self, '_base_url'):
            return self._base_url + WEBSERVICE_SWAGGER_PATH
        else:
            return None

    @_in_state([STATE_DEPLOYING, STATE_FAILED, STATE_RUNNING, STATE_UNKNOWN])
    def update(self, models=None, image_config=None, deployment_config=None, wait=False, inference_config=None):
        """
        Update the LocalWebservice with provided properties.

        Values left as None will remain unchanged in this LocalWebservice.

        :param models: A new list of models contained in the LocalWebservice.
        :type models: list
        :param image_config: Image configuration options to apply to the LocalWebservice.
        :type image_config: azureml.core.image.container.ContainerImageConfig
        :param deployment_config: Deployment configuration options to apply to the LocalWebservice.
        :type deployment_config: azureml.core.webservice.local.LocalWebserviceDeploymentConfiguration
        :param inference_config: An InferenceConfig object used to provide the required model deployment properties.
        :type inference_config: azureml.core.model.InferenceConfig
        :param wait: Wait for the service's container to reach a healthy state. (Default: False)
        :type wait: bool
        :return:
        :rtype: None
        :raises: WebserviceException
        """
        if image_config and not isinstance(image_config, ContainerImageConfig):
            raise WebserviceException('Error, provided image configuration must be of type ContainerImageConfig '
                                      'in order to update a local service.', logger=module_logger)

        if deployment_config and not isinstance(deployment_config, LocalWebserviceDeploymentConfiguration):
            raise WebserviceException('Error, provided deployment configuration must be of type '
                                      'LocalWebserviceDeploymentConfiguration in order to update a local service.',
                                      logger=module_logger)

        if inference_config is not None and not isinstance(inference_config, InferenceConfig):
            raise WebserviceException('Error, provided inference configuration must be of type InferenceConfig '
                                      'in order to update a local service.', logger=module_logger)

        if image_config is not None and inference_config is not None:
            raise WebserviceException('Error, an image configuration and an inference configuration cannot be '
                                      'provided at the same time.', logger=module_logger)

        # Update our cached configuration
        if models is not None:
            self._models_local, self._models_remote = LocalWebservice._identify_models(self._workspace, models)

        if image_config is not None:
            self._image_config = image_config

        if deployment_config is not None:
            self._deployment_config = deployment_config

        if inference_config is not None:
            self._image_config = inference_config._convert_to_image_config()

        self._deployable |= (self._workspace is not None and
                             self._models_local is not None and
                             self._models_remote is not None and
                             self._image_config is not None)

        # Apply the changes
        self._update_docker_context()
        self._build_image()
        self._collect_models()
        self._update_volume()
        self._run_container(wait=wait)

    def update_deployment_state(self, must_exist=False):
        """
        Refresh the current state of the in-memory object.

        Perform an in-place update of the properties of the object based on the current state of the corresponding
        local Docker container.

        :param must_exist: Boolean for if there must be a service deployed in order to get the object (Default: False)
        :type must_exist: bool
        """
        # Look for an existing instance
        container = LocalWebservice._get_container(self._docker_client,
                                                   self._workspace,
                                                   self.name,
                                                   must_exist=must_exist)

        self.updated_time = datetime.datetime.now()

        if container:
            self._container = container
            self._container_name = LocalWebservice._construct_container_name(self.name)
            self._image = container.image
            self._volume = get_docker_volume(self._docker_client,
                                             LocalWebservice._construct_volume_name(self.name),
                                             must_exist=False)
            self._volume_name = self._volume.name if self._volume else None

            self.state = LocalWebservice.STATE_RUNNING

            try:
                self._base_url, self._internal_base_url, self._port = self._generate_base_urls()
            except:
                self.state = LocalWebservice.STATE_FAILED

            try:
                self._deployment_config = LocalWebservice._get_container_deployment_config(container)

                self._image_config = LocalWebservice._get_container_image_config(container)

                self._models_dir = LocalWebservice._get_container_models_dir(container)
                self._models_local = LocalWebservice._get_container_models_local(container)
                self._models_remote = LocalWebservice._get_container_models_remote(self._workspace, container)

                self._volume_name = self._volume_name or self._models_dir

                self._deployable = True
            except:
                self._deployable = False
                self.state = LocalWebservice.STATE_FAILED
        else:
            self.state = LocalWebservice.STATE_UNKNOWN

            self._deployable = False

    @_in_state([STATE_DEPLOYING, STATE_RUNNING])
    def wait_for_deployment(self, show_output=False):
        """
        Poll the running LocalWebservice deployment.

        :param show_output: Option to print more verbose output. (Default: False)
        :type show_output: bool
        :raises: WebserviceException
        """
        try:
            container_health_check(self._port,
                                   self._container,
                                   health_url=self._internal_base_url,
                                   cleanup_if_failed=False)

            self.state = LocalWebservice.STATE_RUNNING

            print('Local webservice is {} at {}'.format(self.state, self._base_url))
        except:
            self.state = LocalWebservice.STATE_FAILED
            raise

    def _build_image(self):
        context = self._generate_build_context()
        self._login_to_registry()
        self._image = build_docker_image(self._docker_client,
                                         context,
                                         self.name,
                                         custom_context=True,
                                         dockerfile_path=self._context_dockerfile_path,
                                         pull=True)

    def _collect_models(self):
        # Short circuit
        if not self._models_local and not self._models_remote:
            return

        # Make sure we have a temporary directory to store the models.
        if not getattr(self, '_models_dir', None):
            self._models_dir = os.path.join(tempfile.gettempdir(),
                                            LocalWebservice.MODELS_DIR_TEMP_PREFIX + self.name)

        # Assemble the right directory structure, providing a fake version for local, unregistered models.
        for model in self._models_local:
            model_dir = os.path.join(self._models_dir, model['name'], '0')
            model_dest = os.path.join(model_dir, model['image_path'])

            print('Copying local model {} to {}'.format(model['local_path'], model_dir))

            if os.path.exists(model_dest):
                if os.path.isdir(model_dest):
                    shutil.rmtree(model_dest)
                else:
                    os.remove(model_dest)

            if os.path.isdir(model['local_path']):
                shutil.copytree(model['local_path'], model_dest)
            else:
                os.makedirs(model_dir, exist_ok=True)
                shutil.copyfile(model['local_path'], model_dest)

        for model in self._models_remote:
            model_dir = os.path.join(self._models_dir, model.name, str(model.version))

            # Registered models are immutable; don't bother re-downloading them.
            if os.path.exists(model_dir):
                print('Model {} is already downloaded to {}'.format(model.id, model_dir))
            else:
                print('Downloading model {} to {}'.format(model.id, model_dir))
                model.download(target_dir=model_dir)

    @staticmethod
    def _construct_base_url(port):
        return 'http://localhost:{}'.format(port)

    @staticmethod
    def _construct_container_name(service_name):
        return service_name

    @staticmethod
    def _construct_internal_base_url(alias):
        return 'http://{}:{}'.format(alias, DOCKER_IMAGE_HTTP_PORT)

    @staticmethod
    def _construct_models_path(image):
        return posixpath.join(LocalWebservice._get_image_aml_app_root(image),
                              LocalWebservice.MODELS_DIR)

    @staticmethod
    def _construct_volume_name(service_name):
        return LocalWebservice.MODELS_DIR_TEMP_PREFIX + service_name

    @staticmethod
    def _copy_local_asset(container, local_path, container_rel_path=None):
        container_path_prefix = LocalWebservice._get_image_aml_app_root(container.image)
        container_rel_path = container_rel_path or os.path.basename(local_path.rstrip(os.sep))
        container_path = posixpath.join(container_path_prefix, container_rel_path)

        if os.path.isdir(local_path):
            write_dir_in_container(container, container_path, local_path)
        else:
            with open(local_path, 'rb') as f:
                write_file_in_container(container, container_path, f.read())

    @staticmethod
    def _deploy(workspace, name, models, image_config, deployment_config, wait=False):
        """
        Deploy the Webservice.

        :param name:
        :type name: str
        :param models:
        :type models: list
        :param image_config:
        :type image_config: azureml.core.image.ContainerImageConfig
        :param deployment_config:
        :type deployment_config: azureml.core.webservice.LocalWebserviceDeploymentConfiguration
        :param wait:
        :type wait: bool
        :return:
        :rtype: LocalDebuggingWebservice
        """
        if not isinstance(image_config, ContainerImageConfig):
            raise WebserviceException('Error, provided image configuration must be of type ContainerImageConfig '
                                      'in order to deploy a local service.', logger=module_logger)

        if not deployment_config:
            deployment_config = LocalWebservice.deploy_configuration()
        elif not isinstance(deployment_config, LocalWebserviceDeploymentConfiguration):
            raise WebserviceException('Error, provided deployment configuration must be of type '
                                      'LocalWebserviceDeploymentConfiguration in order to deploy a local service.',
                                      logger=module_logger)

        service = LocalWebservice(workspace, name, must_exist=False)
        service.update(models=models,
                       image_config=image_config,
                       deployment_config=deployment_config,
                       wait=wait)

        return service

    def _generate_build_context(self):
        files = list(self._context_files)

        def add_local_asset(local_path, image_path=None):
            image_path = image_path or os.path.basename(local_path.rstrip(os.sep))
            files.append((posixpath.join('azureml-app', image_path), local_path))

        if self._image_config.conda_file:
            add_local_asset(self._image_config.conda_file)

        if self._image_config.schema_file:
            add_local_asset(self._image_config.schema_file)

        if self._image_config.dependencies:
            for dependency in self._image_config.dependencies:
                add_local_asset(dependency)

        files.append(('azureml-app/requirements.txt', add_sdk_to_requirements()))

        return create_tar_in_memory(files)

    def _generate_base_urls(self):
        if self._host_container is not None:
            connect_docker_network(self._host_network, self._host_container)
            connect_docker_network(self._host_network, self._container, aliases=[self._container.short_id])

        port = get_docker_port(self._docker_client, self.name, self._container)
        base_url = LocalWebservice._construct_base_url(port)

        if self._host_container is not None:
            internal_base_url = LocalWebservice._construct_internal_base_url(self._container.short_id)
        else:
            internal_base_url = base_url

        return base_url, internal_base_url, port

    @staticmethod
    def _get_container(docker_client, workspace, name, must_exist=True):
        if not workspace or not name:
            return None

        try:
            container_name = LocalWebservice._construct_container_name(name)
            return get_docker_container(docker_client, container_name, all=True, limit=1)
        except WebserviceException as e:
            if not must_exist and 'WebserviceNotFound' in e.message:
                return None
            raise WebserviceException(e.message, logger=module_logger)

    @staticmethod
    def _get_container_deployment_config(container):
        deployment_config = pickle.loads(b64decode(
            container.labels[LocalWebservice.CONTAINER_LABEL_DEPLOYMENT_CONFIG]))
        deployment_config.validate_configuration()
        return deployment_config

    @staticmethod
    def _get_container_image_config(container):
        image_config = pickle.loads(b64decode(container.labels[LocalWebservice.CONTAINER_LABEL_IMAGE_CONFIG]))
        image_config.validate_configuration()
        return image_config

    @staticmethod
    def _get_container_models_dir(container):
        try:
            return pickle.loads(b64decode(container.labels[LocalWebservice.CONTAINER_LABEL_MODELS_DIR]))
        except:
            return None

    @staticmethod
    def _get_container_models_local(container):
        return pickle.loads(b64decode(container.labels[LocalWebservice.CONTAINER_LABEL_MODELS_LOCAL]))

    @staticmethod
    def _get_container_models_remote(workspace, container):
        model_ids = pickle.loads(b64decode(container.labels[LocalWebservice.CONTAINER_LABEL_MODELS_REMOTE]))
        return [Model(workspace, id=model_id) for model_id in model_ids]

    @staticmethod
    def _get_image_aml_app_root(image):
        try:
            envs = image.attrs['Config']['Env']
            return next(e for e in envs if e.startswith('AML_APP_ROOT=')).split('=', 1)[1]
        except:
            return LocalWebservice.APP_ROOT_DIR

    @staticmethod
    def _identify_models(workspace, models):
        local = []
        remote = []

        for model in models:
            if isinstance(model, str):
                try:
                    # Registered model; behave like a normal image build.
                    registered_model = Model(workspace, id=model)
                    remote.append(registered_model)
                except WebserviceException as e:
                    # Unregistered model; keep it local for the local debugging.
                    if 'ModelNotFound' in e.message:
                        model_path = os.path.basename(model.rstrip(os.sep))
                        model_name = model_path[:30]

                        local.append({'name': model_name, 'image_path': model_path, 'local_path': model})
                    else:
                        raise WebserviceException(e.message, logger=module_logger)
            elif isinstance(model, Model):
                remote.append(model)
            else:
                raise NotImplementedError('Models must either be of type azureml.core.model.Model or a str '
                                          'path to a file or folder.')

        return local, remote

    def _login_to_registry(self):
        # Base image credentials are optional
        if self._image_config.base_image_registry is None:
            return

        location = self._image_config.base_image_registry.address
        username = self._image_config.base_image_registry.username
        password = self._image_config.base_image_registry.password

        if location is None and username is None and password is None:
            return

        if location is None or username is None or password is None:
            raise WebserviceException('Base image registry must include all of address, username, and password.',
                                      logger=module_logger)

        login_to_docker_registry(self._docker_client, username, password, location)

    def _run_container(self, wait):
        # Clean up the old container/image.
        if getattr(self, '_container', None) is not None:
            old_image_is_dangling = len(self._container.image.tags) == 0
            self.delete(delete_cache=False, delete_image=old_image_is_dangling, delete_volume=False)

        # Start up the new container.
        container_name = LocalWebservice._construct_container_name(self.name)

        labels = {
            LocalWebservice.CONTAINER_LABEL_DEPLOYMENT_CONFIG:
                b64encode(pickle.dumps(self._deployment_config)).decode('utf-8'),
            LocalWebservice.CONTAINER_LABEL_IMAGE_CONFIG:
                b64encode(pickle.dumps(self._image_config)).decode('utf-8'),
            LocalWebservice.CONTAINER_LABEL_IS_SERVICE: str(True),
            LocalWebservice.CONTAINER_LABEL_MODELS_DIR:
                b64encode(pickle.dumps(self._models_dir)).decode('utf-8'),
            LocalWebservice.CONTAINER_LABEL_MODELS_LOCAL:
                b64encode(pickle.dumps(self._models_local)).decode('utf-8'),
            LocalWebservice.CONTAINER_LABEL_MODELS_REMOTE:
                b64encode(pickle.dumps([model.id for model in self._models_remote])).decode('utf-8'),
            LocalWebservice.CONTAINER_LABEL_SERVICE_NAME: self.name,
        }

        ports = {
            DOCKER_IMAGE_HTTP_PORT: ('127.0.0.1', self._deployment_config.port),  # None assigns a random port
        }

        volumes = {
            self._volume_name: {
                'bind': LocalWebservice._construct_models_path(self._image),
                'mode': 'rw',
            },
        }

        container = create_docker_container(self._docker_client,
                                            self.name,
                                            container_name,
                                            labels=labels,
                                            ports=ports,
                                            volumes=volumes)

        # Copy local assets into the AML working directory.
        LocalWebservice._copy_local_asset(container, self._image_config.execution_script, container_rel_path='main.py')

        if self._image_config.schema_file is not None:
            LocalWebservice._copy_local_asset(container, self._image_config.schema_file)

        if self._image_config.dependencies is not None:
            for dependency in self._image_config.dependencies:
                LocalWebservice._copy_local_asset(container, dependency)

        # Engage!
        start_docker_container(container)

        # Record the state of the deployment.
        self._container = container
        self._container_name = container_name
        self.state = LocalWebservice.STATE_DEPLOYING

        # Make sure we can talk with the container.
        self._base_url, self._internal_base_url, self._port = self._generate_base_urls()

        if wait:
            self.wait_for_deployment()

    def _update_docker_context(self):
        """
        Generate Dockerfile according to the LocalWebservice's models, image config, and workspace.

        :raises: azureml.exceptions.WebserviceException
        """
        print('Generating Docker build context.')

        image_url = '{}/images/generateDockerBuildContext'.format(_get_mms_url(self._workspace))

        headers = self._workspace._auth.get_authentication_header()
        headers['Content-Type'] = 'application/json'

        params = {'api-version': MMS_WORKSPACE_API_VERSION}

        model_ids = [model.id for model in self._models_remote]
        json_payload = self._image_config.create_local_debug_payload(self._workspace, model_ids)

        try:
            response = ClientBase._execute_func(get_requests_session().post, image_url, headers=headers, params=params,
                                                json=json_payload)
            response.raise_for_status()
            response_json = response.json()

            self._context_files = []
            self._context_dockerfile_path = response_json['dockerfilePath']

            for entry in response_json['context']:
                if entry['encoding'].lower() != 'base64':
                    raise ValueError()

                self._context_files.append((entry['path'], b64decode(entry['content'])))
        except (requests.exceptions.HTTPError, KeyError, ValueError):
            raise WebserviceException('Received bad response from Model Management Service:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(response.status_code, response.headers, response.content),
                                      logger=module_logger)

    def _update_volume(self):
        # Skip the extra copying if we're running on the host, because we can just bind mount the models directly.
        if self._host_container is None:
            self._volume = None
            self._volume_name = self._models_dir
            return

        # Get/create the volume for this service.
        if getattr(self, '_volume', None) is None:
            self._volume_name = LocalWebservice._construct_volume_name(self.name)
            self._volume = get_docker_volume(self._docker_client, self._volume_name, must_exist=False) \
                or create_docker_volume(self._docker_client, self._volume_name)

        print('Copying model files to volume mount "{}".'.format(self._volume_name))

        image_models_path = LocalWebservice._construct_models_path(self._image)

        volumes = {
            self._volume_name: {
                'bind': image_models_path,
                'mode': 'rw',
            },
        }

        # Create a dummy container without running it, just to access the volume.
        container = create_docker_container(self._docker_client,
                                            self.name,
                                            'volume-mount',
                                            auto_remove=True,
                                            volumes=volumes)

        LocalWebservice._copy_local_asset(container, self._models_dir, container_rel_path=image_models_path)

        container.remove()


class LocalWebserviceDeploymentConfiguration(WebserviceDeploymentConfiguration):
    """Service deployment configuration object for services deployed locally for debugging."""

    webservice_type = LocalWebservice

    def __init__(self, port=None):
        """
        Create a configuration object for deploying a local service for debugging.

        :param port: The local port on which to expose the service's HTTP endpoint.
        :type port: int
        :raises: WebserviceException
        """
        super(LocalWebserviceDeploymentConfiguration, self).__init__(LocalWebservice)

        self.port = port

        self.validate_configuration()

    def validate_configuration(self):
        """
        Check that the specified configuration values are valid.

        Will raise a WebserviceException if validation fails.

        :raises: WebserviceException
        """
        if self.port and not (isinstance(self.port, int) and 1 <= self.port <= 65535):
            raise WebserviceException('Invalid configuration, port must be an integer in range [1, 65535]',
                                      logger=module_logger)
