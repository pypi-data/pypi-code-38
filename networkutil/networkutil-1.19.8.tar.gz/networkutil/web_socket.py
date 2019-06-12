# -*- coding: utf-8 -*-

import json
import socket
import collections
import logging_helper
from classutils.observer import Observable
from classutils.thread_pool import ThreadPoolMixIn
from websocket import WebSocketApp, WebSocketTimeoutException, WebSocketConnectionClosedException


logging = logging_helper.setup_logging()


class WebsocketError(Exception):
    pass


class WebSocketSubscriber(Observable,
                          ThreadPoolMixIn):

    # States
    WS_OPEN = 'open'
    WS_CLOSED = 'closed'
    WS_ERROR = 'error'

    # Notifies: ws_request, ws_name, ws_state, ws_message, ws_error_message
    WS_REQUEST = u'ws_request'
    WS_NAME = u'ws_name'
    WS_STATE = u'ws_state'
    WS_MESSAGE = u'ws_message'
    WS_ERROR_MESSAGE = u'ws_error_message'

    def __init__(self,
                 request,
                 name=None):

        super(WebSocketSubscriber, self).__init__(worker_threads=2)

        self.request = request
        self.name = name

        self._ws = None
        self._last_message = None

        self.open_pool()
        self.open()

    def open(self):

        try:
            self._ws = WebSocketApp(self.request,
                                    on_open=self._on_open,
                                    on_message=self._on_message,
                                    on_error=self._on_error,
                                    on_close=self._on_close)

        except (socket.timeout, WebSocketTimeoutException, Exception) as err:
            raise WebsocketError(err)

        else:
            self._pool.submit_task(self._ws.run_forever)

    def close(self):

        if self._ws is not None:
            try:
                logging.info(u'Closing WS: {name} ({req})'.format(name=self.name,
                                                                  req=self.request))
                self._ws.close()

            except AttributeError:
                pass

            self._ws = None

    def send(self,
             *args,
             **kwargs):

        if self._ws is not None:
            try:
                return self._ws.send(*args,
                                     **kwargs)

            except (AttributeError, WebSocketConnectionClosedException):
                pass

        raise WebsocketError(u'WebSocket not open yet!')

    def __del__(self):
        self.close()

    @property
    def last_message(self):
        return self._last_message

    # Callbacks
    def _on_message(self,
                    ws,
                    message):
        logging.debug(u'WS MESSAGE: {msg}'.format(msg=message))

        try:
            message = json.loads(message,
                                 object_pairs_hook=collections.OrderedDict)

        except ValueError:
            pass

        self._last_message = message
        self.notify_observers(ws_request=self.request,
                              ws_name=self.name,
                              ws_message=message)

    def _on_error(self,
                  ws,
                  error):
        logging.debug(u'WS ERROR: {err}'.format(err=error))
        self.notify_observers(ws_request=self.request,
                              ws_name=self.name,
                              ws_state=self.WS_ERROR,
                              ws_error_message=error)

    def _on_close(self,
                  ws):
        logging.debug(u'WS CLOSED')
        self.notify_observers(ws_request=self.request,
                              ws_name=self.name,
                              ws_state=self.WS_CLOSED)

    def _on_open(self,
                 ws):
        logging.debug(u'WS OPEN')
        self.notify_observers(ws_request=self.request,
                              ws_name=self.name,
                              ws_state=self.WS_OPEN)


if __name__ == u'__main__':

    host = "wss://demos.kaazing.com/echo"

    ws_sub = WebSocketSubscriber(request=host)

    # Loop forever
    from timingsutil import Timeout, MINUTE
    from time import sleep

    timer = Timeout(MINUTE)

    while not timer.expired:
        sleep(10)
        ws_sub.send(u'test message')

    ws_sub.close()
