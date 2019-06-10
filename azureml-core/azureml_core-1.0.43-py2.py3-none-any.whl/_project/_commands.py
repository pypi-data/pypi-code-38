# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
import time

from azureml._base_sdk_common.common import create_role_assignment
from azureml._base_sdk_common.common import resource_client_factory, give_warning
from azureml._base_sdk_common.common import resource_error_handling
from azureml._base_sdk_common.workspace import AzureMachineLearningWorkspaces
from azureml._base_sdk_common.workspace.models import ErrorResponseWrapperException
from azureml._base_sdk_common.workspace.operations import WorkspacesOperations
from azureml._base_sdk_common.common import get_http_exception_response_string
from azureml._project.project_engine import ProjectEngineClient
from azureml._workspace._utils import (
    delete_kv_armId,
    delete_storage_armId,
    delete_insights_armId
)
from azure.mgmt.resource import ResourceManagementClient
from azureml.exceptions import ProjectSystemException, WorkspaceException
from msrest.exceptions import HttpOperationError
from msrestazure.azure_exceptions import CloudError

module_logger = logging.getLogger(__name__)

# TODO: These keys should be moved to a base_sdk_common place.
# Resource type keys
PROJECT = "Project"
WORKSPACE = "Workspace"

# Project info keys
RESOURCE_GROUP_KEY = "resourceGroups"
WORKSPACE_KEY = "workspaces"
PROJECT_KEY = "projects"
SUBSCRIPTION_KEY = "subscriptions"


# TODO: After passing project_object, we might be able to remove some of function arguments in each function.
""" Modules """


def get_project_info(auth, path, exception_bypass=False):
    """

    :param auth:
    :param path:
    :param exception_bypass:
    :return:
    """
    """Get project information from path"""
    # Get project id from Engine
    project_scope = ProjectEngineClient.get_project_scope_by_path(path)

    if not project_scope:
        if exception_bypass:
            return None
        message = "No cache found for current project, try providing resource group"
        message += " and workspace arguments"
        raise ProjectSystemException(message)
    else:
        content = project_scope.split('/')
        keys = content[1::2]
        values = content[2::2]
        return dict(zip(keys, values))


def attach_project(workspace_object, cloud_project_name, project_path="."):
    """
    Attaches a machine learning project to a local directory, specified by project_path.
    :param workspace_object:
    :type workspace_object: azureml.core.workspace.Workspace
    :param cloud_project_name:
    :param project_path:
    :return: A dict of project attach related information.
    :rtype: dict
    """
    from azureml._restclient.experiment_client import ExperimentClient
    experiment_name = cloud_project_name
    project_path = os.path.abspath(project_path)

    #  Start temporary fix while project service is being deprecated
    workspace_service_object, _ = _get_or_create_workspace(
        workspace_object._auth_object, workspace_object.subscription_id, workspace_object.resource_group,
        workspace_object.name, workspace_object.location)

    experiment_client = ExperimentClient(workspace_object.service_context, experiment_name)

    scope = "{}/{}/{}".format(experiment_client.get_workspace_uri_path(), PROJECT_KEY, experiment_name)
    # End temporary fix

    # Send appropriate information
    project_engine_client = ProjectEngineClient(workspace_object._auth_object)
    reply_dict = project_engine_client.attach_project(experiment_name,
                                                      project_path, scope, workspace_object.compute_targets)

    # Adding location information
    reply_dict["experimentName"] = experiment_name
    return reply_dict


def _get_or_create_workspace(auth, subscription_id, resource_group_name, workspace_name, location):
    """
    Gets or creates a workspace.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    :param location:
    :type location: str
    :return: Returns the workspace object and a bool indicating if the workspace was newly created.
    :rtype: azureml._base_sdk_common.workspace.models.workspace.Workspace, bool
    """
    from azureml._base_sdk_common.workspace.models import Workspace
    newly_created = False
    try:
        # try to get the workspace first
        workspace_object = WorkspacesOperations.get(
            auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
            resource_group_name, workspace_name)
    except HttpOperationError as response_exception:
        if response_exception.response.status_code == 404:
            # if no workspace, create the workspace
            params = Workspace(location=location, friendly_name=workspace_name)
            newly_created = True
            workspace_object = WorkspacesOperations.create_or_update(
                auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
                resource_group_name, workspace_name, params)
        else:
            raise ProjectSystemException(get_http_exception_response_string(response_exception.response))

    return workspace_object, newly_created


def detach_project(project_path="."):
    """
    Deletes the project.json from a project.
    Raises an exception if the file deletion fails.
    :param project_path: The project path.
    :type project_path: str
    :return:
    """
    from azureml._project import project_info
    project_info.delete_project_json(os.path.abspath(project_path))


def list_project(auth, subscription_id=None, resource_group_name=None, workspace_name=None,
                 local=False):
    """
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param local:
    :param subscription_id:
    :return:
    """
    """List Projects"""
    from azureml._restclient.workspace_client import WorkspaceClient
    # If local flag is specified, list all local projects
    if local:
        project_engine_client = ProjectEngineClient(auth)
        return project_engine_client.get_local_projects()

    # Subscription id cannot be none while listing cloud projects.
    if not subscription_id:
        raise ProjectSystemException("Subscription id cannot be none while listing cloud projects.")

    try:
        if resource_group_name and workspace_name:
            workspace_client = WorkspaceClient(None,
                                               auth,
                                               subscription_id,
                                               resource_group_name,
                                               workspace_name)
            experiments = workspace_client.list_experiments()

            return [experiment.as_dict() for experiment in experiments]
        else:
            raise ProjectSystemException("Please specify resource_group_name and workspace_name ")

    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, PROJECT + "s")


def basic_project_info(project_info):
    basic_dict = {
        "id": project_info["id"],
        "name": project_info["name"]
    }

    if "summary" in project_info:
        basic_dict["summary"] = project_info["summary"]

    if "description" in project_info:
        basic_dict["description"] = project_info["description"]

    if "action_hyperlink" in project_info:
        basic_dict["github_link"] = project_info["action_hyperlink"]["address"]

    return basic_dict


def create_workspace(auth, resource_group_name, workspace_name, subscription_id,
                     location=None, create_resource_group=None, friendly_name=None,
                     storage_account=None, key_vault=None, app_insights=None, containerRegistry=None,
                     default_cpu_compute_target=None, default_gpu_compute_target=None,
                     exist_ok=False, show_output=True):
    """
    Create workspace
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param subscription_id:
    :type subscription_id: str
    :param location:
    :param friendly_name:
    :type container_registry: str
    :param default_cpu_compute_target: A configuration that will be used to create a CPU compute.
        If None, no compute will be created.
    :type default_cpu_compute_target: azureml.core.AmlCompute.AmlComputeProvisioningConfiguration
    :param default_gpu_compute_target: A configuration that will be used to create a GPU compute.
        If None, no compute will be created.
    :return:
    :rtype: azureml._base_sdk_common.workspace.models.workspace.Workspace
    """
    resource_management_client = resource_client_factory(auth, subscription_id)
    found = True
    try:
        resource_management_client.resource_groups.get(resource_group_name)
    except CloudError as e:
        if e.status_code == 404:
            # Resource group not found case.
            found = False
        else:
            from azureml._base_sdk_common.common import get_http_exception_response_string
            raise WorkspaceException(get_http_exception_response_string(e.response))

    if not found:
        if not location:
            raise WorkspaceException("Resource group was not found and location was not provided. "
                                     "Provide location with --location to create a new resource group.")
        else:
            rg_location = location

        if create_resource_group is None:
            # Flag was not set, we need to prompt user for creation of resource group
            give_warning("UserWarning: The resource group doesn't exist or was not provided. "
                         "AzureML SDK can create a resource group={} in location={} "
                         "using subscription={}. Press 'y' to confirm".format(resource_group_name,
                                                                              rg_location,
                                                                              subscription_id))

            yes_set = ['yes', 'y', 'ye', '']
            choice = input().lower()

            if choice in yes_set:
                create_resource_group = True
            else:
                raise WorkspaceException("Resource group was not found and "
                                         "confirmation prompt was denied.")

        if create_resource_group:
            # Create the required resource group, give the user details about it.
            give_warning("UserWarning: The resource group doesn't exist or was not provided. "
                         "AzureML SDK is creating a resource group={} in location={} "
                         "using subscription={}.".format(resource_group_name, rg_location, subscription_id))
            from azure.mgmt.resource.resources.models import ResourceGroup
            tags = {"creationTime": str(time.time()),
                    "creationSource": "azureml-sdk"}
            # Adding location as keyworded argument for compatibility with azure-mgmt-resource 1.2.*
            # and azure-mgmt-resource 2.0.0
            resource_group_properties = ResourceGroup(location=rg_location, tags=tags)
            resource_management_client.resource_groups.create_or_update(resource_group_name,
                                                                        resource_group_properties)
        else:
            # Create flag was set to false, this path is not possible through the cli
            raise WorkspaceException("Resource group was not found.")

    from azureml._workspace.custom import ml_workspace_create_resources
    return ml_workspace_create_resources(
        auth, auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
        resource_group_name,
        workspace_name,
        location,
        subscription_id,
        storage_account=storage_account,
        key_vault=key_vault,
        app_insights=app_insights,
        containerRegistry=containerRegistry,
        friendly_name=friendly_name,
        default_cpu_compute_target=default_cpu_compute_target,
        default_gpu_compute_target=default_gpu_compute_target,
        exist_ok=exist_ok,
        show_output=show_output)


def available_workspace_locations(auth, subscription_id):
    """Lists available locations/azure regions where an azureml workspace can be created.
    :param auth: Authentication object.
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id: The subscription id.
    :type subscription_id: str
    :return: The list of azure regions where an azureml workspace can be created.
    :rtype: list[str]
    """
    response = auth._get_service_client(ResourceManagementClient, subscription_id).providers.get(
        "Microsoft.MachineLearningServices")
    for resource_type in response.resource_types:
        # There are multiple resource types like workspaces, 'workspaces/computes', 'operations' and some more.
        # All return the same set of locations.
        if resource_type.resource_type == "workspaces":
            return resource_type.locations


def get_workspace(auth, subscription_id, resource_group_name, workspace_name):
    """
    Returns the workspace object from the service.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :type subscription_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param workspace_name:
    :type workspace_name: str
    :return: The service workspace object.
    :rtype: azureml._base_sdk_common.workspace.models.workspace.Workspace
    """
    try:
        workspaces = auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces
        return WorkspacesOperations.get(
            workspaces,
            resource_group_name,
            workspace_name)
    except ErrorResponseWrapperException as response_exception:
        module_logger.error(
            "get_workspace error using subscription_id={}, resource_group_name={}, workspace_name={}".format(
                subscription_id, resource_group_name, workspace_name
            ))
        resource_error_handling(response_exception, WORKSPACE)


def list_workspace(auth, subscription_id, resource_group_name=None):
    """
    List Workspaces
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param subscription_id:
    :param resource_group_name:
    :return: A list of objects of azureml._base_sdk_common.workspace.models.workspace.Workspace
    :rtype: list[azureml._base_sdk_common.workspace.models.workspace.Workspace]
    """
    try:
        if resource_group_name:
            list_object = WorkspacesOperations.list_by_resource_group(
                auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
                resource_group_name)
            workspace_list = list_object.value
            next_link = list_object.next_link

            while next_link:
                list_object = WorkspacesOperations.list_by_resource_group(
                    auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
                    resource_group_name, next_link=next_link)
                workspace_list += list_object.value
                next_link = list_object.next_link
            return workspace_list
        else:
            # Ignore any params and list all workspaces user has access to optionally scoped by resource group
            from azureml._workspace.custom import ml_workspace_list
            return ml_workspace_list(auth, subscription_id, resource_group_name=resource_group_name)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, WORKSPACE + "s")


def delete_workspace(auth, resource_group_name, workspace_name, subscription_id,
                     delete_dependent_resources, no_wait):
    """
    Delete a workspace.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    from azureml._workspace.custom import ml_workspace_delete
    try:
        if delete_dependent_resources:
            # get the workspace object first
            workspace = WorkspacesOperations.get(
                auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
                resource_group_name,
                workspace_name)

            delete_storage_armId(auth, workspace.storage_account)
            delete_kv_armId(auth, workspace.key_vault)
            delete_insights_armId(auth, workspace.application_insights)

        return ml_workspace_delete(auth, subscription_id, resource_group_name, workspace_name, no_wait)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, WORKSPACE)


def workspace_sync_keys(auth, resource_group_name, workspace_name, subscription_id):
    """
    Sync keys associated with this workspace.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    try:
        return WorkspacesOperations.sync_keys(
            auth._get_service_client(AzureMachineLearningWorkspaces, subscription_id).workspaces,
            resource_group_name, workspace_name)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, WORKSPACE)


def share_workspace(auth, resource_group_name, workspace_name, subscription_id, user, role):
    """
    Share this workspace with another user.
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param subscription_id:
    :param user:
    :param role:
    :type subscription_id: str
    :return:
    """
    scope = '/subscriptions/' + subscription_id + '/resourceGroups/' + resource_group_name + \
        '/providers/Microsoft.MachineLearningServices/workspaces/' + workspace_name
    resolve_assignee = False
    if user.find('@') >= 0: # user principal
        resolve_assignee = True
    create_role_assignment(
        auth,
        role,
        assignee=user,
        resource_group_name=None,
        scope=scope,
        resolve_assignee=resolve_assignee)


def update_workspace(auth, resource_group_name, workspace_name, friendly_name,
                     description, subscription_id, tags=None):
    """
    Update workspace
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param friendly_name:
    :param description: str
    :param subscription_id:
    :type subscription_id: str
    :param tags:
    :return:
    """
    try:
        from azureml._workspace.custom import ml_workspace_update
        return ml_workspace_update(auth._get_service_client(
            AzureMachineLearningWorkspaces, subscription_id).workspaces,
            resource_group_name,
            workspace_name,
            tags,
            friendly_name,
            description)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, WORKSPACE)


def show_workspace(auth, resource_group_name=None, workspace_name=None,
                   subscription_id=None):
    """
    Show Workspace
    :param auth:
    :type auth: azureml.core.authentication.AbstractAuthentication
    :param resource_group_name:
    :param workspace_name:
    :param subscription_id:
    :type subscription_id: str
    :return:
    """
    try:
        if not (resource_group_name and workspace_name and subscription_id):
            project_info = get_project_info(auth, os.getcwd())
            resource_group_name = project_info[RESOURCE_GROUP_KEY]
            workspace_name = project_info[WORKSPACE_KEY]
            subscription_id = project_info[SUBSCRIPTION_KEY]

        return WorkspacesOperations.get(auth._get_service_client(
            AzureMachineLearningWorkspaces, subscription_id).workspaces,
            resource_group_name,
            workspace_name,
            subscription_id=subscription_id)
    except ErrorResponseWrapperException as response_exception:
        resource_error_handling(response_exception, WORKSPACE)
