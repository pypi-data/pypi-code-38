# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The HyperDrive Run object."""

from azureml.core import Run
from azureml.exceptions import TrainingException
# noinspection PyProtectedMember
from azureml._base_sdk_common.service_discovery import get_service_url

import azureml.train.restclients.hyperdrive as HyperDriveClient
from azureml.train.restclients.hyperdrive.models import ErrorResponseException
from azureml.train.hyperdrive import HyperDriveConfig, PrimaryMetricGoal


class HyperDriveRun(Run):
    """HyperDriveRun contains the details of a submitted HyperDrive experiment.

    This class can be used to manage, check status, and retrieve run details for the HyperDrive run and each of
    the generated child runs.

    :param experiment: The Experiment for the HyperDrive run.
    :type experiment: azureml.core.experiment.Experiment
    :param run_id: The HyperDrive run id.
    :type run_id: str
    :param run_config: The RunConfiguration used by the estimator in HyperDriveConfig.
    :type run_config: azureml.core.runconfig.RunConfiguration
    :param hyperdrive_config: A `HyperDriveConfig` that defines the configuration for this HyperDrive run.
    :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig

    """

    RUN_TYPE = 'hyperdrive'
    HYPER_DRIVE_RUN_USER_AGENT = "sdk_run_hyper_drive"

    def __init__(self, experiment, run_id, hyperdrive_config=None):
        """Initialize a HyperDrive run.

        :param experiment: The Experiment for the HyperDrive run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_id: The Hyperdrive run id.
        :type run_id: str
        :param hyperdrive_config: A `HyperDriveConfig` that defines the configuration for this HyperDrive run.
        If None, we assume that the run already exists and will try to hydrate from the cloud.
        :type hyperdrive_config: azureml.train.hyperdrive.HyperDriveConfig
        """
        if not isinstance(run_id, str):
            raise TypeError("RunId must be a string")

        super().__init__(experiment=experiment, run_id=run_id,
                         _user_agent=HyperDriveRun.HYPER_DRIVE_RUN_USER_AGENT)
        if hyperdrive_config is None:
            self._hyperdrive_config = HyperDriveConfig._get_runconfig_from_run_dto(self._client.run_dto)
        else:
            self._hyperdrive_config = hyperdrive_config

        self._output_logs_pattern = "azureml-logs/hyperdrive.txt"

    @property
    def hyperdrive_config(self):
        """Return the hyperdrive run config.

        :return: The hyperdrive run config.
        :rtype: azureml.train.hyperdrive.HyperDriveConfig
        """
        return self._hyperdrive_config

    def cancel(self):
        """Return True if the HyperDrive run was cancelled successfully.

        :return: Whether or not the run was cancelled successfully.
        :rtype: bool
        """
        project_context = HyperDriveConfig._get_project_context(self.experiment.workspace,
                                                                self.experiment.name)
        project_auth = self.experiment.workspace._auth_object
        run_history_host = get_service_url(project_auth, project_context.get_workspace_uri_path(),
                                           self.experiment.workspace._workspace_id)

        host_url = self.hyperdrive_config._get_host_url(self.experiment.workspace, self.experiment.name)
        try:
            # FIXME: remove this fix once hyperdrive code updates ES URL creation
            # project_context.get_experiment_uri_path() gives /subscriptionid/id_value
            # where as hyperdrive expects subscriptionid/id_value
            # project_context.get_experiment_uri_path()
            experiment_uri_path = project_context.get_experiment_uri_path()[1:]
            hyperdrive_client = HyperDriveClient.RestClient(experiment_uri_path, project_auth, host_url)

            cancel_hyperdrive_run_result = hyperdrive_client.cancel_experiment(self._run_id, run_history_host)
            return cancel_hyperdrive_run_result
        except ErrorResponseException as e:
            raise TrainingException("Exception occurred while cancelling HyperDrive run. {}".format(str(e)),
                                    inner_exception=e) from None

    def get_best_run_by_primary_metric(self, include_failed=False, include_canceled=False):
        """Find and return the Run instance that corresponds to the best performing run amongst all the completed runs.

        The best performing run is identified solely based on the primary metric parameter specified in the
        HyperDriveConfig. The PrimaryMetricGoal governs whether the minimum or maximum of the primary metric is
        used. To do a more detailed analysis of all the ExperimentRun metrics launched by this HyperDriveRun, use
        get_metrics. If all of the Runs launched by this HyperDrive run reached the same best metric, only one of the
        runs is returned.

        :param include_failed: Include failed run or not.
        :type include_failed: bool
        :param include_canceled: Include canceled run or not.
        :type include_canceled: bool
        :return: The best Run, or None if no child has the primary metric.
        :rtype: azureml.core.run.Run
        """
        best_run_id = self._get_best_run_id_by_primary_metric(
            include_failed=include_failed, include_canceled=include_canceled)
        if best_run_id:
            return Run(self.experiment, best_run_id)
        else:
            return None

    def get_hyperparameters(self):
        """Return the hyperparameters for all the child runs that were launched by this HyperDriveRun.

        :return: Hyperparameters for all the child runs. It is a dictionary with run_id as key.
        :rtype: dict
        """
        result = {}
        # Hyperparameters of child runs are stored in tags in the format of
        # <parent_run_id>_<index>: <json_string_of_parameter_dictionary>
        prefix = self.id + "_"
        prefix_length = len(prefix)
        for tag_name, tag_value in self.tags.items():
            if tag_name.startswith(prefix) and tag_name[prefix_length:].isdigit():
                result[tag_name] = tag_value

        return result

    def get_children_sorted_by_primary_metric(self, top=0, reverse=False, discard_no_metric=False):
        """Return a list of children sorted by their best primary metric.

        The sorting is done according to the primary metric and its goal: if it is maximize, then the children
        are returned in descending order of their best primary metric. If reverse is True, the order is reversed.

        Each child in the result has run id, hyperparameters, best primary metric value and status.

        Children without primary metric are discarded when discard_no_metric is True. Otherwise, they are appended
        to the list behind other children with primary metric. Note that the reverse option has no impact on them.

        :param top: Number of top children to be returned. If it is 0, all children will be returned.
        :type top: int
        :param reverse: If it is True, the order will be reversed. It only impacts children with primary metric.
        :type reverse: bool
        :param discard_no_metric: If it is False, children without primary metric will be appended to the list.
        :type discard_no_metric: bool
        :return: List of dictionaries with run id, hyperparameters, best primary metric and status
        :rtype: list
        """
        assert isinstance(top, int) and top >= 0, "Value of parameter top should be 0 or a positive integer"
        assert isinstance(reverse, bool), "Type of parameter reverse should be bool"
        assert isinstance(discard_no_metric, bool), "Type of parameter discard_no_metric should be bool"

        hyperparameters = self.get_hyperparameters()

        run_metrics = self.get_metrics()

        metric_name = self.hyperdrive_config._primary_metric_config["name"]
        metric_goal = self.hyperdrive_config._primary_metric_config["goal"]
        metric_func = max if metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower() else min

        children = []
        no_metrics = []
        for run in self.get_children():
            run_id = run.id
            best_metric = None
            if run_metrics and run_id in run_metrics and run_metrics[run_id] and metric_name in run_metrics[run_id]:
                metrics = run_metrics[run_id][metric_name]
                best_metric = metric_func(metrics) if isinstance(metrics, list) else metrics
            child = {"run_id": run_id,
                     "hyperparameters": hyperparameters[run_id] if run_id in hyperparameters else None,
                     "best_primary_metric": best_metric,
                     "status": run.get_status()}
            if best_metric is not None:
                children.append(child)
            elif not discard_no_metric:
                no_metrics.append(child)

        is_maximize = (metric_goal == PrimaryMetricGoal.MAXIMIZE.value.lower())
        sorted_children = sorted(children, key=lambda i: i['best_primary_metric'], reverse=(is_maximize != reverse))

        if no_metrics:
            sorted_children = sorted_children + no_metrics

        return sorted_children if top == 0 else sorted_children[:top]

    def _get_best_run_id_by_primary_metric(self, include_failed=False, include_canceled=False):
        """Return the run id of the instance that corresponds to the best performing child run.

        :param include_failed: Include failed run or not.
        :type include_failed: bool
        :param include_canceled: Include canceled run or not.
        :type include_canceled: bool
        :return: ID of the best run, or None if no child has the primary metric.
        :rtype: str
        """
        children = self.get_children_sorted_by_primary_metric(discard_no_metric=True)
        for child in children:
            if (include_failed and child["status"] == "Failed") \
               or (include_canceled and child["status"] == "Canceled") \
               or (child["status"] not in ["Failed", "Canceled"]):
                return child["run_id"]

        return None

    def get_metrics(self):
        """Return the metrics from all the runs that were launched by this HyperDriveRun.

        :return: The metrics for all the children of this run.
        :rtype: dict
        """
        child_run_ids = [run.id for run in self.get_children()]
        # noinspection PyProtectedMember
        return self._client.get_metrics(run_ids=child_run_ids, use_batch=True)

    # get_diagnostics looks for a zip in AFS based on run_id.
    # For HyperDrive runs, there is no entry in AFS.
    def get_diagnostics(self):
        """Do not use. The get_diagnostics method is not supported for the HyperDriveRun subclass."""
        raise NotImplementedError("Get diagnostics is unsupported for HyperDrive run.")

    def fail(self):
        """Do not use. The fail method is not supported for the HyperDriveRun subclass."""
        raise NotImplementedError("Fail is unsupported for HyperDrive run.")

    @staticmethod
    def _from_run_dto(experiment, run_dto):
        """Return HyperDrive run from a dto.

        :param experiment: The experiment that contains this run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_dto: The HyperDrive run dto as received from the cloud.
        :type run_dto: RunDto
        :return: The HyperDriveRun object.
        :rtype: HyperDriveRun
        """
        hyperdrive_config = HyperDriveConfig._get_runconfig_from_run_dto(run_dto)
        return HyperDriveRun(experiment, run_dto.run_id, hyperdrive_config)
