import json
import threading
import time
import six
import sys
import traceback
import os
from six.moves.urllib.parse import urlparse

from rook.exceptions.tool_exceptions import RookLoadError


def enable_gevent_for_grpc():
    try:
        import gevent.monkey
    except ImportError:
        return

    if not gevent.monkey.is_module_patched('threading'):
        return

    if 'grpc' in sys.modules:
        raise RookLoadError("Rookout must be initialized before gRPC")

    import grpc.experimental.gevent as grpc_gevent
    grpc_gevent.init_gevent()


os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "False"

enable_gevent_for_grpc()

from grpc import insecure_channel, RpcError, StatusCode, secure_channel,\
    ssl_channel_credentials

from rook.logger import logger

from ..services.bdb_location_service import BdbLocationService

from rook.protobuf import rook_pb2_grpc
from rook.protobuf import rook_pb2


from rook.config import AgentComConfiguration

from rook.exceptions import RookCommunicationException, RookInvalidToken


class AgentCom(object):
    """This class handles the communication itself."""

    def __init__(self, aug_manager, trigger_services, output, agent_host, agent_port, token):
        self._aug_manager = aug_manager
        self._output = output
        self._stopping = False

        try:
            self._bdb = trigger_services.get_service(BdbLocationService.NAME)
        except:
            self._bdb = None

        self.agent_host = agent_host
        self.agent_port = agent_port
        self.token = token

        self._metadata = []

        if self.token:
            self._metadata.append(("rookout-token", self.token))

        self._channel = None
        self._client = None
        self._command_request = None
        self.request_timeout_in_seconds = None

        self._retries = 0
        self._last_successful_connection = 0
        self._backoff = AgentComConfiguration.BACK_OFF

        self._bg_connect_thread = None
        self._retry_thread_handle = None
        self._command_thread_handle = None

    def start(self):
        self._stopping = False

        logger.debug("Attempting connection to agent")

        # Passing class as thread argument to retrieve return value, since in python 2.x
        #  closure variables are read-only
        class CommunicationThreadArguments(object):
            def __init__(self):
                self.t, self.v, self.bt = (None, None, None)
                self.success = False

        def bg_connect_to_agent(args):
            try:
                self._start_new_connnection()
                args.success = True
            except RookInvalidToken:
                args.t, args.v, args.bt = sys.exc_info()
            except RookCommunicationException:
                args.t, args.v, args.bt = sys.exc_info()
                # Logger might not exist in interpreter shutdown
                if logger:
                    logger.warn("Failed to connect to agent. Will keep trying")
                self._start_retry_thread()
            except Exception:
                args.t, args.v, args.bt = sys.exc_info()
                # Logger might not exist in interpreter shutdown
                if logger:
                    logger.error("Unexpected error: " + traceback.format_exc())

        arguments = CommunicationThreadArguments()
        self._bg_connect_thread = threading.Thread(target=bg_connect_to_agent, args=(arguments,))
        self._bg_connect_thread.daemon = True
        self._bg_connect_thread.start()
        self._bg_connect_thread.join(AgentComConfiguration.GRPC_TIMEOUT)

        # On windows OS first connection will most likely fail - but will succeed later on (in retry thread)
        if not arguments.success:
            if None not in [arguments.t, arguments.v, arguments.bt]:
                six.reraise(arguments.t, arguments.v, arguments.bt)
            raise RookCommunicationException()

    def send_rook_messages(self, messages):
        # timeout in seconds
        if self._client:
            self._client.send_messages(messages, metadata=self._metadata, timeout=self.request_timeout_in_seconds)

    def stop(self, final=True):
        self._stopping = True
        if final:
            self._output.flush_messages()

        self._output.stop_sending_messages()

        if self._command_request:
            self._command_request.cancel()
            self._command_request = None

        if self._client:
            self._client = None
            self._channel.close()
            self._channel = None

        if self._command_thread_handle:
            self._command_thread_handle.join()
        if self._bg_connect_thread:
            self._bg_connect_thread.join()
        if self._retry_thread_handle:
            self._retry_thread_handle.join()

    def _build_client(self):
        # swap within a single line to avoid races
        self._client, self._channel, current_client, current_channel = None, None, self._client, self._channel
        if current_channel:
            current_channel.close()
        del current_channel
        del current_client

        keepaliveTime = 2 * 60 * 1000
        logger.debug("Connecting to agent-\t%s:%d", self.agent_host, int(self.agent_port))
        options = [('grpc.max_receive_message_length', AgentComConfiguration.MAX_MESSAGE_LENGTH),
                   ('grpc.keepalive_time_ms', keepaliveTime),
                   ('grpc.keepalive_timeout_ms', 2500),
                   ('grpc.http2.max_pings_without_data', 0),
                   # min_time_between_pings_ms by default is 5 mintues - needs to be less then keepaliveTime
                   ('grpc.http2.min_time_between_pings_ms', keepaliveTime - 1000)
                   ]

        self.request_timeout_in_seconds = AgentComConfiguration.REQUEST_TIMEOUT_SECS

        secure_connection = False
        new_host = self.agent_host

        parsed_url = urlparse(self.agent_host)
        if parsed_url.scheme != '':
            new_host = parsed_url.netloc
            secure_connection = (parsed_url.scheme == "https")

        connection_string = new_host + ':' + str(self.agent_port)
        if secure_connection:
            credentials = ssl_channel_credentials()
            self._channel = secure_channel(connection_string, credentials, options=options)
        else:
            self._channel = insecure_channel(connection_string, options=options)

        logger.debug("Creating client")
        self._client = rook_pb2_grpc.AgentManagementServiceStub(self._channel)

    def _start_new_connnection(self):
        logger.debug("Starting a new connection")

        self._build_client()

        logger.debug("Getting rook info")
        info = self._output.get_rook_info()

        logger.debug("Creating request")

        self._command_request = self._client.new_rook_notification(info, metadata=self._metadata)
        # Get initial augs
        success = self._command_loop(self._command_request)
        if success is not True:
            raise RookCommunicationException("Failed to connect to agent")

        self._last_successful_connection = int(time.time())

        # Setup update/retry channel in the background
        logger.debug("Creating commands thread")
        self._command_thread_handle = threading.Thread(target=self._command_thread, args=(self._command_request, ),
                                  name=AgentComConfiguration.COMMAND_THREAD_NAME)
        self._command_thread_handle.daemon = True
        self._command_thread_handle.start()

    def _command_loop(self, commands_request):
        """
        :return: Whether initialization succeeded
        """
        logger.debug("Entering command loop")

        try:
            for command in commands_request:
                if command.command_type == rook_pb2.RookCommand.COMMAND_ADD_AUG:
                    logger.info("Got an add aug command")
                    try:
                        self._aug_manager.add_aug(json.loads(command.aug_json))
                    except:
                        logger.exception("Error processing new aug")

                elif command.command_type == rook_pb2.RookCommand.COMMAND_REMOVE_AUG:
                    logger.info("Got a remove aug command")
                    try:
                        self._aug_manager.remove_aug(command.aug_id)
                    except:
                        logger.exception("Error removing aug")

                elif command.command_type == rook_pb2.RookCommand.COMAND_INIT_FINISHED:
                    logger.info("Finished initialization")
                    self._output.start_sending_messages()
                    return True

                elif command.command_type == rook_pb2.RookCommand.COMMAND_CLEAR_AUGS:
                    logger.info("Got clear augs command")
                    try:
                        self._aug_manager.clear_augs()
                    except:
                        logger.exception("Error in clearing augs")

                elif command.command_type == rook_pb2.RookCommand.COMMAND_SET_ROOK_ID:
                    logger.info("Got set rook_id command- %s", command.rook_id)
                    self._output.set_rook_id(command.rook_id)

                else:
                    logger.error("Unknown command %s", command)
        except RpcError as exc:
            # This exception can occur during process shutdown
            if exc.code() == StatusCode.PERMISSION_DENIED or exc.details() == "GrpcInvalidTokenException":
                logger.error('Bad token while connecting to router', exc_info=1)
                raise RookInvalidToken()

            if self._retries:
                logger.info("Error in command loop", exc_info=1)
            else:
                logger.exception("Error in command loop")
        except:
            if self._retries:
                logger.info("Error in command loop", exc_info=1)
            else:
                logger.exception("Error in command loop")

        self._output.stop_sending_messages()
        logger.warn("Exiting with failure")
        return False

    def _command_thread(self, command_request):
        try:
            logger.debug("Command thread started")
        except TypeError:
            # When running python -m rook, there is a race condition where the thread might start
            # during interpreter shut down
            return

        # Disable bdb monitoring of this thread
        if self._bdb:
            self._bdb.ignore_current_thread()

        if command_request:
            ret = self._command_loop(command_request)
            if ret is False and self._stopping is True:  # failed, but it was because we're stopping
                return

        self._start_retry_thread()

    def _start_retry_thread(self):
        if not self._retry_thread_handle or not self._retry_thread_handle.is_alive():
            logger.debug("Starting retry thread")
            self._retry_thread_handle = threading.Thread(target=self._retry_thread,
                                                         name=AgentComConfiguration.COMMAND_THREAD_NAME)
            self._retry_thread_handle.daemon = True
            self._retry_thread_handle.start()
        else:
            logger.warn("Retry thread already running")

    def _retry_thread(self):
        logger.info("Starting retry thread")

        # Disable bdb monitoring of this thread
        if self._bdb:
            self._bdb.ignore_current_thread()

        min_time_since_last_successful_connection = 60
        if int(time.time() > self._last_successful_connection + min_time_since_last_successful_connection):
            self._retries = 0
            self._backoff = AgentComConfiguration.BACK_OFF

        while True:
            try:
                if not self._client:
                    break

                self._start_new_connnection()
                break
            except:
                # Interpreter shutdown
                if not logger:
                    return

                if self._retries > 0:
                    self._backoff = min(self._backoff * 2, AgentComConfiguration.MAX_SLEEP)
                    logger.debug("Sleeping for %d seconds, retry num %d", self._backoff, self._retries)
                    time.sleep(self._backoff)

                self._retries += 1
