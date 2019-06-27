# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Abstract MultiClass target encoder."""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
from automl.client.core.common.constants import Tasks
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from ..automltransformer import AutoMLTransformer


class AbstractMultiClassTargetEncoder(AutoMLTransformer, ABC):
    """Generic count based target encoder."""

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 task: str = Tasks.CLASSIFICATION,
                 classes: np.ndarray = None) -> None:
        """Construct the target encoder. Outputs len(classes) - 1 number of columns.

        :param logger: The logger.
        :param task: Task type for target (Regression or Classification)
        :param classes: Number of targets to encode.
        """
        super().__init__()
        self._init_logger(logger)

        self._categorical_mappings = {}  # type: Dict[str, Dict[str, Dict[str, Any]]]
        self.target_agg = {}  # type: Dict[str, Dict[str, float]]
        self._prior_map = {}  # type: Dict[str, float]
        self._task = task
        self._classes = classes

    @function_debug_log_wrapped
    def fit(self, X: pd.Series, y: pd.Series) -> "AbstractMultiClassTargetEncoder":
        """
        Get map for data.

        :param X: Data to be transformed.
        :param y: Target data.
        :return: Computed categorical map using y as target.
        """
        class_mapping = {}  # type: Dict[str, Dict[str, Any]]
        class_prior = {}  # type: Dict[str, float]
        if self._task == Tasks.CLASSIFICATION:
            for curr_class in self._classes:
                y_ova = (y == curr_class).astype(int)
                map_curr_class, prior_curr_class = self.get_map_for_target(X, y_ova)
                class_mapping[str(curr_class)] = map_curr_class
                class_prior[str(curr_class)] = prior_curr_class
        else:
            map_curr_class, prior_curr_class = self.get_map_for_target(X, y)
            class_mapping[Tasks.REGRESSION] = map_curr_class
            class_prior[Tasks.REGRESSION] = prior_curr_class

        self._categorical_mappings = class_mapping
        self._prior_map = class_prior

        return self

    @function_debug_log_wrapped
    def transform(self, X: pd.Series) -> np.ndarray:
        """
        Apply transform on X data using mappings passed.

        :param X: Data to be transformed.
        :return: Transformed data.
        """
        transformed_array = np.empty([X.shape[0], self._classes.shape[0]])
        curr_col_index = 0
        for curr_class in self._classes:
            curr_class_mapping = self._categorical_mappings[str(curr_class)]
            curr_class_mean = self._prior_map[str(curr_class)]
            transformed_array[:, curr_col_index] = self.transform_target_class(X, curr_class_mapping, curr_class_mean)
            curr_col_index += 1
        return transformed_array

    @abstractmethod
    def transform_target_class(self, X: pd.Series, curr_class_mapping: Dict[str, Dict[str, float]],
                               default_value: float) -> np.ndarray:
        """
        Return target encoded data for current input data.

        :param X: The data to transform.
        :param curr_class_mapping: Mappings used to map current class
        :param default_value:
        :return: Target encoded values from current X column and curr_class maps.
        """
        raise NotImplementedError("Must be overridden by the implementation.")

    @abstractmethod
    def get_map_for_target(self, X, y):
        """
        Get map for data.

        :param X: Data to be transformed.
        :param y: Target data.
        :return: Computed categorical map using y as target.
        """
        raise NotImplementedError("Must be overridden by the implementation.")
