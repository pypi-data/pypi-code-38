# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""
from typing import Optional, TextIO
from logging import Logger
from azureml.automl.core._experiment_observer import ExperimentObserver, ExperimentStatus
from azureml.core import Run


class AzureExperimentObserver(ExperimentObserver):
    """Observer pattern implementation for the states of an AutoML Experiment."""

    def __init__(self, run_instance: Run, console_logger: Optional[TextIO]=None,
                 file_logger: Optional[Logger]=None) -> None:
        """Initialize an instance of this class.

        :param run_instance: A Run object representing the current experiment.
        :param console_logger: The destination for sending the status output to.
        """
        super(AzureExperimentObserver, self).__init__(console_logger)
        self.run_instance = run_instance
        self._file_logger = file_logger

    def report_status(self, status: ExperimentStatus, description: str) -> None:
        """Report the current status for an experiment.

        :param status: An ExperimentStatus enum value representing current status.
        :param description: A description for the associated experiment status.
        """
        try:
            super(AzureExperimentObserver, self).report_status(status, description)
            tags = {"experiment_status": str(status), "experiment_status_descr": description}
            self.run_instance.set_tags(tags)
        except Exception as ex:
            if self._file_logger is not None:
                self._file_logger.warning("Error while updating experiment progress. {}".format(ex))
