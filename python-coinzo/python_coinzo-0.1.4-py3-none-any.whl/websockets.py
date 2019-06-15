import json
import threading

from autobahn.twisted.websocket import (
    WebSocketClientFactory,
    WebSocketClientProtocol,
    connectWS,
)
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning

# from coinzo.api import coinzo


class CoinzoClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        super(WebSocketClientProtocol, self).__init__()

    def onConnect(self, response):
        # reset the delay after reconnecting
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                payload_obj = json.loads(payload.decode("utf8"))
            except ValueError:
                pass
            else:
                self.factory.callback(payload_obj)


class CoinzoReconnectingClientFactory(ReconnectingClientFactory):

    # set initial delay to a short time
    initialDelay = 0.1

    maxDelay = 10

    maxRetries = 5


class CoinzoClientFactory(WebSocketClientFactory, CoinzoReconnectingClientFactory):

    protocol = CoinzoClientProtocol
    _reconnect_error_payload = {"e": "error", "m": "Max reconnect retries reached"}

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)

    def clientConnectionLost(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)


class CoinzoSocketManager(threading.Thread):

    STREAM_URL = "wss://www.coinzo.com/"

    # DEFAULT_USER_TIMEOUT = 30 * 60  # 30 minutes

    # def __init__(self, client, user_timeout=DEFAULT_USER_TIMEOUT):
    def __init__(self):
        """Initialise the CoinzoSocketManager

        :param client: Coinzo API client
        :type client: coinzo.Client
        :param user_timeout: Custom websocket timeout
        :type user_timeout: int

        """
        threading.Thread.__init__(self)
        self._conns = {}
        # self._user_timer = None
        # self._user_listen_key = None
        # self._user_callback = None
        # self._client = client
        # self._user_timeout = user_timeout

    def _start_socket(self, path, callback, prefix="ws/"):
        if path in self._conns:
            return False

        factory_url = self.STREAM_URL + prefix + path
        factory = CoinzoClientFactory(factory_url)
        factory.protocol = CoinzoClientProtocol
        factory.callback = callback
        factory.reconnect = True
        context_factory = ssl.ClientContextFactory()

        self._conns[path] = connectWS(factory, context_factory)
        return path

    def start_test_socket(self, socket_name, callback):
        return self._start_socket(socket_name, callback)

    def start_symbol_ticker_socket(self, symbol, callback):
        """Start a websocket for a symbol's ticker data

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        """
        return self._start_socket(symbol.lower() + "@ticker", callback)

    def start_ticker_socket(self, callback):
        """Start a websocket for all ticker data

        By default all markets are included in an array.

        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        """
        return self._start_socket("!ticker@arr", callback)

    def stop_socket(self, conn_key):
        """Stop a websocket given the connection key

        :param conn_key: Socket connection key
        :type conn_key: string

        :returns: connection key string if successful, False otherwise
        """
        if conn_key not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_key].factory = WebSocketClientFactory(
            self.STREAM_URL + "tmp_path"
        )
        self._conns[conn_key].disconnect()
        del self._conns[conn_key]

        # check if we have a user stream socket

    #     if len(conn_key) >= 60 and conn_key[:60] == self._user_listen_key:
    #         self._stop_user_socket()

    # def _stop_user_socket(self):
    #     if not self._user_listen_key:
    #         return
    #     # stop the timer
    #     self._user_timer.cancel()
    #     self._user_timer = None
    #     self._user_listen_key = None

    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def close(self):
        """Close all connections

        """
        keys = set(self._conns.keys())
        for key in keys:
            self.stop_socket(key)

        self._conns = {}
