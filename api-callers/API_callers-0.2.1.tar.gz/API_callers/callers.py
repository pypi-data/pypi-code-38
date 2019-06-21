# -*- coding: utf-8 -*-

import requests
import asyncio

from abc import ABC


class Caller(ABC):
    def __init__(self, headers, payloads, url):
        self.url = url
        self.headers = headers
        self.payloads = payloads
        self.responses = list()

    @property
    def results(self):
        return self.send()


class SyncCaller(Caller):
    """
    Call a set of API calls asynchronously.
    """
    def _build(self, payload):
        if type(payload) == dict and 'metadata' in payload.keys():
            metadata = payload['metadata']
            payload.pop('metadata')
        else:
            metadata = None
        response = requests.post(self.url, json=payload, headers=self.headers)
        return {'payload': payload, 'response': response, 'metadata': metadata}

    def send(self):
        self.responses = [self._build(x) for x in self.payloads]
        return self.responses

class AsyncCaller(Caller):

    async def _build(self, payload):
        if type(payload) == dict and 'metadata' in payload.keys():
            metadata = payload['metadata']
            payload.pop('metadata')
        else:
            metadata = None

        response = requests.post(self.url, json=payload, headers=self.headers)
        # callback_list.add({'payload': payload, 'response': response, 'metadata': metadata})
        return {'payload': payload, 'response': response, 'metadata': metadata}

    async def _get_coros(self):
        self.responses = [await self._build(x) for x in self.payloads]
        return self.responses

    def send(self):
        coros = asyncio.gather(self._get_coros())
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(coros)
        inner_list = resp[0]
        return inner_list
