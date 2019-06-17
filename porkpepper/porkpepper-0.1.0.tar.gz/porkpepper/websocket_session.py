from typing import *
import time
import json
import random
import string
from aiohttp.web import WebSocketResponse
from .result import Result
from .utils import create_base58_key


class WebsocketSession:
    def __init__(self):
        self.session_id = create_base58_key(''.join(random.choices(string.ascii_letters, k=12)), length=12, prefix="SS")
        self.create_timestamp = int(time.time() * 1000)
        self.current_user = None
        self.socket: WebSocketResponse = None

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
                    return False
        return False

    async def close(self):
        if self.socket is not None:
            try:
                await self.socket.close()
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
