from typing import *
import asyncio
from aiohttp import web
from .websocket_app import WebsocketApp
from .redis_server_base import RedisServerBase


class PorkPepperNode:
    def __init__(self, redis_server, session_class=None, websocket_path="/porkpepper", **kwargs):
        if redis_server is None:
            raise ValueError
        self._session_class = session_class

        self._app_options = kwargs or dict()
        self._http_app: WebsocketApp = WebsocketApp(session_class=session_class, **self._app_options)
        self._http_app.add_routes([web.route('GET', path, self._http_app.handler) for path in [websocket_path, ]])

        self._redis_server_class = redis_server
        self._redis_server = self._redis_server_class(app=self._http_app)

        self._redis_server_task = None
        self._redis_server_object = None
        self._runner = None

        self.start_event = asyncio.Event()
        self.stop_event = asyncio.Event()

    async def on_start(self):
        pass

    async def on_shutdown(self):
        pass

    async def start(self, enable_websocket=False, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        app = self._http_app
        redis_server: RedisServerBase = self._redis_server
        redis_server.init_property()
        runner = web.AppRunner(app)
        self._runner = runner
        await runner.setup()
        if enable_websocket:
            site = web.TCPSite(runner, **kwargs)
            await site.start()
        await self.on_start()
        redis_server_object = await redis_server.serve(redis_host, redis_port, False)
        self._redis_server_object = redis_server_object
        return self

    async def stop(self):
        if self._redis_server_object:
            self._redis_server_object.close()
            await self._redis_server_object.wait_closed()
            self._redis_server_object = None
        if self._redis_server_task:
            self._redis_server_task.cancel()
            self._redis_server_task = None
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
        await self.on_shutdown()

    async def serve(self, enable_websocket=False, redis_host="127.0.0.1", redis_port=6379, **kwargs):
        self.start_event.clear()
        self.stop_event.clear()
        app = self._http_app
        redis_server: RedisServerBase = self._redis_server
        redis_server.init_property()
        runner = web.AppRunner(app)
        await runner.setup()
        try:
            if enable_websocket:
                site = web.TCPSite(runner, **kwargs)
                await site.start()
            await self.on_start()
            await redis_server.serve(redis_host, redis_port, True, self.start_event.set)
        finally:
            await runner.cleanup()
            await self.on_shutdown()
            self.stop_event.set()
