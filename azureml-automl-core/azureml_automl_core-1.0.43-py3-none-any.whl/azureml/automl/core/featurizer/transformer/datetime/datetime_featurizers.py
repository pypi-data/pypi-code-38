# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for Numeric featurizers."""
from .datetime_transformer import DateTimeFeaturesTransformer


class DateTimeFeaturizers:
    """Container for DateTime featurizers."""

    @classmethod
    def datetime_transformer(cls, *args, **kwargs):
        """Create datetime transformer."""
        return DateTimeFeaturesTransformer(*args, **kwargs)
