from .BaseRegister import ReadRegistersRequestBase, ReadRegistersResponseBase


class ReadInputRegistersRequest(ReadRegistersRequestBase):
    '''
    This function code is used to read from 1 to approx. 125 contiguous
    input registers in a remote device. The Request PDU specifies the
    starting register address and the number of registers. In the PDU
    Registers are addressed starting at zero. Therefore input registers
    numbered 1-16 are addressed as 0-15.
    '''
    function_code = 4

    def __init__(self, slave_id, address=None, count=None, **kwargs):
        ''' Initializes a new instance of the request

        :param address: The starting address to read from
        :param count: The number of registers to read from address
        '''
        ReadRegistersRequestBase.__init__(self, slave_id, address, count, **kwargs)
        self.response = ReadInputRegistersResponse

    def execute(self, context):
        ''' Run a read input request against a datastore

        :param context: The datastore to request from
        :returns: An initialized response, exception message otherwise
        '''
        if not (1 <= self.count <= 0x7d):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadInputRegistersResponse(values)


class ReadInputRegistersResponse(ReadRegistersResponseBase):
    '''
    This function code is used to read from 1 to approx. 125 contiguous
    input registers in a remote device. The Request PDU specifies the
    starting register address and the number of registers. In the PDU
    Registers are addressed starting at zero. Therefore input registers
    numbered 1-16 are addressed as 0-15.
    '''
    function_code = 4

    def __init__(self, values=None, **kwargs):
        ''' Initializes a new response instance

        :param values: The resulting register values
        '''
        ReadRegistersResponseBase.__init__(self, values, **kwargs)
