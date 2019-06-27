# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic bag of words transformer."""
from typing import List, Optional, Tuple, Union

import logging

import numpy as np

from sklearn.pipeline import make_union, make_pipeline, Pipeline, FeatureUnion
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import RobustScaler

from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.types import DataSingleColumnInputType, DataInputType
from azureml.automl.core.column_purpose_detection.types import StatsAndColumnPurposeType
from ..automltransformer import AutoMLTransformer
from .stats_transformer import StatsTransformer
from .constants import TFIDF_VECTORIZER_CONFIG as TFIDF_CONFIG


class BagOfWordsTransformer(AutoMLTransformer):
    """Generic bag of words transformer."""

    def __init__(self, logger: Optional[logging.Logger] = None, max_wordgrams: int = int(2e5),
                 wordgram_range: Tuple[int, int] = (1, 2),
                 chargram_range: Tuple[int, int] = (3, 3), norm: str = "l2", max_df: float = 1.0,
                 include_dense_features: bool = False, use_idf: bool = False) -> None:
        """Create the bag of words transformer."""
        super().__init__()
        self._init_logger(logger)
        self._max_wordgrams = max_wordgrams
        self._wordgram_range = wordgram_range
        self._chargram_range = chargram_range
        self._include_dense_features = include_dense_features
        self._norm = norm
        self._max_df = max_df
        self._pipelines = None  # type: Optional[Union[Pipeline, FeatureUnion]]
        self._use_idf = use_idf

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(BagOfWordsTransformer, self)._to_dict()
        dct['id'] = "bow_transformer"
        dct['type'] = 'text'
        dct['kwargs']['max_wordgrams'] = self._max_wordgrams
        dct['kwargs']['wordgram_range'] = list(self._wordgram_range)
        dct['kwargs']['chargram_range'] = list(self._chargram_range)
        dct['kwargs']['norm'] = self._norm
        dct['kwargs']['max_df'] = self._max_df
        dct['kwargs']['include_dense_features'] = self._include_dense_features
        dct['kwargs']['use_idf'] = self._use_idf

        return dct

    @function_debug_log_wrapped
    def fit(self, X: DataInputType, y: DataSingleColumnInputType) -> "BagOfWordsTransformer":
        """
        Fit the current model to given input data.

        :param X: Input data.
        :param y: Input labels.
        :return: The object itself.
        """
        pipeline_list = []

        if self._include_dense_features:
            pipeline_list.append(make_pipeline(StatsTransformer(),
                                               DictVectorizer(),
                                               RobustScaler(with_centering=False)))

        if self._chargram_range != (0, 0):
            pipeline_list.append(TfidfVectorizer(use_idf=self._use_idf,
                                                 dtype=np.float32,
                                                 analyzer=TFIDF_CONFIG.CHAR_ANALYZER,
                                                 norm=self._norm,
                                                 max_df=self._max_df,
                                                 ngram_range=self._chargram_range))

        if self._wordgram_range != (0, 0):
            pipeline_list.append(TfidfVectorizer(use_idf=self._use_idf,
                                                 dtype=np.float32,
                                                 max_features=self._max_wordgrams,
                                                 analyzer=TFIDF_CONFIG.WORD_ANALYZER,
                                                 ngram_range=self._wordgram_range))

        if pipeline_list:
            self._pipelines = make_union(*pipeline_list)
            self._pipelines.fit(X)
        return self

    @function_debug_log_wrapped
    def transform(self, X: DataInputType) -> DataInputType:
        """Transform the given data.

        :param X: Input data.
        :return: Transformed data.
        """
        if self._pipelines:
            features = self._pipelines.transform(X)
            return features
        else:
            return np.array([])

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        # We will revisit this later.
        return 0
