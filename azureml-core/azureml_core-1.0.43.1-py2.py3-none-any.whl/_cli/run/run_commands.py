# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse

from azureml._cli.run.run_subgroup import RunSubGroup
from azureml._cli.cli_command import command
from azureml._cli import argument
from azureml.core import Run
from azureml.exceptions import UserErrorException
from azureml._restclient import ExperimentClient
from azureml._base_sdk_common.cli_wrapper._common import _parse_key_values, _get_experiment_or_default
import yaml
from azureml.core import RunConfiguration, ScriptRunConfig


PARENT_RUN_ID = argument.Argument("parent_run_id", "--parent-run-id", "", help="Parent Run ID")
PIPELINE_RUN_ID = argument.Argument("pipeline_run_id", "--pipeline-run-id", "", help="Pipeline Run ID")

DENYLISTED_RUNDTO_KEYS = [
    'token',
    'token_expiry_time_utc',
    'options'
]


def _run_to_output_dict(run):
    # TODO: This should move to base run.py
    base_dict = run._run_dto
    for key in DENYLISTED_RUNDTO_KEYS:
        # Not user-meaningful - not a security issue
        base_dict.pop(key, None)
    base_dict['_experiment_name'] = run.experiment.name
    return base_dict


def _get_bandit_policy(hyperdrive_dict):
    from azureml.train.hyperdrive.policy import BanditPolicy
    evaluation_interval = hyperdrive_dict.get('policy').get('evaluation_interval', 1)
    slack_factor = hyperdrive_dict.get('policy').get('slack_factor')
    slack_amount = hyperdrive_dict.get('policy').get('slack_amount')
    if slack_factor is None and slack_amount is None:
        raise ValueError("Please provide a slack factor or slack amount in hyperdrive configuration file.")
    delay_evaluation = hyperdrive_dict.get('policy').get('delay_evaluation', 0)
    return BanditPolicy(evaluation_interval, slack_factor, slack_amount, delay_evaluation)


def _get_median_stopping_policy(hyperdrive_dict):
    from azureml.train.hyperdrive.policy import MedianStoppingPolicy
    evaluation_interval = hyperdrive_dict.get('policy').get('evaluation_interval', 1)
    delay_evaluation = hyperdrive_dict.get('policy').get('delay_evaluation', 0)
    return MedianStoppingPolicy(evaluation_interval, delay_evaluation)


def _get_truncation_selection_policy(hyperdrive_dict):
    from azureml.train.hyperdrive.policy import TruncationSelectionPolicy
    truncation_percentage = hyperdrive_dict.get('policy').get('truncation_percentage')
    evaluation_interval = hyperdrive_dict.get('policy').get('evaluation_interval', 1)
    delay_evaluation = hyperdrive_dict.get('policy').get('delay_evaluation', 0)
    return TruncationSelectionPolicy(truncation_percentage, evaluation_interval, delay_evaluation)


def _get_no_termination_policy(hyperdrive_dict):
    from azureml.train.hyperdrive.policy import NoTerminationPolicy
    return NoTerminationPolicy()


def _get_parameter_space(hyperdrive_dict):
    from azureml.train.hyperdrive.parameter_expressions import choice, randint, uniform, \
        quniform, loguniform, qloguniform, normal, qnormal, lognormal, qlognormal
    expressions = {
        "choice": choice,
        "randint": randint,
        "uniform": uniform,
        "quniform": quniform,
        "loguniform": loguniform,
        "qloguniform": qloguniform,
        "normal": normal,
        "qnormal": qnormal,
        "lognormal": lognormal,
        "qlognormal": qlognormal
    }
    parameter_space = {}
    parameter_space_config = hyperdrive_dict.get('sampling').get('parameter_space')
    if parameter_space_config is None or not parameter_space_config:
        raise ValueError("Please provide parameter space in hyperdrive configuration file.")
    for parameter_space_obj in parameter_space_config:
        name = parameter_space_obj['name']
        exp = parameter_space_obj['expression']
        values = parameter_space_obj['values']
        parameter_space[name] = expressions[exp](*values)
    return parameter_space


def _get_random_sampling(hyperdrive_dict):
    from azureml.train.hyperdrive.sampling import RandomParameterSampling
    parameter_space = _get_parameter_space(hyperdrive_dict)
    return RandomParameterSampling(parameter_space=parameter_space)


def _get_grid_sampling(hyperdrive_dict):
    from azureml.train.hyperdrive.sampling import GridParameterSampling
    parameter_space = _get_parameter_space(hyperdrive_dict)
    return GridParameterSampling(parameter_space=parameter_space)


def _get_bayesian_sampling(hyperdrive_dict):
    from azureml.train.hyperdrive.sampling import BayesianParameterSampling
    parameter_space = _get_parameter_space(hyperdrive_dict)
    return BayesianParameterSampling(parameter_space=parameter_space)


@command(
    subgroup_type=RunSubGroup,
    command="list",
    short_description="List runs",
    argument_list=[
        argument.EXPERIMENT_NAME,
        argument.PROJECT_PATH,
        PARENT_RUN_ID,
        PIPELINE_RUN_ID,
        argument.LAST_N,
        argument.COMPUTE_TARGET_NAME,
        argument.STATUS
    ])
def list_runs_in_workspace(
        workspace=None,
        # We enforce a logger
        logger=None,
        experiment_name=None,
        path=None,
        parent_run_id=None,
        pipeline_run_id=None,
        last_n=None,
        compute_target_name=None,
        status=None):
    # Mutually exclusive parameters
    if pipeline_run_id is not None and experiment_name is not None:
        raise UserErrorException("Cannot provide both {} and {}".format(
            argument.EXPERIMENT_NAME.long_form, PIPELINE_RUN_ID.long_form))

    if last_n is not None:
        if pipeline_run_id is not None:
            raise UserErrorException("Cannot specify {} for pipeline runs".format(argument.LAST_N.long_form))
        try:
            last_n = int(last_n)
        except:  # noqa
            raise UserErrorException("{} must be an int, got: {}".format(argument.LAST_N.long_form, last_n))

    if pipeline_run_id is None:
        # List the top N runs in an experiment
        logger.debug("Pipeline Run ID and experiment name not specified - attempting lookup")
        try:
            experiment = _get_experiment_or_default(
                workspace=workspace, experiment_name=experiment_name, project_path=path, logger=logger)
        except Exception as ex:
            raise UserErrorException("One of {} must be provided.".format([
                arg.long_form for arg in [argument.EXPERIMENT_NAME, PIPELINE_RUN_ID]
            ]), inner_exception=ex)

        if parent_run_id is not None:
            parent_run = Run(experiment, parent_run_id)
            # TODO: Sad, page_size here but last below
            runs = parent_run._client.run.get_child_runs(
                parent_run._root_run_id, caller='azml run list -e',
                page_size=last_n, target_name=compute_target_name, status=status)
        else:
            client = ExperimentClient(experiment.workspace.service_context, experiment.name)
            # Ignore children, can just use parent-run-id if needed
            runs = client.get_runs(caller='azml run list -e', last=last_n,
                                   include_children=False, target_name=compute_target_name, status=status)

        runs = [run.as_dict(keep_readonly=True) for run in runs]
        for run in runs:
            run.update(_experiment_name=experiment.name)
        return runs

    # else, pipeline_run_id
    from azureml.pipeline.core import PipelineRun
    pipeline_runs = PipelineRun.get_pipeline_runs(workspace=workspace, pipeline_id=pipeline_run_id)
    serialized_run_list = []
    for pipeline_run in pipeline_runs:
        info_dict = pipeline_run._get_base_info_dict()

        # Fill in additional properties for a pipeline run
        if hasattr(pipeline_run._client.run_dto, 'start_time_utc') \
                and pipeline_run._client.run_dto.start_time_utc is not None:
            info_dict['StartDate'] = pipeline_run._client.run_dto.start_time_utc.isoformat()

        if hasattr(pipeline_run._client.run_dto, 'end_time_utc') \
                and pipeline_run._client.run_dto.end_time_utc is not None:
            info_dict['EndDate'] = pipeline_run._client.run_dto.end_time_utc.isoformat()

        properties = pipeline_run.get_properties()
        if 'azureml.pipelineid' in properties:
            info_dict['PiplineId'] = properties['azureml.pipelineid']
        serialized_run_list.append(info_dict)

    return serialized_run_list


@command(
    subgroup_type=RunSubGroup,
    command="show",
    short_description="Show run")
def show_run(
        run=None,
        # We enforce a logger
        logger=None):

    return _run_to_output_dict(run)


@command(
    subgroup_type=RunSubGroup,
    command="update",
    short_description="Update the run by adding tags",
    argument_list=[
        argument.ADD_TAG_OPTION
    ])
def update_run(
        run=None,
        add_tags=None,
        # We enforce a logger
        logger=None):

    tag, value = add_tags.split("=", 1)
    logger.debug("Updating run tag %s with value %s based on input %s", tag, value, add_tags)
    run.tag(tag, value)
    return run._client.get_run()


@command(
    subgroup_type=RunSubGroup,
    command="cancel",
    short_description="Cancel run")
def cancel_run(
        run=None,
        # We enforce a logger
        logger=None):

    run.cancel()
    print("Experiment run canceled successfully.")


PIPELINE_ID = argument.Argument("pipeline_id", "--pipeline-id", "-i", required=True,
                                help="ID of the pipeline to submit (guid)")

# TODO: This is sad - agree and remove
PIPELINE_EXPERIMENT_NAME = argument.Argument("experiment_name", "--experiment-name", "-n", required=False,
                                             help="Experiment name for run submission. If unspecified, use "
                                             "the pipeline name")
PIPELINE_PARAMS = \
    argument.Argument("pipeline_params", "--parameters", "-p", required=False,
                      help="Comma-separated list of name=value pairs for pipeline parameter assignments")
DATAPATH_PARAMS = \
    argument.Argument("datapath_params", "--datapaths", "-d", required=False,
                      help="Comma-separated list of name=datastore/path pairs for " +
                      "datapath parameter assignments")


@command(
    subgroup_type=RunSubGroup,
    command="submit-pipeline",
    short_description="Submit a pipeline for execution.",
    argument_list=[
        PIPELINE_ID,
        PIPELINE_EXPERIMENT_NAME,
        PIPELINE_PARAMS,
        DATAPATH_PARAMS
    ]
)
def submit_pipeline(
        workspace=None,  # Auto populated args + object
        pipeline_id=None,
        experiment_name=None,
        pipeline_params=None,
        datapath_params=None,
        # We enforce a logger
        logger=None):
    """
    Submit a pipeline run based on a published pipeline ID
    """

    from azureml.pipeline.core import PublishedPipeline
    pipeline = PublishedPipeline.get(workspace, pipeline_id)
    if experiment_name is None or experiment_name == '':
        # Use the pipeline name as the experiment name
        experiment_name = pipeline._sanitize_name()

    assigned_params = _parse_key_values(pipeline_params, 'Parameter assignment')

    datapaths = _parse_key_values(datapath_params, 'Datapath assignment')
    for datapath_param_name in datapaths:
        datastore_with_path = datapaths[datapath_param_name]
        if '/' not in datastore_with_path:
            raise UserErrorException("Datapath value %s should have format datastore/path" % datastore_with_path)
        path_tokens = datastore_with_path.split('/', 1)
        from azureml.core import Datastore
        from azureml.data.datapath import DataPath
        datastore = Datastore(workspace, path_tokens[0])
        assigned_params[datapath_param_name] = DataPath(datastore=datastore, path_on_datastore=path_tokens[1])

    pipeline_run = pipeline.submit(pipeline_parameters=assigned_params, workspace=workspace,
                                   experiment_name=experiment_name)

    logger.info("Pipeline was submitted with run ID %s".format(pipeline_run.id))
    return _run_to_output_dict(pipeline_run)


USER_SCRIPT_AND_ARGUMENTS = argument.Argument("user_script_and_arguments", "user_script_and_arguments", "",
                                              help="The run submit arguments, like script name and script arguments.",
                                              nargs=argparse.REMAINDER, positional_argument=True)

COMPUTE_TARGET_NAME = argument.Argument("ct_name", ["--target", "--ct"], "",
                                        help="The name of the compute target to use for the run.")


@command(
    subgroup_type=RunSubGroup,
    command="submit-script",
    short_description="Submit a script for execution",
    argument_list=[
        argument.PROJECT_PATH,
        argument.RUN_CONFIGURATION_NAME_OPTION,
        argument.ASYNC_OPTION,
        argument.CONDA_DEPENDENCY_OPTION,
        COMPUTE_TARGET_NAME,
        # TODO: Parameter sweep?
        # argument.RUNCONFIG_SCRIPT_OVERRIDE_OPTION,
        # argument.RUNCONFIG_ARGUMENTS_OVERRIDE_OPTION,
        USER_SCRIPT_AND_ARGUMENTS
    ]
)
def submit_run(
        experiment=None,
        path=None,  # Source directory
        run_configuration_name=None,
        conda_dependencies=None,
        run_async=None,
        ct_name=None,
        user_script_and_arguments=None,
        logger=None):

    from azureml.core import RunConfiguration, ScriptRunConfig

    if user_script_and_arguments and len(user_script_and_arguments) > 0:
        script, arguments = user_script_and_arguments[0], user_script_and_arguments[1:]
    else:
        script, arguments = None, None

    if run_configuration_name is None:
        logger.info("No Run Configuration name provided, using default: local system-managed")
        run_config = RunConfiguration()
    else:
        run_config = RunConfiguration.load(path, run_configuration_name)

    if conda_dependencies:
        from azureml.core.conda_dependencies import CondaDependencies
        cd = CondaDependencies(conda_dependencies_file_path=conda_dependencies)
        run_config.environment.python.conda_dependencies = cd

    if not run_config.script and not script:
        raise UserErrorException("Please specify the script to run either via parameter or in the runconfig")

    if run_config.script and script:
        logger.info("Overriding runconfig script %s with script argument %s", run_config.script, script)

    if script:
        run_config.script = script

    if run_config.arguments and arguments:
        logger.info("Overriding runconfig arguments %s with  %s", run_config.arguments, arguments)

    if arguments:
        run_config.arguments = arguments

    if ct_name:
        run_config.target = ct_name

    logger.info("Running %s with arguments %s", run_config.script, run_config.arguments)
    script_run_config = ScriptRunConfig(path,
                                        run_config=run_config,
                                        arguments=run_config.arguments)

    run = experiment.submit(script_run_config)

    logger.debug("Running asynchronously: %s", run_async)
    if not run_async:
        run.wait_for_completion(show_output=True, wait_post_processing=True)

    return _run_to_output_dict(run)


@command(
    subgroup_type=RunSubGroup,
    command="submit-hyperdrive",
    short_description="Submit a hyper parameter sweep using run config.",
    argument_list=[
        argument.HYPERDRIVE_CONFIGURATION_NAME,
        argument.SOURCE_DIRECTORY,
        argument.RUN_CONFIGURATION_NAME_OPTION,
        argument.PROJECT_PATH,
        argument.ASYNC_OPTION
    ]
)
def submit_hyperdrive(
        experiment,
        hyperdrive_configuration_name,
        source_directory,
        run_configuration_name,
        path=None,
        run_async=None,
        logger=None):
    from azureml.train.hyperdrive.runconfig import HyperDriveConfig, PrimaryMetricGoal
    policies = {
        "BANDITPOLICY": _get_bandit_policy,
        "MEDIANSTOPPINGPOLICY": _get_median_stopping_policy,
        "TRUNCATIONSELECTIONPOLICY": _get_truncation_selection_policy,
        "NOTERMINATIONPOLICY": _get_no_termination_policy
    }

    samplings = {
        "RANDOM": _get_random_sampling,
        "GRID": _get_grid_sampling,
        "BAYESIAN": _get_bayesian_sampling
    }

    hstream = open(hyperdrive_configuration_name, "r")
    hyperdrive_dict = yaml.load(hstream)
    run_config = RunConfiguration.load(path, run_configuration_name)
    # default to path if source directory is missing.
    if source_directory is None:
        source_directory = path

    script_run_config = ScriptRunConfig(source_directory=source_directory, run_config=run_config)
    hyperparameter_sampling_type = hyperdrive_dict.get('sampling').get('type')
    if hyperparameter_sampling_type is None:
        raise ValueError("Please provide hyperparameter sampling type in hyperdrive configuration file.")

    hyperparameter_sampling = samplings[hyperparameter_sampling_type.upper()](hyperdrive_dict)
    policy_type = hyperdrive_dict.get('policy').get('type', 'NOTERMINATIONPOLICY')
    policy = policies[policy_type.upper()](hyperdrive_dict)
    primary_metric_goal = PrimaryMetricGoal.from_str(hyperdrive_dict.get('primary_metric_goal'))
    hyperdrive_config = HyperDriveConfig(hyperparameter_sampling=hyperparameter_sampling,
                                         primary_metric_name=hyperdrive_dict.get('primary_metric_name'),
                                         primary_metric_goal=primary_metric_goal,
                                         max_total_runs=hyperdrive_dict.get('max_total_runs'),
                                         max_concurrent_runs=hyperdrive_dict.get('max_concurrent_runs'),
                                         max_duration_minutes=hyperdrive_dict.get('max_duration_minutes'),
                                         policy=policy,
                                         run_config=script_run_config)
    run = experiment.submit(hyperdrive_config)
    logger.debug("Running asynchronously: %s", run_async)
    if not run_async:
        run.wait_for_completion(show_output=True, wait_post_processing=True)

    return _run_to_output_dict(run)
