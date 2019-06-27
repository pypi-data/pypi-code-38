# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for Categorical featurizers."""
from typing import Any
import numpy as np

from automl.client.core.common import constants

from ..generic.countbased_target_encoder import CountBasedTargetEncoder
from ..generic.crossvalidation_target_encoder import CrossValidationTargetEncoder
from ..generic.woe_target_encoder import WoEBasedTargetEncoder

from .cat_imputer import CatImputer
from .hashonehotvectorizer_transformer import HashOneHotVectorizerTransformer
from .labelencoder_transformer import LabelEncoderTransformer
from .onehotencoder_transformer import OneHotEncoderTransformer


class CategoricalFeaturizers:
    """Container for Categorical featurizers."""

    @classmethod
    def cat_imputer(cls, *args: Any, **kwargs: Any) -> CatImputer:
        """Create categorical imputer."""
        return CatImputer(*args, **kwargs)

    @classmethod
    def hashonehot_vectorizer(cls, *args: Any, **kwargs: Any) -> HashOneHotVectorizerTransformer:
        """Create hash one hot vectorizer."""
        return HashOneHotVectorizerTransformer(*args, **kwargs)

    @classmethod
    def labelencoder(cls, *args: Any, **kwargs: Any) -> LabelEncoderTransformer:
        """Create label encoder."""
        return LabelEncoderTransformer(*args, **kwargs)

    @classmethod
    def cat_targetencoder(cls, *args: Any, **kwargs: Any) -> CrossValidationTargetEncoder:
        """Create categorical target encoder featurizer."""
        if not kwargs:
            kwargs = {}

        return CrossValidationTargetEncoder(CountBasedTargetEncoder, *args, **kwargs)

    @classmethod
    def woe_targetencoder(cls, *args: Any, **kwargs: Any) -> CrossValidationTargetEncoder:
        """Create weight of evidence featurizer."""
        if not kwargs:
            kwargs = {}

        return CrossValidationTargetEncoder(WoEBasedTargetEncoder, *args, **kwargs)

    @classmethod
    def onehotencoder(cls, *args: Any, **kwargs: Any) -> OneHotEncoderTransformer:
        """Create onehotencoder."""
        if constants.FeatureSweeping.LOGGER_KEY in kwargs:
            kwargs.pop(constants.FeatureSweeping.LOGGER_KEY)
        if 'dtype' not in kwargs:
            kwargs['dtype'] = np.uint8
        if 'handle_unknown' not in kwargs:
            kwargs['handle_unknown'] = 'ignore'
        return OneHotEncoderTransformer(*args, **kwargs)
