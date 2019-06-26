# -*- coding: utf-8 -*-
import aiohttp
import ujson

from asyncio.futures import TimeoutError
from aiohttp.client_exceptions import ContentTypeError, InvalidURL, ServerDisconnectedError, ClientConnectorError

from .bitcoinerrors import *


class GramBitcoin:
    """
    This class is needed to create a session and then transfer the class
    instance with already active session to other classes , in order to
    avoid creating multiple sessions. RPC-API https://bitcoincore.org/en/doc/0.17.0/

    :param str url (optional):                      Node URI in format http://alice:bob@127.0.0.1:18332
    :param int read_timeout (20):                   Request operations timeout
    :param object session_required (optional):      Will create session or not

    Important note:
    if you create an instance of this class, then you need to pass the
    session_required parameter with the value True. It is not necessary to pass
    the url parameter, if you do not pass it, then do not forget to pass the url
    to other classes to which you intend to pass an object of this class.
    """

    def __init__(self, url=None, read_timeout=20, session_required=False):
        self.url = url
        self._session_required = session_required
        self.session = None
        self.read_timeout = read_timeout

        self._check_session_required()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

    def _check_session_required(self):
        if self._session_required:
            self.session = aiohttp.ClientSession(read_timeout=self.read_timeout, json_serialize=ujson.dumps)

    def check_gram(self, gram):
        if not gram:
            return aiohttp.ClientSession(read_timeout=self.read_timeout, json_serialize=ujson.dumps)
        else:
            return gram.session

    @staticmethod
    def check_url(url, gram):
        if not url:
            return gram.url

        return url

    async def call_method(self, method, *args):
        headers = {'Content-Type': 'application/json'}
        data = {'jsonrpc': '1.0', 'method': f'{method}', 'params': args}

        try:
            response = await self.session.post(url=self.url, headers=headers, data=ujson.dumps(data))
        except (ServerDisconnectedError, TimeoutError):
            await self.close_session()
            raise NoConnectionToTheDaemon(f'No connection to the daemon {self.url}.')
        except ClientConnectorError:
            raise NoConnectionToTheDaemon(f'Cannot connect to host {self.url}.')
        except InvalidURL:
            raise InvalidURL(url=self.url)
        else:
            try:
                return await response.json()
            except ContentTypeError:
                raise IncorrectCreds(uri=self.url)

    async def close_session(self):
        await self.session.close()
