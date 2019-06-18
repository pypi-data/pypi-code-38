from aiohttp.web import BaseRequest
from aiohttp import web
from logging import getLogger
from threading import Thread
import asyncio


log = getLogger(__name__)


async def websocket_protocol_check(request: BaseRequest):
    """protocol upgrade to WebSocket"""
    ws = web.WebSocketResponse()
    ws.enable_compression()
    available = ws.can_prepare(request)
    if not available:
        raise TypeError('cannot prepare websocket')
    await ws.prepare(request)
    log.debug(f"protocol upgrade to websocket protocol {request.remote}")
    return ws


async def run_in_another_thread(fnc, *args, **kwargs):
    """run blocking fnc in another thread"""
    future = asyncio.Future()

    def waiter():
        try:
            future.set_result(fnc(*args, **kwargs))
        except Exception as e:
            future.set_exception(e)

    Thread(target=waiter).start()
    await future
    return future.result()


__all__ = [
    "websocket_protocol_check",
    "run_in_another_thread",
]
