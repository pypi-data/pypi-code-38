# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for top level text transformation logic."""
from typing import Optional, List

import logging

from automl.client.core.common import constants
from .._engineered_feature_names import _FeatureTransformers, _GenerateEngineeredFeatureNames, \
    _TransformationFunctionNames, _Transformer, _OperatorNames, FeatureTypeRecognizer
from ..featurizer.transformer.automltransformer import AutoMLTransformer
from ..featurizer.transformer.text.constants import TFIDF_VECTORIZER_CONFIG
from ..featurizer.transformer.text.utilities import max_ngram_len
from ..featurizer.transformer.text.text_featurizers import TextFeaturizers
from automl.client.core.common.types import TransformerType


class TextTransformer(AutoMLTransformer):
    """Class for top level text transformation logic."""

    def __init__(self,
                 task_type: Optional[str] = constants.Tasks.CLASSIFICATION,
                 logger: Optional[logging.Logger] = None,
                 is_onnx_compatible: bool = False):
        """
        Preprocessing class for Text.

        :param task_type: 'classification' or 'regression' depending on what kind of ML problem to solve.
        :param logger: The logger to use.
        :param is_onnx_compatible: if works in onnx compatible mode.
        """
        super().__init__()
        self._task_type = task_type
        self.logger = logger
        self.is_onnx_compatible = is_onnx_compatible

    def get_transforms(self,
                       column: str,
                       column_name: str,
                       ngram_len: int,
                       engineered_feature_names: _GenerateEngineeredFeatureNames) -> \
            List[TransformerType]:
        """
        Create a list of transforms for text data.

        :param column: Column name in the data frame.
        :param column_name: Name of the column for engineered feature names
        :param ngram_len: Continous length of characters or number of words.
        :param engineered_feature_names: Existing engineered feature names
        :return: Text transformations to use in a list.
        """
        ngram_len = min(max_ngram_len, ngram_len)

        if not self.is_onnx_compatible:
            # The trichar transform is currently not ONNX compatible.
            # Add the transformations to be done and get the alias name
            # for the trichar transform.
            text_trichar_string_cast_transformer = _Transformer(
                parent_feature_list=[str(column_name)],
                transformation_fnc=_TransformationFunctionNames.StringCast,
                operator=None, feature_type=FeatureTypeRecognizer.Text,
                should_output=False)
            # This transformation depends on the previous transformation
            text_trichar_tfidf_transformer = _Transformer(
                parent_feature_list=[1],
                transformation_fnc=_TransformationFunctionNames.Tf,
                operator=_OperatorNames.CharGram, feature_type=None,
                should_output=True)
            # Create an object to convert transformations into JSON object
            feature_transformers = _FeatureTransformers([
                text_trichar_string_cast_transformer,
                text_trichar_tfidf_transformer])
            # Create the JSON object
            json_obj = feature_transformers.encode_transformations_from_list()
            # Persist the JSON object for later use and obtain an alias name
            tfidf_trichar_column_name = engineered_feature_names.get_raw_feature_alias_name(json_obj)

        # Add the transformations to be done and get the alias name
        # for the bigram word transform.
        text_biword_string_cast_transformer = _Transformer(
            parent_feature_list=[str(column_name)],
            transformation_fnc=_TransformationFunctionNames.StringCast,
            operator=None, feature_type=FeatureTypeRecognizer.Text,
            should_output=False)
        # This transformation depends on the previous transformation
        text_biword_tfidf_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.Tf,
            operator=_OperatorNames.WordGram, feature_type=None,
            should_output=True)
        # Create an object to convert transformations into JSON object
        feature_transformers = _FeatureTransformers([
            text_biword_string_cast_transformer,
            text_biword_tfidf_transformer])
        # Create the JSON object
        json_obj = feature_transformers.encode_transformations_from_list()
        # Persist the JSON object for later use and obtain an alias name
        tfidf_biword_column_name = engineered_feature_names.get_raw_feature_alias_name(json_obj)

        tr = []  # type: List[TransformerType]
        if not self.is_onnx_compatible:
            # The trichar transform is currently not ONNX compatible.
            fea_tup_char = (column,
                            [
                                TextFeaturizers.string_cast(
                                    logger=self.logger),
                                TextFeaturizers.tfidf_vectorizer(use_idf=False,
                                                                 norm=TFIDF_VECTORIZER_CONFIG.NORM,
                                                                 max_df=TFIDF_VECTORIZER_CONFIG.MAX_DF,
                                                                 analyzer=TFIDF_VECTORIZER_CONFIG.CHAR_ANALYZER,
                                                                 ngram_range=(1, ngram_len))
                            ],
                            {
                                'alias': str(tfidf_trichar_column_name)
                            }
                            )
            tr.append(fea_tup_char)

        fea_tup_word = (column,
                        [
                            TextFeaturizers.string_cast(logger=self.logger),
                            TextFeaturizers.tfidf_vectorizer(use_idf=False,
                                                             norm=TFIDF_VECTORIZER_CONFIG.NORM,
                                                             analyzer=TFIDF_VECTORIZER_CONFIG.WORD_ANALYZER,
                                                             ngram_range=TFIDF_VECTORIZER_CONFIG.WORD_NGRAM_RANGE)
                        ],
                        {
                            'alias': str(tfidf_biword_column_name)
                        }
                        )
        tr.append(fea_tup_word)

        return tr
