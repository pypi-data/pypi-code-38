# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common weather enricher class."""

from ..accessories.customer_data import CustomerData
from .enricher import Enricher
from ..granularities.granularity import LocationGranularity, LocationClosestGranularity
from ..selectors.location_closest_selector import LocationClosestSelector
from ..accessories.public_data import PublicData
from ..selectors.time_nearest_selector import TimeNearestSelector
from azureml.telemetry.activity import ActivityType, log_activity

from typing import List, Tuple


class CommonWeatherEnricher(Enricher):
    """
    Common weather enricher(GFS forecast, and ISD).

    They can be used to join with other data easily.
    """

    def __init__(self, public_data_object: PublicData, enable_telemetry: bool = False):
        """Intialize with public data object.

        :param public_data_object: public data
        :param enable_telemetry: whether to send telemetry
        """
        self.public_data = public_data_object
        super(CommonWeatherEnricher, self).__init__(enable_telemetry=enable_telemetry)

    def _get_location_granularity(self, _granularity: str)\
            -> LocationGranularity:
        """Get location granularity instance."""
        return LocationClosestGranularity(_closest_top_n=_granularity)

    def enrich_customer_data_with_agg(
        self,
        customer_data_object: CustomerData,
        agg: str,
        location_match_granularity: int = 1,
        time_round_granularity: str = 'hour')\
            -> Tuple[
                CustomerData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data with specified aggregator.

        :param customer_data_object: an instance of customer_data class
        :param agg: specified aggregator
        :param location_match_granularity: location_granularity.closest_top_n
        :param time_round_granularity: time_granularity
        :return: a tuple of enriched customer data (joined_data)
        """
        if self.enable_telemetry:
            self.log_properties['runtimeEnv'] = type(customer_data_object.env)
            self.log_properties['parameters'] = \
                'agg: %s, location_gran: %d, time_gran: %s' % (agg, location_match_granularity, time_round_granularity)
            with log_activity(
                    self.logger,
                    'enrich_customer_data_with_agg',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                _, _, joined_data, _ = self._enrich_customer_data(
                    customer_data_object, location_match_granularity, time_round_granularity, agg)
                return joined_data
        else:
            _, _, joined_data, _ = self._enrich_customer_data(
                customer_data_object, location_match_granularity, time_round_granularity, agg)
            return joined_data

    def enrich_customer_data_no_agg(
        self,
        customer_data_object: CustomerData,
        location_match_granularity: int = 1,
        time_round_granularity: str = 'hour')\
            -> Tuple[
                CustomerData,
                PublicData,
                List[Tuple[str, str]]]:
        """
        Enrich customer data with default aggregator_all.

        :param customer_data_object: an instance of customer_data class
        :param location_match_granularity: location_granularity.closest_top_n
        :param time_round_granularity: time_granularity
        :return: a tuple of enriched customer data (new_customer_data),
            processed_public_data
        """
        if self.enable_telemetry:
            self.log_properties['runtimeEnv'] = type(customer_data_object.env)
            self.log_properties['parameters'] = \
                'location_gran: %d, time_gran: %s' % (location_match_granularity, time_round_granularity)
            with log_activity(
                    self.logger,
                    'enrich_customer_data_no_agg',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties):
                new_customer_data, processed_public_data, _, _ = \
                    self._enrich_customer_data(
                        customer_data_object, location_match_granularity, time_round_granularity, 'all')
                return new_customer_data, processed_public_data
        else:
            new_customer_data, processed_public_data, _, _ = \
                self._enrich_customer_data(
                    customer_data_object, location_match_granularity, time_round_granularity, 'all')
            return new_customer_data, processed_public_data

    def _enrich_customer_data(
            self,
            customer_data_object: CustomerData,
            location_match_granularity: int = 1,
            time_round_granularity: str = 'hour',
            agg_strategy: str = 'all'):
        """
        Enrich customer data with specified aggregator.

        :param customer_data_object: an instance of customer_data class
        :param location_match_granularity: location_granularity.closest_top_n
        :param time_round_granularity: time_granularity
        :return: a tuple of:
            a new instance of class customer_data,
            unchanged instance of public_data,
            a new joined instance of class customer_data,
            join keys (list of tuple))
        """
        self.public_data.env = customer_data_object.env
        self.time_granularity = self._get_time_granularity(time_round_granularity)
        if self.time_granularity is None:
            raise ValueError('Unsupported time granularity' + time_round_granularity)
        self.time_selector = TimeNearestSelector(self.time_granularity)

        self.location_granularity = self._get_location_granularity(location_match_granularity)
        self.location_selector = LocationClosestSelector(self.location_granularity)

        self.aggregator = self._get_aggregator(agg_strategy)
        if self.aggregator is None:
            raise ValueError('Unsupported aggregator' + agg_strategy)

        return self.enrich(
            customer_data=customer_data_object,
            public_data=self.public_data,
            location_selector=self.location_selector,
            time_selector=self.time_selector,
            aggregator=self.aggregator)
