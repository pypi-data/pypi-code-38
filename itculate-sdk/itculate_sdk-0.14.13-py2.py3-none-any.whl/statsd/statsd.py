#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import six
import random
from socket import socket, AF_INET, SOCK_DGRAM
import logging

import time
import itculate_sdk as itsdk

logger = logging.getLogger(__name__)
_client = None  # type: ITculateStatsdClient


def decrement(metric, delta=1, sample_rate=None, vertex=None, data_type=itsdk.CountDataType):
    """
    Decrement a counter

    :param str|unicode metric: Name of counter
    :param int delta: Amount to decrement
    :param float sample_rate: (optional) between 0 and 1
    :param Vertex|str|unicode vertex: Key of vertex to associate counter with
    :param type data_type: (optional) class of data type to associate counter with (extends DataTypeWithUnit)
    """
    if _client is not None:
        _client.decrement(metric=metric, delta=delta, sample_rate=sample_rate, vertex=vertex, data_type=data_type)


def increment(metric, delta=1, sample_rate=None, vertex=None, data_type=itsdk.CountDataType):
    """
    Increment a counter

    :param str|unicode metric: Name of counter
    :param int delta: Amount to increment
    :param float sample_rate: (optional) between 0 and 1
    :param Vertex|str|unicode vertex: Key of vertex to associate counter with
    :param type data_type: (optional) class of data type to associate counter with (extends DataTypeWithUnit)
    """
    if _client is not None:
        _client.increment(metric=metric, delta=int(delta), sample_rate=sample_rate, vertex=vertex, data_type=data_type)


def gauge(metric, value, sample_rate=None, vertex=None, data_type=None):
    """
    Report a gauge

    :param str|unicode metric: Name of counter
    :param int|float|decimal.Decimal value: Value for gauge
    :param float sample_rate: (optional) between 0 and 1
    :param Vertex|str|unicode vertex: Key of vertex to associate counter with
    :param type data_type: (optional) class of data type to associate counter with (extends DataTypeWithUnit)
    """
    if _client is not None:
        _client.gauge(metric=metric, value=value, sample_rate=sample_rate, vertex=vertex, data_type=data_type)


def timing(metric, time_ms, sample_rate=None, vertex=None, data_type=itsdk.DurationDataType):
    if _client is not None:
        _client.timing(metric=metric, time_ms=int(time_ms), sample_rate=sample_rate, vertex=vertex, data_type=data_type)


def set(metric, value, sample_rate=None, vertex=None, data_type=None):
    if _client is not None:
        _client.set(metric=metric, value=value, sample_rate=sample_rate, vertex=vertex, data_type=data_type)


# noinspection PyPep8Naming
class time_and_count(object):
    """
    Convenience decorator to wrap a function and report the time it took + increment a metric when done
    """

    def __init__(self,
                 time_metric,
                 increment_metric_on_success=None,
                 increment_metric_on_exception=None,
                 vertex=None,
                 data_type=itsdk.DurationDataType):
        self.vertex = vertex
        self.data_type = data_type
        self.time_metric = time_metric
        self.increment_metric_on_success = increment_metric_on_success
        self.increment_metric_on_exception = increment_metric_on_exception

    def __call__(self, wrapped_func):
        def wrapped_f(*args, **kwargs):
            start = time.time() * 1000

            raised = False
            try:
                return wrapped_func(*args, **kwargs)

            except:
                raised = True
                raise

            finally:
                timing(vertex=self.vertex,
                       data_type=self.data_type,
                       metric=self.time_metric,
                       time_ms=time.time() * 1000 - start)

                if raised and self.increment_metric_on_exception is not None:
                    increment(vertex=self.vertex,
                              data_type=itsdk.RequestCountDataType,
                              metric=self.increment_metric_on_exception)

                else:
                    increment(vertex=self.vertex,
                              data_type=itsdk.RequestCountDataType,
                              metric=self.increment_metric_on_success)

        return wrapped_f


class ITculateStatsdClient(object):
    def __init__(self, host, port):
        self._agent = (host, port,)
        self._socket = socket(AF_INET, SOCK_DGRAM)

    def decrement(self, metric, delta=1, sample_rate=None, vertex=None, data_type=None):
        self._send_metric(vertex=vertex,
                          data_type=data_type,
                          metric=metric,
                          value="{}|c".format(-delta),
                          sample_rate=sample_rate)

    def increment(self, metric, delta=1, sample_rate=None, vertex=None, data_type=None):
        self._send_metric(vertex=vertex,
                          data_type=data_type,
                          metric=metric,
                          value="{}|c".format(delta),
                          sample_rate=sample_rate)

    def gauge(self, metric, value, sample_rate=None, vertex=None, data_type=None):
        self._send_metric(vertex=vertex,
                          data_type=data_type,
                          metric=metric,
                          value="{}|g".format(value),
                          sample_rate=sample_rate)

    def timing(self, metric, time_ms, sample_rate=None, vertex=None, data_type=None):
        self._send_metric(vertex=vertex,
                          data_type=data_type,
                          metric=metric,
                          value="{}|ms".format(time_ms),
                          sample_rate=sample_rate)

    def set(self, metric, value, sample_rate=None, vertex=None, data_type=None):
        self._send_metric(vertex=vertex,
                          data_type=data_type,
                          metric=metric,
                          value="{}|s".format(value.encode()),
                          sample_rate=sample_rate)

    def _send_metric(self, metric, value, sample_rate=None, vertex=None, data_type=None):
        """
        Sends a UDP datagram to the ITculate agent

        :param str|unicode metric: Name of counter
        :param str value: Encoded utf-8 str with value and type
        :param float sample_rate: Sample rate
        :param itsdk.Vertex|str|unicode vertex: Key (or Vertex) that this metric should be mapped to
        :param type data_type: (optional) class of data type to associate counter with (extends DataTypeWithUnit)
        """

        try:
            if sample_rate and 1.0 > sample_rate > 0:
                if random.random() <= sample_rate:
                    # Add rate to sample
                    value = "{}|@{}".format(value, sample_rate)
                else:
                    # Skip sample!
                    return

            encoded_metric = self.encode_metric(metric, vertex=vertex, data_type=data_type)
            statsd_packet = "{}:{}".format(encoded_metric, value)

            # Finally, send the packet
            self._socket.sendto(statsd_packet, self._agent)

        except:
            # Log, but don't throw!
            logger.exception("Failed to send metric '{}' to ITculate agent".format(metric))

    @classmethod
    def encode_metric(cls, metric, vertex=None, data_type=None):
        """
        Encode metric in a statsd-compatible way, but include ITculate specific meta-data (like vertex key and type)

        :param str|unicode metric: Metric
        :param itsdk.Vertex|unicode|str vertex: Vertex (or key)
        :param type data_type: Data type class

        :return: Encoded (utf-8) metric name
        :rtype: str
        """
        if isinstance(metric, six.text_type):
            metric = metric.encode()

        if vertex is not None or data_type is not None:
            if isinstance(vertex, itsdk.Vertex):
                vertex = vertex.first_key

            elif isinstance(vertex, six.text_type):
                vertex = vertex.encode()

            # Add our own secret sauce...
            if data_type is not None:
                assert issubclass(data_type, itsdk.DataTypeWithUnit), \
                    "data_type must be a class that subclass DataTypeWithUnit"
                data_type_class_name = data_type.__name__
            else:
                data_type_class_name = ""

            vertex = vertex or ""
            vertex_len = len(vertex)

            return "_it.%s.%s.%s.%s" % (data_type_class_name, vertex_len, vertex, metric)

        else:
            return metric

    @staticmethod
    def decode_metric(encoded_metric):
        """
        :param str|unicode encoded_metric:
        :return: (vertex key, data_type, metric_name) - all string utf-8 encoded
        :rtype: (str, itsdk.DataType, str)
        """
        if not encoded_metric.startswith("_it."):
            # This is not an encoded vertex
            return None, None, encoded_metric

        else:
            start = 4
            end = encoded_metric.find(".", start)
            data_type_class = encoded_metric[start:end]

            start = end + 1
            end = encoded_metric.find(".", start)
            vertex_key_length = int(encoded_metric[start:end])

            start = end + 1
            end = start + vertex_key_length
            vertex_key = encoded_metric[start:end]

            start = end + 1
            metric_name = encoded_metric[start:]

            if not vertex_key:
                vertex_key = None

            if data_type_class:
                # Load the class back (load it from the types module)
                # TODO: Support custom data types
                data_type = getattr(itsdk.types, data_type_class)()
            else:
                data_type = None

            return vertex_key, data_type, metric_name


def init(host="127.0.0.1", port=8125):
    global _client
    _client = ITculateStatsdClient(host=host, port=port)
