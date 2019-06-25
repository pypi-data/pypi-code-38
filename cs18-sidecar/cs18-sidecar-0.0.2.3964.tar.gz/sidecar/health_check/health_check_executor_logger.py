from abc import ABCMeta, abstractmethod
from datetime import datetime
from logging import Logger
from typing import List

from sidecar.app_instance_identifier import IIdentifier, AppInstanceIdentifier, AppIdentifier
from sidecar.cloud_logger.file_logger import ICloudLogger
from sidecar.cloud_logger.logs import AppLogEntry
from sidecar.utils import Utils


class HealthCheckExecutorLogger:
    __metaclass__ = ABCMeta

    def __init__(self,
                 cloud_logger: ICloudLogger,
                 logger: Logger):
        self.logger = logger
        self.cloud_logger = cloud_logger

    @abstractmethod
    def log_start(self, identifier: IIdentifier, cmd: List[str], timeout: int):
        raise NotImplementedError

    @abstractmethod
    def log_line(self, line: str, identifier, error: bool = False):
        raise NotImplementedError

    @abstractmethod
    def log_timeout(self, timeout: int, identifier: IIdentifier):
        raise NotImplementedError

    @abstractmethod
    def log_success(self, identifier: IIdentifier):
        raise NotImplementedError

    @abstractmethod
    def log_error(self, identifier: IIdentifier, exit_code: int):
        raise NotImplementedError


HEALTH_CHECK_TOPIC = "healthcheck"


class AppInstanceHealthCheckExecutorLogger(HealthCheckExecutorLogger):
    def log_start(self, identifier: IIdentifier, cmd: List[str], timeout: int):
        app_instance_identifier = identifier  # type: AppInstanceIdentifier

        line = 'health-check started: {} with command: {}, timeout: {}'.format(
            Utils.get_timestamp(),
            cmd,
            timeout)

        self._log(line, app_instance_identifier)

    def log_line(self, line: str, identifier: AppInstanceIdentifier, error: bool = False):
        app_instance_identifier = identifier
        log_entry = self._create_log_entry(app_instance_identifier, line)

        self.cloud_logger.write(log_entry)

    def log_timeout(self, timeout: int, identifier: IIdentifier):
        app_instance_identifier = identifier  # type: AppInstanceIdentifier
        line = 'health-check: timed out for app {} after {} seconds'.format(app_instance_identifier, timeout)
        self._log(line=line, app_instance_identifier=app_instance_identifier)

    def log_success(self, identifier: IIdentifier):
        app_instance_identifier = identifier  # type: AppInstanceIdentifier
        line = "health-check: done for app '{}'".format(app_instance_identifier)
        self._log(line=line, app_instance_identifier=app_instance_identifier)

    def log_error(self, identifier: IIdentifier, exit_code: int):
        app_instance_identifier = identifier  # type: AppInstanceIdentifier
        line = "health-check: failed for app '{}' with exit_code {}".format(app_instance_identifier, exit_code)
        self._log(line=line, app_instance_identifier=app_instance_identifier)

    def _log(self, line: str, app_instance_identifier: AppInstanceIdentifier):
        log_entry = self._create_log_entry(app_instance_identifier, line)
        self.logger.info(log_entry.get_as_string())
        self.cloud_logger.write(log_entry)

    def _create_log_entry(self, app_instance_identifier, line):
        log_entry = AppLogEntry(app_instance_identifier.name, app_instance_identifier.infra_id,
                                HEALTH_CHECK_TOPIC,
                                [(datetime.utcnow(),
                               line)], "HealthCheck")
        return log_entry


class AppHealthCheckExecutorLogger(HealthCheckExecutorLogger):
    def log_start(self, identifier: IIdentifier, cmd: List[str], timeout: int):
        identifier = identifier  # type: AppIdentifier

        line = 'health-check started: {} with command: {}, timeout: {}'.format(
            Utils.get_timestamp(),
            cmd,
            timeout)

        log_entry = AppLogEntry(identifier.name,
                             "app",
                                HEALTH_CHECK_TOPIC,
                                [(datetime.utcnow(),
                               line)], "HealthCheck")

        self.logger.info(log_entry.get_as_string())

    def log_line(self, line: str, identifier, error: bool = False):
        pass

    def log_timeout(self, timeout: int, identifier: IIdentifier):
        identifier = identifier  # type: AppIdentifier
        line = 'health-check: timed out for app {} after {} seconds'.format(identifier, timeout)
        self._log(line=line, app_identifier=identifier)

    def log_success(self, identifier: IIdentifier):
        identifier = identifier  # type: AppIdentifier
        line = "health-check: done for app '{}'".format(identifier)
        self._log(line=line, app_identifier=identifier)

    def log_error(self, identifier: IIdentifier, exit_code: int):
        identifier = identifier  # type: AppIdentifier
        line = "health-check: failed for app '{}' with exit_code {}".format(identifier, exit_code)
        self._log(line=line, app_identifier=identifier)

    def _log(self, line: str, app_identifier: AppIdentifier):
        log_entry = AppLogEntry(app_identifier.name, "app",
                                HEALTH_CHECK_TOPIC,
                                [(datetime.utcnow(),
                               line)], "HealthCheck")
        self.logger.info(log_entry.get_as_string())
