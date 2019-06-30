from typing import *
import asyncio
from collections import defaultdict
import aiohttp
from aiohttp import web
from .websocket_session import WebsocketSession


class WebsocketApp(web.Application):
    def __init__(self, session_class=WebsocketSession, **kwargs):
        super(WebsocketApp, self).__init__(**kwargs)
        self._session_class = session_class
        self._session_dict: Dict[str, WebsocketSession] = dict()
        self._user_dict: Dict[str, Set[WebsocketSession]] = defaultdict(set)

    def all_sessions(self):
        return list(self._session_dict.values())

    def all_users(self):
        return list(self._user_dict.keys())

    @property
    def sessions_count(self) -> int:
        return len(self._session_dict)

    @property
    def users_count(self) -> int:
        return len(self._user_dict)

    def get_session(self, session_id: str):
        return self._session_dict.get(session_id, None)

    def get_user(self, user: str) -> Set[WebsocketSession]:
        return self._user_dict.get(user, set())

    def remove_user(self, user, session):
        if user is not None and user in self._user_dict and session in self._user_dict[user]:
            self._user_dict[user].remove(session)
            if not len(self._user_dict[user]):
                self._user_dict.pop(user)

    def add_user(self, user, session):
        if user is not None:
            self._user_dict[user].add(session)

    def remove_session(self, session_id):
        if session_id in self._session_dict:
            self._session_dict.pop(session_id)
            return True
        return False

    def add_session(self, session_id, session):
        self._session_dict[session_id] = session

    def setup_session(self, session, ws):
        session.socket = ws
        session.app = self
        self.add_session(session.session_id, session)

    def cleanup_session(self, session):
        if session.current_user:
            self.remove_user(session.current_user, session)
        self.remove_session(session.session_id)
        session.app = None
        session.socket = None

    async def handler(self, request):
        if not self._session_class:
            return
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        session = self._session_class()
        self.setup_session(session, ws)
        try:
            await session.prepare()
            while True:
                read_timeout = session.read_timeout()
                msg = await ws.receive(read_timeout)
                if msg.type in (aiohttp.WSMsgType.TEXT, msg.type == aiohttp.WSMsgType.BINARY, ):
                    message_result = session.message_loads(msg.data)
                    if message_result.is_some:
                        await session.request(message_result.unwrap())
                elif msg.type == aiohttp.WSMsgType.PING:
                    await ws.pong()
                elif msg.type in (
                        aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSING,
                        aiohttp.WSMsgType.CLOSED,
                        aiohttp.WSMsgType.ERROR,):
                    break
        except Exception as e:
            pass
        finally:
            try:
                await session.on_finish()
            except Exception as e:
                pass
            try:
                await ws.close()
            except Exception as e:
                pass
        self.cleanup_session(session)
        return ws


__all__ = ["WebsocketApp", ]
