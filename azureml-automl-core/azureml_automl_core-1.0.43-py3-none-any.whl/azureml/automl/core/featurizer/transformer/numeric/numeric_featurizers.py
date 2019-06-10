# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Container for Numeric featurizers."""
from .bin_transformer import BinTransformer


class NumericFeaturizers:
    """Container for Numeric featurizers."""

    @classmethod
    def bin_transformer(cls, *args, **kwargs):
        """Create bin transformer."""
        return BinTransformer(*args, **kwargs)
