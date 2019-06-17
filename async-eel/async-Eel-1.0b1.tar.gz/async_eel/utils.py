from aiohttp.web import BaseRequest
from aiohttp import web
from logging import getLogger
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


__all__ = [
    "websocket_protocol_check",
]
