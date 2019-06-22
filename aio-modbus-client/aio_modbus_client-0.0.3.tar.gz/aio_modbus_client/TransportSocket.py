from .Transport import Transport
import asyncio


class TransportSocket(Transport):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 502)
        self._reader = None
        self._writer = None

    async def connect(self):
        try:
            if not self._reader:
                self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
                return True
            return True
        except Exception as e:
            raise Exception(str(e)) from None

    async def write(self, data):
        return self._writer.write(data)

    async def read(self, size):
        return await self._reader.read(size)

    async def close(self):
        if self._writer:
            self._writer.close()
