# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Aggregator min class."""

from .aggregator import Aggregator
from ..environ import SparkEnv, PandasEnv
from multimethods import multimethod

from pyspark.sql.functions import min


class AggregatorMin(Aggregator):
    """Get mininum based on join_keys."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'min')

    @multimethod(SparkEnv, object, object, list)
    def process_public_dataset(self, env, _public_dataset, cols, join_keys):
        """
        Get mininum value based on join_keys.

        :param _public_dataset: input object
        :param cols: column name list which the user wants to retrieve
        :param join_keys: join key pairs
        :return: aggregated public dataset
        """
        keys = [pair[1] for pair in join_keys]
        min_aggs = []
        for col in _public_dataset.columns:
            if (cols is None or col in cols) and (col not in keys):
                min_aggs.append(min(col))
        agg_public_dataset = _public_dataset.groupBy(*keys).agg(*min_aggs)
        return agg_public_dataset

    @multimethod(PandasEnv, object, object, list)
    def process_public_dataset(self, env, _public_dataset, cols, join_keys):
        """
        Get mininum value based on join_keys.

        :param _public_dataset: input object
        :param cols: column name list which the user wants to retrieve
        :param join_keys: join key pairs
        :return: aggregated public dataset
        """
        keys = [pair[1] for pair in join_keys]
        agg_public_dataset = _public_dataset.groupby(by=keys).min()
        agg_public_dataset.reset_index(inplace=True)
        return agg_public_dataset
