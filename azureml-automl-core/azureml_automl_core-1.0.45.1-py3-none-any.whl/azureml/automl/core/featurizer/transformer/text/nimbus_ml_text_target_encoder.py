# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic transformer for NimbusML based classifier models."""
from typing import Any, Optional, List
from logging import Logger

import numpy as np

from automl.client.core.common.types import DataSingleColumnInputType, DataInputType
from azureml.automl.core.column_purpose_detection.columnpurpose_detector import StatsAndColumnPurposeType
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common import memory_utilities
from ..automltransformer import AutoMLTransformer


class NimbusMLTextTargetEncoder(AutoMLTransformer):
    """Generic class for NimbusML based classifier pipelines."""

    def __init__(self, featurizer: Any,
                 learner: Any,
                 logger: Optional[Logger] = None) -> None:
        """
        Construct NimbusML based text target encoder.

        :param featurizer: Featurizer to be used.
        :type Any: Ideally should be of type nimbusml.internal.core.base_pipeline_item.BasePipelineItem
        :param learner: Learner to be used for training.
        :type Any: Ideally should be of type nimbusml.internal.core.base_pipeline_item.BasePipelineItem
        :param logger: Logger to be injected for usage in this class.
        """
        from nimbusml import Pipeline as NimbusMLPipeline
        from nimbusml.multiclass import OneVsRestClassifier
        from nimbusml.preprocessing.schema import ColumnDropper
        from nimbusml.internal.core.base_pipeline_item import BasePipelineItem

        if not isinstance(featurizer, BasePipelineItem):
            raise TypeError(
                "featurizer: Expecting type nimbusml.internal.core.base_pipeline_item.BasePipelineItem.")

        if not isinstance(learner, BasePipelineItem):
            raise TypeError(
                "learner: Expecting type nimbusml.internal.core.base_pipeline_item.BasePipelineItem.")

        super().__init__()
        self._init_logger(logger)
        self._featurizer = featurizer
        self._learner = learner
        self.pipeline = NimbusMLPipeline(
            [self._featurizer, OneVsRestClassifier(self._learner, use_probabilities=True)])
        self._pipeline_details = "{} Featurizer-'{}' Learner- {}".format(__name__,
                                                                         type(
                                                                             self._featurizer).__name__,
                                                                         type(self._learner).__name__)
        self._logger_wrapper("info", self._pipeline_details)
        self.column_dropper = ColumnDropper(columns=['PredictedLabel'])
        self._model = None

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(NimbusMLTextTargetEncoder, self)._to_dict()
        dct['id'] = "averaged_perceptron_text_target_encoder"
        dct['type'] = 'text'

        return dct

    @function_debug_log_wrapped
    def fit(self, X: DataInputType, y: DataSingleColumnInputType = None) -> "NimbusMLTextTargetEncoder":
        """
        Nimbusml based classifier transform to learn conditional probablities for textual data.

        :param x: The data to transform.
        :type x: DataInputType
        :param y: Target values.
        :type y: DataSingleColumnInputType
        :return: The instance object: self.
        """
        try:
            self._model = self.pipeline.fit(X, y)
            return self
        except Exception as e:
            self._logger_wrapper(
                "error", "{}: Failed during fit call - {}".format(self._pipeline_details, e))
            raise

    @function_debug_log_wrapped
    def transform(self, X: DataInputType) -> DataInputType:
        """
        Transform data x.

        :param x: The data to transform.
        :type x: DataInputType
        :return: Prediction probability values from NimbusML based classifier model.
        """
        try:
            return self.predict_proba(X)
        except Exception as e:
            self._logger_wrapper(
                "error", "{}: Failed during transform call- {}".format(self._pipeline_details, e))
            raise

    @function_debug_log_wrapped
    def predict_proba(self, X: DataInputType) -> DataInputType:
        """
        Predict probability for the input text data.

        :param x: The data to predict.
        :type x: DataInputType
        """
        try:
            if self._model is None:
                raise Exception("No model found. Call 'fit' method first.")
            scores = self._model.predict(X)
            # drop column
            output = self.column_dropper.fit_transform(scores)
            return output
        except Exception as e:
            self._logger_wrapper(
                "error", "{}: Failed during predict_proba call- {}".format(self._pipeline_details, e))
            raise

    @function_debug_log_wrapped
    def predict(self, X: DataInputType) -> DataInputType:
        """
        Predict probability for the input text data.

        :param x: The data to predict.
        :type x: DataInputType
        """
        return self.predict_proba(X)

    def get_model(self) -> Any:
        """
        Return inner NimbusML Pipeline.

        :return: NimbusML pipeline.
        """
        return self._model

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint estimate for this transformer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken.
        """
        num_rows = len(X)
        n_classes = len(np.unique(y))
        f_size = memory_utilities.get_data_memory_size(float)
        return num_rows * n_classes * f_size
