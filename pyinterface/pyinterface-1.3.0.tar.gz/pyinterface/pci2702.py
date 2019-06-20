
"""
PCI/CPZ-2702 DIO ボードのドライバです。
"""

import struct
from . import core


class pci2702_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('IN1', 'IN2', 'IN3', 'IN4', 'IN5', 'IN6', 'IN7', 'IN8'),
            ('IN9', 'IN10', 'IN11', 'IN12', 'IN13', 'IN14', 'IN15', 'IN16'),
            ('IN17', 'IN18', 'IN19', 'IN20', 'IN21', 'IN22', 'IN23', 'IN24'),
            ('IN25', 'IN26', 'IN27', 'IN28', 'IN29', 'IN30', 'IN31', 'IN32'),
            ('IN33', 'IN34', 'IN35', 'IN36', 'IN37', 'IN38', 'IN39', 'IN40'),
            ('IN41', 'IN42', 'IN43', 'IN44', 'IN45', 'IN46', 'IN47', 'IN48'),
            ('IN49', 'IN50', 'IN51', 'IN52', 'IN53', 'IN54', 'IN55', 'IN56'),
            ('IN57', 'IN58', 'IN59', 'IN60', 'IN61', 'IN62', 'IN63', 'IN64'),
            ('IRIN2', '', '', '', '', 'STB2', 'ACKR2', 'ACK2'),
            ('IRIN1', '', '', '', 'LF', 'ACK1', 'STBR1', 'STB1'),
            ('TD1', 'TD2', 'TD3', 'TD4', '', '', '', ''),
            ('PORT0', 'PORT1', 'PORT2', 'PORT3', 'PORT4', 'PORT5', 'PORT6', 'PORT7'),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'SIGT', 'SIGR', 'SIGRR', ''),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'SIGT', 'SIGR', '', ''),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'EDS1', 'EDS2', 'EDS3', 'EDS4'),
            ('BID0', 'BID1', 'BID2', 'BID3', '', '', '', ''),
        ),
    )
    
    bit_flags_out = (
        (
            ('OUT1', 'OUT2', 'OUT3', 'OUT4', 'OUT5', 'OUT6', 'OUT7', 'OUT8'),
            ('OUT9', 'OUT10', 'OUT11', 'OUT12', 'OUT13', 'OUT14', 'OUT15', 'OUT16'),
            ('OUT17', 'OUT18', 'OUT19', 'OUT20', 'OUT21', 'OUT22', 'OUT23', 'OUT24'),
            ('OUT25', 'OUT26', 'OUT27', 'OUT28', 'OUT29', 'OUT30', 'OUT31', 'OUT32'),
            ('OUT33', 'OUT34', 'OUT35', 'OUT36', 'OUT37', 'OUT38', 'OUT39', 'OUT40'),
            ('OUT41', 'OUT42', 'OUT43', 'OUT44', 'OUT45', 'OUT46', 'OUT47', 'OUT48'),
            ('OUT49', 'OUT50', 'OUT51', 'OUT52', 'OUT53', 'OUT54', 'OUT55', 'OUT56'),
            ('OUT57', 'OUT58', 'OUT59', 'OUT60', 'OUT61', 'OUT62', 'OUT63', 'OUT64'),
            ('', '', '', 'PO10', 'PO11', 'PO12', 'ACK10', 'ACK11'),
            ('', '', '', 'PO20', 'PO21', 'PO22', 'STB20', 'STB21'),
            ('TCTRL1', 'TCTRL2', 'TCTRL3', 'TCTRL4', 'SCK1', 'SCK2', 'SCK3', ''),
            ('PORT0', 'PORT1', 'PORT2', 'PORT3', 'PORT4', 'PORT5', 'PORT6', 'PORT7'),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'SIGT', 'SIGR', '', ''),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'SIGT', 'SIGR', '', ''),
            ('SIG1', 'SIG2', 'SIG3', 'SIG4', 'EDS1', 'EDS2', 'EDS3', 'EDS4'),
            ('', '', '', '', '', '', '', ''),
        ),
    )

    num_input = 64
    num_output = 64
    
    available_input_byte_ranges = [
        'IN1_8',
        'IN9_16',
        'IN17_24',
        'IN25_32',
        'IN33_40',
        'IN41_48',
        'IN49_56',
        'IN57_64',
    ]

    available_input_word_ranges = [
        'IN1_16',
        'IN17_32',
        'IN33_48',
        'IN49_64',
    ]
    
    available_input_dword_ranges = [
        'IN1_32',
        'IN33_64',
    ]

    available_output_byte_ranges = [
        'OUT1_8',
        'OUT9_16',
        'OUT17_24',
        'OUT25_32',
        'OUT33_40',
        'OUT41_48',
        'OUT49_56',
        'OUT57_64',
    ]
    
    available_output_word_ranges = [
        'OUT1_16',
        'OUT17_32',
        'OUT33_48',
        'OUT49_64',
    ]
    
    available_output_dword_ranges = [
        'OUT1_32',
        'OUT33_64',
    ]

    def get_board_id(self):
        bar = 0
        offset = 0x0f
        size = 1
        
        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]
        return bid

    
    def initialize(self):
        self.output_dword('OUT1_32', struct.pack('<i', 0))
        self.output_dword('OUT33_64', struct.pack('<i', 0))
        self.set_latch_status()
        self.set_ack_pulse_command()
        self.set_stb_pulse_command()
        return

    
    def _verify_io_number_access(self, start, num, io_number):
        if (start < 1) or (start+num > io_number+1):
            msg = 'I/O number must be in 1-{0},'.format(io_number)
            msg += ' while {0}-{1} is given.'.format(start, start+num-1)
            raise ValueError(msg)
        return
    
    
    def input_point(self, start, num):
        self._verify_io_number_access(start, num, self.num_input)
        inp1 = self.input_dword('IN1_32')
        inp2 = self.input_dword('IN33_64')
        inp = inp1.to_list() + inp2.to_list()
        bits = inp[start-1:start+num-1]
        return bits
    
    
    def output_point(self, data, start):
        bar = 0
        offset = 0x00
        
        num = len(data)
        self._verify_io_number_access(start, num, self.num_output)
        new_d = self.log_bytes_out[0][0:8]
        new_d = core.bytes2list(new_d)
        new_d[start-1:start+num-1] = data
        new_d = core.list2bytes(new_d)
        self.write(bar, offset, new_d)
        return 
    
    
    def input_byte(self, range_):
        bar = 0
        size = 1
        
        if range_ == 'IN1_8': offset = 0x00
        elif range_ == 'IN9_16': offset = 0x01            
        elif range_ == 'IN17_24': offset = 0x02
        elif range_ == 'IN25_32': offset = 0x03
        elif range_ == 'IN33_40': offset = 0x04
        elif range_ == 'IN41_48': offset = 0x05
        elif range_ == 'IN49_56': offset = 0x06
        elif range_ == 'IN57_64': offset = 0x07
        else:
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        d = self.read(bar, offset, size)
        return d
        
    
    def input_word(self, range_):
        bar = 0
        size = 2
        
        if range_ == 'IN1_16': offset = 0x00
        elif range_ == 'IN17_32': offset = 0x02
        elif range_ == 'IN33_48': offset = 0x04
        elif range_ == 'IN49_64': offset = 0x06
        else:
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        d = self.read(bar, offset, size)
        return d
        
    
    def input_dword(self, range_):
        bar = 0
        size = 4
        
        if range_ == 'IN1_32': offset = 0x00
        elif range_ == 'IN33_64': offset = 0x04
        else:
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        d = self.read(bar, offset, size)
        return d

        
    def output_byte(self, range_, data):
        bar = 0
        
        if range_ == 'OUT1_8': offset = 0x00
        elif range_ == 'OUT9_16': offset = 0x01
        elif range_ == 'OUT17_24': offset = 0x02
        elif range_ == 'OUT25_32': offset = 0x03
        elif range_ == 'OUT33_40': offset = 0x04
        elif range_ == 'OUT41_48': offset = 0x05
        elif range_ == 'OUT49_56': offset = 0x06
        elif range_ == 'OUT57_64': offset = 0x07
        else:
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        self.write(bar, offset, data)
        return 


    def output_word(self, range_, data):
        bar = 0
        
        if range_ == 'OUT1_16': offset = 0x00
        elif range_ == 'OUT17_32': offset = 0x02
        elif range_ == 'OUT33_48': offset = 0x04
        elif range_ == 'OUT49_64': offset = 0x06
        else: 
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        self.write(bar, offset, data)
        return 


    def output_dword(self, range_, data):
        bar = 0
        
        if range_ == 'OUT1_32': offset = 0x00
        elif range_ == 'OUT33_64': offset = 0x04
        else: 
            msg = 'bad range_: {0}'.format(range_)
            raise ValueError(msg)
        
        self.write(bar, offset, data)
        return 
    

    def set_latch_status(self, enable=''):
        bar = 0
        offset = 0x0b        
        self.set_flag(bar, offset, enable)
        return
    

    def get_latch_status(self):
        bar = 0
        offset = 0x0b
        size = 1
        return self.read(bar, offset, size)
    
    
    def get_ack_status(self):
        bar = 0
        offset = 0x08
        size = 1
        return self.read(bar, offset, size)
    
    def set_ack_pulse_command(self, ack='', pulse=''):
        bar = 0
        offset = 0x08
        flags = ack + ' ' + pulse        
        return self.set_flag(bar, offset, flags)
    

    def get_stb_status(self):
        bar = 0
        offset = 0x09
        size = 1        
        return self.read(bar, offset, size)
        
    
    def set_stb_pulse_command(self, stb='', pulse=''):
        bar = 0
        offset = 0x09
        flags = stb + ' ' + pulse        
        return self.set_flag(bar, offset, flags)

    def get_reset_in_status(self):
        raise NotImplementedError()



    
