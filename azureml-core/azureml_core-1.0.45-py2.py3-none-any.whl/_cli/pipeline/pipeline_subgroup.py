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
                         self._command_pipeline_list_steps(),
                         self._command_schedule_create(),
                         self._command_schedule_update(),
                         self._command_schedule_enable(),
                         self._command_schedule_disable(),
                         self._command_last_pipeline_run_show(),
                         self._command_pipeline_runs_list(),
                         self._command_schedule_show()]
        return commands_list

    def _command_pipeline_list(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#list_pipelines"
        return cli_command.CliCommand("list", "List all pipelines and respective schedules in the workspace.",
                                      [argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_show(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#show_pipeline"
        pipeline_id = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                        help="ID of the pipeline to show (guid)")
        return cli_command.CliCommand("show", "Show details of a pipeline and respective schedules.",
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

    def _command_schedule_create(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#create_schedule"
        pipeline_id = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                        help="ID of the pipeline to create schedule (guid)")
        name = argument.Argument("name", "--name", "-n", required=True,
                                 help="Name of schedule")
        experiment_name = argument.Argument("experiment-name", "--experiment-name", "-e", required=True,
                                            help="Name of experiment")
        schedule_yaml = argument.Argument("schedule_yaml", "--schedule-yaml", "-y",
                                          required=False,
                                          help="Schedule  YAML input")
        return cli_command.CliCommand("create-schedule", "Create a schedule.",
                                      [name, pipeline_id, experiment_name,
                                       schedule_yaml,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_schedule_update(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#update_schedule"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        name = argument.Argument("name", "--name", "-n", required=False,
                                 help="Name of the schedule to show (guid)")
        status = argument.Argument("status", "--status", "-t", required=False,
                                   help="Status of the schedule to show (guid)")
        schedule_yaml = argument.Argument("schedule_yaml", "--schedule-yaml", "-y",
                                          required=False,
                                          help="Schedule  YAML input")
        return cli_command.CliCommand("update-schedule", "update a schedule.",
                                      [schedule_id,
                                       name,
                                       status,
                                       schedule_yaml,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_last_pipeline_run_show(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#show_last_pipeline_run"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        return cli_command.CliCommand("last-pipeline-run", "Show last pipeline run for a schedule.",
                                      [schedule_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_pipeline_runs_list(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#list_pipeline_runs"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        return cli_command.CliCommand("pipeline-runs-list", "List pipeline runs generated from a schedule.",
                                      [schedule_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_schedule_disable(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#disable_schedule"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        return cli_command.CliCommand("disable-schedule", "Disable a schedule from running.",
                                      [schedule_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_schedule_enable(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#enable_schedule"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        return cli_command.CliCommand("enable-schedule", "Enable a schedule and allow it to run.",
                                      [schedule_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)

    def _command_schedule_show(self):
        function_path = "azureml.pipeline._cli_wrapper.cmd_pipeline#show_schedule"
        schedule_id = argument.Argument("schedule_id", "--schedule-id", "-s", required=True,
                                        help="ID of the schedule to show (guid)")
        return cli_command.CliCommand("show-schedule", "Show details of a schedule.",
                                      [schedule_id,
                                       argument.RESOURCE_GROUP_NAME,
                                       argument.WORKSPACE_NAME], function_path)
