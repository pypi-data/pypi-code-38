import asyncio
import inspect
import logging
from sys import exit
from inmation_api_client.wsclient import WSClient
from inmation_api_client.model import SubscriptionType


class Client(object):
    """ client class. """

    def __init__(self, ioloop=None):
        # Set up the API Client
        self._ws_client = WSClient(ioloop)

    @staticmethod
    def EnableDebug():
        WSClient.DEBUG_LOG = True

    @staticmethod
    def DisableDebug():
        WSClient.DEBUG_LOG = False

    def GetEventLoop(self):
        return self._ws_client.get_ioloop()

    def RunAsync(self, tasks=[]):
        err_msg = "RunAsync() tasks argument must be a list of coroutines"
        if not (tasks and isinstance(tasks, list)):
            logging.warning(err_msg)
        for t in tasks:
            if not inspect.isawaitable(t):
                logging.warning(err_msg)
        self._ws_client.run_async(tasks)

    def Connect(self, host: str = '127.0.0.1', port: int = 8002, options=None):
        """ Connect to the WebSocket server.
        Args:
            host: Host name or IP address where the Web API is running
            port: The port of the Web API
            options (object): Options object
        Returns:
            void
        """
        try:
            url = 'ws://{}:{}/ws'.format(host, str(port))
            self.GetEventLoop().run_until_complete(self._ws_client.connect(url, options))
        except ConnectionRefusedError as e:
            exit(str(e))

    def Disconnect(self):
        """ Disconnect from the WebSocket server. """
        self.GetEventLoop().run_until_complete(self._ws_client.close())

    def ExecuteFunction(self, context, library_name, function_name, function_arg=None, options=None):
        """ Execute a Lua function async.
        Args:
            context (dict): dict with object like {"p": "/System/Core/Test/Item1"}
            library_name (str): Library Script name.
            function_name (str): Library function name.
            function_arg (dict): Library function arguments packed in a dictionary
            options (object): Options object
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(
            self._ws_client.exec_function(context, library_name, function_name, function_arg, options))

    async def ExecuteFunctionAsync(self, context, library_name, function_name, function_arg=None, options=None):
        """Execute a Lua function.
        Args:
            context (dict): dict with object like {"p": "/System/Core/Test/Item1"}
            library_name (str): Library Script name.
            function_name (str): Library function name.
            function_arg (dict): Library function arguments packed in a dictionary
            options (object): Options object
        Returns:
            dict (response)
        """
        return await self._ws_client.exec_function(context, library_name, function_name, function_arg, options)

    def _on(self, event_name, cbk):
        """ Subscribe a callback to an event. """
        if not inspect.isfunction(cbk):
            return

        self._ws_client.on(event_name, cbk)

    def OnChildrenCountChanged(self, cbk):
        """ Specify a callback for children count changes. """
        # self._on(SubscriptionType.ChildrenCountChanged, cbk)
        raise NotImplementedError

    def OnConfigVersionChanged(self, cbk):
        """ Specify a callback for configuration version changes. """
        # self._on(SubscriptionType.ConfigurationChanged, cbk)
        raise NotImplementedError

    def OnConnectionChanged(self, cbk):
        """ Specify a callback for connection changes. """
        self._on(SubscriptionType.ConnectionChanged, cbk)

    def OnDataChanged(self, cbk):
        """ Specify a callback for data changes. """
        self._on(SubscriptionType.DataChanged, cbk)

    def OnError(self, cbk):
        """ Specify a callback which is triggered when an error occurs. """
        self._on(WSClient.ERROR, cbk)

    def OnMessage(self, cbk):
        """ Specify a callback for each received message. """
        self._on(WSClient.MESSAGE, cbk)

    def OnConnection(self, cbk):
        """ Specify a callback for new connections. """
        self._on(WSClient.CONNECTION, cbk)

    def OnUserStateChanged(self, cbk):
        """ Specify a callback for user state changes. """
        # self._on(SubscriptionType.UserStateChanged, cbk)
        raise NotImplementedError

    def RunScript(self, context, script, options=None):
        """Run a Lua script.
        Args:
            context ([Identity]): list of Identity {"p": "/System/Core/Test/Item1"}
            script (str): Script body
            options (options): Options object
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(self._ws_client.run_script(context, script, options))

    async def RunScriptAsync(self, context, script, options=None):
        """Run a Lua script async.
        Args:
            context ([Identity]): list of Identity {"p": "/System/Core/Test/Item1"}
            script (str): Script body
            options (options): Options object
        Returns:
            dict (response)
        """
        return await self._ws_client.run_script(context, script, options)

    def Read(self, items, options=None):
        """Read items values.
        Args:
            items ([Item]]): list of Item {"p": "/System/Core/Test/Item1"}
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(self._ws_client.read(items, options))

    async def ReadAsync(self, items, options=None):
        """Read items values async.
        Args:
            items ([Item]]): list of Item {"p": "/System/Core/Test/Item1"}
        Returns:
            dict (response)
        """
        return await self._ws_client.read(items, options)

    def ReadHistoricalData(self, items, startTime, endTime, numberOfIntervals, options=None):
        """Read historical item values.
        Args:
            items ([HistoricalDataItem]): list of HistoricalDataItem {
                    "p": "/System/Core/Test/Item1"
                    "aggregate": "AGG_TYPE_RAW"
                }
            startTime (str): Start time in UTC format
            endTime (str): Ent time in UTC format
            numberOfIntervals (int): Number of intervals
            options (object): Options object
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(
            self._ws_client.read_historicaldata(items, startTime, endTime, numberOfIntervals, options))

    async def ReadHistoricalDataAsync(self, items, startTime, endTime, numberOfIntervals, options=None):
        """Read historical item values async.
        Args:
            items ([HistoricalDataItem]): list of HistoricalDataItem {
                    "p": "/System/Core/Test/Item1"
                    "aggregate": "AGG_TYPE_RAW"
                }
            startTime (str): Start time in UTC format
            endTime (str): Ent time in UTC format
            numberOfIntervals (int): Number of intervals
            options (object): Options object
        Returns:
            dict (response)
        """
        return await self._ws_client.read_historicaldata(items, startTime, endTime, numberOfIntervals, options)

    def ReadRawHistoricalData(self, queries, options=None):
        """Read raw historical item values.
        Args:
            queries ([RawHistoricalDataQuery]): list of RawHistoricalDataQuery
            options (object): Options object
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(
            self._ws_client.read_rawhistoricaldata(queries, options))

    async def ReadRawHistoricalDataAsync(self, queries, options=None):
        """Read raw historical item values async.
        Args:
            queries ([RawHistoricalDataQuery]): list of RawHistoricalDataQuery
            options (object): Options object
        Returns:
            dict (response)
        """
        return await self._ws_client.read_rawhistoricaldata(queries, options)

    async def SubscribeAsync(self, items, subcriptionType=SubscriptionType.DataChanged, cbk=None):
        """Subscribe to various changes.
        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            subcriptionType (str): subscription type, SubscriptionType.DataChanged
            cbk (function): Callback
        Returns:
            void
        """
        if subcriptionType in SubscriptionType.get_all():
            await self._ws_client.subscribe(items, subcriptionType, cbk)

    async def UnsubscribeAsync(self, items, subcriptionType, cbk=None):
        """Unsubscribe from various changes.
        Args:
            items ([Item]): list of Item {"p": "/System/Core/Test/Item1"}
            subcriptionType (str): subscription type, SubscriptionType.DataChanged
            cbk (function): Callback
        Returns:
            void
        """
        if subcriptionType in SubscriptionType.get_all():
            await self._ws_client.unsubscribe(items, subcriptionType, cbk)

    def Write(self, items, options=None):
        """Write item values.
        Args:
            items ([ItemValue]): list of ItemValue {
                    "p": "/System/Core/Test/Item1",
                    "v": 10.5,
                    "q":  0, // Quality (optional)
                    "t": "2017-06-19T12:41:19.56Z" // timestamp (optional)
                }
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(self._ws_client.write(items, options))

    async def WriteAsync(self, items, options=None):
        """Write item values async.
        Args:
            items ([ItemValue]): list of ItemValue {
                    "p": "/System/Core/Test/Item1",
                    "v": 10.5,
                    "q":  0, // Quality (optional)
                    "t": "2017-06-19T12:41:19.56Z" // timestamp (optional)
                }
        Returns:
            dict (response)
        """
        return await self._ws_client.write(items, options)

    def Mass(self, items, options=None):
        """Mass config objects.
        Args:
            items ([dict]): list of dict (mass entries)
            options (object): Options object {
                "batch_flags": see MassBatchFlags flag group for a value
                "fields": a list of n,p,c or ALL. Default: ['p,n']
            }
        Returns:
            dict (response)
        """
        return self.GetEventLoop().run_until_complete(self._ws_client.mass(items, options))

    async def MassAsync(self, items, options=None):
        """Mass config objects async.
        Args:
            items ([dict]): list of dict (mass entries)
            options (object): Options object {
                "batch_flags": see MassBatchFlags flag group for a value
                "fields": a list of n,p,c or ALL. Default: ['p,n']
            }
        Returns:
            dict (response)
        """
        return await self._ws_client.mass(items, options)

    @property
    def GetConnectionInfo(self):
        """Get the information about the connection.
        Returns:
            object: WSConnectionInfo with sessionid and autheticated flag
        """
        return self._ws_client.connection_info
