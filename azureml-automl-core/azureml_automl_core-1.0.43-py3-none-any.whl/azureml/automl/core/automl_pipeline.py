# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper class for AutoML pipeline objects."""
from typing import Optional
from automl.client.core.common import constants
from .automl_run_context import AutoMLAbstractRunContext


class AutoMLPipeline:
    """Used to hold pipeline responses."""

    def __init__(self,
                 run_context: AutoMLAbstractRunContext,
                 pipeline_script: str,
                 pipeline_id: str,
                 training_size: Optional[float] = None,
                 predicted_time: Optional[float] = None) -> None:
        """
        Create an AutoMLPipeline object that wraps pipeline metadata.

        :param run_context: the child run context for this pipeline
        :param pipeline_script: a string representing the pipeline to be run
        :param pipeline_id: a hash string used to identify this pipeline
        :param training_size: a float in the range (0.0, 1.0] describing what portion of the data should be used
            during training. If None provided, the full dataset is used.
        :param predicted_time: a float that describes the expected number of seconds needed to run this pipeline.
        """
        self.run_context = run_context
        self.pipeline_id = pipeline_id
        self.pipeline_script = pipeline_script
        self.training_size = training_size or 1.0
        self.predicted_time = predicted_time or 0.0

        if self.training_size <= 0 or self.training_size > 1:
            raise ValueError('Training size must be in the range (0.0, 1.0].')

        if self.predicted_time < 0:
            raise ValueError('Predicted time must be greater than or equal to 0.')

    @property
    def is_ensemble_pipeline(self) -> bool:
        """
        Check whether this pipeline is an ensemble pipeline.

        :return: True if this pipeline is an ensemble pipeline, false otherwise
        """
        return self.pipeline_id in constants.EnsembleConstants.ENSEMBLE_PIPELINE_IDS

    @property
    def training_percent(self) -> float:
        """
        Return the percentage of data that will be used during training.

        :return: a percentage value from 0 to 100 inclusive
        """
        return self.training_size * 100
