# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._cli import abstract_subgroup
from azureml._cli import cli_command
from azureml._cli import argument


class PipelineSubGroup(abstract_subgroup.AbstractSubGroup):
    """This class defines the pipeline sub group."""

    def get_subgroup_name(self):
        """Returns the name of the subgroup.
        This name will be used in the cli command."""
        return "pipeline"

    def get_subgroup_title(self):
        """Returns the subgroup title as string. Title is just for informative purposes, not related
        to the command syntax or options. This is used in the help option for the subgroup."""
        return "pipeline subgroup commands"

    def get_nested_subgroups(self):
        """Returns sub-groups of this sub-group."""
        return super(PipelineSubGroup, self).compute_nested_subgroups(__package__)

    def get_commands(self, for_azure_cli=False):
        """ Returns commands associated at this sub-group level."""
        commands_list = [self._command_pipeline_list(),
                         self._command_pipeline_show(),
                         self._command_pipeline_enable(),
                         self._command_pipeline_disable(),
                         self._command_pipeline_list_steps()]
        return commands_list

    def _command_pipeline_list(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#list_pipelines"
        return cli_command.CliCommand("list", "List all pipelines in the workspace.",
                                      [argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_show(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#show_pipeline"
        pipeline_id = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                        help="ID of the pipeline to show (guid)")
        return cli_command.CliCommand("show", "Show details of a pipeline.",
                                      [pipeline_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_disable(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#disable_pipeline"
        pipeline_id = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                        help="ID of the pipeline to disable (guid)")
        return cli_command.CliCommand("disable", "Disable a pipeline from running.",
                                      [pipeline_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_enable(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#enable_pipeline"
        pipeline_id = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                        help="ID of the pipeline to enable (guid)")
        return cli_command.CliCommand("enable", "Enable a pipeline and allow it to run.",
                                      [pipeline_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_list_steps(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#list_pipeline_steps"
        return cli_command.CliCommand("list-steps", "List the step runs generated from a pipeline run",
                                      [argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME,
                                       argument.RUN_ID_OPTION.get_required_true_copy()], function_path)
