# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Creates word embeddings from pre-trained models."""
from typing import Callable, cast, List, Optional, Pattern

import re
import sys
from logging import Logger

import numpy as np
from gensim.models.keyedvectors import KeyedVectors

from automl.client.core.common import memory_utilities
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.types import DataSingleColumnInputType, DataInputType
from ...._engineered_feature_names import _TransformationFunctionNames, _OperatorNames
from ....column_purpose_detection.types import StatsAndColumnPurposeType
from ..automltransformer import AutoMLTransformer
from ..data import AbstractWordEmbeddingsProvider


class WordEmbeddingTransformer(AutoMLTransformer):
    """Creates word embeddings from pre-trained models."""

    EMBEDDING_PROVIDER_KEY = "embeddings_provider"

    def __init__(self,
                 embeddings_provider: AbstractWordEmbeddingsProvider,
                 logger: Optional[Logger] = None,
                 token_pattern: str = r"(?u)\b\w+\b") -> None:          # TODO Inject tokenizer
        """
        Create word embeddings from pre-trained models.

        :param: embeddings_provider: Embeddings provider for the model.
        :param logger: Logger.
        :param token_pattern: Token pattern for splitting the sentence into words.

        """
        super(WordEmbeddingTransformer, self).__init__(logger=logger)
        self._init_logger(logger)
        # if a text is empty we should return a vector of zeros
        # with the same dimensionality as all the other vectors
        # len(word2vec.itervalues().next())
        self.model = None                                               # type: Optional[KeyedVectors]
        self.dim = 0
        self._is_lower = False
        self.token_pattern = token_pattern
        self.tokenizer = None                                           # type: Optional[Pattern[str]]
        self._provider = embeddings_provider
        self._transformer_name = _TransformationFunctionNames.WordEmbedding
        self._operator_name = _OperatorNames.Mean

    def _get_operator_name(self) -> Optional[str]:
        return self._operator_name

    def _get_transformer_name(self) -> str:
        return self._transformer_name

    def initialize(self) -> None:
        """
        Initialize objects that aren't picklable.

        :return: None.
        """
        self.tokenizer = re.compile(self.token_pattern)
        self.model = self._provider.model
        if not self.model:
            self._logger_wrapper("info", "Word embeddings ignored.")
        else:
            self.dim = self._provider.vector_size
            self._is_lower = self._provider.is_lower

    def _to_dict(self):
        """
        Create dict from transformer for  serialization usage.

        :return: a dictionary
        """
        dct = super(WordEmbeddingTransformer, self)._to_dict()
        dct['id'] = "word_embeddings"
        dct['type'] = 'text'
        dct['kwargs']['token_pattern'] = self.token_pattern
        dct['kwargs']['embeddings_name'] = self._provider._embeddings_name

        return dct

    @function_debug_log_wrapped
    def fit(self, X: DataSingleColumnInputType, y: DataSingleColumnInputType = None) -> "WordEmbeddingTransformer":
        """
        Fit method.

        :param X: Input data.
        :param y: Labels.
        :return: self.
        """
        self.initialize()
        return self

    @function_debug_log_wrapped
    def transform(self, X: DataSingleColumnInputType) -> np.ndarray:
        """
        Transform method.

        :param X: Input data.
        :return: Transformed data.
        """
        if not self.model:
            self.initialize()

        transformed_data = self._agg_transformer(X, np.mean) if self.model else np.array([])
        return transformed_data

    def _analyzer(self, doc: str) -> List[str]:
        """Tokenize and provide a list of tokens.

        :param doc: Document to tokenize.
        :return: List of tokens identified.
        """
        return cast(List[str], self.tokenizer.findall(doc)) if self.tokenizer else []

    def _agg_transformer(self, X: DataSingleColumnInputType, agg_func: Callable[..., np.ndarray]) \
            -> np.ndarray:
        """
        Create word embeddings for the given input. Use agg_func for aggregation to create sentence vectors.

        :param X: Input.
        :param agg_func: Aggregation function to use for creating sentence vectors.
        :return: Embedding vectors for each of the sentences.
        """
        target = []                                                     # type: List[np.ndarray]
        if isinstance(X, np.ndarray):
            X = X.reshape(-1)

        zeros = list(np.zeros(self.dim))
        for doc in X:
            # TODO Inject aggregation function
            words_found = self._analyzer(doc)
            if len(words_found) > 0:
                embedding_vectors = [self._get_embedding(w) for w in self._analyzer(doc)]
                # TODO Inject sentence embedder
                sentence_vector = list(agg_func(embedding_vectors, axis=0))
                target.append(sentence_vector)
            else:
                target.append(zeros)

        t = np.array(target)
        return t

    def _get_embedding(self, x: str) -> np.ndarray:
        """
        Return embeddings found for the input string in training data. Else return zeros.

        :param x: Input string.
        :return: Embeddings of this string or zeros if the string is not found in the training data.
        """
        if self._is_lower:
            x = x.lower()

        if self.model and x in self.model:
            return self.model[x]
        else:
            return np.zeros(self.dim)

    def __getstate__(self):
        """
        Overriden to remove model object when pickling.

        :return: this object's state as a dictionary
        """
        state = super(WordEmbeddingTransformer, self).__getstate__()
        newstate = {**state, **self.__dict__}
        newstate['model'] = None
        newstate['tokenizer'] = None
        newstate['logger'] = None
        return newstate

    def get_memory_footprint(self, X: DataInputType, y: DataSingleColumnInputType) -> int:
        """
        Obtain memory footprint by adding this featurizer.

        :param X: Input data.
        :param y: Input label.
        :return: Amount of memory taken.
        """
        num_rows = len(X)
        f_size = memory_utilities.get_data_memory_size(float)
        try:
            if self.model is None:
                self.initialize()

            return self.dim * f_size * num_rows
        except Exception as e:
            self._logger_wrapper("debug", "Exception while trying to estimate memory footprint: {e}".format(e=e))
            return sys.maxsize
