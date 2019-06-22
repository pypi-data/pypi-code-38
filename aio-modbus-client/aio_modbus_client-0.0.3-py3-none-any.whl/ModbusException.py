class ModbusException(Exception):
    def __init__(self, code):
        codes = {
            '1': 'Illegal Function',
            '2': 'Illegal Data Address',
            '3': 'Illegal Data Value',
            '4': 'Slave Device Failure',
            '5': 'Acknowledge',
            '6': 'Slave Device Busy',
            '7': 'Negative Acknowledge',
            '8': 'Memory Parity Error',
            '10': 'Gateway Path Unavailable',
            '11': 'Gateway Target Device Failed to Respond',
        }
        super().__init__(codes.get(str(code), 'Unknown error code {}'.format(code)))


class BadCRCResponse(Exception):
    pass


class BadCRCRequest(Exception):
    pass
