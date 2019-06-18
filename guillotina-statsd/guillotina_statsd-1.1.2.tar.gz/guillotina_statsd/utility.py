from aiostatsd.client import StatsdClient
from guillotina import app_settings
from guillotina.async_util import IAsyncUtility

import asyncio


class IStatsdUtility(IAsyncUtility):
    pass


class StatsdUtility:

    def __init__(self, settings=None, loop=None):
        self._loop = loop

    async def initialize(self, app=None):
        settings = app_settings['statsd']
        app_settings['statsd_client'] = StatsdClient(
            settings['host'],
            settings['port'],
            settings.get('packet_size', 512),
            settings.get('flush_interval', 1.0)
            )
        asyncio.ensure_future(app_settings['statsd_client'].run())

    async def finalize(self, app):
        await app_settings['statsd_client'].stop()
