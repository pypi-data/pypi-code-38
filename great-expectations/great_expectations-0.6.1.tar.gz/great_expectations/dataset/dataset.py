from __future__ import division

import inspect
import sys
from six import PY3, string_types
from functools import wraps
from numbers import Number
from dateutil.parser import parse
from datetime import datetime

if sys.version_info.major == 2:  # If python 2
    from itertools import izip_longest as zip_longest
    from backports.functools_lru_cache import lru_cache
elif sys.version_info.major == 3:  # If python 3
    from itertools import zip_longest
    from functools import lru_cache

from great_expectations.data_asset.base import DataAsset
from great_expectations.data_asset.util import DocInherit, parse_result_format
from great_expectations.dataset.util import (
    is_valid_partition_object,
    is_valid_categorical_partition_object,
    is_valid_continuous_partition_object,
    _scipy_distribution_positional_args_from_dict,
    validate_distribution_parameters,
)

import pandas as pd
import numpy as np
from scipy import stats


class MetaDataset(DataAsset):
    """
    Holds expectation decorators.
    """

    @classmethod
    def column_aggregate_expectation(cls, func):
        """Constructs an expectation using column-aggregate semantics.

        The column_aggregate_expectation decorator handles boilerplate issues surrounding the common pattern of \
        evaluating truthiness of some condition on an aggregated-column basis.

        Args:
            func (function): \
                The function implementing an expectation using an aggregate property of a column. \
                The function should take a column of data and return the aggregate value it computes.

        Notes:
            column_aggregate_expectation *excludes null values* from being passed to the function

        See also:
            :func:`expect_column_mean_to_be_between <great_expectations.data_asset.dataset.Dataset.expect_column_mean_to_be_between>` \
            for an example of a column_aggregate_expectation
        """
        if PY3:
            argspec = inspect.getfullargspec(func)[0][1:]
        else:
            argspec = inspect.getargspec(func)[0][1:]

        @cls.expectation(argspec)
        @wraps(func)
        def inner_wrapper(self, column, result_format=None, *args, **kwargs):

            if result_format is None:
                result_format = self.default_expectation_args["result_format"]
            # Retain support for string-only output formats:
            result_format = parse_result_format(result_format)

            element_count = self.get_row_count()
            nonnull_count = self.get_column_nonnull_count(column)
            null_count = element_count - nonnull_count

            evaluation_result = func(self, column, *args, **kwargs)

            if 'success' not in evaluation_result:
                raise ValueError(
                    "Column aggregate expectation failed to return required information: success")

            if ('result' not in evaluation_result) or ('observed_value' not in evaluation_result['result']):
                raise ValueError(
                    "Column aggregate expectation failed to return required information: observed_value")

            return_obj = {
                'success': bool(evaluation_result['success'])
            }

            if result_format['result_format'] == 'BOOLEAN_ONLY':
                return return_obj

            return_obj['result'] = {
                'observed_value': evaluation_result['result']['observed_value'],
                "element_count": element_count,
                "missing_count": null_count,
                "missing_percent": null_count * 1.0 / element_count if element_count > 0 else None
            }

            if result_format['result_format'] == 'BASIC':
                return return_obj

            if 'details' in evaluation_result['result']:
                return_obj['result']['details'] = evaluation_result['result']['details']

            if result_format['result_format'] in ["SUMMARY", "COMPLETE"]:
                return return_obj

            raise ValueError("Unknown result_format %s." %
                                (result_format['result_format'],))

        return inner_wrapper


class Dataset(MetaDataset):

    # getter functions with hashable arguments - can be cached
    hashable_getters = [
        'get_column_max',
        'get_column_mean',
        'get_column_median',
        'get_column_min',
        'get_column_modes',
        'get_column_nonnull_count',
        'get_column_stdev',
        'get_column_sum',
        'get_column_unique_count',
        'get_column_value_counts',
        'get_row_count',
        'get_table_columns',
        'get_column_count_in_range',
    ]

    def __init__(self, *args, **kwargs):
        # NOTE: using caching makes the strong assumption that the user will not modify the core data store
        # (e.g. self.spark_df) over the lifetime of the dataset instance
        self.caching = kwargs.pop("caching", False)

        super(Dataset, self).__init__(*args, **kwargs)

        if self.caching:
            for func in self.hashable_getters:
                caching_func = lru_cache(maxsize=None)(getattr(self, func))
                setattr(self, func, caching_func)

    def get_row_count(self):
        """Returns: int, table row count"""
        raise NotImplementedError

    def get_table_columns(self):
        """Returns: List[str], list of column names"""
        raise NotImplementedError

    def get_column_nonnull_count(self, column):
        """Returns: int"""
        raise NotImplementedError

    def get_column_mean(self, column):
        """Returns: float"""
        raise NotImplementedError

    def get_column_value_counts(self, column):
        """Returns: pd.Series of value counts for a column, sorted by value"""
        raise NotImplementedError

    def get_column_sum(self, column):
        """Returns: float"""
        raise NotImplementedError

    def get_column_max(self, column, parse_strings_as_datetimes=False):
        """Returns: any"""
        raise NotImplementedError

    def get_column_min(self, column, parse_strings_as_datetimes=False):
        """Returns: any"""
        raise NotImplementedError

    def get_column_unique_count(self, column):
        """Returns: int"""
        raise NotImplementedError

    def get_column_modes(self, column):
        """Returns: List[any], list of modes (ties OK)"""
        raise NotImplementedError

    def get_column_median(self, column):
        """Returns: any"""
        raise NotImplementedError

    def get_column_stdev(self, column):
        """Returns: float"""
        raise NotImplementedError

    def get_column_hist(self, column, bins):
        """Returns: List[int], a list of counts corresponding to bins"""
        raise NotImplementedError

    def get_column_count_in_range(self, column, min_val=None, max_val=None, min_strictly=False, max_strictly=True):
        """Returns: int"""
        raise NotImplementedError

    def _initialize_expectations(self, config=None, data_asset_name=None):
        """Override data_asset_type with "Dataset"
        """
        super(Dataset, self)._initialize_expectations(config=config, data_asset_name=data_asset_name)
        self._expectations_config["data_asset_type"] = "Dataset"

    @classmethod
    def column_map_expectation(cls, func):
        """Constructs an expectation using column-map semantics.

        The column_map_expectation decorator handles boilerplate issues surrounding the common pattern of evaluating
        truthiness of some condition on a per-row basis.

        Args:
            func (function): \
                The function implementing a row-wise expectation. The function should take a column of data and \
                return an equally-long column of boolean values corresponding to the truthiness of the \
                underlying expectation.

        Notes:
            column_map_expectation intercepts and takes action based on the following parameters:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

            column_map_expectation *excludes null values* from being passed to the function

            Depending on the `result_format` selected, column_map_expectation can additional data to a return object, \
            including `element_count`, `nonnull_values`, `nonnull_count`, `success_count`, `unexpected_list`, and \
            `unexpected_index_list`. See :func:`_format_map_output <great_expectations.data_asset.dataset.Dataset._format_map_output>`

        See also:
            :func:`expect_column_values_to_be_unique <great_expectations.data_asset.dataset.Dataset.expect_column_values_to_be_unique>` \
            for an example of a column_map_expectation
        """
        raise NotImplementedError

    def test_column_map_expectation_function(self, function, *args, **kwargs):
        """Test a column map expectation function

        Args:
            function (func): The function to be tested. (Must be a valid column_map_expectation function.)
            *args          : Positional arguments to be passed the the function
            **kwargs       : Keyword arguments to be passed the the function

        Returns:
            A JSON-serializable expectation result object.

        Notes:
            This function is a thin layer to allow quick testing of new expectation functions, without having to define custom classes, etc.
            To use developed expectations from the command-line tool, you'll still need to define custom classes, etc.

            Check out :ref:`custom_expectations` for more information.
        """

        new_function = self.column_map_expectation(function)
        return new_function(self, *args, **kwargs)

    def test_column_aggregate_expectation_function(self, function, *args, **kwargs):
        """Test a column aggregate expectation function

        Args:
            function (func): The function to be tested. (Must be a valid column_aggregate_expectation function.)
            *args          : Positional arguments to be passed the the function
            **kwargs       : Keyword arguments to be passed the the function

        Returns:
            A JSON-serializable expectation result object.

        Notes:
            This function is a thin layer to allow quick testing of new expectation functions, without having to define custom classes, etc.
            To use developed expectations from the command-line tool, you'll still need to define custom classes, etc.

            Check out :ref:`custom_expectations` for more information.
        """

        new_function = self.column_aggregate_expectation(function)
        return new_function(self, *args, **kwargs)

    ##### Table shape expectations #####

    @DocInherit
    @DataAsset.expectation(["column"])
    def expect_column_to_exist(
        self, column, column_index=None, result_format=None, include_config=False, catch_exceptions=None, meta=None
    ):
        """Expect the specified column to exist.

        expect_column_to_exist is a :func:`expectation <great_expectations.data_asset.dataset.Dataset.expectation>`, not a \
        `column_map_expectation` or `column_aggregate_expectation`.

        Args:
            column (str): \
                The column name.

        Other Parameters:
            column_index (int or None): \
                If not None, checks the order of the columns. The expectation will fail if the \
                column is not in location column_index (zero-indexed).
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        columns = self.get_table_columns()
        if column in columns:
            return {
                # FIXME: list.index does not check for duplicate values.
                "success": (column_index is None) or (columns.index(column) == column_index)
            }
        else:
            return {"success": False}

    @DocInherit
    @DataAsset.expectation(["column_list"])
    def expect_table_columns_to_match_ordered_list(
        self,
        column_list,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the columns to exactly match a specified list.

        expect_table_columns_to_match_ordered_list is a :func:`expectation <great_expectations.data_asset.dataset.Dataset.expectation>`, not a \
        `column_map_expectation` or `column_aggregate_expectation`.

        Args:
            column_list (list of str): \
                The column names, in the correct order.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        columns = self.get_table_columns()
        if list(columns) == list(column_list):
            return {
                "success": True
            }
        else:
            # In the case of differing column lengths between the defined expectation and the observed column set, the
            # max is determined to generate the column_index.
            number_of_columns = max(len(column_list), len(columns))
            column_index = range(number_of_columns)

            # Create a list of the mismatched details
            compared_lists = list(zip_longest(column_index, list(column_list), list(columns)))
            mismatched = [{"Expected Column Position": i,
                           "Expected": k,
                           "Found": v} for i, k, v in compared_lists if k != v]
            return {
                "success": False,
                "details": {"mismatched": mismatched}
            }

    @DocInherit
    @DataAsset.expectation(['min_value', 'max_value'])
    def expect_table_row_count_to_be_between(
        self,
        min_value=None,
        max_value=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the number of rows to be between two values.

        expect_table_row_count_to_be_between is a :func:`expectation <great_expectations.data_asset.dataset.Dataset.expectation>`, \
        not a `column_map_expectation` or `column_aggregate_expectation`.

        Keyword Args:
            min_value (int or None): \
                The minimum number of rows, inclusive.
            max_value (int or None): \
                The maximum number of rows, inclusive.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound, and the number of acceptable rows has no minimum.
            * If max_value is None, then min_value is treated as a lower bound, and the number of acceptable rows has no maximum.

        See Also:
            expect_table_row_count_to_equal
        """
        try:
            if min_value is not None:
                if not float(min_value).is_integer():
                    raise ValueError("min_value must be integer")
            if max_value is not None:
                if not float(max_value).is_integer():
                    raise ValueError("max_value must be integer")
        except ValueError:
            raise ValueError("min_value and max_value must be integers")

        # check that min_value or max_value is set
        if min_value is None and max_value is None:
            raise Exception('Must specify either or both of min_value and max_value')

        row_count = self.get_row_count()

        if min_value is not None and max_value is not None:
            outcome = row_count >= min_value and row_count <= max_value

        elif min_value is None and max_value is not None:
            outcome = row_count <= max_value

        elif min_value is not None and max_value is None:
            outcome = row_count >= min_value

        return {
            'success': outcome,
            'result': {
                'observed_value': row_count
            }
        }

    @DocInherit
    @DataAsset.expectation(['value'])
    def expect_table_row_count_to_equal(self,
                                        value,
                                        result_format=None, include_config=False, catch_exceptions=None, meta=None
                                        ):
        """Expect the number of rows to equal a value.

        expect_table_row_count_to_equal is a basic :func:`expectation <great_expectations.data_asset.dataset.Dataset.expectation>`, \
        not a `column_map_expectation` or `column_aggregate_expectation`.

        Args:
            value (int): \
                The expected number of rows.

        Other Parameters:
            result_format (string or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_table_row_count_to_be_between
        """
        try:
            if not float(value).is_integer():
                raise ValueError("value must be an integer")
        except ValueError:
            raise ValueError("value must be an integer")

        row_count = self.get_row_count()

        return {
            'success': row_count == value,
            'result': {
                'observed_value': row_count
            }
        }

    ##### Missing values, unique values, and types #####

    def expect_column_values_to_be_unique(self,
                                          column,
                                          mostly=None,
                                          result_format=None, include_config=False, catch_exceptions=None, meta=None
                                          ):
        """Expect each column value to be unique.

        This expectation detects duplicates. All duplicated values are counted as exceptions.

        For example, `[1, 2, 3, 3, 3]` will return `[3, 3, 3]` in `result.exceptions_list`, with `unexpected_percent=0.6.`

        expect_column_values_to_be_unique is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.
        """
        raise NotImplementedError

    def expect_column_values_to_not_be_null(self,
                                            column,
                                            mostly=None,
                                            result_format=None, include_config=False, catch_exceptions=None, meta=None
                                            ):
        """Expect column values to not be null.

        To be counted as an exception, values must be explicitly null or missing, such as a NULL in PostgreSQL or an np.NaN in pandas.
        Empty strings don't count as null unless they have been coerced to a null type.

        expect_column_values_to_not_be_null is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_be_null

        """
        raise NotImplementedError

    def expect_column_values_to_be_null(self,
                                        column,
                                        mostly=None,
                                        result_format=None, include_config=False, catch_exceptions=None, meta=None
                                        ):
        """Expect column values to be null.

        expect_column_values_to_be_null is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_not_be_null

        """
        raise NotImplementedError

    def expect_column_values_to_be_of_type(
        self,
        column,
        type_,
        mostly=None,
        result_format=None, include_config=False, catch_exceptions=None, meta=None
    ):
        """Expect each column entry to be a specified data type.

        expect_column_values_to_be_of_type is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            type\_ (str): \
                A string representing the data type that each column should have as entries.
                For example, "double integer" refers to an integer with double precision.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Warning:
            expect_column_values_to_be_of_type is slated for major changes in future versions of great_expectations.

            As of v0.3, great_expectations is exclusively based on pandas, which handles typing in its own peculiar way.
            Future versions of great_expectations will allow for Datasets in SQL, spark, etc.
            When we make that change, we expect some breaking changes in parts of the codebase that are based strongly on pandas notions of typing.

        See also:
            expect_column_values_to_be_in_type_list
        """
        raise NotImplementedError

    def expect_column_values_to_be_in_type_list(
        self,
        column,
        type_list,
        mostly=None,
        result_format=None, include_config=False, catch_exceptions=None, meta=None
    ):
        """Expect each column entry to match a list of specified data types.

        expect_column_values_to_be_in_type_list is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            type_list (list of str): \
                A list of strings representing the data type that each column should have as entries.
                For example, "double integer" refers to an integer with double precision.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Warning:
            expect_column_values_to_be_in_type_list is slated for major changes in future versions of great_expectations.

            As of v0.3, great_expectations is exclusively based on pandas, which handles typing in its own peculiar way.
            Future versions of great_expectations will allow for Datasets in SQL, spark, etc.
            When we make that change, we expect some breaking changes in parts of the codebase that are based strongly on pandas notions of typing.

        See also:
            expect_column_values_to_be_of_type
        """
        raise NotImplementedError

    ##### Sets and ranges #####

    def expect_column_values_to_be_in_set(self,
                                          column,
                                          value_set,
                                          mostly=None,
                                          parse_strings_as_datetimes=None,
                                          result_format=None, include_config=False, catch_exceptions=None, meta=None
                                          ):
        """Expect each column value to be in a given set.

        For example:
        ::

            # my_df.my_col = [1,2,2,3,3,3]
            >>> my_df.expect_column_values_to_be_in_set(
                "my_col",
                [2,3]
            )
            {
              "success": false
              "result": {
                "unexpected_count": 1
                "unexpected_percent": 0.16666666666666666,
                "unexpected_percent_nonmissing": 0.16666666666666666,
                "partial_unexpected_list": [
                  1
                ],
              },
            }

        expect_column_values_to_be_in_set is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.


        Args:
            column (str): \
                The column name.
            value_set (set-like): \
                A set of objects used for comparison.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.
            parse_strings_as_datetimes (boolean or None) : If True values provided in value_set will be parsed as \
                datetimes before making comparisons.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_not_be_in_set
        """
        raise NotImplementedError

    def expect_column_values_to_not_be_in_set(self,
                                              column,
                                              value_set,
                                              mostly=None,
                                              parse_strings_as_datetimes=None,
                                              result_format=None, include_config=False, catch_exceptions=None, meta=None
                                              ):
        """Expect column entries to not be in the set.

        For example:
        ::

            # my_df.my_col = [1,2,2,3,3,3]
            >>> my_df.expect_column_values_to_not_be_in_set(
                "my_col",
                [1,2]
            )
            {
              "success": false
              "result": {
                "unexpected_count": 3
                "unexpected_percent": 0.5,
                "unexpected_percent_nonmissing": 0.5,
                "partial_unexpected_list": [
                  1, 2, 2
                ],
              },
            }

        expect_column_values_to_not_be_in_set is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            value_set (set-like): \
                A set of objects used for comparison.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_be_in_set
        """
        raise NotImplementedError

    def expect_column_values_to_be_between(self,
                                           column,
                                           min_value=None,
                                           max_value=None,
                                           allow_cross_type_comparisons=None,
                                           parse_strings_as_datetimes=False,
                                           output_strftime_format=None,
                                           mostly=None,
                                           result_format=None, include_config=False, catch_exceptions=None, meta=None
                                           ):
        """Expect column entries to be between a minimum value and a maximum value (inclusive).

        expect_column_values_to_be_between is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            min_value (comparable type or None): The minimum value for a column entry.
            max_value (comparable type or None): The maximum value for a column entry.

        Keyword Args:
            allow_cross_type_comparisons (boolean or None) : If True, allow comparisons between types (e.g. integer and\
                string). Otherwise, attempting such comparisons will raise an exception.
            parse_strings_as_datetimes (boolean or None) : If True, parse min_value, max_value, and all non-null column\
                values to datetimes before making comparisons.
            output_strftime_format (str or None): \
                A valid strfime format for datetime output. Only used if parse_strings_as_datetimes=True.

            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound, and the number of acceptable rows has no minimum.
            * If max_value is None, then min_value is treated as a lower bound, and the number of acceptable rows has no maximum.

        See Also:
            expect_column_value_lengths_to_be_between

        """
        raise NotImplementedError

    def expect_column_values_to_be_increasing(self,
                                              column,
                                              strictly=None,
                                              parse_strings_as_datetimes=False,
                                              mostly=None,
                                              result_format=None, include_config=False, catch_exceptions=None, meta=None
                                              ):
        """Expect column values to be increasing.

        By default, this expectation only works for numeric or datetime data.
        When `parse_strings_as_datetimes=True`, it can also parse strings to datetimes.

        If `strictly=True`, then this expectation is only satisfied if each consecutive value
        is strictly increasing--equal values are treated as failures.

        expect_column_values_to_be_increasing is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            strictly (Boolean or None): \
                If True, values must be strictly greater than previous values
            parse_strings_as_datetimes (boolean or None) : \
                If True, all non-null column values to datetimes before making comparisons
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_be_decreasing
        """
        raise NotImplementedError

    def expect_column_values_to_be_decreasing(self,
                                              column,
                                              strictly=None,
                                              parse_strings_as_datetimes=False,
                                              mostly=None,
                                              result_format=None, include_config=False, catch_exceptions=None, meta=None
                                              ):
        """Expect column values to be decreasing.

        By default, this expectation only works for numeric or datetime data.
        When `parse_strings_as_datetimes=True`, it can also parse strings to datetimes.

        If `strictly=True`, then this expectation is only satisfied if each consecutive value
        is strictly decreasing--equal values are treated as failures.

        expect_column_values_to_be_decreasing is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            strictly (Boolean or None): \
                If True, values must be strictly greater than previous values
            parse_strings_as_datetimes (boolean or None) : \
                If True, all non-null column values to datetimes before making comparisons
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_be_increasing

        """
        raise NotImplementedError

    ##### String matching #####

    def expect_column_value_lengths_to_be_between(self,
                                                  column,
                                                  min_value=None,
                                                  max_value=None,
                                                  mostly=None,
                                                  result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                  ):
        """Expect column entries to be strings with length between a minimum value and a maximum value (inclusive).

        This expectation only works for string-type values. Invoking it on ints or floats will raise a TypeError.

        expect_column_value_lengths_to_be_between is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            min_value (int or None): \
                The minimum value for a column entry length.
            max_value (int or None): \
                The maximum value for a column entry length.
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound, and the number of acceptable rows has no minimum.
            * If max_value is None, then min_value is treated as a lower bound, and the number of acceptable rows has no maximum.

        See Also:
            expect_column_value_lengths_to_equal
        """
        raise NotImplementedError

    def expect_column_value_lengths_to_equal(self,
                                             column,
                                             value,
                                             mostly=None,
                                             result_format=None, include_config=False, catch_exceptions=None, meta=None
                                             ):
        """Expect column entries to be strings with length equal to the provided value.

        This expectation only works for string-type values. Invoking it on ints or floats will raise a TypeError.

        expect_column_values_to_be_between is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            value (int or None): \
                The expected value for a column entry length.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_value_lengths_to_be_between
        """
        raise NotImplementedError


    def expect_column_values_to_match_regex(self,
                                            column,
                                            regex,
                                            mostly=None,
                                            result_format=None, include_config=False, catch_exceptions=None, meta=None
                                            ):
        """Expect column entries to be strings that match a given regular expression. Valid matches can be found \
        anywhere in the string, for example "[at]+" will identify the following strings as expected: "cat", "hat", \
        "aa", "a", and "t", and the following strings as unexpected: "fish", "dog".

        expect_column_values_to_match_regex is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            regex (str): \
                The regular expression the column entries should match.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_not_match_regex
            expect_column_values_to_match_regex_list
        """
        raise NotImplementedError

    def expect_column_values_to_not_match_regex(self,
                                                column,
                                                regex,
                                                mostly=None,
                                                result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                ):
        """Expect column entries to be strings that do NOT match a given regular expression. The regex must not match \
        any portion of the provided string. For example, "[at]+" would identify the following strings as expected: \
        "fish", "dog", and the following as unexpected: "cat", "hat".

        expect_column_values_to_not_match_regex is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            regex (str): \
                The regular expression the column entries should NOT match.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_match_regex
            expect_column_values_to_match_regex_list
        """
        raise NotImplementedError

    def expect_column_values_to_match_regex_list(self,
                                                 column,
                                                 regex_list,
                                                 match_on="any",
                                                 mostly=None,
                                                 result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                 ):
        """Expect the column entries to be strings that can be matched to either any of or all of a list of regular expressions.
        Matches can be anywhere in the string.

        expect_column_values_to_match_regex_list is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            regex_list (list): \
                The list of regular expressions which the column entries should match

        Keyword Args:
            match_on= (string): \
                "any" or "all".
                Use "any" if the value should match at least one regular expression in the list.
                Use "all" if it should match each regular expression in the list.
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_match_regex
            expect_column_values_to_not_match_regex
        """
        raise NotImplementedError

    def expect_column_values_to_not_match_regex_list(self, column, regex_list,
                                                     mostly=None,
                                                     result_format=None, include_config=False, catch_exceptions=None, meta=None):
        """Expect the column entries to be strings that do not match any of a list of regular expressions. Matches can \
        be anywhere in the string.


        expect_column_values_to_not_match_regex_list is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            regex_list (list): \
                The list of regular expressions which the column entries should not match

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_match_regex_list
        """
        raise NotImplementedError

    ##### Datetime and JSON parsing #####

    def expect_column_values_to_match_strftime_format(self,
                                                      column,
                                                      strftime_format,
                                                      mostly=None,
                                                      result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                      ):
        """Expect column entries to be strings representing a date or time with a given format.

        expect_column_values_to_match_strftime_format is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.
            strftime_format (str): \
                A strftime format string to use for matching

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        raise NotImplementedError

    def expect_column_values_to_be_dateutil_parseable(self,
                                                      column,
                                                      mostly=None,
                                                      result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                      ):
        """Expect column entries to be parseable using dateutil.

        expect_column_values_to_be_dateutil_parseable is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.
        """
        raise NotImplementedError

    def expect_column_values_to_be_json_parseable(self,
                                                  column,
                                                  mostly=None,
                                                  result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                  ):
        """Expect column entries to be data written in JavaScript Object Notation.

        expect_column_values_to_be_json_parseable is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_match_json_schema
        """
        raise NotImplementedError

    def expect_column_values_to_match_json_schema(self,
                                                  column,
                                                  json_schema,
                                                  mostly=None,
                                                  result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                  ):
        """Expect column entries to be JSON objects matching a given JSON schema.

        expect_column_values_to_match_json_schema is a :func:`column_map_expectation <great_expectations.data_asset.dataset.Dataset.column_map_expectation>`.

        Args:
            column (str): \
                The column name.

        Keyword Args:
            mostly (None or a float between 0 and 1): \
                Return `"success": True` if at least mostly percent of values match the expectation. \
                For more detail, see :ref:`mostly`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_values_to_be_json_parseable

            The JSON-schema docs at: http://json-schema.org/
        """
        raise NotImplementedError

    ##### Aggregate functions #####

    def expect_column_parameterized_distribution_ks_test_p_value_to_be_greater_than(self,
                                                                                    column, distribution,
                                                                                    p_value=0.05, params=None,
                                                                                    result_format=None,
                                                                                    include_config=False,
                                                                                    catch_exceptions=None, meta=None):
        """
        Expect the column values to be distributed similarly to a scipy distribution. \

        This expectation compares the provided column to the specified continuous distribution with a parameteric \
        Kolmogorov-Smirnov test. The K-S test compares the provided column to the cumulative density function (CDF) of \
        the specified scipy distribution. If you don't know the desired distribution shape parameters, use the \
        `ge.dataset.util.infer_distribution_parameters()` utility function to estimate them.

        It returns 'success'=True if the p-value from the K-S test is greater than or equal to the provided p-value.

        expect_column_parameterized_distribution_ks_test_p_value_to_be_greater_than is a \
        :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            distribution (str): \
                The scipy distribution name. See: https://docs.scipy.org/doc/scipy/reference/stats.html
            p_value (float): \
                The threshold p-value for a passing test. Default is 0.05.
            params (dict or list) : \
                A dictionary or positional list of shape parameters that describe the distribution you want to test the\
                data against. Include key values specific to the distribution from the appropriate scipy \
                distribution CDF function. 'loc' and 'scale' are used as translational parameters.\
                See https://docs.scipy.org/doc/scipy/reference/stats.html#continuous-distributions

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "details":
                        "expected_params" (dict): The specified or inferred parameters of the distribution to test against
                        "ks_results" (dict): The raw result of stats.kstest()
                }

            * The Kolmogorov-Smirnov test's null hypothesis is that the column is similar to the provided distribution.
            * Supported scipy distributions:
                -norm
                -beta
                -gamma
                -uniform
                -chi2
                -expon

        """
        raise NotImplementedError

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_distinct_values_to_equal_set(self,
                                                   column,
                                                   value_set,
                                                   parse_strings_as_datetimes=None,
                                                   result_format=None, include_config=False, catch_exceptions=None, meta=None):
        """Expect the set of distinct column values to equal a given set.

        In contrast to expect_column_distinct_values_to_contain_set() this ensures not only that a certain set of values are present in the column but that these _and only these values_ are present.

        For example:
        ::

            # my_df.my_col = [1,2,2,3,3,3]
            >>> my_df.expect_column_distinct_values_to_equal_set(
                "my_col",
                [2,3]
            )
            {
              "success": false
              "result": {
                "observed_value": [1,2,3]
              },
            }

        expect_column_distinct_values_to_equal_set is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.


        Args:
            column (str): \
                The column name.
            value_set (set-like): \
                A set of objects used for comparison.

        Keyword Args:
            parse_strings_as_datetimes (boolean or None) : If True values provided in value_set will be parsed as \
                datetimes before making comparisons.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_distinct_values_to_contain_set
        """
        if parse_strings_as_datetimes:
            parsed_value_set = self._parse_value_set(value_set)
        else:
            parsed_value_set = value_set

        expected_value_set = set(parsed_value_set)
        observed_value_set = set(self.get_column_value_counts(column).index)

        return {
            "success": observed_value_set == expected_value_set,
            "result": {
                "observed_value": sorted(list(observed_value_set))
            }
        }


    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_distinct_values_to_contain_set(self,
                                                    column,
                                                    value_set,
                                                    parse_strings_as_datetimes=None,
                                                    result_format=None, include_config=False, catch_exceptions=None, meta=None):
        """Expect the set of distinct column values to contain a given set.

        In contrast to expect_column_values_to_be_in_set() this ensures not that all column values are members of the given set but that values from the set _must_ be present in the column

        For example:
        ::

            # my_df.my_col = [1,2,2,3,3,3]
            >>> my_df.expect_column_distinct_values_to_contain_set(
                "my_col",
                [2,3]
            )
            {
            "success": true
            "result": {
                "observed_value": [1,2,3]
            },
            }

        expect_column_distinct_values_to_contain_set is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.


        Args:
            column (str): \
                The column name.
            value_set (set-like): \
                A set of objects used for comparison.

        Keyword Args:
            parse_strings_as_datetimes (boolean or None) : If True values provided in value_set will be parsed as \
                datetimes before making comparisons.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        See Also:
            expect_column_distinct_values_to_equal_set
        """
        if parse_strings_as_datetimes:
            parsed_value_set = self._parse_value_set(value_set)
        else:
            parsed_value_set = value_set

        expected_value_set = set(parsed_value_set)
        observed_value_set = set(self.get_column_value_counts(column).index)

        return {
            "success": observed_value_set.issuperset(expected_value_set),
            "result": {
                "observed_value": sorted(list(observed_value_set))
            }
        }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_mean_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the column mean to be between a minimum value and a maximum value (inclusive).

        expect_column_mean_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            min_value (float or None): \
                The minimum value for the column mean.
            max_value (float or None): \
                The maximum value for the column mean.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The true mean for the column
                }

            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound.
            * If max_value is None, then min_value is treated as a lower bound.

        See Also:
            expect_column_median_to_be_between
            expect_column_stdev_to_be_between
        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        if min_value is not None and not isinstance(min_value, (Number)):
            raise ValueError("min_value must be a number")

        if max_value is not None and not isinstance(max_value, (Number)):
            raise ValueError("max_value must be a number")

        col_avg = self.get_column_mean(column)

        # Handle possible missing values
        if col_avg is None:
            return {
                'success': False,
                'result': {
                    'observed_value': col_avg
                }
            }
        else:
            if min_value != None and max_value != None:
                success = (min_value <= col_avg) and (col_avg <= max_value)

            elif min_value == None and max_value != None:
                success = (col_avg <= max_value)

            elif min_value != None and max_value == None:
                success = (min_value <= col_avg)

            return {
                'success': success,
                'result': {
                    'observed_value': col_avg
                }
            }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_median_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the column median to be between a minimum value and a maximum value.

        expect_column_median_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            min_value (int or None): \
                The minimum value for the column median.
            max_value (int or None): \
                The maximum value for the column median.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The true median for the column
                }

            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        See Also:
            expect_column_mean_to_be_between
            expect_column_stdev_to_be_between

        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        column_median = self.get_column_median(column)

        if column_median is None:
            return {
                'success': False,
                'result': {
                    'observed_value': None
                }
            }
        else:
            return {
                "success": (
                    ((min_value is None) or (min_value <= column_median)) and
                    ((max_value is None) or (column_median <= max_value))
                ),
                "result": {
                    "observed_value": column_median
                }
            }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_stdev_to_be_between(self,
                                         column,
                                         min_value=None,
                                         max_value=None,
                                         result_format=None, include_config=False, catch_exceptions=None, meta=None
                                         ):
        """Expect the column standard deviation to be between a minimum value and a maximum value.

        expect_column_stdev_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            min_value (float or None): \
                The minimum value for the column standard deviation.
            max_value (float or None): \
                The maximum value for the column standard deviation.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The true standard deviation for the column
                }

            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        See Also:
            expect_column_mean_to_be_between
            expect_column_median_to_be_between
        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        column_stdev = self.get_column_stdev(column)

        return {
            "success": (
                ((min_value is None) or (min_value <= column_stdev)) and
                ((max_value is None) or (column_stdev <= max_value))
            ),
            "result": {
                "observed_value": column_stdev
            }
        }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_unique_value_count_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the number of unique values to be between a minimum value and a maximum value.

        expect_column_unique_value_count_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            min_value (int or None): \
                The minimum number of unique values allowed.
            max_value (int or None): \
                The maximum number of unique values allowed.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (int) The number of unique values in the column
                }

            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        See Also:
            expect_column_proportion_of_unique_values_to_be_between
        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        unique_value_count = self.get_column_unique_count(column)

        # Handle possible missing values
        if unique_value_count is None:
            return {
                'success': False,
                'result': {
                    'observed_value': unique_value_count
                }
            }
        else:
            return {
                "success": (
                    ((min_value is None) or (min_value <= unique_value_count)) and
                    ((max_value is None) or (unique_value_count <= max_value))
                ),
                "result": {
                    "observed_value": unique_value_count
                }
            }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_proportion_of_unique_values_to_be_between(
        self,
        column,
        min_value=0,
        max_value=1,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the proportion of unique values to be between a minimum value and a maximum value.

        For example, in a column containing [1, 2, 2, 3, 3, 3, 4, 4, 4, 4], there are 4 unique values and 10 total \
        values for a proportion of 0.4.

        Args:
            column (str): \
                The column name.
            min_value (float or None): \
                The minimum proportion of unique values. (Proportions are on the range 0 to 1)
            max_value (float or None): \
                The maximum proportion of unique values. (Proportions are on the range 0 to 1)

        expect_column_unique_value_count_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The proportion of unique values in the column
                }

            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        See Also:
            expect_column_unique_value_count_to_be_between
        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        unique_value_count = self.get_column_unique_count(column)
        total_value_count = self.get_column_nonnull_count(column)

        if total_value_count > 0:
            proportion_unique = float(unique_value_count) / total_value_count
        else:
            proportion_unique = None

        return {
            "success": (
                ((min_value is None) or (min_value <= proportion_unique)) and
                ((max_value is None) or (proportion_unique <= max_value))
            ),
            "result": {
                "observed_value": proportion_unique
            }
        }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_most_common_value_to_be_in_set(
        self,
        column,
        value_set,
        ties_okay=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the most common value to be within the designated value set

        expect_column_most_common_value_to_be_in_set is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name
            value_set (set-like): \
                A list of potential values to match

        Keyword Args:
            ties_okay (boolean or None): \
                If True, then the expectation will still succeed if values outside the designated set are as common (but not more common) than designated values

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (list) The most common values in the column
                }

            `observed_value` contains a list of the most common values.
            Often, this will just be a single element. But if there's a tie for most common among multiple values,
            `observed_value` will contain a single copy of each most common value.

        """
        mode_list = self.get_column_modes(column)
        intersection_count = len(set(value_set).intersection(mode_list))

        if ties_okay:
            success = intersection_count > 0
        else:
            success = len(mode_list) == 1 and intersection_count == 1

        return {
            'success': success,
            'result': {
                'observed_value': mode_list
            }
        }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_sum_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the column to sum to be between an min and max value

        expect_column_sum_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name
            min_value (comparable type or None): \
                The minimum number of unique values allowed.
            max_value (comparable type or None): \
                The maximum number of unique values allowed.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (list) The actual column sum
                }


            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        """
        # TODO check for column type
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        col_sum = self.get_column_sum(column)

        # Handle possible missing values
        if col_sum is None:
            return {
                'success': False,
                'result': {
                    'observed_value': col_sum
                }
            }
        else:
            if min_value is not None and max_value is not None:
                success = (min_value <= col_sum) and (col_sum <= max_value)

            elif min_value is None and max_value is not None:
                success = (col_sum <= max_value)

            elif min_value is not None and max_value is None:
                success = (min_value <= col_sum)

            return {
                'success': success,
                'result': {
                    'observed_value': col_sum
                }
            }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_min_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        parse_strings_as_datetimes=False,
        output_strftime_format=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the column to sum to be between an min and max value

        expect_column_min_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name
            min_value (comparable type or None): \
                The minimum number of unique values allowed.
            max_value (comparable type or None): \
                The maximum number of unique values allowed.

        Keyword Args:
            parse_strings_as_datetimes (Boolean or None): \
                If True, parse min_value, max_values, and all non-null column values to datetimes before making comparisons.
            output_strftime_format (str or None): \
                A valid strfime format for datetime output. Only used if parse_strings_as_datetimes=True.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (list) The actual column min
                }


            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        """
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        if parse_strings_as_datetimes:
            if min_value:
                min_value = parse(min_value)
            if max_value:
                max_value = parse(max_value)

        col_min = self.get_column_min(column, parse_strings_as_datetimes)

        if col_min is None:
            success = False
        elif min_value is not None and max_value is not None:
            success = (min_value <= col_min) and (col_min <= max_value)
        elif min_value is None and max_value is not None:
            success = (col_min <= max_value)
        elif min_value is not None and max_value is None:
            success = (min_value <= col_min)

        if parse_strings_as_datetimes:
            if output_strftime_format:
                col_min = datetime.strftime(col_min, output_strftime_format)
            else:
                col_min = str(col_min)
        return {
            'success': success,
            'result': {
                'observed_value': col_min
            }
        }

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_max_to_be_between(
        self,
        column,
        min_value=None,
        max_value=None,
        parse_strings_as_datetimes=False,
        output_strftime_format=None,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the column max to be between an min and max value

        expect_column_max_to_be_between is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name
            min_value (comparable type or None): \
                The minimum number of unique values allowed.
            max_value (comparable type or None): \
                The maximum number of unique values allowed.

        Keyword Args:
            parse_strings_as_datetimes (Boolean or None): \
                If True, parse min_value, max_values, and all non-null column values to datetimes before making comparisons.
            output_strftime_format (str or None): \
                A valid strfime format for datetime output. Only used if parse_strings_as_datetimes=True.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (list) The actual column max
                }


            * min_value and max_value are both inclusive.
            * If min_value is None, then max_value is treated as an upper bound
            * If max_value is None, then min_value is treated as a lower bound

        """
        # TODO spark tests
        if min_value is None and max_value is None:
            raise ValueError("min_value and max_value cannot both be None")

        if parse_strings_as_datetimes:
            if min_value:
                min_value = parse(min_value)
            if max_value:
                max_value = parse(max_value)

        col_max = self.get_column_max(column, parse_strings_as_datetimes)

        if col_max is None:
            success = False
        elif min_value is not None and max_value is not None:
            success = (min_value <= col_max) and (col_max <= max_value)
        elif min_value is None and max_value is not None:
            success = (col_max <= max_value)
        elif min_value is not None and max_value is None:
            success = (min_value <= col_max)

        if parse_strings_as_datetimes:
            if output_strftime_format:
                col_max = datetime.strftime(col_max, output_strftime_format)
            else:
                col_max = str(col_max)

        return {
            "success": success,
            "result": {
                "observed_value": col_max
            }
        }

    # Distributional expectations
    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_chisquare_test_p_value_to_be_greater_than(
        self,
        column,
        partition_object=None,
        p=0.05,
        tail_weight_holdout=0,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect column values to be distributed similarly to the provided categorical partition. \

        This expectation compares categorical distributions using a Chi-squared test. \
        It returns `success=True` if values in the column match the distribution of the provided partition.

        expect_column_chisquare_test_p_value_to_be_greater_than is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            partition_object (dict): \
                The expected partition object (see :ref:`partition_object`).
            p (float): \
                The p-value threshold for rejecting the null hypothesis of the Chi-Squared test.\
                For values below the specified threshold, the expectation will return `success=False`,\
                rejecting the null hypothesis that the distributions are the same.\
                Defaults to 0.05.

        Keyword Args:
            tail_weight_holdout (float between 0 and 1 or None): \
                The amount of weight to split uniformly between values observed in the data but not present in the \
                provided partition. tail_weight_holdout provides a mechanism to make the test less strict by \
                assigning positive weights to unknown values observed in the data that are not present in the \
                partition.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The true p-value of the Chi-squared test
                    "details": {
                        "observed_partition" (dict):
                            The partition observed in the data.
                        "expected_partition" (dict):
                            The partition expected from the data, after including tail_weight_holdout
                    }
                }
        """
        if not is_valid_categorical_partition_object(partition_object):
            raise ValueError("Invalid partition object.")

        element_count = self.get_column_nonnull_count(column)
        observed_frequencies = self.get_column_value_counts(column)
        # Convert to Series object to allow joining on index values
        expected_column = pd.Series(
            partition_object['weights'], index=partition_object['values'], name='expected') * element_count
        # Join along the indices to allow proper comparison of both types of possible missing values
        # test_df = pd.concat([expected_column, observed_frequencies], axis=1, sort=True) # Sort parameter not available before pandas 0.23.0
        test_df = pd.concat([expected_column, observed_frequencies], axis=1)

        na_counts = test_df.isnull().sum()

        # Handle NaN: if we expected something that's not there, it's just not there.
        test_df[column] = test_df[column].fillna(0)
        # Handle NaN: if something's there that was not expected, substitute the relevant value for tail_weight_holdout
        if na_counts['expected'] > 0:
            # Scale existing expected values
            test_df['expected'] = test_df['expected'] * (1 - tail_weight_holdout)
            # Fill NAs with holdout.
            test_df['expected'] = test_df['expected'].fillna(
                element_count * (tail_weight_holdout / na_counts['expected']))

        test_result = stats.chisquare(
            test_df[column], test_df['expected'])[1]

        return {
            "success": test_result > p,
            "result": {
                "observed_value": test_result,
                "details": {
                    "observed_partition": {
                        "values": test_df.index.tolist(),
                        "weights": test_df[column].tolist()
                    },
                    "expected_partition": {
                        "values": test_df.index.tolist(),
                        "weights": test_df['expected'].tolist()
                    }
                }
            }
        }

    def expect_column_bootstrapped_ks_test_p_value_to_be_greater_than(self,
                                                                      column,
                                                                      partition_object=None,
                                                                      p=0.05,
                                                                      bootstrap_samples=None,
                                                                      bootstrap_sample_size=None,
                                                                      result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                                      ):
        """Expect column values to be distributed similarly to the provided continuous partition. This expectation \
        compares continuous distributions using a bootstrapped Kolmogorov-Smirnov test. It returns `success=True` if \
        values in the column match the distribution of the provided partition.

        The expected cumulative density function (CDF) is constructed as a linear interpolation between the bins, \
        using the provided weights. Consequently the test expects a piecewise uniform distribution using the bins from \
        the provided partition object.

        expect_column_bootstrapped_ks_test_p_value_to_be_greater_than is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            partition_object (dict): \
                The expected partition object (see :ref:`partition_object`).
            p (float): \
                The p-value threshold for the Kolmogorov-Smirnov test.
                For values below the specified threshold the expectation will return `success=False`, rejecting the \
                null hypothesis that the distributions are the same. \
                Defaults to 0.05.

        Keyword Args:
            bootstrap_samples (int): \
                The number bootstrap rounds. Defaults to 1000.
            bootstrap_sample_size (int): \
                The number of samples to take from the column for each bootstrap. A larger sample will increase the \
                specificity of the test. Defaults to 2 * len(partition_object['weights'])

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                    "observed_value": (float) The true p-value of the KS test
                    "details": {
                        "bootstrap_samples": The number of bootstrap rounds used
                        "bootstrap_sample_size": The number of samples taken from
                            the column in each bootstrap round
                        "observed_cdf": The cumulative density function observed
                            in the data, a dict containing 'x' values and cdf_values
                            (suitable for plotting)
                        "expected_cdf" (dict):
                            The cumulative density function expected based on the
                            partition object, a dict containing 'x' values and
                            cdf_values (suitable for plotting)
                        "observed_partition" (dict):
                            The partition observed on the data, using the provided
                            bins but also expanding from min(column) to max(column)
                        "expected_partition" (dict):
                            The partition expected from the data. For KS test,
                            this will always be the partition_object parameter
                    }
                }

        """
        raise NotImplementedError

    @DocInherit
    @MetaDataset.column_aggregate_expectation
    def expect_column_kl_divergence_to_be_less_than(
        self,
        column,
        partition_object=None,
        threshold=None,
        tail_weight_holdout=0,
        internal_weight_holdout=0,
        result_format=None,
        include_config=False,
        catch_exceptions=None,
        meta=None,
    ):
        """Expect the Kulback-Leibler (KL) divergence (relative entropy) of the specified column with respect to the \
        partition object to be lower than the provided threshold.

        KL divergence compares two distributions. The higher the divergence value (relative entropy), the larger the \
        difference between the two distributions. A relative entropy of zero indicates that the data are \
        distributed identically, `when binned according to the provided partition`.

        In many practical contexts, choosing a value between 0.5 and 1 will provide a useful test.

        This expectation works on both categorical and continuous partitions. See notes below for details.

        expect_column_kl_divergence_to_be_less_than is a :func:`column_aggregate_expectation <great_expectations.data_asset.dataset.Dataset.column_aggregate_expectation>`.

        Args:
            column (str): \
                The column name.
            partition_object (dict): \
                The expected partition object (see :ref:`partition_object`).
            threshold (float): \
                The maximum KL divergence to for which to return `success=True`. If KL divergence is larger than the\
                provided threshold, the test will return `success=False`.

        Keyword Args:
            internal_weight_holdout (float between 0 and 1 or None): \
                The amount of weight to split uniformly among zero-weighted partition bins. internal_weight_holdout \
                provides a mechanims to make the test less strict by assigning positive weights to values observed in \
                the data for which the partition explicitly expected zero weight. With no internal_weight_holdout, \
                any value observed in such a region will cause KL divergence to rise to +Infinity.\
                Defaults to 0.
            tail_weight_holdout (float between 0 and 1 or None): \
                The amount of weight to add to the tails of the histogram. Tail weight holdout is split evenly between\
                (-Infinity, min(partition_object['bins'])) and (max(partition_object['bins']), +Infinity). \
                tail_weight_holdout provides a mechanism to make the test less strict by assigning positive weights to \
                values observed in the data that are not present in the partition. With no tail_weight_holdout, \
                any value observed outside the provided partition_object will cause KL divergence to rise to +Infinity.\
                Defaults to 0.

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        Notes:
            These fields in the result object are customized for this expectation:
            ::

                {
                  "observed_value": (float) The true KL divergence (relative entropy) or None if the value is calculated \
                  as infinity, -infinity, or NaN
                  "details": {
                    "observed_partition": (dict) The partition observed in the data
                    "expected_partition": (dict) The partition against which the data were compared,
                                            after applying specified weight holdouts.
                  }
                }

            If the partition_object is categorical, this expectation will expect the values in column to also be \
            categorical.

                * If the column includes values that are not present in the partition, the tail_weight_holdout will be \
                equally split among those values, providing a mechanism to weaken the strictness of the expectation \
                (otherwise, relative entropy would immediately go to infinity).
                * If the partition includes values that are not present in the column, the test will simply include \
                zero weight for that value.

            If the partition_object is continuous, this expectation will discretize the values in the column according \
            to the bins specified in the partition_object, and apply the test to the resulting distribution.

                * The internal_weight_holdout and tail_weight_holdout parameters provide a mechanism to weaken the \
                expectation, since an expected weight of zero would drive relative entropy to be infinite if any data \
                are observed in that interval.
                * If internal_weight_holdout is specified, that value will be distributed equally among any intervals \
                with weight zero in the partition_object.
                * If tail_weight_holdout is specified, that value will be appended to the tails of the bins \
                ((-Infinity, min(bins)) and (max(bins), Infinity).

          If relative entropy/kl divergence goes to infinity for any of the reasons mentioned above, the observed value\
          will be set to None. This is because inf, -inf, Nan, are not json serializable and cause some json parsers to\
          crash when encountered. The python None token will be serialized to null in json. 

        See also:
            expect_column_chisquare_test_p_value_to_be_greater_than
            expect_column_bootstrapped_ks_test_p_value_to_be_greater_than

        """
        if not is_valid_partition_object(partition_object):
            raise ValueError("Invalid partition object.")

        if (not isinstance(threshold, (int, float))) or (threshold < 0):
            raise ValueError(
                "Threshold must be specified, greater than or equal to zero.")

        if (not isinstance(tail_weight_holdout, (int, float))) or (tail_weight_holdout < 0) or (tail_weight_holdout > 1):
            raise ValueError(
                "tail_weight_holdout must be between zero and one.")

        if (not isinstance(internal_weight_holdout, (int, float))) or (internal_weight_holdout < 0) or (internal_weight_holdout > 1):
            raise ValueError(
                "internal_weight_holdout must be between zero and one.")
            
        if(tail_weight_holdout != 0 and "tail_weights" in partition_object):
            raise ValueError(
                "tail_weight_holdout must be 0 when using tail_weights in partition object")

        # TODO: add checks for duplicate values in is_valid_categorical_partition_object
        if is_valid_categorical_partition_object(partition_object):
            if internal_weight_holdout > 0:
                raise ValueError(
                    "Internal weight holdout cannot be used for discrete data.")

            # Data are expected to be discrete, use value_counts
            observed_weights = self.get_column_value_counts(column) / self.get_column_nonnull_count(column)
            expected_weights = pd.Series(
                partition_object['weights'], index=partition_object['values'], name='expected')
            # test_df = pd.concat([expected_weights, observed_weights], axis=1, sort=True) # Sort not available before pandas 0.23.0
            test_df = pd.concat([expected_weights, observed_weights], axis=1)

            na_counts = test_df.isnull().sum()

            # Handle NaN: if we expected something that's not there, it's just not there.
            pk = test_df[column].fillna(0)
            # Handle NaN: if something's there that was not expected, substitute the relevant value for tail_weight_holdout
            if na_counts['expected'] > 0:
                # Scale existing expected values
                test_df['expected'] = test_df['expected'] * \
                    (1 - tail_weight_holdout)
                # Fill NAs with holdout.
                qk = test_df['expected'].fillna(
                    tail_weight_holdout / na_counts['expected'])
            else:
                qk = test_df['expected']

            kl_divergence = stats.entropy(pk, qk)

            if(np.isinf(kl_divergence) or np.isnan(kl_divergence)):
                observed_value = None
            else:
                observed_value = kl_divergence

            return_obj = {
                "success": kl_divergence <= threshold,
                "result": {
                    "observed_value": observed_value,
                    "details": {
                        "observed_partition": {
                            "values": test_df.index.tolist(),
                            "weights": pk.tolist()
                        },
                        "expected_partition": {
                            "values": test_df.index.tolist(),
                            "weights": qk.tolist()
                        }
                    }
                }
            }

        else:
            # Data are expected to be continuous; discretize first
            # Build the histogram first using expected bins so that the largest bin is >=
            hist = np.array(self.get_column_hist(column, partition_object['bins']))
            # np.histogram(column, partition_object['bins'], density=False)
            bin_edges = partition_object['bins']
            # Add in the frequencies observed above or below the provided partition
            # below_partition = len(np.where(column < partition_object['bins'][0])[0])
            # above_partition = len(np.where(column > partition_object['bins'][-1])[0])
            below_partition = self.get_column_count_in_range(column, max_val=partition_object['bins'][0], max_strictly=True)
            above_partition = self.get_column_count_in_range(column, min_val=partition_object['bins'][-1], min_strictly=True)

            #Observed Weights is just the histogram values divided by the total number of observations
            observed_weights = np.array(hist) / self.get_column_nonnull_count(column)

            #Adjust expected_weights to account for tail_weight and internal_weight
            if "tail_weights" in partition_object:
	                partition_tail_weight_holdout = np.sum(partition_object["tail_weights"])
            else:
                partition_tail_weight_holdout = 0

            expected_weights = np.array(
                partition_object['weights']) * (1 - tail_weight_holdout - internal_weight_holdout)

            # Assign internal weight holdout values if applicable
            if internal_weight_holdout > 0:
                zero_count = len(expected_weights) - \
                    np.count_nonzero(expected_weights)
                if zero_count > 0:
                    for index, value in enumerate(expected_weights):
                        if value == 0:
                            expected_weights[index] = internal_weight_holdout / zero_count
        
            # Assign tail weight holdout if applicable
            # We need to check cases to only add tail weight holdout if it makes sense based on the provided partition.
            if (partition_object['bins'][0] == -np.inf) and (partition_object['bins'][-1]) == np.inf:
                if tail_weight_holdout > 0:
                    raise ValueError("tail_weight_holdout cannot be used for partitions with infinite endpoints.")
                if "tail_weights" in partition_object:
                    raise ValueError("There can be no tail weights for partitions with one or both endpoints at infinity")
                expected_bins = partition_object['bins'][1:-1] #Remove -inf and inf
                
                comb_expected_weights=expected_weights
                expected_tail_weights=np.concatenate(([expected_weights[0]],[expected_weights[-1]])) #Set aside tail weights
                expected_weights=expected_weights[1:-1] #Remove tail weights
                
                comb_observed_weights=observed_weights
                observed_tail_weights=np.concatenate(([observed_weights[0]],[observed_weights[-1]])) #Set aside tail weights
                observed_weights=observed_weights[1:-1] #Remove tail weights
                
                
            elif (partition_object['bins'][0] == -np.inf):
                
                if "tail_weights" in partition_object:
                    raise ValueError("There can be no tail weights for partitions with one or both endpoints at infinity")
                
                expected_bins = partition_object['bins'][1:] #Remove -inf
                
                comb_expected_weights=np.concatenate((expected_weights,[tail_weight_holdout]))
                expected_tail_weights=np.concatenate(([expected_weights[0]],[tail_weight_holdout])) #Set aside left tail weight and holdout
                expected_weights = expected_weights[1:] #Remove left tail weight from main expected_weights
                
                comb_observed_weights=np.concatenate((observed_weights,[above_partition / self.get_column_nonnull_count(column)]))
                observed_tail_weights=np.concatenate(([observed_weights[0]],[above_partition / self.get_column_nonnull_count(column)])) #Set aside left tail weight and above parition weight
                observed_weights=observed_weights[1:] #Remove left tail weight from main observed_weights
        
            elif (partition_object['bins'][-1] == np.inf):

                if "tail_weights" in partition_object:
                    raise ValueError("There can be no tail weights for partitions with one or both endpoints at infinity")

                expected_bins = partition_object['bins'][:-1] #Remove inf

                comb_expected_weights=np.concatenate(([tail_weight_holdout],expected_weights))
                expected_tail_weights=np.concatenate(([tail_weight_holdout],[expected_weights[-1]]))  #Set aside right tail weight and holdout
                expected_weights = expected_weights[:-1] #Remove right tail weight from main expected_weights

                comb_observed_weights=np.concatenate(([below_partition/self.get_column_nonnull_count(column)],observed_weights))
                observed_tail_weights=np.concatenate(([below_partition/self.get_column_nonnull_count(column)],[observed_weights[-1]])) #Set aside right tail weight and below partition weight
                observed_weights=observed_weights[:-1] #Remove right tail weight from main observed_weights
            else:

                expected_bins = partition_object['bins'] #No need to remove -inf or inf

                if "tail_weights" in partition_object:
                    tail_weights=partition_object["tail_weights"]
                    comb_expected_weights=np.concatenate(([tail_weights[0]],expected_weights,[tail_weights[1]])) #Tack on tail weights
                    expected_tail_weights=np.array(tail_weights) #Tail weights are just tail_weights
                else:
                    comb_expected_weights=np.concatenate(([tail_weight_holdout / 2],expected_weights,[tail_weight_holdout / 2]))
                    expected_tail_weights=np.concatenate(([tail_weight_holdout / 2],[tail_weight_holdout / 2])) #Tail weights are just tail_weight holdout divided eaually to both tails

                comb_observed_weights=np.concatenate(([below_partition/self.get_column_nonnull_count(column)],observed_weights, [above_partition/self.get_column_nonnull_count(column)]))
                observed_tail_weights=np.concatenate(([below_partition],[above_partition])) / self.get_column_nonnull_count(column) #Tail weights are just the counts on either side of the partition
                #Main expected_weights and main observered weights had no tail_weights, so nothing needs to be removed.

     
            kl_divergence = stats.entropy(comb_observed_weights, comb_expected_weights) 
            
            if(np.isinf(kl_divergence) or np.isnan(kl_divergence)):
                observed_value = None
            else:
                observed_value = kl_divergence

            return_obj = {
                    "success": kl_divergence <= threshold,
                    "result": {
                        "observed_value": observed_value,
                        "details": {
                            "observed_partition": {
                                # return expected_bins, since we used those bins to compute the observed_weights
                                "bins": expected_bins,
                                "weights": observed_weights.tolist(),
                                "tail_weights":observed_tail_weights.tolist()
                            },
                            "expected_partition": {
                                "bins": expected_bins,
                                "weights": expected_weights.tolist(),
                                "tail_weights":expected_tail_weights.tolist()
                            }
                        }
                    }
                }
                
        return return_obj

    ### Column pairs ###

    def expect_column_pair_values_to_be_equal(self,
                                              column_A,
                                              column_B,
                                              ignore_row_if="both_values_are_missing",
                                              result_format=None, include_config=False, catch_exceptions=None, meta=None
                                              ):
        """
        Expect the values in column A to be the same as column B.

        Args:
            column_A (str): The first column name
            column_B (str): The second column name

        Keyword Args:
            ignore_row_if (str): "both_values_are_missing", "either_value_is_missing", "neither"

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        raise NotImplementedError

    def expect_column_pair_values_A_to_be_greater_than_B(self,
                                                         column_A,
                                                         column_B,
                                                         or_equal=None,
                                                         parse_strings_as_datetimes=False,
                                                         allow_cross_type_comparisons=None,
                                                         ignore_row_if="both_values_are_missing",
                                                         result_format=None, include_config=False, catch_exceptions=None, meta=None
                                                         ):
        """
        Expect values in column A to be greater than column B.

        Args:
            column_A (str): The first column name
            column_B (str): The second column name
            or_equal (boolean or None): If True, then values can be equal, not strictly greater

        Keyword Args:
            allow_cross_type_comparisons (boolean or None) : If True, allow comparisons between types (e.g. integer and\
                string). Otherwise, attempting such comparisons will raise an exception.

        Keyword Args:
            ignore_row_if (str): "both_values_are_missing", "either_value_is_missing", "neither

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        raise NotImplementedError

    def expect_column_pair_values_to_be_in_set(self,
                                               column_A,
                                               column_B,
                                               value_pairs_set,
                                               ignore_row_if="both_values_are_missing",
                                               result_format=None, include_config=False, catch_exceptions=None, meta=None
                                               ):
        """
        Expect paired values from columns A and B to belong to a set of valid pairs.

        Args:
            column_A (str): The first column name
            column_B (str): The second column name
            value_pairs_set (list of tuples): All the valid pairs to be matched

        Keyword Args:
            ignore_row_if (str): "both_values_are_missing", "either_value_is_missing", "never"

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        raise NotImplementedError

    ### Multicolumn pairs ###

    def expect_multicolumn_values_to_be_unique(self,
                                              column_list,
                                              ignore_row_if="all_values_are_missing",
                                              result_format=None, include_config=False, catch_exceptions=None, meta=None
                                              ):
        """
        Expect the values for each row to be unique across the columns listed.

        Args:
            column_list (tuple or list): The first column name

        Keyword Args:
            ignore_row_if (str): "all_values_are_missing", "any_value_is_missing", "never"

        Other Parameters:
            result_format (str or None): \
                Which output mode to use: `BOOLEAN_ONLY`, `BASIC`, `COMPLETE`, or `SUMMARY`.
                For more detail, see :ref:`result_format <result_format>`.
            include_config (boolean): \
                If True, then include the expectation config as part of the result object. \
                For more detail, see :ref:`include_config`.
            catch_exceptions (boolean or None): \
                If True, then catch exceptions and include them as part of the result object. \
                For more detail, see :ref:`catch_exceptions`.
            meta (dict or None): \
                A JSON-serializable dictionary (nesting allowed) that will be included in the output without modification. \
                For more detail, see :ref:`meta`.

        Returns:
            A JSON-serializable expectation result object.

            Exact fields vary depending on the values passed to :ref:`result_format <result_format>` and
            :ref:`include_config`, :ref:`catch_exceptions`, and :ref:`meta`.

        """
        raise NotImplementedError

    @staticmethod
    def _parse_value_set(value_set):
        parsed_value_set = [parse(value) if isinstance(value, string_types) else value for value in value_set]
        return parsed_value_set
