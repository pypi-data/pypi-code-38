from datetime import datetime
from logging import Logger
from typing import List, Tuple
from threading import Lock
import jsonpickle


class CloudWatchStreamWriter(object):

    def __init__(self, logs_client, group_name: str, stream_name: str, logger: Logger):
        self.logs_client = logs_client
        self.group_name = group_name
        self.stream_name = stream_name
        self.logger = logger
        self._sequence_token = None
        self._lock = Lock()
        self._init_stream()

    def _init_stream(self):
        try:
            # check if stream already exist
            log_streams = self.logs_client.describe_log_streams(logGroupName=self.group_name,
                                                                logStreamNamePrefix=self.stream_name)
            if len(log_streams['logStreams']) > 0:
                # if exists get SequenceToken
                log_stream = log_streams['logStreams'][0]
                self._sequence_token = log_stream.get('uploadSequenceToken') or "0"
            else:
                # if not exists create the stream
                self.logs_client.create_log_stream(logGroupName=self.group_name,
                                                   logStreamName=self.stream_name)
                self._sequence_token = "0"
                self.write([(datetime.utcnow(), "Start of log stream")])
                self.logger.info("log stream was created: " + self.stream_name)

        except Exception:
            self.logger.exception("Failed to _init_stream for "+self.stream_name)
            raise

    def _get_stream_details(self, streams):
        streams.update(self.logs_client.describe_log_streams(logGroupName=self.group_name,
                                                             logStreamNamePrefix=self.stream_name))
        # protect in case of failure
        if 'logStreams' not in streams or len(streams['logStreams']) == 0:
            self.logger.warning('log_stream details were not returned by aws ' + str(streams))
            return None

        return streams

    @staticmethod
    def _fix_empty_string(string: str) -> str:
        if len(string) == 0:
            return " "
        return string

    def write(self, log_events: List[Tuple[datetime, str]]):
        """Write log events to AWS CloudWatch Logs service

        Args:
            log_events: list of tuples containing timestamp and log message
        """
        try:
            events = [
                {
                    'timestamp': int(time.timestamp() * 1000),
                    'message': self._fix_empty_string(message)
                } for time, message in log_events]

            with self._lock:
                result = self.logs_client.put_log_events(logGroupName=self.group_name,
                                                         logStreamName=self.stream_name,
                                                         logEvents=events,
                                                         sequenceToken=self._sequence_token)
                if "rejectedLogEventsInfo" in result:
                    raise Exception(result["rejectedLogEventsInfo"])

                self._sequence_token = result['nextSequenceToken']
                if not self._sequence_token:
                    raise Exception('nextSequenceToken is empty. Response: '+jsonpickle.dumps(result))

        except Exception:
            self.logger.exception("Failed to write cloud-log to " + self.stream_name)
            raise
