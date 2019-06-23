# -*- coding: utf-8 -*-

# Standard Imports
import asyncio
import json
import weakref

# ThirdParty Imports
import aiohttp


def to_json(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

async def json_or_text(response):
    text = await response.text(encoding='utf-8')
    if response.headers['content-type'] == 'application/json':
        return json.loads(text)
    return text


class Route:
    BASE = 'https://typetalk.com'

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        url = '{}{}'.format(self.BASE, self.path)


class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Typetalk API."""

    def __init__(self, loop=None, token=None, run_async=False, is_bot=False):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.__session = None  # filled in static_login
        self._locks = weakref.WeakValueDictionary()
        self.token = token
        self.is_bot = False

        self.user_agent = 'typetalk-py'

    async def request(self, route, **kwargs):
        bucket = route.bucket
        method = route.method
        url = route.url

        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock(loop=self.loop)
            if bucket is not None:
                self._locks[bucket] = lock

        headers = {
            'User-Agent': self.user_agent,
        }

        if token is not None:
            if self.is_bot:
                headers['X-Typetalk-Token'] = self.token
            else:
                headers['Authorization'] = "Bearer {}".format(self.token)

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = to_json(kwargs.pop('json'))

        kwargs['headers'] = headers

        await lock.acquire()
        async with self.__session.request(method, url, **kwargs) as r:
            data = await json_or_text(r)
            return data
