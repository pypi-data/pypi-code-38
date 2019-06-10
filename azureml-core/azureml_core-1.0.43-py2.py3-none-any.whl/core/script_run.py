# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for handling and monitoring script runs associated with an Experiment object and individual run id."""

from __future__ import print_function
import os

from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration


class ScriptRun(Run):
    """An experiment run class to handle and monitor script runs associated with an Experiment and individual run id.

    .. remarks::

        The Azure Machine Learning SDK provides you with a series of interconnected classes, that are
        designed to help you train and compare machine learning models that are related by the shared
        problem that they are solving.

        An :class:`azureml.core.Experiment` acts as a logical container for these training runs. A
        :class:`azureml.core.RunConfiguration` object is used to codify the information necessary to
        submit a training run in an experiment. A :class:`azureml.core.ScriptRunConfig` object is a
        helper class that packages the RunConfiguration object with an execution script for training;
        see the python code example in the documentation for :class:`azureml.core.RunConfiguration`
        for an example of a ScriptRunConfig object in action.

        A ScriptRunConfig object is used to submit a training run as part of an Experiment
        When a training run is submitted using a ScriptRunConfig object, the submit method returns an
        object of type ScriptRun.

        A ScriptRun object gives you programmatic access to information about the associated training
        run. Some examples include retrieving the logs corresponding to a run, canceling a run if it's
        still in progress, cleaning up the artifacts of a completed run, and waiting for completion of
        a run currently in progress.


    :param experiment: The experiment object
    :type experiment: azureml.core.experiment.Experiment
    :param run_id: Run id.
    :type run_id: str
    :param directory: The source directory
    :type directory: str
    :param _run_config:
    :type _run_config: azureml.core.runconfig.RunConfiguration
    :param kwargs:
    :type kwargs: dict
    """

    RUN_TYPE = "azureml.scriptrun"

    def __init__(self, experiment, run_id, directory=None, _run_config=None, **kwargs):
        """Class ScriptRun constructor."""
        from azureml._project.project import Project
        super(ScriptRun, self).__init__(experiment, run_id, **kwargs)
        project_object = Project(experiment=experiment, directory=directory, _disable_service_check=True)
        if _run_config is not None:
            self._run_config_object = RunConfiguration._get_run_config_object(directory, _run_config)
        else:
            self._run_config_object = None
        self._project_object = project_object
        self._output_logs_pattern = "azureml-logs/[\d]{2}.+\.txt"

    @property
    def _run_config(self):
        if self._run_config_object is None:
            # Get it from experiment in the cloud.
            run_details = self.get_details()
            self._run_config_object = RunConfiguration._get_runconfig_using_run_details(run_details)
        return self._run_config_object

    def cancel(self):
        """Cancel the ongoing run."""
        target = self._run_config.target
        if target == "local":
            self._cancel_local()
        else:
            super(ScriptRun, self).cancel()

    def _cancel_local(self):
        project_temp_dir = _get_project_temporary_directory(self._run_id)

        from azureml._base_sdk_common.common import normalize_windows_paths
        killfile = normalize_windows_paths(os.path.join(project_temp_dir, "azureml-setup", "killfile"))
        if not os.path.exists(killfile):
            with open(killfile, 'w+') as f:
                f.write(self._run_id)

        self._client.run.post_event_canceled()

    @staticmethod
    def _from_run_dto(experiment, run_dto):
        """Return run from dto.

        :param experiment:
        :type experiment: azureml.core.experiment.Experiment
        :param run_dto:
        :type run_dto: object
        :return: Returns the run
        :rtype: ScriptRun
        """
        return ScriptRun(experiment, run_dto.run_id, _run_dto=run_dto)


def _get_project_temporary_directory(run_id):
    import tempfile
    azureml_temp_dir = os.path.join(tempfile.gettempdir(), "azureml_runs")
    if not os.path.isdir(azureml_temp_dir):
        os.mkdir(azureml_temp_dir)

    project_temp_dir = os.path.join(azureml_temp_dir, run_id)
    return project_temp_dir
