# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Aggregator base class for all kinds of aggregator.

    aggregator_all
    aggregator_avg
    aggregator_max
    aggregator_min
    aggregator_top
"""

from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..environ import RuntimeEnv, SparkEnv, PandasEnv
from multimethods import multimethod

import copy

from typing import List, Optional, Tuple


class Aggregator:
    """Do aggregation against specified columns join_keys."""

    should_direct_join = True

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None

    def process_public_dataset(
            self,
            env: RuntimeEnv,
            _public_dataset: object,
            cols: Optional[List[str]],
            join_keys: List[Tuple[str, str]] = []) -> object:
        """
        Do aggregation on specified public data columns.

        :param _public_dataset: public dataset dataframe
        :param cols: column name list which the user wants to retrieve
        :param join_keys: join keys used

        :return：new DataFrame of the public dataset
        """
        return _public_dataset

    @multimethod(SparkEnv, CustomerData, PublicData, list, bool)
    def process(self, env, customer_data, public_data, join_keys, debug):
        """
        Left join customer_data with public_data on join_keys.

        Drop all columns in join_keys and all columns which is in the list of
        to_be_cleaned_up_column_names afterward.

        :param customer_data: customer data
        :type customer_data: CustomerData
        :param public_data: public data
        :type public_data: PublicData
        :param join_keys: join key pairs
        :type join_keys: List[tuple]
        :param debug: print debug info if True
        :type debug: bool

        :return: A tuple of (
            a new instance of class CustomerData,
            unchanged instance of PublicData,
            a new joined instance of class CustomerData,
            join keys (list of tuple))
        :rtype: Tuple[
                    CustomerData,
                    PublicData,
                    CustomerData,
                    List[Tuple[str, str]]]
        """
        customer_dataset = customer_data.data
        public_dataset = public_data.data

        if debug:
            print('* customer_dataset: %d' % customer_dataset.count())
            print(customer_dataset)
            print('* processed_public_dataset: %d' % public_dataset.count())
            print(public_dataset)

        join_conditions = []
        for pair in join_keys:
            join_conditions.append(customer_dataset[pair[0]] == public_dataset[pair[1]])
        joined_dataset = customer_dataset.join(
            public_dataset,
            join_conditions,
            how="left")

        if debug:
            print('* joined_dataset: %d' % joined_dataset.count())
            print(joined_dataset)

        if not debug:
            joined_dataset = self._clean_up_columns(env, customer_data, joined_dataset, join_keys)
        joined_data = copy.copy(customer_data)
        joined_data.data = joined_dataset

        return customer_data, public_data, joined_data, join_keys

    @multimethod(PandasEnv, CustomerData, PublicData, list, bool)
    def process(self, env, customer_data, public_data, join_keys, debug):
        """
        Left join customer_data with public_data on join_keys.

        Drop all columns in join_keys and all columns which is in the list of
        to_be_cleaned_up_column_names afterward.

        :param customer_data: customer data
        :type customer_data: CustomerData
        :param public_data: public data
        :type public_data: PublicData
        :param join_keys: join key pairs
        :type join_keys: List[tuple]
        :param debug: print debug info if True
        :type debug: bool

        :return: A tuple of (
            a new instance of class CustomerData,
            unchanged instance of PublicData,
            a new joined instance of class CustomerData,
            join keys (list of tuple))
        :rtype: Tuple[
                    CustomerData,
                    PublicData,
                    CustomerData,
                    List[Tuple[str, str]]]
        """
        customer_dataset = customer_data.data
        public_dataset = public_data.data

        if debug:
            print('* customer_dataset: %d' % len(customer_dataset.index))
            print(customer_dataset.head(5))
            print('* processed_public_dataset: %d' % len(public_dataset.index))
            print(public_dataset.head(5))

        customer_keys, public_keys = list(zip(*join_keys))
        joined_dataset = customer_dataset.merge(
            public_dataset,
            left_on=customer_keys,
            right_on=public_keys,
            how="left")

        if debug:
            print('* joined_dataset: %d' % len(joined_dataset.index))
            print(joined_dataset.head(5))

        if not debug:
            joined_dataset = self._clean_up_columns(env, customer_data, joined_dataset, join_keys)
        joined_data = copy.copy(customer_data)
        joined_data.data = joined_dataset

        return customer_data, public_data, joined_data, join_keys

    @multimethod(SparkEnv, CustomerData, object, list)
    def _clean_up_columns(self, env, _joined_data, _joined_dataset, join_keys):
        """Clean up columns.

        :param _joined_data: customer data
        :param _joined_dataset: customer data frame
        :param join_keys: join keys
        :return: cleaned data frame
        """
        target_columns = \
            [key for pair in join_keys for key in pair] + \
            _joined_data.to_be_cleaned_up_column_names
        cleaned_joined_dataset = _joined_dataset\
            .drop(*target_columns)
        return cleaned_joined_dataset

    @multimethod(PandasEnv, CustomerData, object, list)
    def _clean_up_columns(self, env, _joined_data, _joined_dataset, join_keys):
        """Clean up columns.

        :param _joined_data: customer data
        :param _joined_dataset: customer data frame
        :param join_keys: join keys
        :return: cleaned data frame
        """
        to_be_target_columns = \
            [key for pair in join_keys for key in pair] + \
            _joined_data.to_be_cleaned_up_column_names
        joined_dataset_columns = list(_joined_dataset.columns)
        target_columns = []
        for col in to_be_target_columns:
            if col in joined_dataset_columns:
                target_columns.append(col)
            else:
                if (col + '_x') in joined_dataset_columns:
                    target_columns.append(col + '_x')
                if (col + '_y') in joined_dataset_columns:
                    target_columns.append(col + '_y')
        cleaned_joined_dataset = _joined_dataset\
            .drop(columns=target_columns, axis=1)
        return cleaned_joined_dataset
