import asyncio
import logging
import queue
from threading import Thread

logger = logging.getLogger(__name__)


class LogGenerator:
    def __init__(self, cont, name=None):
        self.container = cont
        self.logs = None
        self.sleep = asyncio.sleep
        self.queue = queue.Queue()
        self.id = self.container.name
        self.thread = Thread(target=self._read_line_async)
        self.name = name or self.id

    def __aiter__(self):
        logger.debug('%s: START', self.id)

        self.reading = True
        self.logs = self.container.logs(stream=True)
        self.thread.start()
        return self

    def _read_line_async(self):
        for value in self.logs:
            value = bytes([x for x in value if int(x) >= 32])
            self.queue.put_nowait(value)
        self.reading = False

    def _get_line(self):
        try:
            value = self.queue.get_nowait()
            return value
        except queue.Empty:
            return None

    def _has_more_logs(self):
        return self.reading or not self.queue.empty()

    async def __anext__(self):
        await self.sleep(0)

        while self._has_more_logs():

            value = self._get_line()
            if value is None:
                if self._has_more_logs():
                    await self.sleep(1)
                    continue

            return self.name, value

        logger.debug('%s: DONE', self.id)
        raise StopAsyncIteration
