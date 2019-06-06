# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Collect and aggregate metrics
"""
from collections import Counter
from datetime import timedelta
from logging import getLogger

from .exceptions import SqreenException

LOGGER = getLogger(__name__)


class BaseAggregator(object):
    """ Base classes for aggregators.

    It contains the methods to update a period with new data and finalize the
    data just before uploading.
    Aggregators doesn't store any state, it is passed by the MetricsStore.
    """

    name = "Base"

    def update(self, key, value, data=None):
        """ Update the whole data for the period. For updating only the key,
        override update_key instead.
        """
        if data is None:
            data = {}

        data[key] = self.update_key(value, data.get(key))
        return data

    @staticmethod
    def update_key(value, key_data=None):
        """ Update the data for a key in the period. For updating the whole data,
        override update instead.
        """
        raise NotImplementedError("")

    @staticmethod
    def finalize(data):
        """ Finalize the period, by default return the data. Could be override
        to compute a ration or sum some elements.
        """
        return data


class CollectAggregator(BaseAggregator):
    """ Simple aggregator that stores all the observations points,
    used in tests mostly
    """

    name = "Collect"

    @staticmethod
    def update_key(value, data=None):
        if data is None:
            data = []

        data.append(value)
        return data


class SumAggregator(BaseAggregator):

    name = "Sum"

    @staticmethod
    def update_key(value, data=None):
        if data is None:
            data = 0

        return data + value


class ExtensionPerformanceMetricAggregator(BaseAggregator):

    name = "ExtensionPerformance"

    def update(self, key, value, data=None):
        """ Ignore key
        """
        if data is None:
            data = {'v': Counter()}

        return self.update_key(value, data)

    @staticmethod
    def update_key(value, data):
        cur_values = data['v']

        return {
            'u': value['u'],
            'b': value['b'],
            'v': cur_values + Counter(value['v'])
        }


class AverageAggregator(BaseAggregator):

    name = "Average"

    @staticmethod
    def update_key(value, data=None):
        if data is None:
            data = {"sum": 0, "count": 0}

        data["sum"] += value
        data["count"] += 1
        return data

    @staticmethod
    def finalize(data):
        final_data = {}

        for key, value in data.items():
            final_data[key] = value["sum"] / float(value["count"])

        return final_data


class UnknownAggregator(SqreenException):
    """ Exception raised when trying to register a metric with an unknown
    aggregation kind
    """


class AlreadyRegisteredMetric(SqreenException):
    """ Exception raised when trying to register twice the same metric
    name.
    """


class AlreadyRegisteredAggregator(SqreenException):
    """ Exception raised when trying to register twice the same aggregator
    name.
    """


class UnregisteredMetric(SqreenException):
    """ Exception raised when trying to update an unregistered metric.
    """


PRODUCTION_AGGREGATORS = [SumAggregator(),
                          AverageAggregator(),
                          ExtensionPerformanceMetricAggregator()]


class MetricsStore(object):
    """ Store the dict of currently monitored metrics.

    For each metric, store a dict containing:
    - The start time of monitored period.
    - The maximum period time.
    - The kind of aggregator.
    - The aggregated data, the value is managed by the aggregator directly.

    Store also the list of available aggregator indexed by a kind.

    When periods are finished, store them to be retrieved for pushing in
    the store attribute.
    """

    def __init__(self):
        self.store = []
        self.metrics = {}
        self.aggregators = {}

    def register_metric(self, name, kind, period):
        """ Register a new metric
        """
        LOGGER.debug("Register metric '%s'", name)

        if name in self.metrics:
            existing_metric = self.metrics[name]
            saved_metric_kind = existing_metric["kind"]
            if saved_metric_kind != kind:
                err_msg = (
                    "Metric '{}' has already been registered with kind {}"
                )
                raise AlreadyRegisteredMetric(
                    err_msg.format(name, saved_metric_kind)
                )

            # Update the period
            existing_metric["period"] = period
        else:
            if kind not in self.aggregators:
                raise UnknownAggregator(
                    "Unknown aggregation kind: {}".format(kind)
                )
            self.metrics[name] = self._new_metric(kind, period)

    def ensure_ext_perf_metric(self, name, period):
        if name in self.metrics:
            return

        self.register_metric(name, 'ExtensionPerformance', period)

    @staticmethod
    def _new_metric(kind, period):
        """ Return a dict for an empty metric period
        """
        return {
            "kind": kind,
            "period": period,
            "observation": None,
            "start": None,
        }

    def register_aggregator(self, name, aggregator_function):
        """ Register a new aggregator under the name passed in input
        """
        if name in self.aggregators:
            msg = "Aggregator '{}' has already been registered to: {}"
            raise AlreadyRegisteredAggregator(
                msg.format(name, self.aggregators[name])
            )
        self.aggregators[name] = aggregator_function

    def register_production_aggregators(self):
        """ Register production aggregators
        """
        for aggregator in PRODUCTION_AGGREGATORS:
            self.register_aggregator(aggregator.name, aggregator)

    def register_default_metrics(self):
        """ Register production default metrics
        """

        self.register_metric("sqreen_call_counts", "Sum", 60)
        self.register_metric("whitelisted", "Sum", 60)
        self.register_metric("request_overtime", "Sum", 60)

    def update(self, name, at, key, value):
        """ Logic behind metric updating.

        Check if the start time is set for the metric period.
        Check if the metric period has expired, if so save it and create
        a blank metric period.
        Then call the aggregator to compute the new data
        """
        try:
            metric = self.metrics[name]
        except KeyError:
            raise UnregisteredMetric("Unknown metric {}".format(name))

        # Update start time if not set already (registered but never updated)
        if metric["start"] is None:
            metric["start"] = at

        # Check if the metric should be published or not
        else:
            metric = self.check_metric_period_over(metric, name, at, False)

        self._update_metric(metric, key, value)

    def _update_metric(self, metric, key, value):
        """ Actual method that call the aggregator to compute the new data.
        """
        aggregator = self.aggregators[metric["kind"]]

        # Compute the new value
        new_data = aggregator.update(key, value, metric["observation"])
        metric["observation"] = new_data

    def check_metric_period_over(self, metric, name, at, force_finalize=True):
        """ Check a single metric to see if its period is over, if so
        finalize it and returns the new one.
        If force_finalize if False, check that the metric period is over first.
        """
        if not metric["start"]:
            return metric

        period_over = (
            metric["start"] + timedelta(seconds=metric["period"]) < at
        )
        if force_finalize or period_over:
            return self.finalize_period(metric, name, at)

        return metric

    def check_all_metrics_period_over(self, at, force_finalize=True):
        """ Check all registered metrics to see if their period are over, if so
        finalize them.
        If force_finalize if False, check that the metric period is over first.
        """
        for metric_name, metric in self.metrics.items():
            self.check_metric_period_over(
                metric, metric_name, at, force_finalize
            )

    def finalize_period(self, metric, name, at):
        """ Finalize a metric period. For each registered metric, call the
        finalize method on correspondent aggregator and instantiate a new blank
        metric period.

        Called if either the period time was crossed or can forced on logout.
        """
        # If no data has been gathered
        if metric["observation"] is not None:
            # Retrieve the current period
            # Call the finalize method on the aggregator
            aggregator = self.aggregators[metric["kind"]]

            finished = {}
            finished["observation"] = aggregator.finalize(
                metric["observation"]
            )
            finished["finish"] = at
            finished["name"] = name
            finished["start"] = metric["start"]
            self.store.append(finished)

        # Reset the period
        metric = self._new_metric(metric["kind"], metric["period"])
        metric["start"] = at
        self.metrics[name] = metric
        return metric

    def get_data_to_publish(self, at, force_finalize=True):
        """ Return the list of finished periods, reset the list of
        finished periods after.
        """
        self.check_all_metrics_period_over(at, force_finalize)

        finished_periods = self.store
        self.store = []
        return finished_periods

    ###
    # Helpers for debug and tests
    ###

    def list_metrics(self):
        """ Return the list of registered metrics
        """
        return self.metrics.keys()

    def get_metric_kind(self, name):
        """ Return the kind of a given metric
        """
        return self.metrics[name]["kind"]

    def get_metric_period(self, name):
        """ Return the period of a given metric
        """
        return self.metrics[name]["period"]

    def get_metric_start(self, name):
        """ Return the start time for a given metric
        """
        return self.metrics[name]["start"]

    def get_metric_aggregate(self, name):
        """ Return the current aggregated data for a given metric
        """
        return self.metrics[name]["observation"]
