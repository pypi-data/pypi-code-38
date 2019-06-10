# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating stack ensembles from previous Automated Machine Learning iterations."""
from azureml.automl.core import stack_ensemble_base
from . import ensemble_helper
from ._azureautomlsettings import AzureAutoMLSettings


class StackEnsemble(stack_ensemble_base.StackEnsembleBase):
    """
    Class for stack ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    def __init__(self,
                 automl_settings: AzureAutoMLSettings,
                 ensemble_run_id: str,
                 experiment_name: str,
                 workspace_name: str,
                 subscription_id: str,
                 resource_group_name: str,
                 **kwargs: str):
        """Create a StackEnsemble pipeline out of a collection of already fitted pipelines.

        Arguments:
            automl_settings -- The settings for this current experiment
            ensemble_run_id -- The id of the current ensembling run
            experiment_name -- The name of the current Azure ML experiment
            workspace_name --  The name of the current Azure ML workspace where the experiment is run
            subscription_id --  The id of the current Azure ML subscription where the experiment is run
            resource_group_name --  The name of the current Azure resource group
        """
        super(StackEnsemble, self).__init__(automl_settings)
        self.helper = ensemble_helper.EnsembleHelper(
            self._automl_settings,
            ensemble_run_id,
            experiment_name,
            workspace_name,
            subscription_id,
            resource_group_name)

    def _download_fitted_models_for_child_runs(self, logger, child_runs, model_remote_path):
        """Override the base implementation for downloading the fitted pipelines in an async manner.

        :param logger -- logger instance
        :param child_runs -- collection of child runs for which we need to download the pipelines
        :param model_remote_path -- the remote path where we're downloading the pipelines from
        """
        return self.helper.download_fitted_models_for_child_runs(logger, child_runs, model_remote_path)

    def _get_ensemble_and_parent_run(self):
        return self.helper.get_ensemble_and_parent_run()

    def _get_logger(self):
        return self.helper.get_logger()
