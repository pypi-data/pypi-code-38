# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for generic featurizers."""

from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import Imputer, MaxAbsScaler

from automl.client.core.common import constants
from .imputation_marker import ImputationMarker
from .lambda_transformer import LambdaTransformer


class GenericFeaturizers:
    """Container for generic featurizers."""

    @classmethod
    def imputation_marker(cls, *args, **kwargs):
        """Create imputation marker."""
        return ImputationMarker(*args, **kwargs)

    @classmethod
    def lambda_featurizer(cls, *args, **kwargs):
        """Create lambda featurizer."""
        return LambdaTransformer(*args, **kwargs)

    @classmethod
    def imputer(cls, *args, **kwargs):
        """Create Imputer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return Imputer(*args, **kwargs)

    @classmethod
    def minibatchkmeans_featurizer(cls, *args, **kwargs):
        """Create mini batch k means featurizer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return MiniBatchKMeans(*args, **kwargs)

    @classmethod
    def maxabsscaler(cls, *args, **kwargs):
        """Create maxabsscaler featurizer."""
        # remove logger key as we don't own this featurizer
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        return MaxAbsScaler(*args, **kwargs)
