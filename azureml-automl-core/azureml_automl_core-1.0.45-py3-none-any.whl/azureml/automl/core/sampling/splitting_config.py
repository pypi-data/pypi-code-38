# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration for sampling."""
from typing import Optional

from automl.client.core.common import constants


class SplittingConfig:
    """Hold information on how to split a sampled dataset for feature sweeping."""

    def __init__(self, task: str = constants.Tasks.CLASSIFICATION, train_size: Optional[float] = None,
                 test_size: Optional[float] = None, number_cross_validation: Optional[int] = None) -> None:
        """Initialize an instance of this class.

        param task: ML task
        param train_size: Fraction of the sampled dataset to be used for training.
        param test_size: Factrion of the sampled dataset to be used for validation.
        param number_cross_validation: Number of folds for doing Cross-Validation.
        """
        self.task = task
        self.train_size = train_size
        self.test_size = test_size
        self.number_cross_validation = number_cross_validation
