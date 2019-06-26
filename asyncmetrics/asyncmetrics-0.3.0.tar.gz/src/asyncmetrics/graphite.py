from asyncio import CancelledError, Queue, sleep
from logging import getLogger
from time import time
from typing import Optional

from aiographite.aiographite import AIOGraphite, AioGraphiteSendException, connect

__all__ = [
    'Graphite',
]

logger = getLogger(__package__)


class Graphite:
    DEFAULT_LIMIT = 1000000

    @classmethod
    async def connect(cls, *args, **kwargs) -> 'Graphite':
        limit = kwargs.pop('limit', None)
        return cls(await connect(*args, **kwargs), limit=limit)

    def __init__(self, conn: AIOGraphite, *, limit: Optional[int] = None):
        self._conn = conn
        self._queue = Queue()
        self._sender_task = conn.loop.create_task(self._sender())
        self._running = True
        self._limit = limit or self.DEFAULT_LIMIT

    async def _sender(self):
        queue = self._queue
        send_failed = False

        while self._running:
            try:
                if send_failed:
                    logger.debug("Sleeping for 60 seconds.")
                    await sleep(60)

                metrics = [await queue.get()]
            except CancelledError:
                self._running = False
                metrics = []

            while not queue.empty():
                metrics.append(queue.get_nowait())

            metrics_len = len(metrics)
            off_limit = metrics_len - self._limit

            if off_limit > 0:
                logger.warning("Dropping %s metrics over the limit.", off_limit)
                metrics = metrics[-self._limit:]

            try:
                await self._conn.send_multiple(metrics)
            except AioGraphiteSendException as exc:
                logger.error("%s", exc)

                for metric in metrics:
                    queue.put_nowait(metric)

                send_failed = True
            else:
                if metrics_len:
                    logger.debug("Sent %s metrics.", metrics_len)

                send_failed = False

    async def close(self):
        self._sender_task.cancel()

        try:
            await self._sender_task
        except CancelledError:
            pass
        except Exception as exc:
            logger.error("Error at %s sender task: %s", self.__class__.__name__, exc, exc_info=exc)

        await self._conn.close()

    def send(self, metric: str, value: int, timestamp: Optional[int] = None):
        try:
            self._queue.put_nowait((str(metric), int(value), int(timestamp or time())))
        except ValueError as exc:
            logger.error("Invalid metric %r: %s", (metric, value, timestamp), exc)
