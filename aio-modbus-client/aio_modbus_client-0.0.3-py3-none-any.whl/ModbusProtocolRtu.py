from .ModbusProtocol import ModbusProtocol
from .ModbusException import ModbusException, BadCRCResponse
from .utilites import computeCRC, checkCRC
import time
import struct
import asyncio


class ModbusProtocolRtu(ModbusProtocol):
    def encode(self, message):
        """
        Creates a ready to send modbus packet

        :param message: The populated request/response to send
        """
        data = message.encode()
        packet = struct.pack('>BB',
                             message.slave_id,
                             message.function_code) + data
        packet += struct.pack(">H", computeCRC(packet))
        return packet

    def decode(self, data):
        crc = computeCRC(data[:-2])
        current_crc = struct.unpack(">H", data[-2:])[0]
        if crc == current_crc:
            return data[2: -2]
        # if not checkCRC(data[:-2], struct.unpack(">H", data[-2:])[0]):
        raise BadCRCResponse('Bad CRC data:{data} crc:{crc} current_crc:{current_crc}'.format(
            data=data, crc=crc, current_crc=current_crc))

    async def execute(self, message, serial):
        if not await self.transport.connect():
            raise Exception('modbus transport not connected')
        request_data = self.encode(message)
        if self.last_request:
            if time.time() - self.last_request < 0.003:
                print('pause')
                await asyncio.sleep(0.003)
            self.last_request = time.time()
        await self.transport.write(request_data)
        data = await asyncio.wait_for(self.read_response(message.get_response_pdu_size()), self.timeout)
        response = message.response()
        try:
            response.decode(self.decode(data))
        except asyncio.TimeoutError:
            await asyncio.wait_for(self.read_response(254), self.timeout)
        except BadCRCResponse:
            await self.repair()
        return response

    async def repair(self):
        try:
            await asyncio.wait_for(self.read_response(254), self.timeout)
        except asyncio.TimeoutError:
            pass

    async def read_response(self, pdu_size):
        data = await self.transport.read(2)
        if data[1] >= 0x80:  # exception func_code
            data += await self.transport.read(3)  # error_code + CRC
            raise ModbusException(data[2])
        data += await self.transport.read(pdu_size + 2)
        return data
