# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from abc import ABCMeta, abstractmethod
from azureml._base_sdk_common.service_discovery import get_service_url

from azureml.exceptions import ProjectSystemException

module_logger = logging.getLogger(__name__)

_PROJECT_FILE_ACCOUNT_ID = "AccountId"
_PROJECT_FILE_PROJECT_ID = "Id"
_PROJECT_FILE_FIELDS = [_PROJECT_FILE_ACCOUNT_ID, _PROJECT_FILE_PROJECT_ID]


def create_project_context(auth, subscription_id, resource_group,
                           workspace_name, project_name, workspace_id):
    """
    Creates the project context.
    :param auth: Authentication object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id: subscription id
    :type subscription_id: str
    :param resource_group: resource group name
    :type resource_group: str
    :param workspace_name: workspace name
    :type workspace_name: str
    :param project_name: project name
    :type project_name: str
    :param workspace_id: workspace region name
    :type workspace_id: str
    :return: A project context
    :rtype: ProjectContext
    """
    project_context = ARMProjectContext(auth, subscription_id, resource_group,
                                        workspace_name, project_name, workspace_id)

    if not project_context:
        raise ProjectSystemException("Failed to get the project context.")

    return project_context


class ProjectMetadataFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_project_metadata(self):
        pass


class ProjectContext(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_workspace_uri_path(self):
        pass

    @abstractmethod
    def get_workspace_id(self):
        pass

    def get_auth(self):
        """
        :return: Returns auth object.
        :rtype: azureml.core.authentication.AbstractAuthentication
        """
        pass

    @abstractmethod
    def get_history_service_uri(self):
        pass

    @abstractmethod
    def get_cloud_execution_service_address(self):
        pass


class ARMProjectContext(ProjectContext):
    def __init__(self, auth, subscription_id, resource_group, workspace, project_name,
                 workspace_id):
        """

        :param auth: auth object.
        :type auth: azureml.core.authentication.AbstractAuthentication
        :param subscription_id:
        :param resource_group:
        :param workspace:
        :param project_name:
        :type project_name: str
        :param workspace_id:
        :type workspace_id: str
        """
        self._auth = auth

        self._subscription_id = subscription_id
        self._resource_group = resource_group
        self._workspace = workspace
        self._project_name = project_name
        self._workspace_id = workspace_id

    @property
    def subscription(self):
        return self._subscription_id

    @property
    def resource_group(self):
        return self._resource_group

    @property
    def workspace(self):
        return self._workspace

    @property
    def project(self):
        return self._project_name

    def get_workspace_uri_path(self):
        return "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices" \
               "/workspaces/{}".format(self.subscription, self.resource_group, self.workspace)

    def get_experiment_uri_path(self):
        return self.get_workspace_uri_path() + "/experiments/{}".format(self.project)

    def get_history_service_uri(self):
        return get_service_url(self._auth, self.get_workspace_uri_path(), self._workspace_id)

    def get_cloud_execution_service_address(self):
        return self.get_history_service_uri()

    def get_auth(self):
        return self._auth

    def get_workspace_id(self):
        return self._workspace_id
