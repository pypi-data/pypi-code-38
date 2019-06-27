# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generate dense text statistics."""
from typing import Dict, List, Optional

import logging
import re

from ..automltransformer import AutoMLTransformer
from automl.client.core.common.types import DataSingleColumnInputType, DataInputType
from azureml.automl.core.column_purpose_detection.columnpurpose_detector import StatsAndColumnPurposeType
from automl.client.core.common import memory_utilities


class StatsTransformer(AutoMLTransformer):
    """Extract features from each document for DictVectorizer."""

    def __init__(self, logger: Optional[logging.Logger] = None, token_pattern: str = r"(?u)\w\w+\b") -> None:
        """Create a Stats transformer."""
        super().__init__()
        self._init_logger(logger)
        self._token_pattern = token_pattern

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(StatsTransformer, self)._to_dict()
        dct['id'] = "text_stats"
        dct['type'] = 'text'
        dct['kwargs']['token_pattern'] = self._token_pattern

        return dct

    def fit(self, *args, **kwargs):
        """Create and tokenizer."""
        self._tokenizer = re.compile(self._token_pattern)
        return self

    def transform(self, X: DataSingleColumnInputType) -> List[Dict[str, float]]:
        """
        Return various stats from the text data.

        :param X: Input data.
        :return: Transformed data.
        """
        stats = []
        for text in X:
            tokens = self._tokens(text)
            n_words = self._n_words(tokens)
            n_capitals = self._n_capitals(tokens)

            stats.append({
                'n_periods': float(text.count('.')),
                'n_words': float(n_words),
                'n_capitals': float(n_capitals),
                'n_exclamations': float(text.count('!')),
                'n_questions': float(text.count('?')),
                'n_chars': float(len(text))
            })

        return stats

    def _tokens(self, text: str) -> List[str]:
        """
        Tokenizer.

        :param text: Input text.
        :return: List of tokens found using the tokenizer.
        """
        return self._tokenizer.findall(text)

    def _n_words(self, tokens: List[str]) -> int:
        """
        Return the number of words found in the text.

        :param tokens: List of tokens.
        :return: Number of words.
        """
        return len(tokens)

    def _n_capitals(self, tokens: List[str]) -> int:
        """
        Return the number of words with at least one capital letter in them.

        :param tokens: List of tokens.
        :return: Number of words with at least one capital letter in them.
        """
        return sum(1 for w in tokens if not w.islower())

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint estimate for this transformer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken.
        """
        num_stats = 6  # Number of stats returned for each row in transform method.
        return len(X) * num_stats * memory_utilities.get_data_memory_size(float)
