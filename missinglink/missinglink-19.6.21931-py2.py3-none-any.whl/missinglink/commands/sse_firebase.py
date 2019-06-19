# -*- coding: utf-8 -*-
import datetime
import json
import logging
import socket
import threading
import abc
import time
from _bisect import bisect_right

import requests
from colorama import Fore, Style
from sseclient import SSEClient
from requests import HTTPError


class StopListening(Exception):
    pass


class AuthExpired(Exception):
    pass


class LogsCanceled(Exception):
    pass


class KeyWrapper:
    def __init__(self, iterable, key):
        self.it = iterable
        self.key = key

    def __getitem__(self, i):
        return self.key(self.it[i])

    def __len__(self):
        return len(self.it)


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
    _MAX_TOKEN_REFRESH_RETRIES = 3

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, top_records):
        self._sse = None
        self._sleeping_since = None
        self._refresh_token_retry = 0
        self._last_ts = None
        self._top_records = top_records
        self.exception = None
        super(SSEThread, self).__init__(name=name)

    @abc.abstractmethod
    def create_sse_client(self):
        pass

    @abc.abstractmethod
    def on_sse_event(self, data):
        pass

    @classmethod
    def __handle_events_types(cls, msg):
        if msg.event == 'auth_revoked':
            raise AuthExpired()

        if msg.event == 'cancel':
            raise LogsCanceled()

    def __check_if_server_back_online(self):
        if self._sleeping_since is not None:
            logging.info("server back online, total downtime %s", datetime.datetime.utcnow())
            self._sleeping_since = None

        return True

    def __check_if_token_refreshed(self):
        if self._refresh_token_retry > 0:
            logging.info("token refresh OK")
            self._refresh_token_retry = 0

    def __return_logs_from_last_ts(self, values):
        i = bisect_right(KeyWrapper(values, key=lambda t: t["ts"]), self._last_ts)

        if i == len(values):
            return []

        return values[i:]

    def __handle_snapshot(self, data):
        is_snapshot = data['path'] == '/'
        if is_snapshot:
            values = sorted(data['data'].values(), key=lambda d: d['ts'])

            if self._last_ts is not None:
                return self.__return_logs_from_last_ts(values)

            return values[-self._top_records:]

        return [data['data']]

    def _sse_loop(self):
        for msg in self._sse:
            self.__check_if_server_back_online()

            self.__handle_events_types(msg)

            self.__check_if_token_refreshed()

            if msg.event == 'keep-alive':
                continue

            data = json.loads(msg.data)

            data = self.__handle_snapshot(data)

            self.on_sse_event(data)

    def _sleep_and_retry(self):
        if self._sleeping_since is None:
            self._sleeping_since = datetime.datetime.utcnow()

        logging.warning("error during processing, sleep and retry")
        time.sleep(1)

    @classmethod
    def __inner_run_loop_http_error(cls, ex):
        if ex.response.status_code == 401:
            raise AuthExpired()

    def _inner_run_loop(self):
        try:
            self._sse = self.create_sse_client()
            self._sse_loop()
        except HTTPError as ex:
            self.__inner_run_loop_http_error(ex)
            raise
        except EOFError:
            self._sleep_and_retry()
        except (StopListening, AuthExpired):
            raise
        except Exception as ex:
            logging.exception("error during processing crashing")
            self.exception = ex
            raise

    def __handle_run_auth(self):
        self._refresh_token_retry += 1
        logging.info('SSE 401, refresh token and retry (%s)', self._refresh_token_retry)

        if self._refresh_token_retry > self._MAX_TOKEN_REFRESH_RETRIES - 1:
            logging.warning('Too much retries on token refresh (%s)', self._refresh_token_retry)
            raise

    def run(self):
        while True:
            try:
                self._inner_run_loop()
            except StopListening:
                return
            except AuthExpired:
                self.__handle_run_auth()

    def close(self):
        if self._sse is not None:
            self._sse.close()


class LogsThread(SSEThread):
    def __init__(self, logs_endpoint_gen, disable_colors, top_records):
        self._logs_endpoint_gen = logs_endpoint_gen
        self._session = requests.session()  # ok to use default session as the auth is inside the URL
        self._disable_colors = disable_colors
        super(LogsThread, self).__init__('logs', top_records)

    def create_sse_client(self):
        return ClosableSSEClient(self._logs_endpoint_gen(), self._session)

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

    def _on_message(self, ts, category, level, message):
        msg = self.__get_message(category, level)

        color = self.__get_color(level)

        return color + msg.format(ts=ts, category=category, level=level, message=message)

    def on_sse_event(self, data):
        for val in data:
            ts = val['ts']
            self._last_ts = ts if self._last_ts is None else max(self._last_ts, ts)

            msg = self._on_message(val['ts'], val.get('category'), val.get('level'), val['message'])

            print(msg)
