import asyncio
from .ModbusProtocolRtu import ModbusProtocolRtu


class Transport:
    def __init__(self, **kwargs):
        pass

    async def connect(self):
        pass

    async def send(self, data):
        pass

    async def receive(self, size):
        pass

    async def close(self):
        pass