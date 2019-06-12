import asyncio
import json
from inspect import isfunction
from websockets import connect
from websockets.protocol import State
from websockets.exceptions import ConnectionClosed

from inmation_api_client.eventemitter import EventEmitter
from inmation_api_client.error import Error
from inmation_api_client.model import AuthenticateRPC, CloseRPC, ExecFunctionRPC, RunScriptRPC, \
    SubscribeRPC, ReadRPC, ReadHistoricalDataRPC, ReadRawHistoricalDataRPC, WriteRPC, MassRPC, \
    WSConnectionInfo, SubscriptionType, Item, ItemValue, RawHistoricalDataQuery
from inmation_api_client.options import Options

import logging
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def invoke_callback(cbk, *args):
    """ invoke_callback """
    if isfunction(cbk):
        return cbk(*args)


RECONNECT_DELAY_TIME = 1
RECONNECT_DELAY_TIME_AFTER_ERROR = 5
MAX_RECCONNECT_ATTEMPTS_AFTER_ERROR = 2


class WSClient(EventEmitter):
    """Set up the WebSocket client."""
    DEBUG_LOG = False

    def __init__(self, ioloop):
        self._reconnect_delay_time = RECONNECT_DELAY_TIME
        self.auto_reconnect = False
        self._ws = None
        # Connection Info contains e.g. sessionid, state and whether the authentication went well.
        self._connection_info = WSConnectionInfo()
        self._subscribed_items = {}
        self.url = None
        self.options = None
        self.ioloop = ioloop or asyncio.get_event_loop()
        self.reconnect_counter = 0

        super().__init__(loop=self.ioloop)

        def process_ready_state_cb(ready_state):
            if self._connection_info.set_ready_state(ready_state):
                self.emit(SubscriptionType.ConnectionChanged,
                          self._connection_info)

        self._process_ready_state = process_ready_state_cb

    def get_ioloop(self):
        """ Get the asyncio event loop"""
        return self.ioloop

    @property
    def connection_info(self):
        """ Get connection info """
        return self._connection_info

    def _subscribe_req_id_callback(self, reqid, cbk):
        if isfunction(cbk):
            self.once(str(reqid), lambda *args: cbk(*args))

    async def authenticate(self, options):
        """ Authentication request to the WebSocket server.
        Args:
            options (Options): The options object with auth or authorization info
        Returns:
            void
        """
        msg = AuthenticateRPC(options)
        await self.send(msg)

    async def close(self):
        """ Close connection to the WebSocket server."""
        self.auto_reconnect = False

        if self._ws is not None:
            if isfunction(self.remove_all_listeners):
                self.remove_all_listeners()
            if WSClient.DEBUG_LOG:
                print('Closing the WebSocket connection')
            await self.send(CloseRPC())
            self._ws.close()

            self._process_ready_state(self._ws.state)

    async def connect(self, url, options):
        """ Connect to the WebSocket server.
        Args:
            url (str): URL of the WebSocket
            options (object): Options object
        """

        if not isinstance(url, str):
            raise Error('A WebSocket URL is not specified in the configuration.')
        if not (isinstance(options, Options) or isinstance(options, dict)):
            raise Error('The <<options>> argument is required when establishing a connection.')

        self.url = url
        self.options = options

        if WSClient.DEBUG_LOG:
            logging.info('Connecting to: {}'.format(self.url))

        async def _connect(self):
            """connect to the websocket server."""
            try:
                # Disable asynchronous context manager functionality
                # max_size = None disables the size limit of incoming messages
                self._ws = await connect(self.url, timeout=options.tim or 10, loop=self.ioloop, max_size=None).__iter__()
            except OSError as err:
                if err.strerror is not None:
                    return err.strerror
            except Exception as e:
                return str(e)

        _con_res = await _connect(self)

        if self._ws:
            self.onopen(self._ws.state)
        else:
            await self.onerror(Error(_con_res))

        self.auto_reconnect = True
        await self.authenticate(options)

        try:
            if self._ws is not None:
                if self._ws._pop_message_waiter is None:
                    msg = await self._ws.recv()
                    await self.onmessage(msg)
        except ConnectionClosed as e:
            await self.onclose(e)

    async def reconnect(self):
        """ reconnect. """
        if not self.auto_reconnect:
            return

        await asyncio.sleep(self._reconnect_delay_time)

        logging.info('Re-connecting to: {} ...'.format(self.url))
        await self.connect(self.url, self.options)

        while True:
            if not self._connection_info.state_string == WSConnectionInfo.CONNECTEDSTRING \
                    and not self._connection_info.authenticated:
                await self.connect(self.url, self.options)
            else:
                break

    def onopen(self, ready_state):
        """ onopen. """
        if WSClient.DEBUG_LOG:
            print('WebSocket onopen')
        # Restore reconnect delay time.
        self._reconnect_delay_time = RECONNECT_DELAY_TIME
        self._process_ready_state(ready_state)

    async def onerror(self, err):
        """ onerror. """
        if WSClient.DEBUG_LOG:
            print('WebSocket onerror: {}'.format(err.message))
        if err:
            if 'Failed to connect' in err.message:
                self._reconnect_delay_time = RECONNECT_DELAY_TIME_AFTER_ERROR
                if self.reconnect_counter <= MAX_RECCONNECT_ATTEMPTS_AFTER_ERROR:
                    self.reconnect_counter += 1
                    await self.reconnect()
                else:
                    self.reconnect_counter = 0
                    raise ConnectionRefusedError(
                        'Failed to connect, either the credentials are invalid or the Core service is down.')
            elif 'call failed' in err.message:
                raise ConnectionRefusedError(err.message)

        self.emit(WSClient.ERROR, err.message)

    async def onclose(self, exception):
        """ onclose. """
        if WSClient.DEBUG_LOG:
            print('WebSocket onclose, message: {}'.format(exception))

        self._process_ready_state(self._ws.state)
        if isfunction(self.remove_all_listeners):
            self.remove_all_listeners()

        if self.auto_reconnect:
            self.emit(WSClient.ERROR, str(exception))
            await self.reconnect()
        else:
            await self.close()

    # all the self.emit() will be invoked asap with ioloop.call_soon()
    async def onmessage(self, msg):
        """ onmessage. """
        if msg is None:
            return

        message = json.loads(msg)

        if WSClient.DEBUG_LOG:
            print("Receiving: {}".format(msg))

        err = None
        code = None
        if 'code' in message:
            code = int(message['code'])

        if code < 200 or code > 299 and 'error' in message:
            err_msg = ''
            if 'code' in message.keys():
                err_msg += '\nFailed with Code {:d}'.format(
                    message['code'])
            if 'error' in message.keys():
                err_msg += ", Message: {}".format(message['error'])

            err = Error(err_msg)

        # Store or wipe Connection Info.
        connection_changed = False
        if 'type' in message and 'data' in message:
            if message['type'] == WSClient.CONNECTION or message['type'] == WSClient.AUTHENTICATION:
                connection_changed = self._connection_info.process_info(
                    message['data'], self._ws.state)

        # Emit Error
        if err is not None:
            # if 'type' in message:
            #     if message['type'] == 'authentication':
            await self.onerror(err)
            self.emit(WSClient.ERROR, err)

        # Emit connection_changed on new Connection Info or readyState.
        if connection_changed:
            self.emit(SubscriptionType.ConnectionChanged,
                      self._connection_info)

        # Emit the whole message
        self.emit(WSClient.MESSAGE, err, message)

        # Emit for those who listens to a specific reqid.
        if 'reqid' in message and 'data' in message:
            self.emit(str(message['reqid']), err, message['data'], code)

        try:
            if str(message['data']['authenticated']).lower() == 'true':
                self._connection_info['_authenticated'] = True
        except:
            pass

        # Emit for those who listens to a specific type.
        if 'type' in message and 'data' in message:
            self.emit(message['type'], err, message['data'])

            # Integrated actions
            # if message['type'] == WSClient.AUTHENTICATION:
            #     await self.subscribe()

        if 'reqid' in message and 'type' in message:
            if message['type'] == WSClient.CONNECTION:
                await self.authenticate(self.options)

    def run_async(self, tasks):
        loop = self.get_ioloop()
        loop.run_until_complete(
            asyncio.wait(
                tasks
            )
        )

    async def receive_msg(self):
        try:
            msg = await asyncio.wait_for(self._ws.recv(), timeout=10)
        except asyncio.TimeoutError:
            # No data in x seconds, check the connection
            try:
                pong_waiter = await self._ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=5)
            except:
                # No response to ping in x seconds, reconnect
                await self.reconnect()
        except ConnectionClosed as e:
            await self.onclose(e)
        except Exception as e:
            await self.onerror(Error(str(e)))
        else:
            await self.onmessage(msg)
            return json.loads(msg)

    async def exec_function(self, context, library_name, function_name, function_arg=None, options=None):
        err_msg = ''
        if not isinstance(context, Item):
            err_msg += 'The context arg must be of type Item.\n'
        if not isinstance(library_name, str):
            err_msg += 'The library_name arg must be of type str.\n'
        if not isinstance(function_name, str):
            err_msg += 'The function_name arg must be of type str.\n'
        if function_arg:
            if not isinstance(function_arg, dict):
                err_msg += 'The function_arg arg must be of type dict.\n'
        if err_msg:
            logging.error("[exec_function]\n{}".format(err_msg))

        return await self.send(ExecFunctionRPC(
            context, library_name, function_name, function_arg, options))

    async def send(self, data):
        """Send a data message.
        Args:
            data (object): Data object which needs to be sent
        Returns:
            dict (response)
        """
        if self._ws is not None:
            if self._ws.state == State.OPEN:
                json_data = json.dumps(data)
                if WSClient.DEBUG_LOG:
                    print("Sending: {}".format(json_data))

                await self._ws.send(json_data)
                if self._ws._pop_message_waiter is None:
                    return await self.receive_msg()

    async def subscribe(self, items, subsc_type, cbk=None, options=None):
        """ Subscribe item(s) of a specific subscription type"""
        subscription_types = SubscriptionType.get_all()
        if isinstance(items, Item):
            items = [items]

        if items and isinstance(items, list) and subsc_type in subscription_types:
            if subsc_type not in self._subscribed_items.keys():
                self._subscribed_items[subsc_type] = []

            new_items = []
            for item in items:
                if isinstance(item, Item):
                    self._subscribed_items[subsc_type].append(item['p'])
                    new_items.append(item)
                    if WSClient.DEBUG_LOG:
                        print('Subscribe item: {}, subscription type: {}'.format(
                            item, subsc_type))
            msg = SubscribeRPC(new_items, subsc_type, options)
            self._subscribe_req_id_callback(msg.reqid, cbk)

            await self.send(msg)

            async def receive(self):
                while len(self._subscribed_items[subsc_type]) > 0:
                    await self.receive_msg()

            await receive(self)

    async def unsubscribe(self, items=None, subsc_type=None, cbk=None, options=None):
        """ Unsubscribe item(s) of a specific subscription type"""
        subscription_types = SubscriptionType.get_all()
        if isinstance(items, Item):
            items = [items]

        if items and isinstance(items, list) and subsc_type in subscription_types:
            if subsc_type not in self._subscribed_items.keys():
                logging.info('There are no subscribed item(s) with {} type'.format(subsc_type))
            else:
                subscribed_items = self._subscribed_items[subsc_type]
                items = items.copy()

                for item in items:
                    if isinstance(item, Item) and item['p'] in subscribed_items:
                        if WSClient.DEBUG_LOG:
                            print('Unsubscribe item: {}, subscription type: {}'.format(
                                item, subsc_type))
                        subscribed_items.remove(item['p'])

                new_items = [Item(i) for i in subscribed_items]

                msg = SubscribeRPC(new_items, subsc_type, options)
                self._subscribe_req_id_callback(msg.reqid, cbk)

                await self.send(msg)

    async def read(self, items, options):
        if items and not isinstance(items, list):
            logging.error('The items arg must be a list of type Item')

        return await self.send(ReadRPC(items, options))

    async def read_historicaldata(self, items, start_time, end_time, number_of_intervals, options):
        if not isinstance(items, list):
            logging.error('The items arg must be a list of type HistoricalDataItem')

        return await self.send(ReadHistoricalDataRPC(
            items, start_time, end_time, number_of_intervals, options))

    async def read_rawhistoricaldata(self, queries, options):
        if not (isinstance(queries, list) or isinstance(queries, RawHistoricalDataQuery)):
            logging.error('The queries arg must be a list of RawHistoricalDataQuery or a single RawHistoricalDataQuery')

        return await self.send(ReadRawHistoricalDataRPC(queries, options))

    async def run_script(self, context, script, options=None):
        if not isinstance(context, dict):
            logging.error('The context arg must be of type Identity')
        if not isinstance(script, str):
            logging.error('The script arg must be of type str')

        return await self.send(RunScriptRPC(context, script, options))

    async def write(self, items, options):
        if isinstance(items, ItemValue):
            items = [items]
        if not isinstance(items, list):
            logging.error('The items arg must be a list of type ItemValue')

        return await self.send(WriteRPC(items, options))

    async def mass(self, entires, options=None):
        if not isinstance(entires, list):
            logging.error('The entires arg must be a list of type dict')
        required_attrs = ['path', 'class']
        for entry in entires:
            if not isinstance(entry, dict):
                logging.error('The entry must be of type dict')
            for attr in required_attrs:
                if attr not in entry.keys():
                    logging.error('Entry is missing a required field: {}'.format(attr))

        return await self.send(MassRPC(entires, options))

WSClient.AUTHENTICATION = 'authentication'
WSClient.CONNECTION = 'connection'
WSClient.ERROR = 'error'
WSClient.MESSAGE = 'message'
WSClient.READ = 'read'
WSClient.WRITE = 'write'
