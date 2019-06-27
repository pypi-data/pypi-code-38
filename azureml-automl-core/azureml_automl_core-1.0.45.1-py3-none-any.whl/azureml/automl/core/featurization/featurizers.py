# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Featurizer factory."""
from typing import Any

from automl.client.core.common.exceptions import ConfigException
from ..featurizer.transformer.text import TextFeaturizers
from ..featurizer.transformer.numeric import NumericFeaturizers
from ..featurizer.transformer.generic import GenericFeaturizers
from ..featurizer.transformer.categorical import CategoricalFeaturizers
from ..configuration.feature_config import FeatureConfig
from ..featurizer.transformer.datetime import DateTimeFeaturizers


class Featurizers:
    """Featurizer factory."""

    FEATURE_NAME_TO_FACTORY = {
        "text": TextFeaturizers,
        "numeric": NumericFeaturizers,
        "categorical": CategoricalFeaturizers,
        "generic": GenericFeaturizers,
        "datetime": DateTimeFeaturizers
    }

    @classmethod
    def get(cls, config: FeatureConfig) -> Any:
        """Get featurizer given an id and type. Initialize with params defined in the config.

        :param config: Configuration containing required feature details.
        :return: Featurizer instance or None.
        """
        assert config is not None and isinstance(config, FeatureConfig)
        assert isinstance(config, FeatureConfig) and isinstance(config.id, str)
        assert isinstance(config.featurizer_type, str)
        feature_type = config.featurizer_type
        if feature_type not in cls.FEATURE_NAME_TO_FACTORY:
            raise ConfigException("{feature_type} is not a valid feature type.".format(feature_type=feature_type))

        factory = cls.FEATURE_NAME_TO_FACTORY[feature_type]
        feature_id = config.id
        if not hasattr(factory, feature_id):
            raise ConfigException("{feature_id} is not a valid featurizer in the feature type {feature_type}.".format(
                feature_id=feature_id,
                feature_type=feature_type
            ))

        factory_method = getattr(factory, feature_id)

        if not callable(factory_method):
            raise ConfigException("{feature_id} is not a callable featurizer "
                                  "in the feature type {feature_type}.".format(feature_id=feature_id,
                                                                               feature_type=feature_type
                                                                               ))

        return factory_method(*config.featurizer_args, **config.featurizer_kwargs)
