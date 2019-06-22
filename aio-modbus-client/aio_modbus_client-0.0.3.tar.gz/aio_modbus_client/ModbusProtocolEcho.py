from .ModbusProtocol import ModbusProtocol
from .ModbusException import ModbusException, BadCRCResponse
from .utilites import computeCRC, checkCRC
import struct
import asyncio


class ModbusProtocolEcho(ModbusProtocol):

    async def execute(self, message, serial):
        data = self.transport[message.encode().decode()].encode()
        response = message.response()
        response.decode(data)
        return response



