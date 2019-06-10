# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""

from typing import Optional, TextIO
import enum


class ExperimentStatus(enum.Enum):
    """Possible status codes for an Experiment."""

    DatasetEvaluation = 'DatasetEvaluation'
    FeaturesGeneration = 'FeaturesGeneration'
    DatasetCrossValidationSplit = 'DatasetCrossValidationSplit'
    DatasetFeaturization = 'DatasetFeaturization'
    DatasetFeaturizationCompleted = 'DatasetFeaturizationCompleted'
    ModelSelection = 'ModelSelection'

    def __str__(self) -> str:
        """Return the value of the enumeration."""
        return str(self.value)


class ExperimentObserver:
    """Observer pattern implementation for the states of an AutoML Experiment."""

    def __init__(self, file_handler: Optional[TextIO]) -> None:
        """Initialize an instance of this class."""
        self.file_handler = file_handler

    def report_status(self, status: ExperimentStatus, description: str) -> None:
        """Report the current status for an experiment."""
        try:
            if self.file_handler is not None:
                self.file_handler.write("Current status: {}. {}\n".format(status, description))
        except Exception as ex:
            print("Failed to report status due to {}".format(ex))


class NullExperimentObserver(ExperimentObserver):
    """Null pattern implementation for an ExperimentObserver."""

    def __init__(self) -> None:
        """Instantiate a new instance of this class."""
        super(NullExperimentObserver, self).__init__(None)

    def report_status(self, status: ExperimentStatus, description: str) -> None:
        """Report the current status for an experiment. Does nothing in this implementation."""
        pass
