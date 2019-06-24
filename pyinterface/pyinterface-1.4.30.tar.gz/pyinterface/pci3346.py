

import time
from . import core



def ch2byte(ch):
    ch_bit = '{0:08b}'.format(ch-1)[::-1]
    ch_byte = core.bit2bytes(ch_bit)
    return ch_byte

def byte2ch(ch_byte):
    return ch_byte.to_uint() + 1

def range2flag(range_):
    if range_ == '0_10V': return 'RG0'
    elif range_ == '5V': return 'RG1'
    elif range_ == '10V': return 'RG0 RG1'
    raise Exception('wrong range_ : %s'%(range_))

def flag2range(flag):
    f = flag.to_flags()
    if f == 'RG0': return '0_10V'
    elif f == 'RG1': return '5V'
    elif f == 'RG0 RG1': return '10V'
    raise Exception('wrong flag : %s'%(f))

def volt2bytes(da_volt, range_):
    if range_ == '0_10V':
        lsb = 10 / 4096
        start = 0
        end = 10 - lsb
    elif range_ == '5V':
        lsb = 10 / 4096
        start = -5
        end = 5 - lsb
    elif range_ == '10V':
        lsb = 20 / 4096
        start = -10
        end = 10 - lsb
    else:
        raise Exception('wrong range_ : %s'%(range_))
    
    if (da_volt < start) | (da_volt > end):
        raise Exception('wrong da_volt : {da_volt}  (must be {start:.6f}--{end:.6f})'.format(**locals()))
    
    da_int = int((da_volt - start) / lsb)
    da_bytes = da_int.to_bytes(2, 'little')
    return da_bytes

def bytes2volt(da_bytes, range_):
    if range_ == '0_10V':
        lsb = 10 / 4096
        start = 0
    elif range_ == '5V':
        lsb = 10 / 4096
        start = -5
    elif range_ == '10V':
        lsb = 20 / 4096
        start = -10
    else:
        raise Exception('wrong range_ : %s'%(range_))
    
    da_volt = da_bytes.to_uint() * lsb + start
    return da_volt



class pci3346_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'), # 00
            ('B8', 'B9', 'B10', 'B11', '', '', '', ''), # 01
            ('CA0', 'CA1', 'CA2', 'CA3', '', '', '', ''), # 02
            ('', '', '', '', '', '', '', ''), # 03
            ('', '', '', '', '', '', '', ''), # 04
            ('', '', '', '', '', '', '', ''), # 05
            ('RG0', 'RG1', '', '', '', '', '', ''), # 06
            ('CH0', 'CH1', 'CH2', 'CH3', '', '', '', ''), # 07
            ('', '', '', '', '', '', '', ''), # 08
            ('GATE', '', '', '', '', '', '', ''), # 09
            ('', '', '', '', '', '', '', ''), # 0A
            ('', '', '', '', '', '', '', ''), # 0B
            ('', '', '', '', '', '', '', ''), # 0C
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''), #0D
            ('', '', '', '', '', '', '', ''), #0E
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''), #0F
            ('', '', 'EINT2', '', '', '', '', ''), #10
            ('', '', '', '', '', '', '', ''), #11
            ('', '', '', '', '', '', '', ''), #12
            ('', '', '', '', '', '', '', ''), #13
            ('', '', '', '', '', '', '', ''), #14
            ('', '', '', '', '', '', '', ''), #15
            ('', '', '', '', '', '', '', ''), #16
            ('BID0', 'BID1', 'BID2', 'BID3', 'M/S', 'CLKOEN', 'TRGOEN', ''), # 17
            ('', '', '', '', '', '', '', ''), #18
            ('', '', '', '', '', '', '', ''), #19
            ('', '', '', '', '', '', '', ''), #1A
            ('AO', '', '', '', '', '', '', ''), #1B
            ('', '', '', '', '', '', '', ''), #1C
            ('', '', '', '', '', '', '', ''), #1D
            ('IN1', 'IN2', '', '', '', '', '', ''), #1E
            ('', '', '', '', '', '', '', '') #1F
        ),
    )

    bit_flags_out = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'), #00
            ('B8', 'B9', 'B10', 'B11', '', '', '', ''), #01
            ('CA0', 'CA1', 'CA2', 'CA3', '', '', '', ''), #02
            ('', '', '', '', '', '', '', ''), #03
            ('', '', '', '', '', '', '', ''), #04
            ('MD0', 'MD1', '', '', '', '', '', ''), #05
            ('RG0', 'RG1', '', '', '', '', '', ''), #06
            ('CH0', 'CH1', 'CH2', 'CH3', '', '', '', ''), #07
            ('', '', '', '', '', '', '', ''), #08
            ('GATE', '', '', '', '', '', '', ''), #09
            ('', '', '', '', '', '', '', ''), #0A
            ('', '', '', '', '', '', '', ''), #0B
            ('', '', '', '', '', '', '', ''), #0C
            ('', '', '', '', '', '', '', ''), #0D
            ('', '', '', '', '', '', '', ''), #0E
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''), #0F
            ('', '', 'EINT2', '', '', '', '', ''), #10
            ('', '', '', '', '', '', '', ''), #11
            ('', '', '', '', '', '', '', ''), #12
            ('', '', '', '', '', '', '', ''), #13
            ('', '', '', '', '', '', '', ''), #14
            ('', '', '', '', '', '', '', ''), #15
            ('', '', '', '', '', '', '', ''), #16
            ('', '', '', '', 'M/S', 'CLKOEN', 'TRGOEN', ''), #17
            ('', '', '', '', '', '', '', ''), #18
            ('', '', '', '', '', '', '', ''), #19
            ('', '', '', '', '', '', '', ''), #1A
            ('AO', '', '', '', '', '', '', ''), #1B
            ('', '', '', '', '', '', '', ''), #1C
            ('', '', '', '', '', '', '', ''), #1D
            ('IN1', 'IN2', '', '', '', '', '', ''), #1E
            ('', '', '', '', '', '', '', '') #1F
        ),
    )
    
    available_ranges = [
        '0_10V',
        '5V',
        '10V',
    ]
    available_da_channel_num = 16
    available_di_channel_num = 2
    available_do_channel_num = 2

    last = {}

    def get_board_id(self):
        bar = 0
        offset = 0x17
        size = 1

        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]

        return bid

    def initialize(self):
        self.last = {
            'output': {_: 0 for _ in range(1, 17)},
            'output_ch': 1,
            'output_onoff': 'OFF',
            'control_mode': 'ASYNC',
            'range_ch': 1,
            'range': {_: '0_10V' for _ in range(1, 17)},
        }
        self.output_da([{'ch_no': i+1, 'range': '0_10V'}
                        for i in range(self.available_da_channel_num)],
                       [0 for i in range(self.available_da_channel_num)])
        self._set_output_ch(1)
        self._set_control_mode_clear()
        self._set_range_ch(1)
        self._set_output_off()
        self._da_set_do(core.bit2bytes('00'))
        return

    def set_sampling_config(self, smpl_ch_req=None, sampling_mode=None,
                            smpl_freq=None, smpl_repeat=None, trig_mode=None,
                            trig_point=None, trig_delay=None, eclk_edge=None,
                            trig_edge=None, trig_di=None):
        raise NotImplemented()

    def get_sampling_config(self):
        raise NotImplemented()
        
    def set_sampling_data(self, data):
        raise NotImplemented()

    def clear_sampling_data(self):
        raise NotImplemented()
    
    def start_sampling(self, sync_flag):
        raise NotImplemented()
    
    def stop_sampling(self):
        raise NotImplemented()
    
    def get_status(self):
        raise NotImplemented()
    
    def output_da(self, smpl_ch_req, data):
        self._set_output_on()
        self._set_control_mode_wait()
        for req, d in zip(smpl_ch_req, data):
            self._set_output_voltage(req['ch_no'], req['range'], d)
            continue
        self._set_control_mode_sync()
        return
    
    def input_di(self):
        raise NotImplemented()
    
    def output_do(self, data):
        raise NotImplemented()
    
    def set_current_dir(self, direction):
        raise NotImplemented()
    
    def get_current_dir(self):
        raise NotImplemented()
    
    def set_power_supply(self, onoff):
        raise NotImplemented()
    
    def get_power_supply(self):
        raise NotImplemented()
    
    def get_relay_status(self):
        raise NotImplemented()
    
    def get_0v_status(self):
        raise NotImplemented()
    
    def set_excess_voltage(self, oven, exoven):
        raise NotImplemented()

    def _set_output_voltage(self, ch, range_, volt):
        self._set_output_range(ch, range_)
        self._set_output_ch(ch)
        volt_bytes = volt2bytes(volt, range_)
        self._da_set_output(volt_bytes)
        self.last['output'][ch] = volt
        return
    
    def _set_output_ch(self, ch):
        if self.last['output_ch'] != ch:
            ch_byte = ch2byte(ch)
            self._da_set_output_ch(ch_byte)
            self.last['output_ch'] = ch
            pass
        return        
    
    def _set_control_mode_async(self):
        if self.last['control_mode'] != 'ASYNC':
            self._da_set_control_mode('')
            self.last['control_mode'] = 'ASYNC'
            pass
        return
            
    def _set_control_mode_wait(self):
        if self.last['control_mode'] != 'WAIT':
            self._da_set_control_mode('MD0 MD1')
            self.last['control_mode'] = 'WAIT'
            pass
        return
    
    def _set_control_mode_sync(self):
        if self.last['control_mode'] != 'SYNC':
            self._da_set_control_mode('MD0')
            self.last['control_mode'] = 'SYNC'
            pass
        return
    
    def _set_control_mode_clear(self):
        if self.last['control_mode'] != 'CLEAR':
            self._da_set_control_mode('MD1')
            self.last['control_mode'] = 'CLEAR'
            pass
        return

    def _set_output_range(self, ch, range_):
        if self.last['range'][ch] != range_:
            self._set_range_ch(ch)
            range_flag = range2flag(range_)
            self._da_set_output_range(range_flag)
            self.last['range'][ch] = range_
            pass
        return
    
    def _set_range_ch(self, ch):
        if self.last['range_ch'] != ch:
            ch_byte = ch2byte(ch)
            self._da_set_range_ch(ch_byte)
            self.last['range_ch'] = ch
            pass
        return
        
    def _set_output_on(self):
        if self.last['output_onoff'] != 'ON':
            self._da_set_output_onoff('AO')
            self.last['output_onoff'] = 'ON'
            pass
        return

    def _set_output_off(self):
        if self.last['output_onoff'] != 'OFF':
            self._da_set_output_onoff('')
            self.last['output_onoff'] = 'OFF'
            pass
        return
    
    
    def _da_set_output(self, da_byte):
        bar = 0
        offset = 0x00        
        self.write(bar, offset, da_byte)
        return
    
    def _da_get_output(self):
        bar = 0
        size = 2
        offset = 0x00        
        return self.read(bar, offset, size)
    
    def _da_set_output_ch(self, ch_byte):
        bar = 0
        offset = 0x02
        self.write(bar, offset, ch_byte)
        return
    
    def _da_get_output_ch(self):
        bar = 0
        size = 1
        offset = 0x02
        return self.read(bar, offset, size)

    def _da_set_control_mode(self, mode_flag):
        bar = 0
        offset = 0x05
        self.set_flag(bar, offset, mode_flag)
        return

    def _da_set_output_range(self, range_flag):
        bar = 0
        offset = 0x06
        self.set_flag(bar, offset, range_flag)
        return

    def _da_get_output_range(self):
        bar = 0
        offset = 0x06
        size = 1
        return self.read(bar, offset, size)

    def _da_set_range_ch(self, ch_byte):
        bar = 0
        offset = 0x07
        self.write(bar, offset, ch_byte)
        return
        
    def _da_get_range_ch(self):
        bar = 0
        size = 1
        offset = 0x07
        return self.read(bar, offset, size)
    
    def _da_set_output_onoff(self, flag):
        bar = 0
        offset = 0x1b
        self.set_flag(bar, offset, flag)
        return
    
    def _da_get_output_onoff(self):
        bar = 0
        offset = 0x1b
        size = 1
        return self.read(bar, offset, size)

    def _da_set_do(self, do_byte):
        bar = 0
        offset = 0x1e
        self.write(bar, offset, do_byte)
        return
    
    def _da_get_di(self):
        bar = 0
        offset = 0x1e
        size = 1
        return self.read(bar, offset, size)

    
    
    
    
    

 

    
