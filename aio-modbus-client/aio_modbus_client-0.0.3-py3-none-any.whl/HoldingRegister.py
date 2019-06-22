from .BaseRegister import ReadRegistersRequestBase, ReadRegistersResponseBase
import struct


class ReadHoldingRegistersRequest(ReadRegistersRequestBase):
    '''
    This function code is used to read the contents of a contiguous block
    of holding registers in a remote device. The Request PDU specifies the
    starting register address and the number of registers. In the PDU
    Registers are addressed starting at zero. Therefore registers numbered
    1-16 are addressed as 0-15.
    '''
    function_code = 3

    def __init__(self, slave_id, address=None, count=None, **kwargs):
        ''' Initializes a new instance of the request

        :param address: The starting address to read from
        :param count: The number of registers to read from address
        '''
        ReadRegistersRequestBase.__init__(self, slave_id, address, count, **kwargs)
        self.response = ReadHoldingRegistersResponse


class ReadHoldingRegistersResponse(ReadRegistersResponseBase):
    '''
    This function code is used to read the contents of a contiguous block
    of holding registers in a remote device. The Request PDU specifies the
    starting register address and the number of registers. In the PDU
    Registers are addressed starting at zero. Therefore registers numbered
    1-16 are addressed as 0-15.
    '''
    function_code = 3

    def __init__(self, values=None, **kwargs):
        ''' Initializes a new response instance

        :param values: The resulting register values
        '''
        ReadRegistersResponseBase.__init__(self, values, **kwargs)


class WriteSingleRegisterRequest(ReadRegistersRequestBase):
    '''
    This function code is used to write a single holding register in a
    remote device.

    The Request PDU specifies the address of the register to
    be written. Registers are addressed starting at zero. Therefore register
    numbered 1 is addressed as 0.
    '''
    function_code = 6
    _rtu_frame_size = 8

    def __init__(self, slave_id, address=None, value=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start writing add
        :param value: The values to write
        '''
        ReadRegistersRequestBase.__init__(self, slave_id, address, 1,  **kwargs)
        self.value = value
        self.response = WriteSingleRegisterResponse

    def encode(self):
        ''' Encode a write single register packet packet request

        :returns: The encoded packet
        '''
        packet = struct.pack('>H', self.address)
        # if self.skip_encode:
        #     packet += self.value
        # else:
        packet += struct.pack('>H', self.value)
        return packet

    def decode(self, data):
        ''' Decode a write single register packet packet request

        :param data: The request to decode
        '''
        self.address, self.value = struct.unpack('>HH', data)

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Register Address(2 byte) + Register Value (2 bytes)
        :return:
        """
        return 1 + 2 + 2

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        return "WriteRegisterRequest %d" % self.address


class WriteSingleRegisterResponse:
    '''
    The normal response is an echo of the request, returned after the
    register contents have been written.
    '''
    function_code = 6
    _rtu_frame_size = 8

    def __init__(self, address=None, value=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start writing add
        :param value: The values to write
        '''
        # ModbusResponse.__init__(self, **kwargs)
        self.address = address
        self.value = value

    def encode(self):
        ''' Encode a write single register packet packet request

        :returns: The encoded packet
        '''
        return struct.pack('>HH', self.address, self.value)

    def decode(self, data):
        ''' Decode a write single register packet packet request

        :param data: The request to decode
        '''
        self.address, self.value = struct.unpack('>HH', data)

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        params = (self.address, self.value)
        return "WriteRegisterResponse %d => %d" % params


class WriteMultipleRegistersRequest(ReadRegistersRequestBase):
    '''
    This function code is used to write a block of contiguous registers (1
    to approx. 120 registers) in a remote device.

    The requested written values are specified in the request data field.
    Data is packed as two bytes per register.
    '''
    function_code = 16
    _rtu_byte_count_pos = 6
    _pdu_length = 5  # func + adress1 + adress2 + outputQuant1 + outputQuant2

    def __init__(self, slave_id, address=None, values=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start writing to
        :param values: The values to write
        '''
        if values is None:
            values = []
        elif not hasattr(values, '__iter__'):
            values = [values]
        self.values = values
        ReadRegistersRequestBase.__init__(self, slave_id, address, len(self.values), **kwargs)
        self.byte_count = self.count * 2
        self.response = WriteMultipleRegistersResponse

    def encode(self):
        ''' Encode a write single register packet packet request

        :returns: The encoded packet
        '''
        packet = struct.pack('>HHB', self.address, self.count, self.byte_count)
        # if self.skip_encode:
        # return packet + b''.join(self.values)

        for value in self.values:
            packet += struct.pack('>H', value)

        return packet

    # def decode(self, data):
    #     ''' Decode a write single register packet packet request
    #
    #     :param data: The request to decode
    #     '''
    #     self.address, self.count, \
    #     self.byte_count = struct.unpack('>HHB', data[:5])
    #     self.values = []  # reset
    #     for idx in range(5, (self.count * 2) + 5, 2):
    #         self.values.append(struct.unpack('>H', data[idx:idx + 2])[0])
    #
    # def execute(self, context):
    #     ''' Run a write single register request against a datastore
    #
    #     :param context: The datastore to request from
    #     :returns: An initialized response, exception message otherwise
    #     '''
    #     if not (1 <= self.count <= 0x07b):
    #         return self.doException(merror.IllegalValue)
    #     if (self.byte_count != self.count * 2):
    #         return self.doException(merror.IllegalValue)
    #     if not context.validate(self.function_code, self.address, self.count):
    #         return self.doException(merror.IllegalAddress)
    #
    #     context.setValues(self.function_code, self.address, self.values)
    #     return WriteMultipleRegistersResponse(self.address, self.count)
    #
    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Starting Address (2 byte) + Quantity of Reggisters  (2 Bytes)
        :return:
        """
        return 1 + 2 + 2

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        params = (self.address, self.count)
        return "WriteMultipleRegisterRequest %d => %d" % params


class WriteMultipleRegistersResponse:
    '''
    "The normal response returns the function code, starting address, and
    quantity of registers written.
    '''
    function_code = 16
    _rtu_frame_size = 8

    def __init__(self, address=None, count=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start writing to
        :param count: The number of registers to write to
        '''
        self.address = address
        self.count = count

    def encode(self):
        ''' Encode a write single register packet packet request

        :returns: The encoded packet
        '''
        return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        ''' Decode a write single register packet packet request

        :param data: The request to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def __str__(self):
        ''' Returns a string representation of the instance

        :returns: A string representation of the instance
        '''
        params = (self.address, self.count)
        return "WriteMultipleRegisterResponse (%d,%d)" % params
