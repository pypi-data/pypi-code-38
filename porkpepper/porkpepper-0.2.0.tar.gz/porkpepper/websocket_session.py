from typing import *
import time
import json
import random
import string
from aiohttp import WSCloseCode
from aiohttp.web import WebSocketResponse
from .result import Result
from .utils import create_base58_key
from .fifo_lock import FifoLock


class WebsocketSession:
    def __init__(self):
        self.session_id = create_base58_key(''.join(random.choices(string.ascii_letters, k=12)), length=22, prefix="SS")
        self.create_timestamp = int(time.time() * 1000)
        self._current_user = None
        self.socket: WebSocketResponse = None
        self.lock = FifoLock()
        self.app = None

    def read_timeout(self):
        return None

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, v: Optional[str]):
        current_user = self._current_user
        self._current_user = v
        app = self.app
        if app is not None:
            if current_user is not None:
                app.remove_user(current_user, self)
            if v is not None:
                app.add_user(v, self)

    async def prepare(self):
        pass

    async def on_finish(self):
        pass

    async def request(self, message):
        pass

    async def send(self, message):
        if self.socket is not None:
            message_result = self.message_dumps(message)
            if message_result.is_some:
                try:
                    data = message_result.unwrap()
                    if isinstance(data, str):
                        await self.socket.send_str(data)
                    else:
                        await self.socket.send_bytes(data)
                    return True
                except Exception as e:
                    await self.close()
                    app = self.app
                    if app is not None:
                        app.cleanup_session(self)
                    return False
        return False

    async def close(self, message: bytes = b'Server shutdown'):
        if self.socket is not None:
            try:
                await self.socket.close(code=WSCloseCode.GOING_AWAY, message=message)
            except Exception as e:
                pass

    @classmethod
    def message_loads(cls, data) -> Result[Any]:
        try:
            return Result(json.loads(data))
        except Exception as e:
            return Result(e)

    @classmethod
    def message_dumps(cls, o) -> Result[Union[str, bytes]]:
        try:
            return Result(json.dumps(o))
        except Exception as e:
            return Result(e)


__all__ = ["WebsocketSession", ]
