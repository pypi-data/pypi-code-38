import asyncio
import functools
import json
import logging
import uuid
from collections import defaultdict
from queue import Queue
import websockets
import jwt
import websockets
from websockets import exceptions
from traceback import format_exc
from missinglink.resource_manager.docker.config import get_active_config
from .api_commands import WsAPI

logger = logging.getLogger(__name__)


def wrap_socket_command(fn):
    @functools.wraps(fn)
    async def wrapped(bb, *args, **kwargs):
        return await bb.wrapped(fn, *args, **kwargs)

    return wrapped


def cancelable_task(fn):
    @functools.wraps(fn)
    async def wrapped(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except asyncio.CancelledError:
            logger.debug('%s cancelled', fn.__name__)

    return wrapped


class Backbone(object):
    # there are no async contextmanagers in 3.6 so lets just hack this for now
    async def wrapped(self, fn, *args, **kwargs):
        fn_name = fn.__name__
        hint = '%s: %s %s' % (fn_name, args, kwargs)
        allow_in_connecting = kwargs.pop('allow_in_connecting', False)
        logger.debug(hint)

        while True:
            await self.await_connect(hint=hint, allow_connecting=allow_in_connecting)

            try:
                return await fn(self, *args, **kwargs)
            except (exceptions.InvalidState, websockets.exceptions.ConnectionClosed) as known_error:
                logger.warning('FAILED %s (%s)', hint, str(known_error))
                self.connected = False
                self.connecting = False
                self.reconnect_future.set_result(True)
                logger.info('Sleeping for %s seconds before reconnect', self.reconnect_sleep)
                await  asyncio.sleep(self.reconnect_sleep, loop=self.loop)

            except asyncio.CancelledError:
                raise
            except Exception as ex:
                logger.error('Failed to proc %s: %s', hint, str(ex), exc_info=1)

    def __init__(self, active_config=None, loop=None, **kwargs):
        self.loop = loop or asyncio.get_event_loop()
        self.active_config = active_config or get_active_config()
        self.server_address = self.active_config.general.ws_server

        self.api = WsAPI(self.active_config, self.job_completed_callback)
        self.api_mapping = self.api.api_mapping()
        self.api_mapping['KILL_SERVER:1'] = self.kill_server
        self.jwt = jwt.decode(self.active_config.general.jwt, verify=False)
        self.sid = self.jwt.get("uid")
        self.endpoint = f'{self.server_address}/{self.sid}'
        logger.debug('Connection endpoint: %s', self.endpoint)
        self.reconnect_sleep = kwargs.get('reconnect_sleep', 20)
        self.recv_timeout = kwargs.get('recv_timeout', 60)
        self.ping_timeout = kwargs.get('ping_timeout', 10)
        self.ping_interval = kwargs.get('ping_interval', 30)
        self.socket_connection = None
        self.connected = False
        self.connecting = False
        self.reconnection_queue = Queue()
        self.rpc_dict = defaultdict(asyncio.Future)
        self.reconnect_future = asyncio.Future(loop=self.loop)
        self.single_job = self.active_config.general.get('pull_job')
        self.single_job_mode = self.single_job is not None
        self.loop.set_debug(kwargs.pop('debug', False))
        self.execution_future = None

    async def kill_server(self, send_async=None, **kwargs):
        logger.error('kill_server! %s', kwargs)
        self.cancel()
        return True

    def cancel(self):
        logger.info('Exiting')
        if self.execution_future:
            self.execution_future.cancel()

    def job_completed_callback(self, job_id, task):
        if self.single_job_mode:
            logger.debug('%s completed, exiting', job_id)
            self.cancel()

    async def await_connect(self, allow_connecting=False, hint=None):
        hint = hint or uuid.uuid4()
        if self.connected and self.reconnection_queue.empty():
            return
        if self.connecting and allow_connecting:
            return
        logger.debug('%s enqueue', hint)
        reconnect_future = asyncio.Future(loop=self.loop)
        self.reconnection_queue.put(reconnect_future)
        await asyncio.sleep(0)
        await reconnect_future
        logger.debug('%s resumed', hint)

    @cancelable_task
    async def disconnection_monitor(self):
        logger.debug(f'disconnection_monitor start')
        while True:
            if self.reconnect_future is not None:
                logger.debug(f'wait for disconnect')
                await  self.reconnect_future
            logger.debug('Connecting...')
            self.connected = False
            self.connecting = False

            self.socket_connection = await  self._connect()
            logger.debug('_connected... %s', self.socket_connection)
            self.connecting = True
            self.reconnect_future = asyncio.Future(loop=self.loop)

            task = self.task_from_msg(dict(command='_on_connect'), admin=True)
            if task:
                await task
            self.connected = True
            logger.debug('_connected... queue empty? %s', self.reconnection_queue.empty())

            while not self.reconnection_queue.empty():
                future = self.reconnection_queue.get_nowait()
                future.set_result(True)

    async def _connect(self):
        logger.debug('_connect')
        while True:
            try:
                logger.info('Connect to %s', self.endpoint)
                x = await asyncio.wait_for(
                    websockets.connect(
                        self.endpoint,
                        ping_interval=self.ping_interval,
                        ping_timeout=self.ping_timeout,
                        loop=self.loop
                    ),
                    loop=self.loop, timeout=5)
                return x
            except asyncio.TimeoutError:
                logger.warning('Failed to connect to [%s] : Timeout. Will retry in %s ', self.endpoint, self.reconnect_sleep)
                await asyncio.sleep(self.reconnect_sleep, loop=self.loop)

            except asyncio.CancelledError:
                raise

            except Exception as ex:
                logger.error('Failed to connect to %s, will retry in %s: %s', self.server_address, self.reconnect_sleep, str(ex))
                await asyncio.sleep(self.reconnect_sleep, loop=self.loop)

    @wrap_socket_command
    async def send(self, rpc=False, **kwargs):
        call_rpc = None
        call_id = uuid.uuid4().hex
        if rpc:
            kwargs['__RPC_CALL_ID'] = call_id
            call_rpc = self._rpc_register(call_id)
        msg = json.dumps(kwargs)
        logger.debug("     > %s", msg)
        await self.socket_connection.send(msg)
        if rpc:
            return await call_rpc
        return

    def _rpc_register(self, call_id):
        return self.rpc_dict[call_id]

    @wrap_socket_command
    async def recv(self):
        msg_ = await self.socket_connection.recv()
        logger.debug("     < %s", msg_)
        return json.loads(msg_)

    def handle_rpc(self, msg):
        rpc_id = msg.pop('__RPC_CALL_ID')
        future = self.rpc_dict.pop(rpc_id, None)
        if future is not None:
            future.set_result(msg)
        else:
            logger.warning('Got response for RPC_CALL_ID: %s but no future is present :( %s', rpc_id, msg)

    async def _read_msgs(self):
        logger.debug('_read_msgs')
        while True:
            msg = await self.recv()
            if msg is None:
                return

            if msg.get('__RPC_CALL_ID') is not None:
                self.handle_rpc(msg)
            else:
                yield msg

    async def _task_send_command(self, admin, **kwargs):
        kwargs.pop('allow_in_connecting', None)
        return await self.send(allow_in_connecting=admin, **kwargs)

    def task_from_msg(self, msg, admin=False):
        logger.debug('%s, admin? %s', msg, admin)
        cmd_name = msg.get("command")
        command = self.api_mapping.get(cmd_name)

        if command is None:
            logger.warning("Command not found %s", cmd_name)
            return
        data = msg.get('data')

        if isinstance(data, dict):
            logger.debug('%s(%s)', cmd_name, data)
            return command(send_async=functools.partial(self._task_send_command, admin), **data)
        else:
            if data is not None:
                logger.warning('No valid data in %s', json.dumps(data))
                return

            logger.debug('%s', cmd_name)
            return command(send_async=functools.partial(self._task_send_command, admin))

    @classmethod
    def task_result(cls, msg, future: asyncio.Future):
        try:
            task_response = future.result()
            if task_response is not None:
                logger.debug('JOB: %s => %s', task_response, msg)
            else:
                logger.warning('JOB:F %s', msg)
        except Exception as e:
            logger.exception('JOB:E %s -> %s', str(e), msg)
            return

    @cancelable_task
    async def listen_for_messages(self):
        logger.debug('listen_for_messages')
        async for msg in self._read_msgs():
            coro = self.task_from_msg(msg)
            task = asyncio.ensure_future(coro, loop=self.loop)
            task.add_done_callback(functools.partial(self.task_result, msg))
            await asyncio.sleep(0)

    async def single_job_timeout(self):
        if not self.single_job_mode:
            return
        logger.debug('Scheduling Single Mode timer')
        await asyncio.sleep(self.recv_timeout)
        logger.debug('Scheduling Single Mode timer.. timeout')
        if not self.api.get_running():
            logger.debug('No running jobs and running in single mode... leaving')
            self.cancel()

    def get_serve_futures(self):
        return [asyncio.ensure_future(x, loop=self.loop) for x in [self.single_job_timeout(), self.listen_for_messages(), self.disconnection_monitor()]]

    async def serve(self):
        logger.info("Server starting")
        self.reconnect_future.set_result(True)
        futures = self.get_serve_futures()
        self.execution_future = asyncio.ensure_future(asyncio.wait(futures, loop=self.loop))
        try:
            await self.execution_future
        except asyncio.CancelledError:
            for f in futures:
                if not f.done():
                    logger.debug('Cancelling %s', f)
                    f.cancel()
            logger.debug('Bye')

    @classmethod
    def run(cls, *args, **kwargs):
        bb = cls(*args, **kwargs)
        bb.loop.run_until_complete(bb.serve())
