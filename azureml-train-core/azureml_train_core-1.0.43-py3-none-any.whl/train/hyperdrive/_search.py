# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The search function."""
import json
import tempfile
import os
import uuid

from azureml._base_sdk_common import _ClientSessionId
from azureml.core import Experiment, ComputeTarget
from azureml.core.compute import AmlCompute, DsvmCompute, RemoteCompute
from azureml._restclient.snapshots_client import SnapshotsClient

from azureml.train.hyperdrive.run import HyperDriveRun
from azureml.exceptions import TrainingException, UserErrorException

import azureml.train.restclients.hyperdrive as HyperDriveClient
from azureml.train.restclients.hyperdrive.models import CreateExperimentDtoGeneratorConfig, \
    CreateExperimentDtoPolicyConfig, CreateExperimentDtoPrimaryMetricConfig, ErrorResponseException
from azureml.train._telemetry_logger import _TelemetryLogger


def _create_experiment_dto(hyperdrive_config, workspace, experiment_name,
                           telemetry_values=None, activity_logger=None):
    user_email = "nobody@example.com"

    if activity_logger is not None:
        activity_logger.info("Creating snapshot...")

    platform_config = hyperdrive_config._get_platform_config(workspace, experiment_name)
    # source_directory might be None if this run is a hydrate from cloud.
    if hyperdrive_config.source_directory is not None:
        snapshot_client = SnapshotsClient(workspace.service_context)
        snapshot_id = snapshot_client.create_snapshot(hyperdrive_config.source_directory)

        if activity_logger is not None:
            activity_logger.info("Snapshot was created. SnapshotId=%s", snapshot_id)

        platform_config['Definition']['SnapshotId'] = snapshot_id

    # collect client side telemetry
    if telemetry_values is not None:
        platform_config['Definition']['TelemetryValues'] = telemetry_values

    generator_config = CreateExperimentDtoGeneratorConfig.from_dict(hyperdrive_config._generator_config)
    policy_config = CreateExperimentDtoPolicyConfig.from_dict(hyperdrive_config._policy_config)
    primary_metric_config = CreateExperimentDtoPrimaryMetricConfig.from_dict(hyperdrive_config.
                                                                             _primary_metric_config)

    # TODO: once CreateExperimentDto() supports taking run config inputs, change this
    return HyperDriveClient.models.CreateExperimentDto(generator_config=generator_config,
                                                       max_concurrent_jobs=hyperdrive_config.
                                                       _max_concurrent_runs,
                                                       max_total_jobs=hyperdrive_config._max_total_runs,
                                                       max_duration_minutes=hyperdrive_config.
                                                       _max_duration_minutes,
                                                       platform=hyperdrive_config._platform,
                                                       platform_config=platform_config,
                                                       policy_config=policy_config,
                                                       primary_metric_config=primary_metric_config,
                                                       user=user_email, name=experiment_name)


def search(hyperdrive_config, workspace, experiment_name):
    """Launch a HyperDrive run on the given configs.

    :param hyperdrive_config: A `HyperDriveConfig` that defines the configuration for this HyperDrive run.
    :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
    :param workspace: The workspace in which to run the experiment.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: Name of the experiment
    :type experiment_name: str
    :returns: A `HyperDriveRun` object that has the launched run id.
    :rtype: azureml.train.hyperdrive.HyperDriveRun
    :raises: ExperimentExecutionException: If the HyperDrive run is not launched successfully.
    """
    compute_target = None
    if hyperdrive_config.estimator is not None:
        compute_target = hyperdrive_config.estimator._compute_target
    if hyperdrive_config.run_config is not None:
        compute_target = ComputeTarget(workspace=workspace, name=hyperdrive_config.run_config.run_config.target)

    if compute_target is not None \
            and not _is_supported_compute_target(compute_target):
        raise UserErrorException(("Automated hyperparameter tuning is only supported for the compute target "
                                  "types AmlCompute, DsvmCompute and RemoteCompute. The following compute target "
                                  " type was provided: {}.").format(type(compute_target)))

    logger = _TelemetryLogger.get_telemetry_logger(__name__)
    telemetry_values = _get_telemetry_values(hyperdrive_config, workspace)
    with _TelemetryLogger.log_activity(logger,
                                       "train.hyperdrive.submit",
                                       custom_dimensions=telemetry_values) as activity_logger:

        workspace_auth = workspace._auth_object

        host_url = hyperdrive_config._get_host_url(workspace=workspace, run_name=experiment_name)

        experiment_dto = _create_experiment_dto(hyperdrive_config, workspace, experiment_name,
                                                telemetry_values, activity_logger)

        try:
            with tempfile.TemporaryDirectory() as temporary_config:
                activity_logger.info("Write config.json to temporary folder.")
                config_path = os.path.join(temporary_config, "config.json")
                with open(config_path, 'w') as config_f:
                    json.dump(experiment_dto.serialize(), config_f)

                activity_logger.info("Submitting HyperDrive experiment...")
                hyperdrive_client = HyperDriveClient.RestClient(experiment_dto.platform_config["ServiceArmScope"],
                                                                workspace_auth, host_url)
                with open(config_path, 'rb') as config_f:
                    api_response = hyperdrive_client.create_experiment(config_f)

                parent_run_id = api_response.result.platform_config["ParentRunId"]
                activity_logger.info("Experiment was submitted. ParentRunId=%s", parent_run_id)

                experiment = Experiment(workspace, experiment_name)
                return HyperDriveRun(experiment=experiment,
                                     hyperdrive_config=hyperdrive_config,
                                     run_id=parent_run_id)
        except ErrorResponseException as e:
            raise TrainingException("Exception occurred while creating the "
                                    "HyperDrive run {}".format(str(e)), inner_exception=e) from None


def _get_telemetry_values(config, workspace):
    telemetry_values = {}

    # client common...
    telemetry_values['amlClientType'] = 'azureml-sdk-train'
    telemetry_values['amlClientModule'] = __name__
    telemetry_values['amlClientFunction'] = search.__name__
    try:
        from azureml._base_sdk_common.common import fetch_tenantid_from_aad_token
        telemetry_values['tenantId'] = fetch_tenantid_from_aad_token(workspace._auth_object._get_arm_token())
    except Exception as e:
        telemetry_values['tenantId'] = "Error retrieving tenant id: {}".format(e)

    # Used for correlating hyperdrive runs submitted to execution service
    telemetry_values['amlClientRequestId'] = str(uuid.uuid4())
    telemetry_values['amlClientSessionId'] = _ClientSessionId

    # hyperdrive related...
    telemetry_values['subscriptionId'] = workspace.subscription_id
    telemetry_values['estimator'] = config.estimator.__class__.__name__
    telemetry_values['samplingMethod'] = config._generator_config['name']
    telemetry_values['terminationPolicy'] = config._policy_config['name']
    telemetry_values['primaryMetricGoal'] = config._primary_metric_config['goal']
    telemetry_values['maxTotalRuns'] = config._max_total_runs
    telemetry_values['maxConcurrentRuns'] = config._max_concurrent_runs
    telemetry_values['maxDurationMinutes'] = config._max_duration_minutes
    if config.estimator is not None:
        compute_target = config.estimator._compute_target
        telemetry_values['computeTarget'] = compute_target if isinstance(compute_target, str) else \
            compute_target.type if compute_target else "amlcompute"
    elif config.run_config is not None:
        telemetry_values['computeTarget'] = config.run_config.run_config.target
    telemetry_values['vmSize'] = None
    if config.estimator is not None:
        telemetry_values['vmSize'] = config.estimator.run_config.amlcompute.vm_size if \
            config.estimator.run_config.amlcompute else None
    elif config.run_config is not None:
        telemetry_values['vmSize'] = config.run_config.run_config.amlcompute.vm_size if \
            config.run_config.run_config.amlcompute else None

    return telemetry_values


def _is_supported_compute_target(compute_target):
    """Return whether the compute target passed as input is supported by HyperDrive."""
    return isinstance(compute_target, (AmlCompute, DsvmCompute, RemoteCompute))
