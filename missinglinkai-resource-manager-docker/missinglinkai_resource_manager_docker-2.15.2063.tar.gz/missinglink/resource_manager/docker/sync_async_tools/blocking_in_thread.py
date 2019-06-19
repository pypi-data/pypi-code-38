import asyncio
import logging
from threading import Thread

from dateutil import parser
from typing import Callable
from functools import partial

_logger = logging.getLogger(__name__)


def _send_result(future: asyncio.Future, result=None, ex=None):
    if future.cancelled():
        logging.debug('%s:\t Failed to send %s %s - future canceled', future, result, ex)
        return

    if not ex:
        future.set_result(result)
    else:
        future.set_exception(ex)


def run_blocking_code_in_thread(func_: Callable, loop: asyncio.AbstractEventLoop = None, logger=None) -> asyncio.Future:
    """
    Runs a blocking code in other thread. GIL still applies
    :param func_: blocking function
    :param loop: [optional] loop
    :param logger: [optional] logger to be used
    :return: returns a future that will return result or exception
    """
    logger = logger or _logger
    loop = loop or asyncio.get_event_loop()
    future = asyncio.Future(loop=loop)

    def wait():
        try:
            logger.debug('%s in thread stared' % func_)

            res = func_()
            logger.debug('%s func completed' % func_)
            loop.call_soon_threadsafe(partial(_send_result, future, res, None))

        except Exception as ex:
            if not isinstance(ex, StopAsyncIteration):
                logger.exception('%s func failed' % func_)
            loop.call_soon_threadsafe(partial(_send_result, future, None, ex))

    thread = Thread(target=wait)
    thread.start()
    logger.debug('%s func stared' % func_)
    return future
