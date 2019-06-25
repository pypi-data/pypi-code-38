# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Generic enricher class for joining with different granularity and aggregators."""

from ..aggregators.aggregator import Aggregator
from ..aggregators.aggregator_all import AggregatorAll
from ..aggregators.aggregator_avg import AggregatorAvg
from ..aggregators.aggregator_max import AggregatorMax
from ..aggregators.aggregator_min import AggregatorMin
from ..aggregators.aggregator_top import AggregatorTop
from ..selectors.enricher_selector import (EnricherLocationSelector, EnricherTimeSelector)
from ..granularities.granularity import TimeGranularity, HourGranularity, DayGranularity, MonthGranularity
from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..aggregators.aggregator import Aggregator

from datetime import datetime
from dateutil.relativedelta import relativedelta
from multimethods import multimethod
from typing import List, Optional, Tuple

from .._utils.telemetry_utils import get_opendatasets_logger
from azureml.telemetry.activity import ActivityType, log_activity


@multimethod(datetime, HourGranularity)
def get_max_date_by_granularity(max_date, _granularity):
    """Get max date based on hour granularity."""
    return max_date + relativedelta(hours=1)


@multimethod(datetime, DayGranularity)
def get_max_date_by_granularity(max_date, _granularity):
    """Get max date based on day granularity."""
    return max_date + relativedelta(days=1)


@multimethod(datetime, MonthGranularity)
def get_max_date_by_granularity(max_date, _granularity):
    """Get max date based on month granularity."""
    return max_date + relativedelta(months=1)


class Enricher:
    """Enricher class."""

    debug = False

    def __init__(self, enable_telemetry: bool = False):
        """Intialize a new instance.

        :param enable_telemetry: whether to send telemetry
        """
        self.enable_telemetry = enable_telemetry
        if self.enable_telemetry:
            self.logger = get_opendatasets_logger(__name__)
            self.log_properties = self.get_common_log_properties()

    def _get_time_granularity(self, _granularity: str)\
            -> Optional[TimeGranularity]:
        """Get time granularity instance."""
        if _granularity.lower() == 'hour':
            return HourGranularity()
        elif _granularity.lower() == 'day':
            return DayGranularity()
        elif _granularity.lower() == 'month':
            return MonthGranularity()
        return None

    def _get_aggregator(self, name: str) -> Optional[Aggregator]:
        """Get aggregator instance."""
        if name.lower() == 'all':
            return AggregatorAll()
        elif name.lower() == 'avg':
            return AggregatorAvg()
        elif name.lower() == 'max':
            return AggregatorMax()
        elif name.lower() == 'min':
            return AggregatorMin()
        elif name.lower() == 'top':
            return AggregatorTop()
        return None

    def enrich(
            self,
            customer_data: CustomerData,
            public_data: PublicData,
            location_selector: EnricherLocationSelector,
            time_selector: EnricherTimeSelector,
            aggregator: Aggregator)\
            -> Tuple[
                CustomerData,
                PublicData,
                CustomerData,
                List[Tuple[str, str]]]:
        """
        Enrich input customer_data by applying selectors and aggregators.

        :param customer_data: an instance of customer_data derived class
        :param public_data: an instance of public_data derived class
        :param location_selector: an instance of
            enricher_time_selectorlocation_selector derived class
        :param time_selector: an instance of enricher_time_selector derived
            class
        :param aggregator: an instance of aggregator derived class
        :return: a tuple of:
            a new instance of class customer_data,
            unchanged instance of public_data,
            a new joined instance of class customer_data,
            join keys (list of tuple))
        """
        if self.enable_telemetry:
            self.log_properties['RegistryId'] = public_data.registry_id
            location_gran_log_property = location_selector.granularity.get_log_property()
            if location_gran_log_property is not None and len(location_gran_log_property) == 2:
                self.log_properties[location_gran_log_property[0]] = \
                    location_gran_log_property[1]
            time_gran_log_property = time_selector.granularity.get_log_property()
            if time_gran_log_property is not None and len(time_gran_log_property) == 2:
                self.log_properties[time_gran_log_property[0]] = \
                    time_gran_log_property[1]
            agg_log_property = aggregator.get_log_property()
            if agg_log_property is not None and len(agg_log_property) == 2:
                self.log_properties[agg_log_property[0]] = \
                    agg_log_property[1]
            with log_activity(
                    self.logger,
                    'enrich',
                    ActivityType.INTERNALCALL,
                    custom_dimensions=self.log_properties) as activity_logger:
                return self._enrich(
                    customer_data,
                    public_data,
                    location_selector,
                    time_selector,
                    aggregator,
                    activity_logger)
        else:
            return self._enrich(
                customer_data,
                public_data,
                location_selector,
                time_selector,
                aggregator,
                None)

    def _enrich(
            self,
            customer_data: CustomerData,
            public_data: PublicData,
            location_selector: EnricherLocationSelector,
            time_selector: EnricherTimeSelector,
            aggregator: Aggregator,
            activity_logger):
        """Enrich method, internal to override."""
        max_date = get_max_date_by_granularity(customer_data.max_date, time_selector.granularity)
        public_data.data = public_data.filter(public_data.env, customer_data.min_date, max_date)
        customer_data.add_row_id(customer_data.env)
        return self._process(customer_data, public_data, location_selector, time_selector, aggregator)

    def _process(
            self,
            customer_data: CustomerData,
            public_data: PublicData,
            location_selector: EnricherLocationSelector,
            time_selector: EnricherTimeSelector,
            aggregator: Aggregator)\
            -> Tuple[
                CustomerData,
                PublicData,
                CustomerData,
                List[Tuple[str, str]]]:
        """Process based on wrapped customer and public data objects."""
        all_aggregator = AggregatorAll()
        local_customer_data, location_filtered_public_data, join_keys =\
            location_selector.process(
                public_data.env,
                customer_data,
                public_data,
                all_aggregator,
                [],
                self.debug)

        if self.debug:
            self.location_filtered_customer_dataset = local_customer_data.data
            self.location_filtered_public_dataset = location_filtered_public_data.data

        local_customer_data, time_filtered_public_data, join_keys =\
            time_selector.process(
                public_data.env,
                local_customer_data,
                location_filtered_public_data,
                aggregator,
                join_keys,
                self.debug)

        if self.debug:
            self.time_filtered_customer_dataset = local_customer_data.data
            self.time_filtered_public_dataset = time_filtered_public_data.data

        return aggregator.process(
            public_data.env,
            local_customer_data,
            time_filtered_public_data,
            join_keys,
            self.debug)

    def get_common_log_properties(self):
        """Get common log properties."""
        return {}
