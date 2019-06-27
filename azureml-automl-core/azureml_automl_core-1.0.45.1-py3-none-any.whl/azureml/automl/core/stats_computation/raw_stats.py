# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for computing feature stats_computation from raw features."""
from typing import cast, DefaultDict, Optional
from collections import defaultdict

import numpy as np
import pandas


from automl.client.core.common import utilities
from automl.client.core.common.utilities import is_known_date_time_format
from automl.client.core.common.utilities import _check_if_column_data_type_is_datetime,\
    _check_if_column_data_type_is_numerical
from .._engineered_feature_names import FeatureTypeRecognizer


class RawFeatureStats:
    """
    Class for computing feature stats_computation from raw features.

    :param raw_column: Column having raw data.
    :type raw_column: pandas.Series
    """

    # max size in characters for ngram
    _max_ngram = 3
    # Hashing seed value for murmurhash
    _hashing_seed_value = 314489979

    def __init__(self, raw_column: pandas.Series):
        """
        Calculate stats_computation for the input column.

        These stats_computation are needed for deciding the data type of the column.

        :param raw_column: Column having raw data.
        :type raw_column: numpy.ndarray
        """
        # --- Common stats for all data types --- #
        # Number of unique values in the column
        self.num_unique_vals = raw_column.unique().shape[0]
        # Total number of values in the column
        self.total_number_vals = raw_column.shape[0]
        # Number of missing values in the column
        self.num_na = raw_column.isnull().sum()
        # Get the column type
        self.column_type = utilities._get_column_data_type_as_str(raw_column.values)

        # Create a series having lengths of the entries in the column
        self.lengths = None     # type: Optional[pandas.Series]
        # Calculate the number of lengths of the entries in the column
        self.num_unique_lens = 0
        # Average lengths of an entry in the column
        self.average_entry_length = 0
        # Average number of spaces in an entry in the column
        self.average_number_spaces = 0
        # Ratio of number of unique value to total number of values
        self.cardinality_ratio = 0
        # Check if the column is of type datetime
        self.is_datetime = False
        # Check if the column has all nan values
        self.is_all_nan = False

        # Get stats based on the type of data
        if self.num_na == self.total_number_vals:
            self.is_all_nan = True
        elif _check_if_column_data_type_is_numerical(self.column_type):
            self._fill_stats_if_numeric_feature(raw_column)
        elif _check_if_column_data_type_is_datetime(self.column_type):
            self.is_datetime = is_known_date_time_format(
                str(raw_column[raw_column.first_valid_index()]))
        else:
            self._fill_stats_if_text_or_categorical_feature(raw_column)

    def _fill_stats_if_numeric_feature(self, raw_column: pandas.Series) -> None:
        """
        Get the stats applicable to numeric types.

        :param raw_column: Column having raw data.
        :type raw_column: pandas.Series
        """
        # TODO: Maybe add max/min value from the data set
        pass

    def _fill_stats_if_text_or_categorical_feature(self, raw_column: pandas.Series) -> None:
        """
        Get the stats applicable to text or categorical types.

        :param raw_column: Column having raw data.
        :type raw_column: pandas.Series
        """
        # Check if the string column is date time
        self.is_datetime = self._check_if_column_is_datetime(raw_column)

        # If the type is detected as date time, then return as other stats don't apply
        if self.is_datetime:
            return

        # If this is not date time feature, then compute the further stats for text data
        # Convert values in the column to strings
        raw_column_str = raw_column.apply(str)
        self.lengths = raw_column_str.apply(len)
        self.num_unique_lens = self.lengths.unique().shape[0]

        for column_entry in raw_column_str:
            self.average_number_spaces += column_entry.count(' ')

        self.average_entry_length = 1.0 * (sum(self.lengths) / self.total_number_vals)
        self.average_number_spaces /= 1.0 * self.total_number_vals

        self.cardinality_ratio = (1.0 * self.num_unique_vals) / self.total_number_vals

    def _check_if_column_is_datetime(self, raw_column: pandas.Series) -> bool:
        """
        Take a raw column and return 'True' if this is detected as datetime and 'False' otherwise.

        :param raw_column: Column having raw data.
        :type raw_column: pandas.Series
        :return: True is detected type is datetime and False otherwise
        """
        # If the first valid entry is not datetime format, then return False
        if not is_known_date_time_format(
                str(raw_column[raw_column.first_valid_index()])):
            return False

        # Drop all invalid entries from the column
        non_na = raw_column.dropna()

        # Convert non_na to strings
        nan_na_str = non_na.apply(str)

        # Detect if the column has date time data in a known format
        num_dates = np.sum(nan_na_str.apply(is_known_date_time_format))

        # Check if the all valid strings match the date time format
        if num_dates != nan_na_str.shape[0]:
            return False

        # Try inferring dates
        try:
            actual_dates = pandas.to_datetime(nan_na_str, infer_datetime_format=True,
                                              box=False)
        except ValueError:
            # If dates cannot be inferred, then return False
            return False

        # Check if all the valid entries pass by pandas date time function
        if actual_dates.shape[0] == non_na.shape[0] and non_na.shape[0] > 0:
            return True

        # date time not detected case
        return False


class PreprocessingStatistics:
    """
    Keeps statistics about the pre-processing stage in AutoML.

    Records the number of various feature types detected from
    the raw data
    """

    def __init__(self):
        """Initialize all statistics about the raw data."""
        # Dictionary to capture all raw feature stats_computation
        self.num_raw_feature_type_detected = defaultdict(int)   # type: DefaultDict[str, int]

    def update_raw_feature_stats(self, feature_type):
        """Increment the counters for different types of features."""
        if feature_type in FeatureTypeRecognizer.FULL_SET:
            self.num_raw_feature_type_detected[feature_type] += 1

    def get_raw_data_stats(self):
        """Return the string for overall raw feature stats_computation."""
        str_overall_raw_stats = 'The stats_computation for raw data are following:-'
        for feature_type in FeatureTypeRecognizer.FULL_SET:
            str_overall_raw_stats += \
                '\n\tNumber of ' + feature_type + ' features: ' + \
                str(self.num_raw_feature_type_detected[feature_type])

        return str_overall_raw_stats
