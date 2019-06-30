import asyncio
from queue import Queue


class FifoLock:
    def __init__(self, maxsize: int = 0):
        self._lock_queue = Queue(maxsize=maxsize)

    async def acquire(self):
        lock = asyncio.Lock()
        if not self._lock_queue.empty():
            await lock.acquire()
        self._lock_queue.put(lock)
        await lock.acquire()

    async def release(self):
        if self._lock_queue.empty():
            return
        self._lock_queue.get()
        if self._lock_queue.empty():
            return
        lock = self._lock_queue.queue[0]
        if lock.locked():
            lock.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.release()


__all__ = ["FifoLock", ]
