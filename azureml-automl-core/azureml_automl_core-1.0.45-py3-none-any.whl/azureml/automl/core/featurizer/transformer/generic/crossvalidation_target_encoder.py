# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic cross validation target encoder."""
from typing import Any, Dict, Optional, List, Type
import logging

from sklearn.model_selection import KFold, StratifiedKFold
import numpy as np
import pandas as pd

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.types import DataSingleColumnInputType
from automl.client.core.common.constants import Tasks

from ...._engineered_feature_names import _TransformationFunctionNames, _OperatorNames
from ..automltransformer import AutoMLTransformer
from .countbased_target_encoder import CountBasedTargetEncoder
from .woe_target_encoder import WoEBasedTargetEncoder


class CrossValidationTargetEncoder(AutoMLTransformer):
    """Generic cross validation target encoder."""

    def __init__(self,
                 target_encoder_cls: Type[AutoMLTransformer],
                 logger: Optional[logging.Logger] = None,
                 task: str = Tasks.CLASSIFICATION,
                 num_folds: int = 5,
                 **kwargs: Any) -> None:
        """Construct the target encoder.

        :param blending_param: Value for num of samples where smoothening applies
        :param smoothing_param: Parameter to control smoothening, higher value will lead to more regularization.
        :param logger: The logger.
        :param num_folds: Number of folds to use in Cross Validation strategy.
        :param kwargs: kwargs to be passed to target_encoder.
        """
        super().__init__()
        self._init_logger(logger)

        if issubclass(target_encoder_cls, AutoMLTransformer):
            self.target_encoder_cls = target_encoder_cls
        else:
            self.target_encoder_cls = None

        self._target_encoder_folds = []  # type: List[AutoMLTransformer]
        self._fold_indices = []  # type: np.ndarray
        self._num_folds = num_folds
        self._target_encoder_full_fit = None  # type: Optional[AutoMLTransformer]
        self._num_classes = 0
        self._task = task
        self._te_params = kwargs
        self._te_params['task'] = task
        if issubclass(target_encoder_cls, CountBasedTargetEncoder):
            self._transformer_name = _TransformationFunctionNames.TargetEncoding
        elif issubclass(target_encoder_cls, WoEBasedTargetEncoder):
            self._transformer_name = _TransformationFunctionNames.WoETargetEncoding
        self._operator_name = None

    def _get_operator_name(self) -> Optional[str]:
        return self._operator_name

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(CrossValidationTargetEncoder, self)._to_dict()
        if self.target_encoder_cls is CountBasedTargetEncoder:
            dct['id'] = "cat_targetencoder"
        elif self.target_encoder_cls is WoEBasedTargetEncoder:
            dct['id'] = "woe_targetencoder"
        else:
            dct['id'] = None
        dct['type'] = 'categorical'
        dct['kwargs']['task'] = self._task
        dct['kwargs']['num_folds'] = self._num_folds

        return dct

    @function_debug_log_wrapped
    def fit(self, X: DataSingleColumnInputType, y: DataSingleColumnInputType) -> "CrossValidationTargetEncoder":
        """
        Instantiate and train on the input data.

        :param X: The data to transform.
        :param y: Target values.
        :return: The instance object: self.
        """
        if not isinstance(X, pd.Series):
            X = pd.Series(X)
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        if self._task == Tasks.CLASSIFICATION:
            # we need only n-1 classes
            classes = y.unique()[:-1]
        else:
            classes = np.array([Tasks.REGRESSION])
        self._te_params['classes'] = classes
        self._num_classes = classes.shape[0]

        self._generate_fold_indices(X)
        self._fit(X, y)
        return self

    @function_debug_log_wrapped
    def transform(self, X: DataSingleColumnInputType) -> np.ndarray:
        """
        Return target encoded data for current input data.

        :param X: The data to transform.
        :return: Target encoded values from current X column.
        """
        if not isinstance(X, pd.Series):
            X = pd.Series(X)

        # _fold_indices are precomputed while we fit the data. If folds are still present, we know that we have not
        # transformed data as yet. Folds will be cleaned up post transform

        if len(self._fold_indices) > 1:
            # KFold TE with holdout
            self._logger_wrapper('debug', 'Apply cv transform using folds ({}).'.format(len(self._fold_indices)))
            transformed_data = self._cv_transform(X)
        else:
            # TE without holdout
            self._logger_wrapper('debug', 'Apply cv transform on whole data')
            transformed_data = self._apply_transform(X)

        self._num_folds = 0
        self._fold_indices = []
        return transformed_data

    def _generate_fold_indices(self, X: pd.Series) -> None:
        """
        Generate indices for folds.

        :param X: Data for transform.
        """
        if self._num_folds > 1:
            try:
                skf = StratifiedKFold(n_splits=self._num_folds, shuffle=True, random_state=42)
                self._logger_wrapper('debug', 'Using stratified {} fold.'.format(self._num_folds))
                for train_index, test_index in skf.split(X, X):
                    self._fold_indices.append(test_index)
            except Exception as ex:
                if self._logger_wrapper:
                    self._logger_wrapper('debug', 'Error trying to perform StratifiedKFold split.'
                                                  ' Falling back to KFold. Exception: {}'.format(ex))

                self._fold_indices = []
                kf = KFold(n_splits=self._num_folds, shuffle=True, random_state=42)
                self._logger_wrapper('debug', 'Using {} fold .'.format(self._num_folds))
                for train_index, test_index in kf.split(X):
                    self._fold_indices.append(test_index)

    def _cv_transform(self, X: pd.Series) -> np.ndarray:
        """
        Transform using cross validation.

        :param X: Data to transform.
        :return: Transformed data
        """
        num_folds = len(self._fold_indices)

        transformed_data = np.empty([X.shape[0], self._num_classes])  # type: np.ndarray
        for in_fold in range(0, num_folds):
            in_fold_data = X[self._fold_indices[in_fold]]

            if self._target_encoder_folds[in_fold]:
                target_encoder = self._target_encoder_folds[in_fold]

                self._logger_wrapper('debug', 'Transform infold data using out of fold mapping')
                # Put data in same order as in X
                transformed_data[self._fold_indices[in_fold], :] = \
                    target_encoder.transform(in_fold_data)

        return transformed_data

    def _apply_transform(self, X: pd.Series) -> np.ndarray:
        """
        Apply transform on X data using mappings passed.

        :param X: Data to be transformed.
        :param mapping: Mappings to use for transforming the data.
        :return: Transformed data.
        """
        if self._target_encoder_full_fit is None:
            raise ValueError("CrossValidationTargetEncoder fit not called")

        return self._target_encoder_full_fit.transform(X)

    def _fit(self, X: pd.Series, y: pd.Series) -> None:
        """
        Compute categorical mappings for passed Data and target.

        :param X: Data to be transformed.
        :param y: Target data to use for categorical mappings.
        """
        # If foldColumnName was provided, means we are in train case, hence do a KFoldCV and get out of fold maps
        # These out of fold maps will be used to generate Features for InFold data, when we do a transform
        if len(self._fold_indices) > 1:

            # We need to ensure that folds start with index 0
            for curr_fold_indices in self._fold_indices:
                out_fold_indices = ~y.index.isin(curr_fold_indices)

                y_out_fold = y[out_fold_indices]
                X_out_fold = X[out_fold_indices]

                target_encoder = self.target_encoder_cls(**self._te_params)

                target_encoder_fit = target_encoder.fit(X_out_fold, y_out_fold)
                self._target_encoder_folds.append(target_encoder_fit)

        # generate a full categorical map as well
        self._target_encoder_full_fit = self.target_encoder_cls(**self._te_params).fit(X, y)

    def __getstate__(self):
        """
        Overridden to remove _num_folds and _fold_indices while pickling.

        :return: this object's state as a dictionary
        """
        state = super(CrossValidationTargetEncoder, self).__getstate__()
        newstate = {**state, **self.__dict__}

        # _fold_indices and _num_folds if set tell us that code is in train flow.
        # We want to lose that information on pickling.
        # In case model is unpickled, it will be used on inferencing or refitted.
        # In case it is refitted after unpickling, _fold_indices and _num_folds are again populated.

        newstate['_fold_indices'] = []
        newstate['_num_folds'] = 0
        newstate['_target_encoder_folds'] = []
        return newstate

    def __repr__(self) -> str:
        """
        Create and return representation of the CrossValidationTargetEncoder.

        :return: String representing the CrossValidationTargetEncoder.
        """
        return self.__str__()

    def __str__(self) -> str:
        """
        Create and return string representation of the CrossValidationTargetEncoder.

        :return: String representing the CrossValidationTargetEncoder.
        """
        return "Encoder: {encoder}, task_type: {task}, num_classes: {num_classes}" \
            .format(encoder=self._transformer_name, task=self._task, num_classes=self._num_classes + 1)
