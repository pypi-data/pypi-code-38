# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Default data splitter."""
from typing import Optional, Tuple, List

import pickle
from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split

from automl.client.core.common import constants
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from . import SplittingConfig


class DataProvider(ABC):
    """An abstract provider of dataset for doing sampling."""

    @abstractmethod
    def get_train_validation_sets(self) \
            -> Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]:
        """Return a Tuple(X_train, y_train, X_valid, y_valid) from the input dataset."""
        raise NotImplementedError()

    @abstractmethod
    def get_cross_validation_sets(self) \
            -> List[Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, y_train, X_valid, y_valid)."""
        raise NotImplementedError()


class InMemoryDataProvider(DataProvider):
    """Default data provider using in-memory representation of training data."""

    def __init__(self, X: DataInputType, y: DataSingleColumnInputType,
                 splitting_config: SplittingConfig, seed: int = constants.hashing_seed_value) -> None:
        """Initialize an instance of this class.

        :param X: Input training data
        :param y: Input target data
        :param splitting_config: configuration for doing splitting over the input training set.
        """
        self._X = X
        self._y = y
        self._splitting_config = splitting_config
        self._random_seed = seed

    def get_train_validation_sets(self) \
            -> Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]:
        """Return a Tuple(X_train, y_train, X_valid, y_valid) from the input dataset."""
        stratify = self._y if self._splitting_config.task == constants.Tasks.CLASSIFICATION else None

        try:
            X_train, y_train, X_valid, y_valid = train_test_split(
                self._X, self._y, train_size=self._splitting_config.train_size,
                test_size=self._splitting_config.test_size, stratify=stratify, random_state=self._random_seed)
        except ValueError:
            # in case stratification fails, fall back to non-stratify train/test split
            X_train, y_train, X_valid, y_valid = train_test_split(
                self._X, self._y, train_size=self._splitting_config.train_size,
                test_size=self._splitting_config.test_size, stratify=None, random_state=self._random_seed)

        return (X_train, y_train, X_valid, y_valid)

    def get_cross_validation_sets(self) \
            -> List[Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, y_train, X_valid, y_valid)."""
        raise NotImplementedError()


class DiskBasedDataProvider(DataProvider):
    """Data provider which uses files on disk to lazily load into memory the training set."""

    def __init__(self, pickled_dataset_file: str, splitting_config: SplittingConfig,
                 seed: int = constants.hashing_seed_value) -> None:
        """Initialize an instance of this class.

        :param pickled_dataset_file: the file where to read the input dataset from.
        :param splitting_config: the config to use for splitting the dataset into training / validation sets.
        """
        self._picked_dataset_file = pickled_dataset_file
        self._splitting_config = splitting_config
        self._random_seed = seed
        self._decoratedProvider = None  # type: Optional[DataProvider]

    def get_train_validation_sets(self) \
            -> Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]:
        """Return a Tuple(X_train, y_train, X_valid, y_valid) from the input dataset."""
        if self._decoratedProvider is None:
            self._decoratedProvider = self._lazy_create_provider()
        return self._decoratedProvider.get_train_validation_sets()

    def get_cross_validation_sets(self) \
            -> List[Tuple[DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType]]:
        """Return a list of CV splits represented by a Tuple (X_train, y_train, X_valid, y_valid)."""
        if self._decoratedProvider is None:
            self._decoratedProvider = self._lazy_create_provider()
        return self._decoratedProvider.get_cross_validation_sets()

    def _lazy_create_provider(self) -> DataProvider:
        """Create lazily an InMemoryDataProvider from the input file holding the pickled dataset."""
        with open(self._picked_dataset_file, "rb") as f:
            (X, y) = pickle.load(f)
            return InMemoryDataProvider(X, y, self._splitting_config, seed=self._random_seed)
