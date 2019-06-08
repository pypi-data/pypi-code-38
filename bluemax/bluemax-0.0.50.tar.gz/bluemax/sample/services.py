import asyncio
import logging
import time
from bluemax import context

LOGGER = logging.getLogger(__name__)


async def clock():
    while True:
        message = {"now": time.time()}
        LOGGER.debug(message)
        context.broadcast("time", message)
        await asyncio.sleep(5)
