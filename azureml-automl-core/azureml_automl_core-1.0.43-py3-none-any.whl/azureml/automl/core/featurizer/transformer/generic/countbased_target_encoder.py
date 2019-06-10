# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic count based target encoder."""
import logging
from typing import Optional, Tuple, Dict

import numpy as np
import pandas as pd
from .abstract_multiclass_target_encoder import AbstractMultiClassTargetEncoder
from automl.client.core.common.constants import Tasks


class CountBasedTargetEncoder(AbstractMultiClassTargetEncoder):
    """Generic count based target encoder."""

    def __init__(self,
                 blending_param: float = 20,
                 smoothing_param: float = 10,
                 logger: Optional[logging.Logger] = None,
                 task: str = Tasks.CLASSIFICATION,
                 classes: np.ndarray = None) -> None:
        """Construct the target encoder. Outputs len(classes) - 1 number of columns.

        :param blending_param: Value for num of samples where smoothening applies
        :param smoothing_param: Parameter to control smoothening, higher value will lead to more regularization.
        :param logger: The logger.
        :param task: Task type for target (Regression or Classification)
        :param classes: Number of targets to encode.
        """
        super().__init__(logger, task, classes)
        self._blending_param = blending_param
        self._smoothing_param = smoothing_param

    def get_map_for_target(self, X: pd.Series, y: pd.Series) ->\
            Tuple[Dict[str, Dict[str, float]], Dict[str, float]]:
        """
        Get map for data.

        :param X: Data to be transformed.
        :param y: Target data.
        :return: Computed categorical map using y as target.
        """
        prior = y.mean()
        target_agg = y.groupby(X).agg(['sum', 'count'])

        # TODO make count for novels a configurable parameter
        # Remove novel categories, they can be represented by single value/bin
        target_agg = target_agg[target_agg['count'] > 1]
        target_agg['mean'] = target_agg['sum'] / target_agg['count']
        exponent = (target_agg["count"] - self._blending_param) / self._smoothing_param

        # computing a sigmoid for smoothing
        sigmoid = 1 / (1 + np.exp(-1 * exponent))
        custom_smoothing = prior * (1 - sigmoid) + target_agg['mean'] * sigmoid
        target_agg['smoothing'] = custom_smoothing

        return target_agg.to_dict(orient='index'), prior

    def transform_target_class(self, X: pd.Series, curr_class_mapping: Dict[str, Dict[str, float]],
                               default_value: float) -> np.ndarray:
        """
        Return target encoded data for current input data.

        :param X: The data to transform.
        :param curr_class_mapping:
        :param default_value:
        :return: Target encoded values from current X column and curr_class maps.
        """
        return X.apply(lambda x: curr_class_mapping.get(x, {'smoothing': default_value})['smoothing'])
