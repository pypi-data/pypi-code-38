import asyncio
from enum import Enum


class Gate:
    def __init__(self, n=32, *, loop=None):
        loop = loop if loop else asyncio.get_event_loop()
        self._loop = loop
        self._res = asyncio.Semaphore(n, loop=loop)
        self._state = asyncio.Event(loop=loop)
        self._emtpy_statue = asyncio.Event(loop=loop)
        self._emtpy_statue.set()
        self._counter = 0

    async def acquire(self):
        await self._state.wait()
        self._emtpy_statue.clear()
        self._counter += 1
        await self._res.acquire()
        return True

    async def release(self):
        self._res.release()
        self._counter -= 1
        if self._counter == 0:
            self._emtpy_statue.set()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.release()

    async def open(self):
        self._state.set()

    async def close(self):
        self._state.clear()

    async def close_until_complete(self):
        self._state.clear()
        await self._emtpy_statue.wait()


class ServerStatusEnum(Enum):
    Zero = 0
    Running = 1
    NotAvailable = 2
    Updating = 3


class ServerStatus:
    def __init__(self, gate: Gate = None):
        self._gate = gate or Gate()
        self._state = ServerStatusEnum.Zero
        self.gate = self._gate

    async def error(self):
        self._state = ServerStatusEnum.NotAvailable
        await self.gate.close_until_complete()

    async def ready(self):
        self._state = ServerStatusEnum.Running
        await self.gate.open()

    async def left(self):
        self._state = ServerStatusEnum.Zero
        await self.gate.close_until_complete()

    async def update(self):
        self._state = ServerStatusEnum.Updating
        await self.gate.close_until_complete()


__all__ = ["Gate", "ServerStatusEnum", "ServerStatus", ]
