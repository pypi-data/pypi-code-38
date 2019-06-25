# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""**ServiceContext** container for scope and authentication of a workspace."""
import copy
import logging
import os
import six

from azureml._base_sdk_common.service_discovery import get_service_url, PIPELINES_SERVICE_ENUM
from azureml._logging.chained_identity import ChainedIdentity
from .rest_client import RestClient

DEVLEOPER_URL_TEMPLATE = "AZUREML_DEV_URL_{}"

module_logger = logging.getLogger(__name__)


class _ServiceKeys(object):
    """Enum of keys for retrieving service urls from discovery service."""
    MMS_DISCOVERY_KEY = "modelmanagement"
    EXPERIMENTATION_DISCOVERY_KEY = "experimentation"
    HISTORY_DISCOVERY_KEY = "history"
    PIPELINES_DISCOVERY_KEY = PIPELINES_SERVICE_ENUM
    HYPERDRIVE_DISCOVERY_KEY = "hyperdrive"

    # For datastore:
    # DATASTORE = "datastore"

    ARTIFACTS = "artifacts"
    ASSETS = "assets"
    METRICS = "metrics"
    JASMINE = "jasmine"
    EXECUTION = "execution"
    ENVIRONMENT = "environment"
    EXPERIMENTATION = "experimentation"
    HYPERDRIVE = "hyperdrive"
    PIPELINES = "pipelines"
    RUN_HISTORY = "run_history"
    PROJECT_CONTENT = "project_content"

    _names = []
    _discovery_keys = []
    _override_env_vars = []
    _name_to_key = {}
    _initialized = False

    @classmethod
    def initialize(cls):
        cls.register_discovery_url(cls.ARTIFACTS, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.RUN_HISTORY, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.METRICS, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.JASMINE, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.ASSETS, cls.MMS_DISCOVERY_KEY)
        cls.register_discovery_url(cls.EXECUTION, cls.HISTORY_DISCOVERY_KEY)
        cls.register_discovery_url(cls.EXPERIMENTATION, cls.EXPERIMENTATION_DISCOVERY_KEY)
        cls.register_discovery_url(cls.ENVIRONMENT, cls.EXPERIMENTATION_DISCOVERY_KEY)
        cls.register_discovery_url(cls.HYPERDRIVE, cls.HYPERDRIVE_DISCOVERY_KEY)
        cls.register_discovery_url(cls.PIPELINES, cls.PIPELINES_DISCOVERY_KEY)
        cls.register_discovery_url(cls.PROJECT_CONTENT, cls.HISTORY_DISCOVERY_KEY)

        # For datastore:
        # cls.register_discover_url(cls.DATASTORE, cls.DATASTORE_DISCOVERY_KEY)
        cls._initialized = True

    @classmethod
    def register_discovery_url(cls, name, discovery_key=None):
        cls._names.append(name)
        discovery_key = discovery_key if discovery_key is not None else name
        cls._discovery_keys.append(discovery_key)

        cls._name_to_key[name] = discovery_key

        env_var = cls.generate_environment_variable(name)
        cls._override_env_vars.append(env_var)

    @classmethod
    def generate_environment_variable(cls, key):
        env_var = DEVLEOPER_URL_TEMPLATE.format(key.upper())
        return env_var

    @classmethod
    def get_discovery_key(cls, name):
        return cls._name_to_key[name]

    @classmethod
    def get_names(cls):
        return cls._names

    @classmethod
    def get_discovery_keys(cls):
        return cls._discovery_keys

    @classmethod
    def get_override_env_vars(cls):
        return cls._override_env_vars


_ServiceKeys.initialize()


class ServiceContext(ChainedIdentity):
    """
    A container for workspace scope, authentication, and service location information.

    :param subscription_id: The subscription id.
    :type subscription_id: str
    :param resource_group_name: The name of the resource group.
    :type resource_group_name: str
    :param workspace_name: The name of the workspace.
    :type workspace_name: str
    :param authentication: The auth object.
    :type authentication: azureml.core.authentication.AbstractAuthentication
    :param kwargs:
    """

    def __init__(self,
                 subscription_id, resource_group_name, workspace_name, workspace_id,
                 authentication, **kwargs):
        """
        Store scope information and fetch service locations.

        :param subscription_id: The subscription id.
        :type subscription_id: str
        :param resource_group_name: The name of the resource group.
        :type resource_group_name: str
        :param workspace_name: The name of the workspace.
        :type workspace_name: str
        :param authentication: The auth object.
        :type authentication: azureml.core.authentication.AbstractAuthentication
        :param kwargs:
        """
        super(ServiceContext, self).__init__(**kwargs)

        self._sub_id = subscription_id
        self._rg_name = resource_group_name
        self._ws_name = workspace_name
        self._workspace_id = workspace_id

        from azureml.core.authentication import AbstractAuthentication
        assert isinstance(authentication, AbstractAuthentication)
        self._authentication = authentication

        self._endpoints = self._fetch_endpoints()

        self.runhistory_restclient = None
        self.artifacts_restclient = None
        self.assets_restclient = None
        self.metrics_restclient = None
        self.project_content_restclient = None
        self.execution_restclient = None
        self.environment_restclient = None
        self.jasmine_restclient = None

    def __deepcopy__(self, memo):
        # Details on how to override deepcopy https://stackoverflow.com/questions/1500718
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            # Skip serializing RestClient as it will get re-instialized in the new object.
            if isinstance(v, RestClient):
                setattr(result, k, None)
            # Skip serializing the logger and initialize it in the new object.
            elif isinstance(v, logging.Logger):
                setattr(result, k, logging.getLogger(v.name))
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    @property
    def subscription_id(self):
        """
        Return the subscription id for this workspace.

        :return: The subscription id.
        :rtype: str
        """
        return self._sub_id

    @property
    def resource_group_name(self):
        """
        Return the resource group name for this workspace.

        :return: The resource group name.
        :rtype: str
        """
        return self._rg_name

    @property
    def workspace_name(self):
        """
        Return the workspace name.

        :return: The workspace name.
        :rtype: str
        """
        return self._ws_name

    @property
    def workspace_id(self):
        """
        Return the workspace id.

        :return: The workspace id.
        :rtype: str
        """
        return self._workspace_id

    def get_auth(self):
        """
        Return the authentication object.

        :return: The authentication object.
        :rtype: azureml.core.authentication.AbstractAuthentication
        """
        return self._authentication

    def _get_workspace_scope(self):
        """
        Return the scope information for the workspace.

        :param workspace_object: The workspace object.
        :type workspace_object: azureml.core.workspace.Workspace
        :return: The scope information for the workspace.
        :rtype: str
        """
        return ("/subscriptions/{}/resourceGroups/{}/providers"
                "/Microsoft.MachineLearningServices"
                "/workspaces/{}").format(self.subscription_id,
                                         self.resource_group_name,
                                         self.workspace_name)

    def _get_developer_override(self, key):
        environment_variable = _ServiceKeys.generate_environment_variable(key)
        developer_endpoint = os.environ.get(environment_variable)
        if developer_endpoint is not None:
            self._logger.debug("Loaded endpoint {} from environment variable {}.".format(
                developer_endpoint, environment_variable))
        return developer_endpoint

    def _fetch_endpoints(self):
        """
        Fetch service endpoints from service discovery.

        :return: Dictionary of service discovery key to service url.
        :rtype: dict[str] -> str
        """
        scope = self._get_workspace_scope()
        endpoints = {}
        for discovery_key in _ServiceKeys.get_discovery_keys():
            url = get_service_url(self._authentication, scope, self._workspace_id,
                                  service_name=discovery_key)
            endpoints[discovery_key] = url
        return endpoints

    def _get_endpoint(self, key):
        """
        Get service endpoint from environment variable if set, otherwise from service discovery.

        :return: The service endpoint.
        :rtype: str
        """
        developer_endpoint = self._get_developer_override(key)
        if developer_endpoint is not None:
            endpoint = developer_endpoint
        else:
            discovery_key = _ServiceKeys.get_discovery_key(key)
            endpoint = self._endpoints[discovery_key]
        return endpoint

    def _get_run_history_url(self):
        """
        Return the url to the run history service.

        :return: The run history service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.RUN_HISTORY)

    def _get_metrics_url(self):
        """
        Return the url to the metrics service.

        :return: The metrics service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.METRICS)

    def _get_jasmine_url(self):
        """
        Return the url to Jasmine service.

        :return: The Jasmine service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.JASMINE)

    def _get_experimentation_url(self):
        """
        Return the url to the experimentation service.

        :return: The experimentation service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.EXPERIMENTATION)

    def _get_artifacts_url(self):
        """
        Return the url to the artifacts service.

        :return: The artifacts service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.ARTIFACTS)

    def _get_pipelines_url(self):
        """
        Return the url to the pipelines service.

        :return: The pipelines service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.PIPELINES)

    def _get_hyperdrive_url(self):
        """
        Return the url to the hyperdrive service.

        :return: The hyperdrive service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.HYPERDRIVE)

    def _get_assets_url(self):
        """
        Return the url to the model management service.

        :return: The model management service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.ASSETS)

    def _get_project_content_url(self):
        """
        Return the url to the project content service.

        :return: The project content service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.PROJECT_CONTENT)

    def _get_execution_url(self):
        """
        Return the url to the execution service.

        :return: The execution service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.EXECUTION)

    def _get_environment_url(self):
        """
        Return the url to the environment management service.

        :return: The environment management service endpoint.
        :rtype: str
        """
        return self._get_endpoint(_ServiceKeys.ENVIRONMENT)

    def _get_run_history_restclient(self, host=None, user_agent=None):
        if self.runhistory_restclient is None:
            host = host if host is not None else self._get_run_history_url()
            self.runhistory_restclient = RestClient(self.get_auth(), base_url=host)
            self._add_user_agent(self.runhistory_restclient, user_agent=user_agent)

        return self.runhistory_restclient

    def _get_metrics_restclient(self, user_agent=None):
        if self.metrics_restclient is None:
            self.metrics_restclient = RestClient(self.get_auth(), base_url=self._get_metrics_url())
            self._add_user_agent(self.metrics_restclient, user_agent=user_agent)

        return self.metrics_restclient

    def _get_jasmine_restclient(self, user_agent=None):
        if self.jasmine_restclient is None:
            self.jasmine_restclient = RestClient(self.get_auth(), base_url=self._get_jasmine_url())
            self._add_user_agent(self.jasmine_restclient, user_agent=user_agent)

        return self.jasmine_restclient

    def _get_artifacts_restclient(self, user_agent=None):
        if self.artifacts_restclient is None:
            self.artifacts_restclient = RestClient(self.get_auth(), base_url=self._get_artifacts_url())
            self._add_user_agent(self.artifacts_restclient, user_agent=user_agent)

        return self.artifacts_restclient

    def _get_assets_restclient(self, user_agent=None):
        if self.assets_restclient is None:
            self.assets_restclient = RestClient(self.get_auth(), base_url=self._get_assets_url())
            self._add_user_agent(self.assets_restclient, user_agent=user_agent)

        return self.assets_restclient

    def _get_project_content_restclient(self, user_agent=None):
        if self.project_content_restclient is None:
            host = self._get_project_content_url()
            self.project_content_restclient = RestClient(self.get_auth(), base_url=host)
            self._add_user_agent(self.project_content_restclient, user_agent=user_agent)

        return self.project_content_restclient

    def _get_execution_restclient(self, user_agent=None):
        if self.execution_restclient is None:
            host = self._get_execution_url()
            self.execution_restclient = RestClient(self.get_auth(), base_url=host)
            self._add_user_agent(self.execution_restclient, user_agent=user_agent)

        return self.execution_restclient

    def _get_environment_restclient(self, user_agent=None):
        if self.environment_restclient is None:
            host = self._get_environment_url()
            self.environment_restclient = RestClient(self.get_auth(), base_url=host)
            self._add_user_agent(self.environment_restclient, user_agent=user_agent)

        return self.environment_restclient

    def _add_user_agent(self, rest_client, user_agent=None):
        if user_agent is not None:
            if isinstance(user_agent, six.text_type):
                rest_client.config.add_user_agent(user_agent)
            else:
                self._logger.warning("Client agent setting is not a string, it is ignored.")
