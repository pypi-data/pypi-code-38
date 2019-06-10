# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""systemusage_telemetry.py, A file system usage telemetry classes."""
import abc
import logging
import os
import sys

from .timer_utilities import TimerCallback


class SystemResourceUsageTelemetry:
    """System usage telemetry abstract class."""

    def __init__(self, logger, interval=10):
        """
        Initialize system resource usage telemetry class.

        :param logger: logger
        :param interval: interval in sec
        """
        self.logger = logger
        self.interval = interval
        self._timer = None

    def __enter__(self):
        """Start usage collection using a context manager."""
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        """Stop usage collection using a context manager."""
        self.stop()

    def start(self):
        """Start usage collection."""
        if self._timer is None:
            self.logger.info("Starting usage telemetry collection")
            self._timer = TimerCallback(interval=self.interval, logger=self.logger, callback=self._get_usage)

    def stop(self):
        """Stop timer."""
        if self._timer is not None:
            self.logger.info("Stopping usage telemetry collection")
            self._timer.stop()
            self._timer = None

    def __del__(self):
        """Cleanup."""
        self.stop()

    def _log_memory_usage(self, mem_usage, prefix_message=''):
        """Log memory usage."""
        extra_info = {'properties': {'Type': 'MemoryUsage', 'Usage': mem_usage}}
        if prefix_message is None:
            prefix_message = ''
        self.logger.info("{}memory usage {}".format(prefix_message, mem_usage), extra=extra_info)

    def _log_cpu_usage(self, cpu_time, cores, system_time=None, prefix_message=''):
        """Log cpu usage."""
        extra_info = {'properties': {'Type': 'CPUUsage', 'CPUTime': cpu_time, 'Cores': cores}}
        if system_time is not None:
            extra_info['properties']["SystemTime"] = system_time
        if prefix_message is None:
            prefix_message = ''
        self.logger.info("{}cpu time {}".format(prefix_message, cpu_time), extra=extra_info)

    def send_usage_telemetry_log(self, prefix_message=None, is_sending_telemetry=True):
        """
        Send the usage telemetry log based on automl settings with message.

        :param prefix_message: The prefix of logging message.
        :param is_sending_telemetry: the switch controls whether send log or not.
        :return: None
        """
        if not is_sending_telemetry:
            return

        try:
            self._get_usage(prefix_message)
        except Exception:
            pass  # do nothing

    @abc.abstractmethod
    def _get_usage(self, prefix_message=None):
        raise NotImplementedError


class _WindowsSystemResourceUsageTelemetry(SystemResourceUsageTelemetry):
    """Telemetry Class for collecting system usage."""

    def __init__(self, logger, interval=10):
        """
        Constructor.

        :param logger: logger
        :param interval: collection frequency in seconds
        """
        super(_WindowsSystemResourceUsageTelemetry, self).__init__(logger, interval=interval)

        from automl.client.core.common.win32_helper import Win32Helper
        self._helper = Win32Helper()

    def _get_usage(self, prefix_message=None):
        """Get usage."""
        if prefix_message is None:
            prefix_message = ''

        try:
            phys_mem, _, kernel_cpu, user_cpu, \
                child_phys_mem, _, child_kernel_cpu, child_user_cpu = self._helper.get_resource_usage()

            self._log_memory_usage(phys_mem, prefix_message)
            self._log_memory_usage(child_phys_mem, '{}child '.format(prefix_message))

            self._log_cpu_usage(user_cpu, os.cpu_count(), kernel_cpu, prefix_message)
            self._log_cpu_usage(child_user_cpu, os.cpu_count(), child_kernel_cpu,
                                '{}child '.format(prefix_message))
        except Exception as e:
            self.logger.info(e)


class _NonWindowsSystemResourceUsageTelemetry(SystemResourceUsageTelemetry):
    """Linux, Mac & other os System Usage Telemetry."""

    def _get_usage(self, prefix_message=None):
        """Get usage."""
        if prefix_message is None:
            prefix_message = ''

        try:
            import resource
            res = resource.getrusage(resource.RUSAGE_SELF)
            child_res = resource.getrusage(resource.RUSAGE_CHILDREN)

            self._log_memory_usage(res.ru_maxrss, prefix_message)
            self._log_memory_usage(child_res.ru_maxrss, '{}child '.format(prefix_message))

            self._log_cpu_usage(res.ru_utime, os.cpu_count(), res.ru_stime, prefix_message)
            self._log_cpu_usage(child_res.ru_utime, os.cpu_count(), child_res.ru_stime,
                                '{}child '.format(prefix_message))
        except Exception as e:
            self.logger.info(e)


class SystemResourceUsageTelemetryFactory:
    """System resource usage telemetry collection factory class."""

    @staticmethod
    def get_system_usage_telemetry(logger: logging.Logger, interval: int = 10) -> SystemResourceUsageTelemetry:
        """
        Get system usage telemetry object based on platform.

        :param logger: logger
        :param interval: interval in sec
        :return: SystemResourceUsageTelemetry : platform specific object
        """
        if sys.platform == "win32":
            return _WindowsSystemResourceUsageTelemetry(logger, interval=interval)

        return _NonWindowsSystemResourceUsageTelemetry(logger, interval=interval)
