
MB_MAX_READ_WORDS_NB = 127

EXC_ILLEGAL_FN_CODE = 0x01
EXC_ILLEGAL_DATA_ADDRESS = 0x02
EXC_ILLEGAL_DATA_VALUE = 0x03
EXC_SERVER_FAILURE = 0x04
EXC_ACKNOWLEDGE = 0x05
EXC_SERVER_BUSY = 0x06
EXC_CANT_PROCESS_FN = 0x07
EXC_MEM_PARITY = 0x08
EXC_GATEWAY_PROBLEM_1 = 0x0A
EXC_GATEWAY_PROBLEM_2 = 0x0B

def mb_lo_byte(w: int):
    return w & 0xff

def mb_hi_byte(w: int):
    return (w >> 8) & 0xff

EXC_NAMES = {
    EXC_ILLEGAL_FN_CODE:        'EXC_ILLEGAL_FN_CODE',
    EXC_ILLEGAL_DATA_ADDRESS:   'EXC_ILLEGAL_DATA_ADDRESS',
    EXC_ILLEGAL_DATA_VALUE:     'EXC_ILLEGAL_DATA_VALUE',
    EXC_SERVER_FAILURE:         'EXC_SERVER_FAILURE',
    EXC_ACKNOWLEDGE:            'EXC_ACKNOWLEDGE',
    EXC_SERVER_BUSY:            'EXC_SERVER_BUSY',
    EXC_CANT_PROCESS_FN:        'EXC_CANT_PROCESS_FN',
    EXC_MEM_PARITY:             'EXC_MEM_PARITY',
    EXC_GATEWAY_PROBLEM_1:      'EXC_GATEWAY_PROBLEM_1',
    EXC_GATEWAY_PROBLEM_2:      'EXC_GATEWAY_PROBLEM_2',
}

FN_NAMES = {
    1: '?',
    2: '?',
    3: 'ReadOutWords',
    4: 'ReadInWords',
    5: 'WriteBit',
    6: 'WriteWord',
    15: 'WriteBits',
    16: 'WriteWords',
}

class ModbusException(Exception):
    def __init__(self, code, msg = None):
        if msg:
            super().__init__('Modbus exception {:X} ({}): {}'.format(code, EXC_NAMES.get(code, ''), msg))
        else:
            super().__init__('Modbus exception {:X} ({})'.format(code, EXC_NAMES.get(code, '')))
        self.exc_code = code
        self.exc_name = EXC_NAMES.get(code, '')
