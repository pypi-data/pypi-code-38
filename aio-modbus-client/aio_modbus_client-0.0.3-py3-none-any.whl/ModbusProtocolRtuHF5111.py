from .ModbusProtocolRtu import ModbusProtocolRtu
from .ModbusException import ModbusException
import logging
_logger = logging.getLogger(__name__)


class ModbusProtocolRtuHF5111(ModbusProtocolRtu):

    async def read_response(self, pdu_size):
        data = await self.read_ff(2)
        if data[1] >= 0x80:  # exception func_code
            data += await self.transport.read(3)  # error_code + CRC
            raise ModbusException(data[2])
        data += await self.transport.read(pdu_size + 2)
        return data

    async def read_ff(self, size):
        data = b''
        receive_size = size
        while receive_size > 0:
            data += await self.transport.read(receive_size)
            while data and data[0] == 0xff:
                data = data[1:]
            receive_size = size - len(data)
        return data
