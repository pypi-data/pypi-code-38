from logging import Logger
from threading import Lock
from typing import Dict

from sidecar.aws_session import AwsSession
from sidecar.cloud_logger import FileLogger
from sidecar.cloud_logger.file_logger import ICloudLogger
from sidecar.model.objects import ISidecarConfiguration
from .stream_writer import CloudWatchStreamWriter
from ..logs import AppLogEntry


class CloudWatchLogger(ICloudLogger):
    def __init__(self, config: ISidecarConfiguration, logger: Logger, aws_session: AwsSession, file_logger: FileLogger):
        cloud_external_key = config.cloud_external_key
        self.sandbox_id = config.sandbox_id
        self.logger = logger
        self.logs = aws_session.get_cloudwatch_client() if aws_session else None
        self.group_name = "colony-{cloud_external_key}".format(cloud_external_key=cloud_external_key)
        self._stream_writers = dict()  # type: Dict[str, CloudWatchStreamWriter]
        self._lock = Lock()
        self.file_logger = file_logger

    def _get_writer(self, log_entry: AppLogEntry) -> CloudWatchStreamWriter:
        stream_name = "/{sandbox_id}/{app_name}/{instance_id}/{log_type}".format(sandbox_id=self.sandbox_id,
                                                                                 app_name=log_entry.app,
                                                                                 instance_id=log_entry.instance,
                                                                                 log_type=log_entry.topic)
        writer = self._stream_writers.get(stream_name)
        if writer is None:
            with self._lock:
                writer = self._stream_writers.get(stream_name)
                if writer is None:
                    writer = CloudWatchStreamWriter(self.logs, self.group_name, stream_name, self.logger)
                self._stream_writers[stream_name] = writer
        return writer

    def write(self, log_entry: AppLogEntry):
        writer = self._get_writer(log_entry)
        writer.write(log_entry.log_events)
        self.file_logger.write(log_entry)
