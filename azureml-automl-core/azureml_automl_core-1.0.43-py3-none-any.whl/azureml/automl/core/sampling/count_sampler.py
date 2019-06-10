# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Default sampler."""
from typing import Any, Optional, Tuple

import numpy as np
from sklearn.model_selection import train_test_split

from automl.client.core.common import constants
from automl.client.core.common.exceptions import ConfigException
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from . import AbstractSampler, SplittingConfig


class CountSampler(AbstractSampler):
    """Default sampler."""

    def __init__(self,
                 seed: int, min_examples_per_class: int = 2000, max_rows: int = 10000,
                 is_constraint_driven: bool = True,
                 task: str = constants.Tasks.CLASSIFICATION,
                 train_frac: Optional[float] = None,
                 *args: Any, **kwargs: Any) -> None:
        """
        Create default sampler.

        :param seed: Random seed to use to sample.
        :param min_examples_per_class: Minimum examples per class to sample.
        :param max_rows: Maximum rows to output.
        :param is_constraint_driven: Is constraint driven or not.
        :param train_frac: Fraction of data to be considered for training.
        """
        task_key = "task"
        kwargs[task_key] = kwargs.get(task_key, task)

        super(CountSampler, self).__init__(*args, **kwargs)
        self._min_examples_per_class = min_examples_per_class
        self._max_rows = max_rows
        self._seed = seed
        self._is_constraint_driven = is_constraint_driven
        self._train_frac = train_frac

    def sample(self, X: DataInputType, y: DataSingleColumnInputType) \
            -> Tuple[DataInputType, DataSingleColumnInputType, SplittingConfig]:
        """
        Sample the give input data.

        :param X: Input data.
        :param y: Output label.
        :return: Sampled data.
        """
        # min max logic
        # minimum possible is n_classes * min_examples_per_class
        # max possible
        nrows = np.shape(X)[0]

        # for regression we want to use up to _max_rows from input
        n_train = self._max_rows
        if self._task == constants.Tasks.CLASSIFICATION:
            class_labels = np.unique(y)
            n_train_by_min_class_examples = len(class_labels) * self._min_examples_per_class
            n_train = min(n_train_by_min_class_examples, self._max_rows)

        constraint_train_frac = n_train / float(nrows)
        if self._is_constraint_driven:
            train_frac = constraint_train_frac
        else:
            if self._train_frac is None:
                raise ConfigException("If constrain train fraction is set to false, train_frac must be specified.")
            train_frac = self._train_frac

        # in case it's a really small dataset!, train_frac could be > 0.8 or even 1.
        train_frac = min(train_frac, 0.8)  # 0.8 guarantees and 80 20 split
        stratify = y if self._task == constants.Tasks.CLASSIFICATION else None

        # when sampling we want to use the same percentage for validation as well for more accurate scoring
        # but, for small datasets (where train > 50%) we need to make sure train & test don't overalap
        # hence the test_fraction would be 1 - train_frac
        test_frac = train_frac if train_frac < 0.5 else 1 - train_frac
        # here we just scale down the dataset, the splitter will handle it further to do TrainValidation or CV split
        sample_fraction = train_frac + test_frac
        if sample_fraction < 1:
            try:
                X_sampled, _, y_sampled, _ = train_test_split(
                    X, y, train_size=sample_fraction, random_state=self._seed, stratify=stratify)
            except ValueError:
                # in case stratification fails, fall back to non-stratify train/test split
                X_sampled, _, y_sampled, _ = train_test_split(
                    X, y, train_size=sample_fraction, random_state=self._seed, stratify=None)

        else:
            X_sampled, y_sampled = X, y

        self._logger.debug("Feature sweeping sampling: train_frac = {}, test_frac={}".format(
            train_frac, test_frac))
        split_config = SplittingConfig(task=self._task,
                                       test_size=test_frac / (train_frac + test_frac),
                                       train_size=None)

        return X_sampled, y_sampled, split_config
