# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods and classes used during an AutoML experiment to determine purpose of various data columns."""
from typing import List, Optional, Tuple, Type

import pandas as pd
import numpy as np

from .._engineered_feature_names import FeatureTypeRecognizer
from ..stats_computation import RawFeatureStats
from .types import StatsAndColumnPurposeType
from automl.client.core.common.utilities import _check_if_column_data_type_is_int, \
    _check_if_column_data_type_is_numerical


class ColumnPurposeDetector:
    """Methods and classes used during an AutoML experiment to determine purpose of various data columns."""

    # ratio of unique values to total values to be considered categoricals
    _min_ratio_uniq_cats = 0.05
    # max number of unique values to be considered cats
    _max_num_cats = 200
    # max number of unique values to be considered categorical hash
    _max_num_cat_hash = 10000
    # max number of unique values to be considered cats for integer
    _max_num_cats_int = 50
    # ratio of unique values to total values to be considered hashes
    _min_ratio_hashes = 0.9
    # number of maxrows allowed for tfidf computation since tfidf vectorizer is expensive
    _maxrows_for_tfidf = 1e5
    # max number of unique lengths in a column to be considered hash
    _max_uniqhashlens = 3
    # min number of rows for hashes to be present
    _min_num_hashrows = 200

    @classmethod
    def detect_column_purpose(cls: Type["ColumnPurposeDetector"], column: str, df: pd.DataFrame)\
            -> StatsAndColumnPurposeType:
        """
        Calculate the stats_computation on the raw column and decide the data type of the input column.

        :param column: Column name in the data frame.
        :param df: Input dataframe.
        :return: Raw column stats_computation, Type of feature.
        """
        raw_stats = RawFeatureStats(df[column])
        if raw_stats.is_all_nan:
            feature_type_detected = FeatureTypeRecognizer.AllNan
        elif raw_stats.num_unique_vals == 1:
            # If there is only one unique value, then we don't need to include
            # this column for transformations
            feature_type_detected = FeatureTypeRecognizer.Ignore
        elif raw_stats.is_datetime:
            feature_type_detected = FeatureTypeRecognizer.DateTime
        elif raw_stats.num_unique_vals >= min(
                cls._max_num_cats,
                cls._min_ratio_uniq_cats * raw_stats.total_number_vals):
            # If number of unique values is higher than a ratio of input data
            if _check_if_column_data_type_is_numerical(
                    raw_stats.column_type):
                feature_type_detected = FeatureTypeRecognizer.Numeric
            else:
                if raw_stats.cardinality_ratio > 0.85 and \
                        raw_stats.average_number_spaces > 1.0:
                    feature_type_detected = FeatureTypeRecognizer.Text
                elif raw_stats.cardinality_ratio < 0.7 and \
                        raw_stats.num_unique_vals < cls._max_num_cat_hash:
                    feature_type_detected = \
                        FeatureTypeRecognizer.CategoricalHash
                elif raw_stats.average_number_spaces > 1.0:
                    feature_type_detected = FeatureTypeRecognizer.Text
                elif raw_stats.cardinality_ratio > 0.9:
                    feature_type_detected = FeatureTypeRecognizer.Hashes
                else:
                    feature_type_detected = FeatureTypeRecognizer.Ignore
        else:
            if _check_if_column_data_type_is_int(
                    raw_stats.column_type):
                if raw_stats.num_unique_vals <= min(
                        cls._max_num_cats_int,
                        cls._min_ratio_uniq_cats *
                        raw_stats.total_number_vals):
                    feature_type_detected = \
                        FeatureTypeRecognizer.Categorical
                else:
                    feature_type_detected = FeatureTypeRecognizer.Numeric
            elif _check_if_column_data_type_is_numerical(
                    raw_stats.column_type):
                feature_type_detected = FeatureTypeRecognizer.Numeric
            else:
                feature_type_detected = FeatureTypeRecognizer.Categorical
        return raw_stats, feature_type_detected, column

    @classmethod
    def get_raw_stats_and_column_purposes(cls: Type["ColumnPurposeDetector"], df: pd.DataFrame) -> \
            List[StatsAndColumnPurposeType]:
        """
        Obtain raw feature stats and column purposes for the dataframe.

        :param df: Input data frame.
        :return: Rawfeature stats and column purpose for each column.
        """
        return [(cls.detect_column_purpose(column, df)) for column in df.columns]
