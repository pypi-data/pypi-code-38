class ModbusProtocol:
    def __init__(self, transport, **kwargs):
        self.transport = transport
        self.last_request = None
        self.timeout = kwargs.get('timeout', 4)

    def encode(self, msg):
        raise NotImplemented()

    def decode(self, data):
        raise NotImplemented()

    async def execute(self, message, serial):
        raise NotImplemented()

    async def close(self):
        await self.transport.close()
