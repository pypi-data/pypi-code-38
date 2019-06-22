import struct
from .utilites import unpack_bitstring, pack_bitstring
# from six import int2byte, byte2int


# class ReadRegistersRequestBase(ModbusRequest):
class ReadRegistersRequestBase:
    '''
    Base class for reading a modbus register
    '''
    _rtu_frame_size = 8
    function_code = None

    def __init__(self, slave_id, address, count, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start the read from
        :param count: The number of registers to read
        '''
        # ModbusRequest.__init__(self, **kwargs)
        self.slave_id = slave_id
        self.address = address
        self.count = count
        self.response = ReadRegistersResponseBase
        self.timeout = None
        # self.skip_encode = kwargs.get('skip_encode')

    def encode(self):
        ''' Encodes the request packet

        :return: The encoded packet
        '''
        return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        ''' Decode a register request packet

        :param data: The request to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Byte Count(1 byte) + 2 * Quantity of Coils (n Bytes)
        :return:
        """
        return 1 + 1 + 2 * self.count

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        return "ReadRegisterRequest (%d,%d)" % (self.address, self.count)

    def init_response(self, response_data):
        ''' Run a read holding request against a datastore

        :param context: The datastore to request from
        :returns: An initialized response, exception message otherwise
        '''
        # if not (1 <= self.count <= 0x7d):
        #     return self.doException(merror.IllegalValue)
        # if not context.validate(self.function_code, self.address, self.count):
        #     return self.doException(merror.IllegalAddress)
        # values = context.getValues(self.function_code, self.address, self.count)
        # return ReadHoldingRegistersResponse(values)
        result = self.response()
        result.decode(response_data)
        return result

    async def execute(self, device):
        pdu = self.encode()
        response_pdu_size = self.get_response_pdu_size()
        response_data =  await device.protocol.execute(
            self.slave_id,
            self.function_code,
            pdu,
            response_pdu_size,
            device.serial)
        return self.init_response(response_data)


# class ReadRegistersResponseBase(ModbusResponse):
class ReadRegistersResponseBase:
    '''
    Base class for responsing to a modbus register read
    '''

    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        ''' Initializes a new instance

        :param values: The values to write to
        '''
        # ModbusResponse.__init__(self, **kwargs)
        self.registers = values or []

    def encode(self):
        ''' Encodes the response packet

        :returns: The encoded packet
        '''
        result = int2byte(len(self.registers) * 2)
        for register in self.registers:
            result += struct.pack('>H', register)
        return result

    def decode(self, data):
        ''' Decode a register response packet

        :param data: The request to decode
        '''
        byte_count = data[0]
        self.registers = []
        for i in range(1, byte_count + 1, 2):
            self.registers.append(struct.unpack('>H', data[i:i + 2])[0])

    def getRegister(self, index):
        ''' Get the requested register

        :param index: The indexed register to retrieve
        :returns: The request register
        '''
        return self.registers[index]

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        return "ReadRegisterResponse (%d)" % len(self.registers)


class ReadBitsRequestBase:
    ''' Base class for Messages Requesting bit values '''

    _rtu_frame_size = 8

    def __init__(self, slave_id, address, count, **kwargs):
        ''' Initializes the read request data

        :param address: The start address to read from
        :param count: The number of bits after 'address' to read
        '''
        self.slave_id = slave_id
        self.address = address
        self.count = count
        self.timeout = None
        self.response = ReadBitsResponseBase

    def encode(self):
        ''' Encodes a request pdu

        :returns: The encoded pdu
        '''
        return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        ''' Decodes a request pdu

        :param data: The packet data to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Byte Count(1 byte) + Quantity of Coils (n Bytes)/8,
        if the remainder is different of 0 then N = N+1
        :return:
        """
        count = self.count // 8
        if self.count % 8:
            count += 1

        return 1 + 1 + count

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        return "ReadBitRequest(%d,%d)" % (self.address, self.count)

    def init_response(self, response_data):
        ''' Run a read holding request against a datastore

        :param context: The datastore to request from
        :returns: An initialized response, exception message otherwise
        '''
        # if not (1 <= self.count <= 0x7d):
        #     return self.doException(merror.IllegalValue)
        # if not context.validate(self.function_code, self.address, self.count):
        #     return self.doException(merror.IllegalAddress)
        # values = context.getValues(self.function_code, self.address, self.count)
        # return ReadHoldingRegistersResponse(values)
        result = self.response()
        result.decode(response_data)
        return result


class ReadBitsResponseBase:
    ''' Base class for Messages responding to bit-reading values '''

    _rtu_byte_count_pos = 2

    def __init__(self, values=None, **kwargs):
        ''' Initializes a new instance

        :param values: The requested values to be returned
        '''
        self.bits = values or []

    def encode(self):
        ''' Encodes response pdu

        :returns: The encoded packet message
        '''
        result = pack_bitstring(self.bits)
        packet = struct.pack(">B", len(result)) + result
        return packet

    def decode(self, data):
        ''' Decodes response pdu

        :param data: The packet data to decode
        '''
        self.byte_count = data[0]
        self.bits = unpack_bitstring(data[1:])

    def setBit(self, address, value=1):
        ''' Helper function to set the specified bit

        :param address: The bit to set
        :param value: The value to set the bit to
        '''
        self.bits[address] = (value != 0)

    def resetBit(self, address):
        ''' Helper function to set the specified bit to 0

        :param address: The bit to reset
        '''
        self.setBit(address, 0)

    def getBit(self, address):
        ''' Helper function to get the specified bit's value

        :param address: The bit to query
        :returns: The value of the requested bit
        '''
        return self.bits[address]

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        return "ReadBitResponse(%d)" % len(self.bits)
