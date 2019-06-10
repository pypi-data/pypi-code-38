# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._base_sdk_common.common import set_correlation_id, CLICommandOutput
from azureml._base_sdk_common.cli_wrapper._common import get_cli_specific_output, get_workspace_or_default
from azureml.pipeline.core import PublishedPipeline, PipelineRun


def _setup_and_get_workspace(workspace_name, resource_group_name):
    set_correlation_id()

    workspace_object = get_workspace_or_default(workspace_name=workspace_name, resource_group=resource_group_name)
    return workspace_object


def _add_run_properties(info_dict, run_object):
    """Fill in additional properties for a pipeline run"""
    if hasattr(run_object._client.run_dto, 'start_time_utc')\
            and run_object._client.run_dto.start_time_utc is not None:
        info_dict['StartDate'] = run_object._client.run_dto.start_time_utc.isoformat()

    if hasattr(run_object._client.run_dto, 'end_time_utc')\
            and run_object._client.run_dto.end_time_utc is not None:
        info_dict['EndDate'] = run_object._client.run_dto.end_time_utc.isoformat()

    properties = run_object.get_properties()
    if 'azureml.pipelineid' in properties:
        info_dict['PiplineId'] = properties['azureml.pipelineid']


def list_pipelines(workspace_name=None, resource_group_name=None):
    """List the published pipelines in a workspace."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipelines = PublishedPipeline.get_all(workspace_object)

    serialized_pipeline_list = []
    for pipeline in pipelines:
        serialized_pipeline_list.append(pipeline._to_dict_cli(verbose=False))

    command_output = CLICommandOutput("")
    command_output.merge_dict(serialized_pipeline_list)

    return get_cli_specific_output(command_output)


def show_pipeline(pipeline_id, workspace_name=None, resource_group_name=None):
    """Show the details of a published pipeline."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
    output_dict = pipeline._to_dict_cli(verbose=True)

    command_output = CLICommandOutput("")
    command_output.merge_dict(output_dict)

    return get_cli_specific_output(command_output)


def enable_pipeline(pipeline_id, workspace_name=None, resource_group_name=None):
    """Enable a pipeline for execution."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
    pipeline.activate()

    command_output = CLICommandOutput("Pipeline '%s' (%s) was enabled successfully." % (pipeline.name, pipeline.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def disable_pipeline(pipeline_id, workspace_name=None, resource_group_name=None):
    """Disable a pipeline from running."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline = PublishedPipeline.get(workspace_object, pipeline_id)
    pipeline.disable()

    command_output = CLICommandOutput("Pipeline '%s' (%s) was disabled successfully." % (pipeline.name, pipeline.id))
    command_output.set_do_not_print_dict()
    return get_cli_specific_output(command_output)


def list_pipeline_steps(run_id, workspace_name=None, resource_group_name=None):
    """List child steps for a pipeline run."""
    workspace_object = _setup_and_get_workspace(workspace_name=workspace_name, resource_group_name=resource_group_name)

    pipeline_run = PipelineRun.get(workspace=workspace_object, run_id=run_id)
    aeva_graph = pipeline_run.get_graph()

    step_runs = pipeline_run.get_steps()
    serialized_run_list = []
    for step_run in step_runs:
        info_dict = step_run._get_base_info_dict()
        _add_run_properties(info_dict, step_run)

        # Get the step name from the Aeva graph
        if step_run._is_reused:
            node_id = step_run._current_node_id
        else:
            node_id = step_run._node_id
        info_dict['Name'] = aeva_graph.get_node(node_id).name
        serialized_run_list.append(info_dict)

    command_output = CLICommandOutput("")
    command_output.merge_dict(serialized_run_list)

    return get_cli_specific_output(command_output)
