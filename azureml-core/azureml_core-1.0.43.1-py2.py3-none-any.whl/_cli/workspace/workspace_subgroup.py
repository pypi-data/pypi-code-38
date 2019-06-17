# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli import abstract_subgroup
from azureml._cli import cli_command
from azureml._cli import argument


class WorkspaceSubGroup(abstract_subgroup.AbstractSubGroup):
    """This class defines the project sub group."""

    def get_subgroup_name(self):
        """Returns the name of the subgroup.
        This name will be used in the cli command."""
        return "workspace"

    def get_subgroup_title(self):
        """Returns the subgroup title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the subgroup."""
        return "workspace subgroup commands"

    def get_nested_subgroups(self):
        """Returns sub-groups of this sub-group."""
        return super(WorkspaceSubGroup, self).compute_nested_subgroups(__package__)

    def get_commands(self, for_azure_cli=False):
        """ Returns commands associated at this sub-group level."""
        # TODO: Adding commands to a list can also be automated, if we assume the
        # command function name to start with a certain prefix, like _command_*
        auto_registered_commands = super(WorkspaceSubGroup, self).get_commands()
        commands_list = auto_registered_commands + \
            [
                self._command_workspace_create(),
                self._command_workspace_list()
            ]
        return commands_list

    def _command_workspace_create(self):
        function_path = "azureml._cli.workspace.workspace_commands#create_workspace"

        workspace_friendly_name = argument.FRIENDLY_NAME.clone()
        workspace_friendly_name.help = "Friendly name for this workspace."

        key_vault = argument.Argument("key_vault",
                                      "--keyvault",
                                      "",
                                      help="Key Vault to be associated with this workspace.")
        storage_argument = argument.Argument("storage_account",
                                             "--storage-account",
                                             "",
                                             help="Storage account to be associated with this workspace.")
        container_registry_argument = argument.Argument(
            "container_registry",
            "--container-registry",
            "",
            help="Container Registry to be associated with this workspace.")
        application_insights_argument = argument.Argument(
            "app_insights",
            "--application-insights",
            "",
            help="Application Insights to be associated with this workspace.")
        create_resource_group_argument = argument.Argument(
            "create_resource_group",
            "--yes",
            "-y",
            action="store_true",
            help="Create a resource group for this workspace.")
        exist_ok_workspace_argument = argument.Argument(
            "exist_ok",
            "--exist-ok",
            "",
            action="store_true",
            help="Do not fail if workspace exists.")

        return cli_command.CliCommand("create", "Create a workspace",
                                      [argument.WORKSPACE_NAME.get_required_true_copy(),
                                       workspace_friendly_name,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.LOCATION,
                                       storage_argument,
                                       key_vault,
                                       application_insights_argument,
                                       container_registry_argument,
                                       create_resource_group_argument,
                                       exist_ok_workspace_argument
                                       ], function_path)

    def _command_workspace_list(self):
        function_path = "azureml._cli.workspace.workspace_commands#list_workspace"

        return cli_command.CliCommand("list", "List workspaces.",
                                      [argument.RESOURCE_GROUP_NAME], function_path)
