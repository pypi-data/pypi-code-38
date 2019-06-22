from .BaseRegister import ReadBitsRequestBase, ReadBitsResponseBase
from .utilites import pack_bitstring, unpack_bitstring
import struct


class ReadCoilsRequest(ReadBitsRequestBase):
    '''
    This function code is used to read from 1 to 2000(0x7d0) contiguous status
    of coils in a remote device. The Request PDU specifies the starting
    address, ie the address of the first coil specified, and the number of
    coils. In the PDU Coils are addressed starting at zero. Therefore coils
    numbered 1-16 are addressed as 0-15.
    '''
    function_code = 1

    def __init__(self, slave_id, address=None, count=None, **kwargs):
        ''' Initializes a new instance

        :param address: The address to start reading from
        :param count: The number of bits to read
        '''
        ReadBitsRequestBase.__init__(self, slave_id, address, count, **kwargs)

    def execute(self, context):
        ''' Run a read coils request against a datastore

        Before running the request, we make sure that the request is in
        the max valid range (0x001-0x7d0). Next we make sure that the
        request is valid against the current datastore.

        :param context: The datastore to request from
        :returns: The initializes response message, exception message otherwise
        '''
        if not (1 <= self.count <= 0x7d0):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadCoilsResponse(values)


class ReadCoilsResponse(ReadBitsResponseBase):
    '''
    The coils in the response message are packed as one coil per bit of
    the data field. Status is indicated as 1= ON and 0= OFF. The LSB of the
    first data byte contains the output addressed in the query. The other
    coils follow toward the high order end of this byte, and from low order
    to high order in subsequent bytes.

    If the returned output quantity is not a multiple of eight, the
    remaining bits in the final data byte will be padded with zeros
    (toward the high order end of the byte). The Byte Count field specifies
    the quantity of complete bytes of data.
    '''
    function_code = 1

    def __init__(self, values=None, **kwargs):
        ''' Intializes a new instance

        :param values: The request values to respond with
        '''
        ReadBitsResponseBase.__init__(self, values, **kwargs)


class ReadDiscreteInputsRequest(ReadBitsRequestBase):
    '''
    This function code is used to read from 1 to 2000(0x7d0) contiguous status
    of discrete inputs in a remote device. The Request PDU specifies the
    starting address, ie the address of the first input specified, and the
    number of inputs. In the PDU Discrete Inputs are addressed starting at
    zero. Therefore Discrete inputs numbered 1-16 are addressed as 0-15.
    '''
    function_code = 2

    def __init__(self, address=None, count=None, **kwargs):
        ''' Intializes a new instance

        :param address: The address to start reading from
        :param count: The number of bits to read
        '''
        ReadBitsRequestBase.__init__(self, address, count, **kwargs)

    def execute(self, context):
        ''' Run a read discrete input request against a datastore

        Before running the request, we make sure that the request is in
        the max valid range (0x001-0x7d0). Next we make sure that the
        request is valid against the current datastore.

        :param context: The datastore to request from
        :returns: The initializes response message, exception message otherwise
        '''
        if not (1 <= self.count <= 0x7d0):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadDiscreteInputsResponse(values)


class ReadDiscreteInputsResponse(ReadBitsResponseBase):
    '''
    The discrete inputs in the response message are packed as one input per
    bit of the data field. Status is indicated as 1= ON; 0= OFF. The LSB of
    the first data byte contains the input addressed in the query. The other
    inputs follow toward the high order end of this byte, and from low order
    to high order in subsequent bytes.

    If the returned input quantity is not a multiple of eight, the
    remaining bits in the final data byte will be padded with zeros
    (toward the high order end of the byte). The Byte Count field specifies
    the quantity of complete bytes of data.
    '''
    function_code = 2

    def __init__(self, values=None, **kwargs):
        ''' Intializes a new instance

        :param values: The request values to respond with
        '''
        ReadBitsResponseBase.__init__(self, values, **kwargs)


class WriteMultipleCoilsRequest:
    '''
    "This function code is used to force each coil in a sequence of coils to
    either ON or OFF in a remote device. The Request PDU specifies the coil
    references to be forced. Coils are addressed starting at zero. Therefore
    coil numbered 1 is addressed as 0.
    The requested ON/OFF states are specified by contents of the request
    data field. A logical '1' in a bit position of the field requests the
    corresponding output to be ON. A logical '0' requests it to be OFF."
    '''
    function_code = 15
    _rtu_byte_count_pos = 6

    def __init__(self, slave_id, address=None, values=None, **kwargs):
        ''' Initializes a new instance
        :param address: The starting request address
        :param values: The values to write
        '''
        self.address = address
        if not values:
            values = []
        elif not hasattr(values, '__iter__'):
            values = [values]
        self.values = values
        self.byte_count = (len(self.values) + 7) // 8
        self.slave_id = slave_id
        self.response = WriteMultipleCoilsResponse

    def encode(self):
        ''' Encodes write coils request
        :returns: The byte encoded message
        '''
        count = len(self.values)
        self.byte_count = (count + 7) // 8
        packet = struct.pack('>HHB', self.address, count, self.byte_count)
        packet += pack_bitstring(self.values)
        return packet

    def decode(self, data):
        ''' Decodes a write coils request
        :param data: The packet data to decode
        '''
        self.address, count, self.byte_count = struct.unpack('>HHB', data[0:5])
        values = unpack_bitstring(data[5:])
        self.values = values[:count]

    def execute(self, context):
        ''' Run a write coils request against a datastore
        :param context: The datastore to request from
        :returns: The populated response or exception message
        '''
        count = len(self.values)
        if not (1 <= count <= 0x07b0):
            return self.doException(merror.IllegalValue)
        if (self.byte_count != (count + 7) // 8):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, count):
            return self.doException(merror.IllegalAddress)

        context.setValues(self.function_code, self.address, self.values)
        return WriteMultipleCoilsResponse(self.address, count)

    def __str__(self):
        ''' Returns a string representation of the instance
        :returns: A string representation of the instance
        '''
        params = (self.address, len(self.values))
        return "WriteNCoilRequest (%d) => %d " % params

    def get_response_pdu_size(self):
        """
        Func_code (1 byte) + Output Address (2 byte) + Quantity of Outputs  (2 Bytes)
        :return:
        """
        return 1 + 2 + 2


class WriteMultipleCoilsResponse:
    '''
    The normal response returns the function code, starting address, and
    quantity of coils forced.
    '''
    function_code = 15
    _rtu_frame_size = 8

    def __init__(self, address=None, count=None, **kwargs):
        ''' Initializes a new instance
        :param address: The starting variable address written to
        :param count: The number of values written
        '''
        self.address = address
        self.count = count

    def encode(self):
        ''' Encodes write coils response
        :returns: The byte encoded message
        '''
        return struct.pack('>HH', self.address, self.count)

    def decode(self, data):
        ''' Decodes a write coils response
        :param data: The packet data to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def __str__(self):
        ''' Returns a string representation of the instance
        :returns: A string representation of the instance
        '''
        return "WriteNCoilResponse(%d, %d)" % (self.address, self.count)


# ---------------------------------------------------------------------------#
# Exported symbols
# ---------------------------------------------------------------------------#
__all__ = [
    "ReadCoilsRequest", "ReadCoilsResponse",
    "ReadDiscreteInputsRequest", "ReadDiscreteInputsResponse",
]