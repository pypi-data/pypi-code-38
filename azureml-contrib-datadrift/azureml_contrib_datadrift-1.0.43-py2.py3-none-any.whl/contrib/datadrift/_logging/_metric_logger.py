# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Metric logger to track customer metrics."""

from applicationinsights import TelemetryClient
from applicationinsights.channel import TelemetryContext, TelemetryChannel
from applicationinsights.channel.contracts import DataPointType

from azureml.contrib.datadrift._datadiff import Metric


class _MetricLogger:
    """Metric logger to track customer data drift metrics and data profile metrics to Application Insights."""

    def __init__(self, instrumentation_key):
        """Initialize a new instance of the class.

        :param instrumentation_key: the instrumentation key to use while sending telemetry to the service.
        :type instrumentation_key: str
        """
        if not instrumentation_key:
            raise ValueError('Instrumentation key was required but not provided')

        telemetry_context = TelemetryContext()
        channel = TelemetryChannel(telemetry_context)

        self._client = TelemetryClient(instrumentation_key, channel)

    def log_metric(self, metric):
        """Log customer metric.

        :param metric: customer metric object
        :type metric: Metric
        :return: None
        """
        if not metric:
            raise ValueError('The metric object is required but not provided')

        if not isinstance(metric, Metric):
            raise ValueError("Argument must be of Metric type")

        if not metric.name:
            raise ValueError('The metric name is required but not provided')

        # Cast extended properties to string, since AppInsights uses JSON serialization
        properties = {k: str(v) for k, v in metric.extended_properties.items()}

        self._client.track_metric(name=metric.name,
                                  value=float(metric.value),
                                  type=DataPointType.measurement,
                                  properties=properties)
        self._client.flush()
