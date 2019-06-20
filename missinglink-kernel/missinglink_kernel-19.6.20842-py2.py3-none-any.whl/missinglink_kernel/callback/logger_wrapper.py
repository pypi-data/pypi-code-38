# -*- coding: utf-8 -*-
import logging
import os
from .root_logger_sniffer import RootLoggerSniffer


class LoggerWrapper(object):
    class RootLogsMemoryCache(RootLoggerSniffer):
        def __init__(self, log_level):
            super(LoggerWrapper.RootLogsMemoryCache, self).__init__(log_level)

            from missinglink_kernel.callback import get_global_root_logger_sniffer

            if get_global_root_logger_sniffer() is not None:
                log_records = get_global_root_logger_sniffer().log_records
                get_global_root_logger_sniffer().stop_capture_global()
            else:
                log_records = []

            self.log_records = log_records[:]

            self._activate()

        def on_root_log(self, record):
            self.log_records.append(record)

        def close(self):
            self.log_records = []
            super(LoggerWrapper.RootLogsMemoryCache, self).close()

    def __init__(self, log_level=logging.DEBUG):
        self.remote_logger = None
        self.logger = self._create_null_logger(log_level)
        self.log_cache = self._create_logs_cache(log_level)

    def activate_if_needed(self):
        if self.remote_logger is not None:
            self.remote_logger.activate_if_needed()

    def close(self):
        if self.remote_logger is not None:
            self.remote_logger.close()

    @classmethod
    def _create_logs_cache(cls, log_level):
        return LoggerWrapper.RootLogsMemoryCache(log_level)

    @classmethod
    def _create_null_logger(cls, log_level):
        logger = logging.getLogger('missinglink')

        return logger

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def _create_remote_logger(self, session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint):
        self.info('remote_logger global level: %s filter: %s', remote_log_level, remote_log_filter)
        self.debug('__create_remote_logger %s %s %s %s %s', session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint)

        from .remote_logger import RemoteLoggerHandler

        disable_process_monkey_patch = os.environ.get('ML_DISABLE_PROCESS_MONKEY_PATCH')

        remote_logger = RemoteLoggerHandler(
            session_id, endpoint, remote_log_level, self.log_cache.log_records, remote_log_filter, terminate_endpoint)

        remote_logger.start_remote_script(disable_process_monkey_patch)
        return remote_logger

    def activate_remote_logging(self, session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint):
        self.remote_logger = self._create_remote_logger(
            session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint)

        self.log_cache.close()
