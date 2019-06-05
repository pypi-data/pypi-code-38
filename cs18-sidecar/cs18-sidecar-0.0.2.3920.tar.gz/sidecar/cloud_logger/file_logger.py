import os
from abc import abstractmethod, ABCMeta
from typing import List

from sidecar.cloud_logger.logs import ILogEntry


LogPath = "/var/ftp/sandbox/logs"


class ICloudLogger(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def write(cls, log_entry: ILogEntry):
        pass


class FileLogger(ICloudLogger):
    def write(self, log_entry: ILogEntry):
        if not os.path.exists(LogPath):
            os.makedirs(LogPath)

        with open(log_entry.get_log_filepath(LogPath), "ab") as stream:
            for time, line in log_entry.log_events:
                line_bytes = "[{LOG_TYPE}][{TIME}]{LINE}\n" \
                    .format(LOG_TYPE=log_entry.log_type, TIME=time.strftime('%Y-%m-%d %H:%M:%S'), LINE=line) \
                    .encode('utf8')
                stream.write(line_bytes)


class FakeFileLogger(ICloudLogger):

    def __init__(self):
        super().__init__()
        self.entries = []

    def write(self, log_entry: ILogEntry):
        self.entries.append(log_entry)

    def get_entries(self) -> List[ILogEntry]:
        return self.entries
