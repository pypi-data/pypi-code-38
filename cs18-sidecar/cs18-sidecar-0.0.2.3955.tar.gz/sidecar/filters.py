import logging
import os
import platform
import socket

from sidecar.model.objects import ISidecarConfiguration


class LoggingFilter(logging.Filter):
    def __init__(self, config: ISidecarConfiguration):
        logging.Filter.__init__(self)
        self.config = config

    def filter(self, record: logging.LogRecord):
        record.__dict__['colony.application'] = 'sidecar'
        record.__dict__['colony.branch'] = os.getenv('branch', "none")
        record.__dict__['colony.environment'] = self.config.environment
        record.__dict__['colony.hostname'] = self._get_hostname()
        record.__dict__['colony.level'] = record.levelname
        record.__dict__['colony.sandbox_id'] = self.config.sandbox_id
        record.__dict__['colony.production_id'] = self.config.production_id
        record.__dict__['colony.threadId'] = record.thread
        record.logger = '{0} {1}'.format(record.filename, record.funcName)
        return record

    @staticmethod
    def _get_hostname():
        n1 = platform.node()
        n2 = socket.gethostname()
        n3 = os.getenv("COMPUTERNAME")
        if n1 == n2 == n3:
            return n1
        elif n1 == n2:
            return n1
        elif n1 == n3:
            return n1
        elif n2 == n3:
            return n2
        else:
            return "local-pc"
