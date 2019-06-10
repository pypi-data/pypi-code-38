# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Aggregator top class."""

from .aggregator import Aggregator
from ..environ import SparkEnv, PandasEnv
from .._utils.random_utils import random_tag
from multimethods import multimethod

import pandas as pd

from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window


class AggregatorTop(Aggregator):
    """Get top N based on join_keys."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'top')

    def __init__(self, n: int = 1):
        """Initialize with top numbers."""
        self.top = n

    @multimethod(SparkEnv, object, object, list)
    def process_public_dataset(self, env, _public_dataset, cols, join_keys):
        """
        Get top N values based on the input join_keys.

        :param _public_dataset: input object
        :param join_keys: join key pairs
        :param cols: column name list which the user wants to retrieve
        :return: aggregated public dataset
        """
        keys = [pair[1] for pair in join_keys]
        window = Window.partitionBy(keys).orderBy(*keys)
        rn = 'rn' + random_tag()
        top_public_dataset = _public_dataset.withColumn(rn, row_number().over(window))\
            .where(col(rn) <= self.top).drop(rn)
        return top_public_dataset

    @multimethod(PandasEnv, object, object, list)
    def process_public_dataset(self, env, _public_dataset, cols, join_keys):
        """
        Get top N values based on the input join_keys.

        :param _public_dataset: input object
        :param join_keys: join key pairs
        :param cols: column name list which the user wants to retrieve
        :return: aggregated public dataset
        """
        keys = [pair[1] for pair in join_keys]
        agg_public_dataset = _public_dataset.groupby(by=keys)\
            .apply(pd.DataFrame.head, self.top)
        return agg_public_dataset.reset_index(drop=True)
