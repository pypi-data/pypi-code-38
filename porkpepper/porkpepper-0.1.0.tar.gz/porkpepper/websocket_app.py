from typing import *
import aiohttp
from aiohttp import web
from .websocket_session import WebsocketSession


class WebsocketApp(web.Application):
    def __init__(self, session_class=WebsocketSession, **kwargs):
        super(WebsocketApp, self).__init__(**kwargs)
        self._session_class = session_class
        self._session_dict: Dict[str, WebsocketSession] = dict()

    def all_sessions(self):
        return list(self._session_dict.values())

    def __getitem__(self, item) -> WebsocketSession:
        return self._session_dict.__getitem__(item)

    def __contains__(self, item):
        return self._session_dict.__contains__(item)

    async def handler(self, request):
        if not self._session_class:
            return
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        session = self._session_class()
        session.socket = ws
        self._session_dict[session.session_id] = session
        await session.prepare()
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT or msg.type == aiohttp.WSMsgType.BINARY:
                    message_result = session.message_loads(msg.data)
                    if message_result.is_some:
                        await session.request(message_result.unwrap())
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        finally:
            try:
                await ws.close()
            except Exception as e:
                pass
            try:
                await session.on_finish()
            except Exception as e:
                pass
            if session.session_id in self._session_dict:
                del self._session_dict[session.session_id]
        return ws


__all__ = ["WebsocketApp", ]
