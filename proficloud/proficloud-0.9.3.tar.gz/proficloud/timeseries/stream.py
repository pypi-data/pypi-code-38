from .kairos import KairosConnector
from streamz.core import Stream
import time
import tornado.ioloop
from tornado import gen
from pandas import DataFrame
import numpy
import datetime

class MetricsStream(Stream):
    """
    This class creates a "streamz"-stream from a KairosConnector (or one of its child classes such as ProficloudMetrics).

    :type connector: KairosConnector (or subclass)
    :param connector: An initialized connector.
    :type metrics: list(str), str
    :param metrics: A list of metric names (or a single metric name) to query. 
    :type intervalMs: int
    :param intervalMs: Polling interval in milliseconds
    :type bufferTime: dict
    :param bufferTime: The buffer time is the current date and time minus the specified value and unit. Possible unit values are “milliseconds”, “seconds”, “minutes”, “hours”, “days”, “weeks”, “months”, and “years”. For example, if the start time is 5 minutes, the query will return all matching data points for the last 5 minutes. Example value: { "value": "10", "unit": "minutes" } 
    :type convertTimestamp: boolean
    :param convertTimestamp: Convert the timestamp to datetime (Default: False)
    """

    def __init__(self, connector, metrics, intervalMs, bufferTime, convertTimestamp=False, **kwargs):
        self.__connector = connector
        self.__metrics = metrics
        self.__intervalMs = intervalMs
        self.__bufferTime = bufferTime
        self.__convertTimestamp = convertTimestamp
        self.header = DataFrame(columns=["Timestamp"] + metrics)
        """The header for DataFrame creation with the streamz package"""
        super().__init__(ensure_io_loop=True, **kwargs)
        self.stopped = True

    @gen.coroutine
    def poll_metrics(self):
        """
        Polling co-routine. This retrieves metrics from the connector.
        """
        previousTs = None
        newSamples = None
        lastEmit = None

        while True:

            #Check interval after successful emit:
            if lastEmit is None:
                lastEmit = datetime.datetime.utcnow()
            else:
                diffMs = (datetime.datetime.utcnow() - lastEmit).total_seconds()*1000
                if diffMs < self.__intervalMs and diffMs > 0:
                    yield(gen.sleep((self.__intervalMs - diffMs)/1000.0))


            try:
                currentFrame = self.__connector.queryMetrics(self.__metrics, start_relative=self.__bufferTime, dropTrailingNa=True, createDf=True, convertTimestamp=self.__convertTimestamp)
            except:
                raise
                
            if currentFrame is not None:
                if ~currentFrame.empty:
                    if previousTs is not None:
                        newSamples = currentFrame[~currentFrame.Timestamp.isin(previousTs)]
                    else:
                        newSamples = currentFrame   
                    previousTs = currentFrame["Timestamp"]

                    if (~newSamples.empty) and numpy.array_equal(newSamples.columns, self.header.columns):
                        lastEmit = datetime.datetime.utcnow()
                        yield self._emit(newSamples)
                    else:
                        yield gen.sleep(self.__intervalMs/1000.0)
                else:
                    yield gen.sleep(self.__intervalMs/1000.0)
            else:
                yield gen.sleep(self.__intervalMs/1000.0)
            if self.stopped:
                break

    def start(self):
        """
        Start the stream.
        """
        if self.stopped:
            self.stopped = False
            self.loop.add_callback(self.poll_metrics)

    def stop(self):
        """
        Stop the stream.
        """
        if not self.stopped:
            self.stopped = True

    def changeInterval(self, intervalMs):
        self.__intervalMs = intervalMs



