# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli.workspace.workspace_subgroup import WorkspaceSubGroup
from azureml._cli.cli_command import command
from azureml._cli import argument

from azureml.core.workspace import Workspace


def create_workspace(workspace_name, resource_group_name=None, location=None,
                     friendly_name=None, storage_account=None, key_vault=None, app_insights=None,
                     container_registry=None, create_resource_group=None, exist_ok=False):

    from azureml._base_sdk_common.cli_wrapper._common import get_cli_specific_auth, get_default_subscription_id, \
        get_resource_group_or_default_name

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    # resource group can be None, as we create on user's behalf.
    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth)

    workspace_object = Workspace.create(workspace_name, auth=auth, subscription_id=default_subscription_id,
                                        resource_group=resource_group_name, location=location,
                                        create_resource_group=create_resource_group,
                                        friendly_name=friendly_name, storage_account=storage_account,
                                        key_vault=key_vault, app_insights=app_insights,
                                        container_registry=container_registry, exist_ok=exist_ok)

    # TODO: Need to add a message that workspace created successfully.
    return workspace_object._get_create_status_dict()


def list_workspace(resource_group_name=None):

    from azureml._base_sdk_common.cli_wrapper._common import get_cli_specific_auth, get_default_subscription_id, \
        get_resource_group_or_default_name

    auth = get_cli_specific_auth()
    default_subscription_id = get_default_subscription_id(auth)

    # resource group can be None, as we create on user's behalf.
    resource_group_name = get_resource_group_or_default_name(resource_group_name, auth=auth)

    workspaces_dict = Workspace.list(default_subscription_id, auth=auth,
                                     resource_group=resource_group_name)
    serialized_workspace_list = list()
    for workspace_name in workspaces_dict:
        for workspace_object in workspaces_dict[workspace_name]:
            serialized_workspace_list.append(workspace_object._to_dict())

    return serialized_workspace_list


NO_WAIT = argument.Argument(
    "no_wait",
    "--no-wait", "",
    action="store_true",
    help="Do not wait for the workspace deletion to complete.")


DELETE_DEPENDENT_RESOURCES = argument.Argument(
    "delete_dependent_resources",
    "--all-resources", "",
    action="store_true",
    help="Deletes resources which this workspace depends on like storage, acr, kv and app insights.")


@command(
    subgroup_type=WorkspaceSubGroup,
    command="delete",
    short_description="Delete a workspace.",
    argument_list=[
        DELETE_DEPENDENT_RESOURCES,
        NO_WAIT
    ])
def delete_workspace(
        workspace=None,
        delete_dependent_resources=False,
        no_wait=False,
        logger=None):

    return workspace.delete(delete_dependent_resources=delete_dependent_resources, no_wait=no_wait)


@command(
    subgroup_type=WorkspaceSubGroup,
    command="sync-keys",
    short_description="Sync workspace keys  for dependent resources such as storage, acr, and app insights.")
def sync_workspace_keys(
        workspace=None,
        # We should enforce a logger
        logger=None):

    return workspace._sync_keys()


@command(
    subgroup_type=WorkspaceSubGroup,
    command="show",
    short_description="Show a workspace.")
def show_workspace(
        workspace=None,
        logger=None):

    return workspace.get_details()


USER = argument.Argument("user", "--user", "", help="User with whom to share this workspace.", required=True)
ROLE = argument.Argument("role", "--role", "", help="Role to assign to this user.", required=True)


@command(
    subgroup_type=WorkspaceSubGroup,
    command="share",
    short_description="Share a workspace with another user with a given role.",
    argument_list=[
        USER,
        ROLE
    ])
def share_workspace(
        workspace=None,
        user=None,
        role=None,
        logger=None):

    return workspace._share(user, role)


DESCRIPTION = argument.Argument("description", "--description", "-d", help="Description of this workspace.",
                                required=False)

TAGS = argument.Argument("tags", "--tags", "", help="Tags associated with this workspace.", required=False)


@command(
    subgroup_type=WorkspaceSubGroup,
    command="update",
    short_description="Update a workspace.",
    argument_list=[
        argument.FRIENDLY_NAME,
        DESCRIPTION,
        TAGS
    ])
def update_workspace(
        workspace=None,
        friendly_name=None,
        description=None,
        tags=None,
        logger=None):

    # Returns a dict containing the update details.
    return workspace._update(friendly_name, description, tags=tags)
