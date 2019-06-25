# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDriveConfig module defines the allowed configuration options for a HyperDrive experiment."""
import enum
import json
import copy
import warnings
import uuid

from azureml.core.script_run_config import get_run_config_from_script_run, ScriptRunConfig
from azureml.train.hyperdrive.policy import NoTerminationPolicy, _policy_from_dict
from azureml.train.hyperdrive.sampling import BayesianParameterSampling, _sampling_from_dict
from azureml.train._estimator_helper import _get_arguments

from azureml._base_sdk_common.service_discovery import get_service_url
from azureml._base_sdk_common.project_context import create_project_context
from azureml._base_sdk_common.utils import convert_list_to_dict
from azureml._execution._commands import _serialize_run_config_to_dict
from azureml.exceptions import UserErrorException, TrainingException

HYPERDRIVE_URL_SUFFIX = "/hyperdrive/v1.0"
MAX_DURATION_MINUTES = 10080  # after this max duration the HyperDrive run is cancelled.
RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN = 20
RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN = 20


class PrimaryMetricGoal(enum.Enum):
    """The supported metric goals.

    A metric goal is used to determine whether a higher value for a metric is better or worse. This is used when
    comparing runs based on the primary metric. For example, you may want to maximize accuracy or minimize error.
    """

    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"

    @staticmethod
    def from_str(goal):
        """Return the PrimaryMetric goal that corresponds to the given value.

        :param goal: The string name of the goal.
        :type goal: str
        """
        if goal.lower() == PrimaryMetricGoal.MAXIMIZE.name.lower():
            return PrimaryMetricGoal.MAXIMIZE
        elif goal.lower() == PrimaryMetricGoal.MINIMIZE.name.lower():
            return PrimaryMetricGoal.MINIMIZE
        raise TrainingException("Unknown goal '{}'".format(goal))


class HyperDriveConfig(object):
    """Configuration that defines a HyperDrive run.

    This includes information about parameter space sampling, termination policy,
    primary metric, estimator and the compute target to execute the experiment runs on.

    :param estimator: An estimator that will be called with sampled hyper parameters.
    :type estimator: azureml.train.estimator.MMLBaseEstimator
    :param hyperparameter_sampling: The hyperparameter sampling space.
    :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
    :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.
                   The MedianTerminationPolicy with delay_evaluation of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
    :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
    :param primary_metric_name: The name of the primary metric reported by the experiment runs.
    :type primary_metric_name: str
    :param primary_metric_goal: One of maximize / minimize.
                                It determines if the primary metric has to be
                                minimized/maximized in the experiment runs' evaluation.
    :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
    :param max_total_runs: Maximum number of runs. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
    :type max_total_runs: int
    :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, all runs are launched in parallel.
    :type max_concurrent_runs: int
    :param max_duration_minutes: Maximum duration of the run. Once this time is exceeded, the run is cancelled.
    :type max_duration_minutes: int
    """

    _PLATFORM = "AML"

    def __init__(self,
                 hyperparameter_sampling,
                 primary_metric_name, primary_metric_goal,
                 max_total_runs,
                 max_concurrent_runs=None,
                 max_duration_minutes=MAX_DURATION_MINUTES,
                 policy=None,
                 estimator=None,
                 run_config=None
                 ):
        """Initialize the HyperDriveConfig.

        :param hyperparameter_sampling: Hyperparameter space sampling definition.
        :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
        :param primary_metric_name: The name of the primary metric reported by the experiment runs.
        :type primary_metric_name: str
        :param primary_metric_goal: One of maximize / minimize.
                                    It determines if the primary metric has to be
                                    minimized/maximized in the experiment runs evaluation.
        :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
        :param max_total_runs: Maximum number of runs. This is the upper bound - we may
                               have less for instance when the space samples is less than this value.
        :type max_total_runs: int
        :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, launch all runs in parallel.
        :type max_concurrent_runs: int
        :param max_duration_minutes: Max duration of the run. After this time, the experiment is cancelled.
        :type max_duration_minutes: int
        :param policy: The early termination policy to use. If None - the default,
                       no early termination policy will be used.
                       The MedianTerminationPolicy with delay_evaluation of 5
                       is a good termination policy to start with. These are conservative settings,
                       that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
        :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
        :param estimator: An estimator that will be called with sampled hyper parameters.
                          If missing, the run_config is mandatory.
        :type estimator: azureml.train.estimator.MMLBaseEstimator
        :param run_config: An object for setting up configuration for script/notebook runs.
                           If missing, the estimator is mandatory.
        :type run_config: azureml.core.ScriptRunConfig
        """
        self._estimator = estimator
        self._run_config = run_config

        if self._estimator is None and self._run_config is None:
            raise UserErrorException("One of 'estimator' and 'run_config' arguments are mandatory.")

        if self._estimator is not None and self._run_config is not None:
            raise UserErrorException("Only one of 'estimator' and 'run_config' can be present.")

        if self._run_config is not None and not isinstance(self._run_config, ScriptRunConfig):
            raise UserErrorException("Got {} for 'run_config' type, expected 'ScriptRunConfig'.".format(
                type(self._run_config)))

        if isinstance(hyperparameter_sampling, BayesianParameterSampling) and \
                (policy is not None and not isinstance(policy, NoTerminationPolicy)):
            raise UserErrorException("No early termination policy is currently supported with Bayesian sampling. "
                                     "'{}' was provided".format(policy))

        if policy is None:
            policy = NoTerminationPolicy()

        self._policy_config = policy.to_json()
        self._generator_config = hyperparameter_sampling.to_json()
        self._primary_metric_config = {
            'name': primary_metric_name,
            'goal': primary_metric_goal.name.lower()}
        self._max_total_runs = max_total_runs
        self._max_concurrent_runs = max_concurrent_runs or max_total_runs
        self._max_duration_minutes = max_duration_minutes
        self._platform = self._PLATFORM
        self._host_url = None
        # This property is set the first time the platform_config is built.
        self._platform_config = None
        self._is_cloud_hydrate = False

        warnings.formatwarning = _simple_warning
        if self._max_duration_minutes > MAX_DURATION_MINUTES:
            warnings.warn(("The experiment maximum duration provided ({} minutes) exceeds the service limit of "
                           "{} minutes. The maximum duration will be overridden with {} minutes.").format(
                self._max_duration_minutes, MAX_DURATION_MINUTES, MAX_DURATION_MINUTES))

        if isinstance(hyperparameter_sampling, BayesianParameterSampling):
            # Needs to be updated once conditional/nested space definitions are added
            num_parameters = len(hyperparameter_sampling._parameter_space)
            recommended_max_total_runs = RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN * num_parameters

            if self._max_total_runs < recommended_max_total_runs:
                warnings.warn(("For best results with Bayesian Sampling we recommend using a maximum number of runs "
                               "greater than or equal to {} times the number of hyperparameters being tuned. Current "
                               "value for max_total_runs:{}. Recommendend value:{}.").format(
                    RECOMMENDED_MIN_RUNS_PER_PARAMETER_BAYESIAN,
                    self._max_total_runs,
                    recommended_max_total_runs))
            if self._max_concurrent_runs > RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN:
                warnings.warn(("We recommend using {} max concurrent runs or fewer when using Bayesian sampling "
                               "since a higher number might not provide the best result. Current max "
                               "concurrent runs:{}.").format(
                    RECOMMENDED_MAX_CONCURRENT_RUNS_BAYESIAN,
                    self._max_concurrent_runs))

    @property
    def estimator(self):
        """Return the estimator in this config.

        The estimator may be None if this object was built from server side data or using a run_config.

        :return: The estimator.
        :rtype: azureml.train.estimator.Estimator
        """
        return self._estimator

    @property
    def run_config(self):
        """Return the run_config in this config.

        :return: The run_config.
        :rtype: azureml.core.ScriptRunConfig
        """
        return self._run_config

    @property
    def source_directory(self):
        """Return the source directory from the config to run.

        :return: The source directory
        :rtype: str
        """
        if self._is_cloud_hydrate:
            return None

        if self.estimator is not None:
            return self.estimator.source_directory
        elif self.run_config is not None:
            return self.run_config.source_directory

        return None

    def _get_host_url(self, workspace, run_name):
        """Return the host url for the HyperDrive service.

        :param workspace: The workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param run_name: The name of the run.
        :type run_name: str
        :return: The host url for HyperDrive service.
        :rtype: str
        """
        if not self._host_url:
            service_url = self._get_service_address("hyperdrive", workspace, run_name)
            self._host_url = service_url + HYPERDRIVE_URL_SUFFIX
        return self._host_url

    @staticmethod
    def _get_project_context(workspace, run_name):
        project_context = create_project_context(auth=workspace._auth_object,
                                                 subscription_id=workspace.subscription_id,
                                                 resource_group=workspace.resource_group,
                                                 workspace_name=workspace.name,
                                                 project_name=run_name,
                                                 workspace_id=workspace._workspace_id)
        return project_context

    @staticmethod
    def _get_service_address(service, workspace, run_name):
        project_context = HyperDriveConfig._get_project_context(workspace, run_name)
        service_address = get_service_url(project_context.get_auth(),
                                          project_context.get_workspace_uri_path(),
                                          workspace._workspace_id,
                                          service_name=service)
        return service_address

    @staticmethod
    def _get_runconfig_from_run_dto(run_dto):
        hyperparameter_sampling = _sampling_from_dict(json.loads(run_dto.tags['generator_config']))
        primary_metric_config = json.loads(run_dto.tags["primary_metric_config"])
        primary_metric_name = primary_metric_config["name"]
        primary_metric_goal = PrimaryMetricGoal.from_str(primary_metric_config["goal"])
        max_total_runs = int(run_dto.tags["max_total_jobs"])
        max_concurrent_runs = int(run_dto.tags["max_concurrent_jobs"])
        max_duration_minutes = int(run_dto.tags["max_duration_minutes"])
        policy = _policy_from_dict(json.loads(run_dto.tags['policy_config']))

        hyperdrive_config = HyperDriveConfig(hyperparameter_sampling=hyperparameter_sampling,
                                             primary_metric_name=primary_metric_name,
                                             primary_metric_goal=primary_metric_goal,
                                             max_total_runs=max_total_runs,
                                             max_concurrent_runs=max_concurrent_runs,
                                             max_duration_minutes=max_duration_minutes,
                                             policy=policy,
                                             run_config=ScriptRunConfig('.'))

        hyperdrive_config._platform_config = HyperDriveConfig._get_platform_config_from_run_dto(run_dto)
        hyperdrive_config._is_cloud_hydrate = True
        return hyperdrive_config

    @staticmethod
    def _get_platform_config_from_run_dto(run_dto):
        return json.loads(run_dto.tags['platform_config'])

    def _get_platform_config(self, workspace, run_name):
        """Return `dict` containing platform config definition.

        Platform config contains the AML config information about the execution service.
        """
        if self._platform_config is not None:
            return self._platform_config

        if self.estimator is not None:
            run_config = get_run_config_from_script_run(self.estimator._get_script_run_config())
        elif self.run_config is not None:
            run_config = get_run_config_from_script_run(self.run_config)
        else:
            raise TrainingException("Invalid HyperDriveConfig object. "
                                    "The estimator, run_config and platform config are missing.")

        run_config = self._remove_duplicate_arguments(run_config,
                                                      self._generator_config,
                                                      self.estimator is not None)

        project_context = self._get_project_context(workspace, run_name)
        service_address = self._get_service_address("experimentation", workspace, run_name)

        if run_config.target == "amlcompute":
            self._set_amlcompute_runconfig_properties(run_config)

        run_config_serialized = _serialize_run_config_to_dict(run_config)
        try:
            # Conda dependencies are being serialized into a string representation of
            # ordereddict by autorest. Convert to dict here so that it is properly
            # serialized.
            conda_dependencies = run_config_serialized['environment']['python']['condaDependencies']
            run_config_serialized['environment']['python']['condaDependencies'] = \
                json.loads(json.dumps(conda_dependencies))
        except KeyError:
            pass

        self._platform_config = \
            {
                "ServiceAddress": service_address,
                # FIXME: remove this fix once hyperdrive code updates ES URL creation
                # project_context.get_experiment_uri_path() gives /subscriptionid/id_value
                # where as hyperdrive expects subscriptionid/id_value
                # "ServiceArmScope": project_context.get_experiment_uri_path(),
                "ServiceArmScope": project_context.get_experiment_uri_path()[1:],
                "SubscriptionId": workspace.subscription_id,
                "ResourceGroupName": workspace.resource_group,
                "WorkspaceName": workspace.name,
                "ExperimentName": run_name,
                "Definition": {
                    "Overrides": run_config_serialized,
                    "TargetDetails": None
                }
            }
        return self._platform_config

    @staticmethod
    def _remove_duplicate_arguments(run_config, generator_config, is_estimator=True):
        """Remove duplicate arguments from the run_config.

        If HyperDrive parameter space definition has the same script parameter as the run_config,
        remove the script parameter from the run_config. If both have the same parameter, HyperDrive
        parameter space will take precedence over the run_config script parameters.
        """
        warning = False
        run_config_copy = copy.deepcopy(run_config)
        run_config_args = convert_list_to_dict(run_config.arguments)
        input_params = copy.deepcopy(run_config_args).keys() if run_config_args else []
        parameter_space = [item.lstrip("-") for item in generator_config["parameter_space"].keys()]
        duplicate_params = []

        if is_estimator:
            for param in input_params:
                # Add lstrip: The run_config script param input expects the -- to be specified for script_params.
                # In HyperDrive, parameter space, user doesn't specify hyphens in the beginning of the parameter.
                if param.lstrip("-") in parameter_space:
                    run_config_args.pop(param)
                    warning = True
                    duplicate_params.append(param)
        else:
            for param_idx in range(len(input_params)):
                if '-n' in run_config_args:
                    notebook_args = json.loads(run_config_args['-n'])
                    for param in copy.deepcopy(notebook_args).keys() if notebook_args else []:
                        if param.lstrip("-") in parameter_space:
                            notebook_args.pop(param)
                            warning = True
                            duplicate_params.append(param)
                    run_config_args['-n'] = json.dumps(notebook_args)
                    break

        if warning:
            warnings.formatwarning = _simple_warning
            warnings.warn("The same input parameter(s) are specified in estimator/run_config script params "
                          "and HyperDrive parameter space. HyperDrive parameter space definition will override "
                          "these duplicate entries. "
                          "{} is the list of overridden parameter(s).".format(duplicate_params))
            run_config_copy.arguments = _get_arguments(run_config_args)

        return run_config_copy

    def _set_amlcompute_runconfig_properties(self, run_config):
        # A new amlcompute cluster with this name will be created for this HyperDrive run.
        run_config.amlcompute._name = str(uuid.uuid4())
        # All the child runs will use the same cluster.
        # HyperDrive service will delete the cluster once the parent run reaches a terminal state.
        run_config.amlcompute._retain_cluster = True
        run_config.amlcompute._cluster_max_node_count = run_config.node_count * self._max_concurrent_runs
        warnings.formatwarning = _simple_warning
        warnings.warn("A AML compute with {} node count will be created for this HyperDriveRun. "
                      "Please consider modifying max_concurrent_runs if this will exceed the "
                      "quota on the Azure subscription.".format(run_config.amlcompute._cluster_max_node_count))


class HyperDriveRunConfig(HyperDriveConfig):
    """Configuration that defines a HyperDrive run.

    This includes information about parameter space sampling, termination policy,
    primary metric, estimator and the compute target to execute the experiment runs on.

    :param estimator: An estimator that will be called with sampled hyper parameters.
    :type estimator: azureml.train.estimator.MMLBaseEstimator
    :param hyperparameter_sampling: The hyperparameter sampling space.
    :type hyperparameter_sampling: azureml.train.hyperdrive.HyperParameterSampling
    :param policy: The early termination policy to use. If None - the default,
                   no early termination policy will be used.
                   The MedianTerminationPolicy with delay_evaluation of 5
                   is a good termination policy to start with. These are conservative settings,
                   that can provide 25%-35% savings with no loss on primary metric (based on our evaluation data).
    :type policy: azureml.train.hyperdrive.EarlyTerminationPolicy
    :param primary_metric_name: The name of the primary metric reported by the experiment runs.
    :type primary_metric_name: str
    :param primary_metric_goal: One of maximize / minimize.
                                It determines if the primary metric has to be
                                minimized/maximized in the experiment runs' evaluation.
    :type primary_metric_goal: azureml.train.hyperdrive.PrimaryMetricGoal
    :param max_total_runs: Maximum number of runs. This is the upper bound; there may
                           be fewer runs when the sample space is smaller than this value.
    :type max_total_runs: int
    :param max_concurrent_runs: Maximum number of runs to run concurrently. If None, all runs are launched in parallel.
    :type max_concurrent_runs: int
    :param max_duration_minutes: Maximum duration of the run. Once this time is exceeded, the run is cancelled.
    :type max_duration_minutes: int
    """

    def __new__(cls,
                estimator,
                hyperparameter_sampling,
                primary_metric_name, primary_metric_goal,
                max_total_runs,
                max_concurrent_runs=None,
                max_duration_minutes=MAX_DURATION_MINUTES,
                policy=None
                ):
        """Initialize the HyperDriveRunConfig. This class is deprecated, please use HyperDriveConfig class."""
        warnings.formatwarning = _simple_warning
        warnings.warn("HyperDriveRunConfig is deprecated. Please use the new HyperDriveConfig class.")

        return HyperDriveConfig(hyperparameter_sampling=hyperparameter_sampling,
                                primary_metric_name=primary_metric_name,
                                primary_metric_goal=primary_metric_goal,
                                max_total_runs=max_total_runs,
                                max_concurrent_runs=max_concurrent_runs,
                                max_duration_minutes=max_duration_minutes,
                                policy=policy,
                                estimator=estimator)


def _simple_warning(message, category, filename, lineno, file=None, line=None):
    """Override detailed stack trace warning with just the message."""
    return str(message) + '\n'
