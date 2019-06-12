import asyncio
import logging

from typing import Any, Callable, Optional

LOGGER: logging.Logger


def set_logger(name: str):  # pragma: nocover
    global LOGGER
    try:
        LOGGER
        raise RuntimeError('App logger has already been set')
    except NameError:
        LOGGER = logging.getLogger(name)


def get_logger() -> logging.Logger:  # pragma: nocover
    return LOGGER


def reverse_hex(h: str):
    '''Reverses a hex-serialized bytestring'''
    return bytes.fromhex(h)[::-1].hex()


async def queue_logger(
        q: asyncio.Queue,
        transform: Optional[Callable[[Any], Any]] = None) -> None:  # pragma: nocover  # noqa: E501
    '''
    Logs a queue as entries come in
    Useful for debugging

    Args:
        q (asyncio.Queue): the queue to log
    '''
    LOGGER.info('registering queue logger')

    def do_nothing(k: Any) -> Any:
        return k
    t = transform if transform is not None else do_nothing
    while True:
        LOGGER.info(t(await q.get()))


async def queue_forwarder(
        inq: asyncio.Queue,
        outq: asyncio.Queue,
        transform: Optional[Callable[[Any], Any]] = None) -> None:  # pragma: nocover  # noqa: E501
    '''
    Forwards everything from a queue to another queue
    Useful for combining queues

    Args:
        inq  (asyncio.Queue): input queue
        outq (asyncio.Queue): output queue
        transform (function): A function to transform the q items with

    '''
    def do_nothing(k: Any) -> Any:
        return k
    t = transform if transform is not None else do_nothing
    while True:
        msg = await inq.get()
        await outq.put(t(msg))
