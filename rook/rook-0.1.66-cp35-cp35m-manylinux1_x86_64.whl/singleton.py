"""This module is in charge of managing the rook's module state.

The external interface for the module is Rook located in rook.rook."""

import os
import sys
import platform
import atexit

# This must be the first import, otherwise enable_gevent_for_grpc will fail since grpc has already been imported
from rook.logger import logger

from rook.config import ControllerAddress, AgentComConfiguration

from .augs.augs_manager import AugsManager
from .trigger_services import TriggerServices

from rook.exceptions import RookInterfaceException, RookVersionNotSupported

from .atfork import install_fork_handler


class _Singleton(object):
    """This is singleton is the class managing the module.

    It should never be referred to directly, instead use obj in this module."""

    def __init__(self):
        """Initialize the object, sets member variables."""
        self._check_version_supported()

        logger.info("Initializing Rook under process-%d", os.getpid())

        self._services_started = False

        self._trigger_services = TriggerServices()
        self._aug_manager = None
        self._fork_handler = None
        self._output = None

        self._agent_com = None

    def _start_trigger_services(self):
        """Start trigger services.

        Calling this method multiple times will have no effect.
        """
        # Don't double init services
        if self._services_started:
            return

        if self._output is None:
            from rook.com.output import Output
            self._output = Output(self._trigger_services)

        self._trigger_services.start()
        self._aug_manager = AugsManager(self._trigger_services, self._output)
        self._services_started = True

    def _stop_trigger_services(self):
        if not self._services_started:
            return

        self._aug_manager = None
        self._trigger_services.close()

        self._services_started = False

    def get_trigger_services(self):
        return self._trigger_services

    def connect(self, token, host, port, tags=None, labels=None, async_start=False):
        """Connect to the Agent."""
        if self._agent_com:
            raise RookInterfaceException("Multiple connection attempts not supported!")

        self._fork_handler = install_fork_handler()

        if not host:
            host = ControllerAddress.HOST

        if not port:
            port = int(ControllerAddress.PORT)

        if not token:
            token = os.environ.get('ROOKOUT_TOKEN')

        logger.debug("Initiating AgentCom-\t%s:%d", host, int(port))
        if host.startswith('ws://') or host.startswith('wss://'):
            from rook.protobuf2 import variant_pb2
            import rook.processor.namespace_serializer
            rook.processor.namespace_serializer.rook_pb2 = variant_pb2

            from rook.com_ws.agent_com_ws import AgentCom
            from rook.com_ws.command_handler import CommandHandler
            from rook.com_ws.output_ws import Output

            labels = labels or {}
            tags = tags or []

            self._output = Output()
            self._agent_com = AgentCom(host, port, token, labels, tags)
            self._start_trigger_services()
            self._command_handler = CommandHandler(self._agent_com, self._aug_manager)
            self._output.set_agent_com(self._agent_com)
            self._agent_com.start()
            if async_start is False:
                self._agent_com.wait_for_ready(AgentComConfiguration.GRPC_TIMEOUT)
        else:
            from .com.agent_com import AgentCom
            from rook.com.output import Output

            if async_start is True:
                AgentComConfiguration.GRPC_TIMEOUT = 0

            self._output = Output(self._trigger_services)

            if tags is not None:
                self._output.tags = tags
            if labels is not None:
                self._output.labels = labels

            self._start_trigger_services()
            self._agent_com = AgentCom(self._aug_manager, self._trigger_services, self._output, host, port, token)
            self._output.set_agent_com(self._agent_com)
            self._agent_com.start()


    logger.info("Successful connection to agent")

    def flush(self):
        self._output.flush_messages()

    def stop(self):
        logger.debug("Shutting down")

        if self._agent_com is not None:
            self._agent_com.stop()

        self._stop_trigger_services()

        self._agent_com = None

    @staticmethod
    def _check_version_supported():
        try:
            supported_platforms = ['pypy', 'cpython']
            supported_version = ['2.7', '3.5', '3.6', '3.7']

            current_platform = platform.python_implementation().lower()
            if current_platform not in supported_platforms:
                raise RookVersionNotSupported("Rook is not supported in this platform: " + current_platform)

            major, minor, _, _, _ = sys.version_info
            current_version = "{}.{}".format(major, minor)
            if current_version not in supported_version:
                raise RookVersionNotSupported("Rook is not supported in this python version: " + current_version)

        except Exception as e:
            import traceback
            traceback.print_exc()

            raise e


singleton_obj = _Singleton()


def exit_handler():
    try:
        logger.info("Exit handler called - flushing")
        if singleton_obj._agent_com:
            singleton_obj.flush()
    except:
        logger.exception("Flush failed")
    logger.info("Exit handler finished")


atexit.register(exit_handler)
