# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Time nearest selector class."""

from ..aggregators.aggregator import Aggregator
from .enricher_selector import EnricherTimeSelector
from ..granularities.granularity import TimeGranularity
from ..accessories.time_data import TimeData
from .._utils.random_utils import random_tag

import copy

from multimethods import multimethod
from ..environ import RuntimeEnv, SparkEnv, PandasEnv

from pyspark.sql.functions import udf
from pyspark.sql.types import TimestampType


class TimeNearestSelector (EnricherTimeSelector):
    """Time nearest selector with rounding to different time granularities."""

    def __init__(self, _granularity: TimeGranularity):
        """Intialize with time granularity."""
        self.granularity = _granularity

    @multimethod(SparkEnv, TimeData, object)
    def _prepare_time_join(self, env, public_data, nearest_udf):
        """Prepare time join by adding rounded time column."""
        _public_dataset = public_data.data

        # round time to nearest hour for joining data and for input customer_data
        ds_join_time = 'ds_join_time' + random_tag()
        public_dataset = _public_dataset.withColumn(
            ds_join_time,
            nearest_udf(_public_dataset[public_data.time_column_name]))\
            .drop(public_data.time_column_name)

        return public_dataset, ds_join_time

    @multimethod(PandasEnv, TimeData, object)
    def _prepare_time_join(self, env, public_data, nearest_udf):
        """Prepare time join by adding rounded time column."""
        public_dataset = public_data.data

        # round time to nearest hour for joining data and for input customer_data
        ds_join_time = 'ds_join_time' + random_tag()
        public_dataset[ds_join_time] = public_dataset[public_data.time_column_name].apply(
            nearest_udf).drop(columns=[public_data.time_column_name], axis=1)

        return public_dataset, ds_join_time

    @multimethod(SparkEnv, TimeData, TimeData, Aggregator, list, bool)
    def _time_join_nearest(self, env, customer_data, public_data, aggregator, join_keys, debug):
        """Join customer data with public data, with aggregator applied."""
        nearest_udf = udf(self.round_to(self.granularity), TimestampType())
        public_dataset, ds_join_time = self._prepare_time_join(env, public_data, nearest_udf)

        # add 3p data in (cols already filtered for only join cols + cols that are needed)
        # join on time
        # make new col for time join if necessary
        customer_join_time = 'customer_join_time' + random_tag()
        join_keys.append((customer_join_time, ds_join_time))

        id_time_customer_dataset = customer_data.data.withColumn(
            customer_join_time,
            nearest_udf(customer_data.data[customer_data.time_column_name]))

        altered_customer_data = copy.copy(customer_data)
        altered_customer_data.data = id_time_customer_dataset

        if debug:
            print('* id_time_customer_dataset: %d' % id_time_customer_dataset.count())
            print(id_time_customer_dataset)

        public_dataset = aggregator.process_public_dataset(env, public_dataset, public_data.cols, join_keys)

        if debug:
            print('* public_dataset in time_nearest_selector: %d' % public_dataset.count())
            print(public_dataset)

        if not aggregator.should_direct_join:
            join_conditions = []
            for pair in join_keys:
                join_conditions.append(id_time_customer_dataset[pair[0]] == public_dataset[pair[1]])
            public_dataset = public_dataset.alias('a').join(
                id_time_customer_dataset.alias('b'),
                join_conditions)\
                .select('a.*')

        if debug:
            print(
                '* public_dataset after join with id_time_customer_dataset: %d' %
                (public_dataset.count()))
            print(public_dataset)

        filtered_public_data = copy.copy(public_data)
        filtered_public_data.data = public_dataset

        if debug:
            print('* join_keys: %s' + str(join_keys))

        return altered_customer_data, filtered_public_data, join_keys

    @multimethod(PandasEnv, TimeData, TimeData, Aggregator, list, bool)
    def _time_join_nearest(self, env, customer_data, public_data, aggregator, join_keys, debug):
        """Join customer data with public data, with aggregator applied."""
        nearest_udf = self.round_to(self.granularity)
        public_dataset, ds_join_time = self._prepare_time_join(env, public_data, nearest_udf)

        # add 3p data in (cols already filtered for only join cols + cols that are needed)
        # join on time
        # make new col for time join if necessary
        customer_join_time = 'customer_join_time' + random_tag()
        join_keys.append((customer_join_time, ds_join_time))

        id_time_customer_dataset = customer_data.data
        id_time_customer_dataset[customer_join_time] = id_time_customer_dataset[customer_data.time_column_name].apply(
            nearest_udf)

        altered_customer_data = copy.copy(customer_data)
        altered_customer_data.data = id_time_customer_dataset

        if debug:
            print('* id_time_customer_dataset: %d' % len(id_time_customer_dataset.index))
            print(id_time_customer_dataset.head(5))
            print('* public_dataset in time_nearest_selector: %d' % len(public_dataset.index))
            print(public_dataset.head(5))

        public_dataset = aggregator.process_public_dataset(env, public_dataset, public_data.cols, join_keys)

        if debug:
            print('* public_dataset in time_nearest_selector: %d' % len(public_dataset.index))
            print(public_dataset.head(5))

        if not aggregator.should_direct_join:
            customer_keys, public_keys = list(zip(*join_keys))
            public_dataset = public_dataset.merge(
                id_time_customer_dataset,
                left_on=list(public_keys),
                right_on=list(customer_keys))[list(public_dataset.columns)]

        if debug:
            print('* public_dataset after join with id_time_customer_dataset: %d' % len(public_dataset.index))
            print(public_dataset.head(5))

        filtered_public_data = copy.copy(public_data)
        filtered_public_data.data = public_dataset

        if debug:
            print('* join_keys: %s' + str(join_keys))

        return altered_customer_data, filtered_public_data, join_keys

    def process(
            self,
            env: RuntimeEnv,
            customer_data: TimeData,
            public_data: TimeData,
            aggregator: Aggregator,
            join_keys: list = [],
            debug: bool = False):
        """Do enrichment."""
        # Round down timestamp to nearest hour

        # join on time
        return self._time_join_nearest(env, customer_data, public_data, aggregator, join_keys, debug)
