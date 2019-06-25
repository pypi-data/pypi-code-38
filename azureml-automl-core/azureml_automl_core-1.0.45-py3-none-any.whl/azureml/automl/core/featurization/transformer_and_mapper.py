# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataModel class that holds tranformer and corresponding dataframe mapper together."""
from typing import List, Any

from sklearn_pandas import DataFrameMapper


class TransformerAndMapper:
    """DataModel class that holds tranformer and corresponding dataframe mapper together."""

    def __init__(self, transformers: List[Any], mapper: DataFrameMapper) -> None:
        """Construct."""
        self.transformers = transformers
        self.mapper = mapper
        self.memory_footprint_estimate = 0
