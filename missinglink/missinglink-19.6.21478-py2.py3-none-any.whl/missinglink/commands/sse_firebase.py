# -*- coding: utf-8 -*-
import datetime
import json
import logging
import socket
import threading
import abc
import time
import requests
from colorama import Fore, Style
from sseclient import SSEClient
from requests import HTTPError


class ClosableSSEClient(SSEClient):
    """
    Hack in some closing functionality on top of the SSEClient
    """

    def __init__(self, url, session, *args, **kwargs):
        self.should_connect = True
        super(ClosableSSEClient, self).__init__(url, session=session, *args, **kwargs)

    def _connect(self):
        if self.should_connect:
            super(ClosableSSEClient, self)._connect()
        else:
            raise StopIteration()

    # noinspection PyProtectedMember
    def close(self):
        self.should_connect = False
        self.retry = 0
        # dig through the sseclient library to the requests library down to the underlying socket.
        # then close that to raise an exception to get out of streaming. I should probably file an issue w/ the
        # requests library to make this easier
        self.resp.raw._fp.fp._sock.shutdown(socket.SHUT_RDWR)
        self.resp.raw._fp.fp._sock.close()


class SSEThread(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        self._sse = None
        self._sleeping_since = None
        super(SSEThread, self).__init__(name=name)

    @abc.abstractmethod
    def create_sse_client(self):
        pass

    @abc.abstractmethod
    def on_sse_event(self, path, data):
        pass

    def _handle_data(self, data):
        if data is None:
            return

        msg_data = json.loads(data)

        if msg_data is None:
            return

        self.on_sse_event(**msg_data)

    def _sse_loop(self):
        for msg in self._sse:
            if self._sleeping_since is not None:
                logging.info("server back online, total downtime %s", datetime.datetime.utcnow())
                self._sleeping_since = None

            self._handle_data(msg.data)

    def _inner_run_loop(self):
        try:
            self._sse = self.create_sse_client()
            self._sse_loop()
        except (EOFError, HTTPError):
            if self._sleeping_since is not None:
                self._sleeping_since = datetime.datetime.utcnow()

            logging.exception("error during processing, sleep and retry")
            time.sleep(1)
        except Exception:
            logging.exception("error during processing crashing")
            raise

    def run(self):
        while True:
            self._inner_run_loop()

    def close(self):
        if self._sse is not None:
            self._sse.close()


class LogsThread(SSEThread):
    def __init__(self, config, logs_endpoint, disable_colors):
        self._url = logs_endpoint
        self._session = requests.session()
        self._disable_colors = disable_colors
        self._config = config
        super(LogsThread, self).__init__(name='logs')

    def create_sse_client(self):
        return ClosableSSEClient(self._url, self._session)

    def __get_color(self, level):
        if self._disable_colors:
            return ''

        color = Style.RESET_ALL + Fore.WHITE

        levels = {
            'ERROR': Style.RESET_ALL + Fore.RED,
            'INFO': Style.RESET_ALL + Style.DIM,
            'WARNING': Style.RESET_ALL + Fore.YELLOW
        }

        return levels.get(level, color)

    @classmethod
    def __get_message(cls, category, level):
        if category is not None and level is not None:
            msg = '{ts} [{category} {level}] {message}'
        else:
            msg = '{ts} {message}'

        return msg

    def on_sse_event(self, path, data):
        if data is None:
            return

        if path == '/':  # snapshot
            values = sorted(data.values(), key=lambda d: d['ts'])
        else:
            values = [data]

        for val in values:
            msg = self.__get_message(val.get('category'), val.get('level'))

            color = self.__get_color(val.get('level'))
            print(color + msg.format(**val))
