# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for handling SDK dependencies required during Ensemble iterations."""
import os

from azureml import _async
from azureml.core import Run
from azureml.exceptions import AzureMLException

from azureml.automl.core import ensemble_base
from . import _logging
from ._azureautomlsettings import AzureAutoMLSettings


class EnsembleHelper(object):
    """
    Helper class for ensembling previous AutoML iterations.

    This helper class is used for handling SDK dependencies used during Ensemble iterations (like model downloading)
    """

    DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC = 5 * 60  # 5 minutes

    def __init__(self,
                 automl_settings: AzureAutoMLSettings,
                 ensemble_run_id: str,
                 experiment_name: str,
                 workspace_name: str,
                 subscription_id: str,
                 resource_group_name: str):
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        Arguments:
            automl_settings -- The settings for this current experiment
            ensemble_run_id -- The id of the current ensembling run
            experiment_name -- The name of the current Azure ML experiment
            workspace_name --  The name of the current Azure ML workspace where the experiment is run
            subscription_id --  The id of the current Azure ML subscription where the experiment is run
            resource_group_name --  The name of the current Azure resource group
        """
        # input validation
        if automl_settings is None:
            raise ValueError("automl_settings parameter should not be None")

        if ensemble_run_id is None:
            raise ValueError("ensemble_run_id parameter should not be None")

        if experiment_name is None:
            raise ValueError("experiment_name parameter should not be None")

        if subscription_id is None:
            raise ValueError("subscription_id parameter should not be None")

        if resource_group_name is None:
            raise ValueError("resource_group_name parameter should not be None")

        if workspace_name is None:
            raise ValueError("workspace_name parameter should not be None")

        self._automl_settings = automl_settings
        self._ensemble_run_id = ensemble_run_id
        self._experiment_name = experiment_name
        self._subscription_id = subscription_id
        self._resource_group_name = resource_group_name
        self._workspace_name = workspace_name

        parent_run_id_length = self._ensemble_run_id.rindex("_")
        self._parent_run_id = self._ensemble_run_id[0:parent_run_id_length]

        # for potentially large models, we should allow users to override this timeout
        if hasattr(self._automl_settings, "ensemble_download_models_timeout_sec"):
            # TODO: Can this be converted into a real attribute?
            self._download_models_timeout_sec = \
                self._automl_settings.ensemble_download_models_timeout_sec  # type: ignore
        else:
            self._download_models_timeout_sec = self.DEFAULT_DOWNLOAD_MODELS_TIMEOUT_IN_SEC

    def download_fitted_models_for_child_runs(self, logger, child_runs, model_remote_path):
        """Override the base implementation for downloading the fitted pipelines in an async manner.

        :param logger -- logger instance
        :param child_runs -- collection of child runs for which we need to download the pipelines
        :param model_remote_path -- the remote path where we're downloading the pipelines from
        """
        with _async.WorkerPool() as worker_pool:
            task_queue = _async.TaskQueue(worker_pool=worker_pool,
                                          _ident="download_fitted_models",
                                          _parent_logger=logger)
            index = 0
            tasks = []
            for run in child_runs:
                task = task_queue.add(ensemble_base.EnsembleBase._download_model, run, index, model_remote_path)
                tasks.append(task)
                index += 1
            try:
                task_queue.flush(source=task_queue.identity, timeout_seconds=self._download_models_timeout_sec)
            except AzureMLException as e:
                msg = "Failed to download all {} the models within {} seconds due to exception {}."
                msg += "Proceeding with only {} models"
                logger.warning(msg.format(len(tasks),
                                          self._download_models_timeout_sec,
                                          e,
                                          len(list(task_queue.results))))
            return [task.wait() for task in tasks if task.done()]

    def get_ensemble_and_parent_run(self):
        """Return a tuple (ensemble_run_instance, parent_run_instance)."""
        # we'll instantiate the current run from the environment variables
        ensemble_run = Run.get_context()
        parent_run = Run(ensemble_run.experiment, self._parent_run_id)

        return ensemble_run, parent_run

    def get_logger(self):
        """Return a logger instance."""
        if (not os.path.exists(self._automl_settings.debug_log)):
            logger = _logging.get_logger("ensemble.log", self._automl_settings.verbosity, self._automl_settings)
        else:
            logger = _logging.get_logger(
                self._automl_settings.debug_log, self._automl_settings.verbosity, self._automl_settings)

        logger.update_default_properties({
            "parent_run_id": self._parent_run_id,
            "child_run_id": self._ensemble_run_id
        })

        return logger
