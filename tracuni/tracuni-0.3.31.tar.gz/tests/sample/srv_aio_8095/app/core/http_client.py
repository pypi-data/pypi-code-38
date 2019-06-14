import json

import aiohttp
import logging
import os
import ssl
import sys
import traceback
from urllib.parse import urlparse

from aiohttp import TCPConnector, ClientSession, client_exceptions

from app.core.component import Component
from app.core.helper import annotate_bytes


class HttpClient(Component):
    async def prepare(self):
        pass

    async def start(self):
        pass

    async def stop(self):
        pass

    async def request(
        self,
        method,
        url,
        body=None,
        time_out=None,
        headers=None,
        cert=None,
        **kwargs
    ):
        if cert:
            pem_file = '%s/cert/%s' % (os.path.realpath(os.path.dirname(sys.argv[0])), cert)
            sslcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            sslcontext.load_cert_chain(pem_file)
        else:
            sslcontext = None

        if not time_out:
            time_out = self.app.config['system']['time_out']

        conn = TCPConnector(ssl_context=sslcontext)
        headers = headers or {}

        async with ClientSession(
                loop=self.loop,
                headers=headers,
                connector=conn
        ) as session:
            try:
                timeout = aiohttp.ClientTimeout(total=time_out)
                resp = await session._request(method, url, data=body, headers=headers, timeout=timeout, **kwargs)
            except BaseException as e:
                logging.error('[x] Error connecting to %s' % url)
                a_resp = None
            else:
                response_body = await resp.read()
                a_resp = await self.adapt_resp(resp)
                resp.release()
            return a_resp

    @staticmethod
    async def adapt_resp(resp):
        html = await resp.read()
        html = html.decode()
        http_code = resp.status
        _resp_hdrs = resp.headers
        resp_hdrs = {}
        for i in _resp_hdrs:
            resp_hdrs[i] = _resp_hdrs[i]

        # return {
        #     'http_code': http_code,
        #     'response_headers': resp_hdrs,
        #     'response': json.loads(html),
        # }
        return json.loads(html)
