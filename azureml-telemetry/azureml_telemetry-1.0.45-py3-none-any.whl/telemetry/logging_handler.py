# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A file for AppInsights telemetry classes."""

import datetime
import json
import logging
import platform

from applicationinsights import TelemetryClient
from applicationinsights.channel import AsynchronousQueue, AsynchronousSender, SynchronousSender, \
    SynchronousQueue, TelemetryChannel, TelemetryContext

from azureml.telemetry._customtraceback import format_exc

try:
    from azureml._base_sdk_common import _ClientSessionId
except ImportError:
    from uuid import uuid4
    _ClientSessionId = str(uuid4())

try:
    # Python 2.x
    import urllib2 as http_client_t
    from urllib2 import HTTPError
except ImportError:
    # Python 3.x
    import urllib.request as http_client_t
    from urllib.error import HTTPError

SUCCESS = True
FAILURE = False

TRACEBACK_LOOKUP_STR = "Traceback (most recent call last)"

# extract traceback path from message
reformat_traceback = True


def _get_reformat_traceback():
    return reformat_traceback


def _set_reformat_traceback(reformat=True):
    global reformat_traceback
    reformat_traceback = reformat


def get_appinsights_log_handler(instrumentation_key, logger=None, *args, **kwargs):
    """Enable the Application Insights logging handler for the root logger for the supplied instrumentation key.

    :param instrumentation_key: instrumentation key
    :param args:
    :param kwargs:
    :return:
    """
    if logger is None:
        logger = logging.getLogger()
    context = TelemetryContext()
    custom_properties = {'PythonVersion': platform.python_version()}
    if 'properties' in kwargs:
        context._properties.update(kwargs.pop('properties'))
    context._properties.update(custom_properties)
    # register the logging handler to root logger
    handler = AppInsightsLoggingHandler(instrumentation_key, logger, telemetry_context=context)

    return handler


class AppInsightsLoggingHandler(logging.Handler):
    """Integration point between Python's logging framework and the Application Insights service."""

    def __init__(self, instrumentation_key, logger, sender=None, *args, **kwargs):
        """
        Initialize a new instance of the class.

        Args:
            instrumentation_key (str). the instrumentation key to use while sending telemetry to the service.
            sender (SynchronousSender). application insight sender object.
        """
        if not instrumentation_key:
            raise Exception('Instrumentation key was required but not provided')

        telemetry_context = None
        if 'telemetry_context' in kwargs:
            telemetry_context = kwargs.pop('telemetry_context')
        else:
            telemetry_context = TelemetryContext()

        if 'properties' in kwargs:
            telemetry_context._properties.update(kwargs.pop('properties'))

        self.logger = logger
        self._sender = sender or _RetrySynchronousSender

        # Configuring an asynchronous client as default telemetry client (fire and forget mode)
        self._default_client = TelemetryClient(instrumentation_key,
                                               self._create_asynchronous_channel(telemetry_context))

        #  Configuring a synchronous client and should be only used in critial scenarios
        self._synchronous_client = TelemetryClient(instrumentation_key,
                                                   self._create_synchronous_channel(telemetry_context))

        super(AppInsightsLoggingHandler, self).__init__(*args, **kwargs)

    def flush(self):
        """Flush the queued up telemetry to the service."""
        self._default_client.flush()
        return super(AppInsightsLoggingHandler, self).flush()

    def emit(self, record):
        """Emit a record.

        Args:
            record (:class:`logging.LogRecord`). the record to format and send.
        """
        try:
            if reformat_traceback and \
                    record.levelno >= logging.WARNING and \
                    hasattr(record, 'message') and \
                    record.message.find(TRACEBACK_LOOKUP_STR) != -1:
                record.message = format_exc()
                record.msg = record.message

            properties = {'level': record.levelname, 'sessionId': _ClientSessionId}
            properties.update(self._default_client.context.properties)

            if hasattr(record, 'properties'):
                properties.update(record.properties)

            formatted_message = self.format(record)

            # if we have exec_info, send it as an exception
            if record.exc_info and \
                    not all(item is None for item in record.exc_info):
                # for compliance we not allowed to collect trace with file path
                self._synchronous_client.track_trace(format_exc(), severity=record.levelname, properties=properties)
                return
            # otherwise, send the trace
            self._default_client.track_trace(formatted_message, severity=record.levelname, properties=properties)
        except Exception:
            # ignore exceptions, telemetry should not block because of trimming
            return

    def _create_synchronous_channel(self, context):
        """Create a synchronous app insight channel.

        :param context: App insight context
        :return: TelemetryChannel
        """
        channel = TelemetryChannel(context=context, queue=SynchronousQueue(self._sender(self.logger)))
        # the behavior is same to call flush every time
        channel.queue.max_queue_length = 1
        return channel

    def _create_asynchronous_channel(self, context):
        """Create an async app insight channel.

        :param context: App insight context
        :return: TelemetryChannel
        """
        sender = _RetryAsynchronousSender(self.logger)
        queue = AsynchronousQueue(sender)
        channel = TelemetryChannel(context, queue)

        # flush telemetry if we have 10 or more telemetry items in our queue
        channel.queue.max_queue_length = 10
        # send telemetry to the service in batches of 10
        channel.sender.send_buffer_size = 10
        # the background worker thread will be active for 1 seconds before it shuts down. if
        # during this time items are picked up from the queue, the timer is reset.
        channel.sender.send_time = 1
        # the background worker thread will poll the queue every 0.1 seconds for new items
        # 100ms is the most aggressive setting we can set
        channel.sender.send_interval = 0.1

        return channel


class _RetrySynchronousSender(SynchronousSender):
    """Synchronous sender with limited retry. SenderBase does infinite retry; this class avoids that."""

    def __init__(self, logger, timeout=10, retry=1):
        super(_RetrySynchronousSender, self).__init__()
        self._logger = logger
        self.send_timeout = timeout
        self.retry = retry
        self.consecutive_failures = 0

    def send(self, data_to_send):
        """Override the default resend mechanism in SenderBase. Stop resend based on retry during failure."""
        status = _http_send(self._logger, data_to_send, self.service_endpoint_uri, self.send_timeout)
        if status is SUCCESS:
            self.consecutive_failures = 0
            return
        else:
            self.consecutive_failures = self.consecutive_failures + 1

        if self.consecutive_failures <= self.retry:
            for data in data_to_send:
                self._queue.put(data)


class _RetryAsynchronousSender(AsynchronousSender):
    """Asynchronous sender with limited retry. SenderBase does infinite retry; this class avoids that."""

    def __init__(self, logger, timeout=10, retry=3):
        super(_RetryAsynchronousSender, self).__init__()
        self._logger = logger
        self.send_timeout = timeout
        self.retry = retry
        self.consecutive_failures = 0

    def send(self, data_to_send):
        """Override the default resend mechanism in SenderBase. Stop resend based on retry during failure."""
        status = _http_send(self._logger, data_to_send, self.service_endpoint_uri, self.send_timeout)
        if status is SUCCESS:
            self.consecutive_failures = 0
            return
        else:
            self.consecutive_failures = self.consecutive_failures + 1

        if self.consecutive_failures <= self.retry:
            for data in data_to_send:
                self._queue.put(data)


def _json_serialize_unknown(obj):
    """
    JSON serializer for objects not serializable by default json code.

    :param obj: the object to be serialized
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def _http_send(logger, data_to_send, service_endpoint_uri, send_timeout=10):
    """Replicate AppInsights SenderBase send method.

    :param logger: logger
    :param data_to_send: items to send
    :param service_endpoint_uri: endpoint
    :param send_timeout: timeout
    :return: SUCCESS/FAILURE
    """
    request_payload = json.dumps([a.write() for a in data_to_send], default=_json_serialize_unknown)

    content = bytearray(request_payload, 'utf-8')
    begin = datetime.datetime.now()
    request = http_client_t.Request(service_endpoint_uri, content,
                                    {'Accept': 'application/json',
                                     'Content-Type': 'application/json; charset=utf-8'})
    try:
        response = http_client_t.urlopen(request, timeout=send_timeout)
        logger.info('Sending %d bytes', len(content))
        status_code = response.getcode()
        if 200 <= status_code < 300:
            return SUCCESS
    except HTTPError as e:
        logger.error('Upload failed. HTTPError: %s', e)
        if e.getcode() == 400:
            return SUCCESS
    except OSError as e:  # socket timeout
        # stop retry during socket timeout
        logger.error('Upload failed. OSError: %s', e)
    except Exception as e:  # pylint: disable=broad-except
        logger.error('Unexpected exception: %s', e)
    finally:
        logger.info('Finish uploading in %f seconds.', (datetime.datetime.now() - begin).total_seconds())

    return FAILURE
