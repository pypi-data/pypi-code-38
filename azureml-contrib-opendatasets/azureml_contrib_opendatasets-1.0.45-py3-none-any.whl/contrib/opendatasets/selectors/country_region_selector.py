# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Time nearest selector class."""

from ..aggregators.aggregator import Aggregator
from .enricher_selector import EnricherLocationSelector
from ..accessories.country_region_data import CORAvailableType, CountryOrRegionData
from ..granularities.granularity import Granularity

import copy

from typing import List, Tuple
from ..environ import RuntimeEnv
from .._utils.random_utils import random_tag


class EnricherCountryRegionSelector(EnricherLocationSelector):
    """CountryRegion related fundamental calculations, all are static member functions."""

    def __init__(self):
        """Intialize with none granularity."""
        self.granularity = Granularity()

    def countryregion_join(
            self,
            env,
            customer_data: CountryOrRegionData,
            public_data: CountryOrRegionData,
            aggregator: Aggregator,
            join_keys: list = [],
            debug: bool = False)\
            -> Tuple[
                CountryOrRegionData,
                CountryOrRegionData,
                List[Tuple[str, str]]]:
        """Join customer data with public data, with aggregator applied.

        :param customer_data: an instance of CountryOrRegionData class for customer data
        :param public_data: an instance of CountryOrRegionData class for public data
        :param aggregator: a specified aggregator
        :param join_keys: list of join key pairs
        :param debug: print debug logs if True
        :return: a tuple of:
            altered customer data class instance
            altered public data class instance
            a list of join key pairs
        """
        public_dataset = public_data.data
        id_countryregion_customer_dataset = customer_data.data

        pub_countryCode_column_name = public_data.countrycode_column_name
        pub_countryregion_column_name = public_data.country_or_region_column_name
        customer_countryCode_column_name = customer_data.countrycode_column_name
        customer_countryregion_column_name = customer_data.country_or_region_column_name

        ds_join_countryregion = "ds_join_" + pub_countryregion_column_name + random_tag()
        ds_join_countrycode = "ds_join_" + pub_countryCode_column_name + random_tag()
        customer_join_countryregion = "customer_join_countryregion" + random_tag()
        customer_join_countryCode = "customer_join_countryCode" + random_tag()

        if customer_data.available_column_type == CORAvailableType.All or \
           customer_data.available_column_type == CORAvailableType.CountryOrRegionName:

            join_keys.append((customer_join_countryregion, ds_join_countryregion))
            public_dataset = public_dataset.withColumnRenamed(pub_countryregion_column_name, ds_join_countryregion)

            id_countryregion_customer_dataset = id_countryregion_customer_dataset.withColumn(
                customer_join_countryregion,
                id_countryregion_customer_dataset[customer_countryregion_column_name])

        if customer_data.available_column_type == CORAvailableType.All or \
           customer_data.available_column_type == CORAvailableType.CountryCode:

            join_keys.append((customer_join_countryCode, ds_join_countrycode))
            public_dataset = public_dataset.withColumnRenamed(pub_countryCode_column_name, ds_join_countrycode)

            id_countryregion_customer_dataset = id_countryregion_customer_dataset.withColumn(
                customer_join_countryCode,
                id_countryregion_customer_dataset[customer_countryCode_column_name])

        # add 3p data in (cols already filtered for only join cols + cols that are needed)
        # join on time
        # make new col for time join if necessary
        altered_customer_data = copy.copy(customer_data)
        altered_customer_data.data = id_countryregion_customer_dataset

        if debug:
            print('* id_countryregion_customer_dataset: %d' % id_countryregion_customer_dataset.count())
            print(id_countryregion_customer_dataset)

        public_dataset = aggregator.process_public_dataset(env, public_dataset, join_keys)

        if debug:
            print('* public_dataset in country_region_selector: %d' % public_dataset.count())
            print(public_dataset)

        if debug:
            print(
                '* public_dataset after join with id_countryregion_customer_dataset: %d' %
                (public_dataset.count()))
            print(public_dataset)

        filtered_public_data = copy.copy(public_data)
        filtered_public_data.data = public_dataset

        if debug:
            print('* join_keys: %s' + str(join_keys))

        return altered_customer_data, filtered_public_data, join_keys

    def process(
            self,
            env: RuntimeEnv,
            customer_data: CountryOrRegionData,
            public_data: CountryOrRegionData,
            aggregator: Aggregator,
            join_keys: list = [],
            debug: bool = False)\
            -> Tuple[
                CountryOrRegionData,
                CountryOrRegionData,
                List[Tuple[str, str]]]:
        """
        Do enrichment for customer data with specified aggregator for public data.

        :param customer_data: an instance of CountryOrRegionData class
        :param public_data: an instance of CountryOrRegionData class
        :param aggregator: a specified aggregator
        :param join_keys: list of join key pairs
        :param debug: print debug logs if True
        :return: a tuple of:
            altered customer data class instance
            altered public data class instance
            a list of join key pairs
        """
        # join on time
        return self.countryregion_join(env, customer_data, public_data, aggregator, join_keys, debug)
