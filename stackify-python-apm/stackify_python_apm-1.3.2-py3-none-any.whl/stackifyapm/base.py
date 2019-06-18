from __future__ import absolute_import

import atexit
import logging
import os
import platform
import socket
import sys
try:
    import Queue as queue
except ImportError:  # pragma: no cover
    import queue

import stackifyapm
from stackifyapm.conf import Config
from stackifyapm.conf.constants import ASYNC_MAX_WAITING_TIME_IN_SEC
from stackifyapm.conf.constants import ASYNC_WAITING_TIME_IN_SEC
from stackifyapm.conf.constants import BASE_PATH
from stackifyapm.conf.constants import QUEUE_MAX_SIZE
from stackifyapm.conf.constants import TRACE_CONTEXT_VERSION
from stackifyapm.queue import QueueListener
from stackifyapm.traces import Tracer
from stackifyapm.utils.encoding import keyword_field

__all__ = ("Client",)


class Client(object):
    """
    The base StackifyAPM client, which handles loggings.

    Provides process, system and applicaiton info.
    """

    logger = logging.getLogger("stackifyapm")

    def __init__(self, config=None, **kwargs):
        self.error_logger = logging.getLogger("stackifyapm.errors")
        self.apm_logger = logging.getLogger('stackify_apm')

        _queue = queue.Queue(QUEUE_MAX_SIZE)
        self.queue_listener = QueueListener(_queue, self.transaction_handler)
        self.queue_listener.start()
        atexit.register(self.queue_listener.stop)

        self._service_info = None
        self.config = Config(config, inline_dict=kwargs)
        if self.config.errors:
            for msg in self.config.errors.values():
                self.error_logger.error(msg)

        self.tracer = Tracer(
            queue=self.queue,
        )

        self.property_info_data = self.get_property_info()

    def queue(self, transaction, delay=0):
        if delay:
            if self.queue_listener.started():
                self.queue_listener.enqueue(transaction, delay)
            else:
                self.queue_listener.enqueue(transaction, delay)
                self.queue_listener.start()
        else:
            self.transaction_handler(transaction)

    def transaction_handler(self, transaction, delay=0):
        # if transaction is done log immediately
        if transaction.is_done():
            self.apm_logger.debug(transaction.to_dict())
        else:
            # check if transaction waiting time is already exhausted
            if delay > ASYNC_MAX_WAITING_TIME_IN_SEC:
                # drop transaction if exhausted
                self.error_logger.error('Dropping transaction id: {}. Reason: Exhausted.'.format(transaction.get_id()))
            else:
                # increase waiting time and back to queue
                delay = delay * 2 or ASYNC_WAITING_TIME_IN_SEC
                self.queue(transaction, delay=delay)

    def begin_transaction(self, transaction_type, trace_parent=None, client=None):
        return self.tracer.begin_transaction(transaction_type, trace_parent=trace_parent, client=client)

    def end_transaction(self, name=None):
        return self.tracer.end_transaction(name)

    def capture_exception(self, exception=None, **kwargs):
        return self.tracer.capture_exception(exception=exception)

    def get_service_info(self):
        if self._service_info:
            return self._service_info

        language_version = platform.python_version()
        if hasattr(sys, "pypy_version_info"):
            runtime_version = ".".join(map(str, sys.pypy_version_info[:3]))
        else:
            runtime_version = language_version

        result = {
            "name": keyword_field(self.config.service_name),
            "environment": keyword_field(self.config.environment),
            "version": keyword_field(self.config.service_version),
            "agent": {
                "name": "python",
                "version": stackifyapm.VERSION or TRACE_CONTEXT_VERSION or 'unknown',
            },
            "language": {
                "name": "python",
                "version": keyword_field(platform.python_version()),
            },
            "runtime": {
                "name": keyword_field(platform.python_implementation()),
                "version": keyword_field(runtime_version),
            },
        }

        if self.config.framework_name:
            result["framework"] = {
                "name": keyword_field(self.config.framework_name),
                "version": keyword_field(self.config.framework_version),
            }

        self._service_info = result
        return result

    def get_process_info(self):
        return {
            "pid": os.getpid(),
            "ppid": os.getppid() if hasattr(os, "getppid") else None,
            "argv": sys.argv,
        }

    def get_system_info(self):
        return {
            "hostname": keyword_field(socket.gethostname()),
            "architecture": platform.machine(),
            "platform": platform.system().lower(),
        }

    def get_application_info(self):
        return {
            "application_name": self.config.application_name,
            "base_dir": self.config.base_dir,
            "environment": not self.config.environment == 'None' and self.config.environment or 'Test',
            "config_file": self.config.config_file,
        }

    def get_meta_data(self):
        if not self.property_info_data:
            self.property_info_data = self.get_property_info()

        return {
            "service_info": self.get_service_info(),
            "process_info": self.get_process_info(),
            "system_info": self.get_system_info(),
            "application_info": self.get_application_info(),
            "property_info": self.property_info_data,
        }

    def get_property_info(self):
        property_file = "{}stackify.properties".format(BASE_PATH)
        property_data = self.get_property_info_from_environment()

        if not os.path.exists(property_file):
            return property_data

        with open(property_file) as file:
            for line in file:
                line = line.rstrip("\n").split("=")
                if len(line) > 1:
                    property_data[line[0]] = line[1]

        return property_data

    def get_property_info_from_environment(self):
        stackify_env = os.getenv('STACKIFY_ENV', '')
        stackify_rum_domain = os.getenv('STACKIFY_RUM_DOMAIN')

        property_data = {}

        if stackify_env:
            envs = stackify_env.split('|')

            # if stackify environment is present
            # i will assume that client id and device id is always present
            assert len(envs) >= 2

            property_data["clientId"] = envs[0]
            property_data["deviceId"] = envs[1]

        if stackify_rum_domain:
            property_data["clientRumDomain"] = stackify_rum_domain

        return property_data
