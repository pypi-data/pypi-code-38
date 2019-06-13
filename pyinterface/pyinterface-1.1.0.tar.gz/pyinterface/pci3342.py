

import time
import struct
from . import core




class InvalidChTypeError(Exception):
    pass




class InvalidChRangeError(Exception):
    pass




class InvalidVoltageError(Exception):
    pass




class pci3342_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15'),
            ('C0', 'C1', 'C2', 'C3', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('RG0', 'RG1', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('GATE', '', '', '', '', '', '', ''),
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''),
            ('', '', 'EINT', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('MRD', '', '', '', '', '', '', 'MWR'),
            ('OFS0', 'OFS1', 'OFS2', 'OFS3', 'OFS4', 'OFS5', 'OFS6', 'OFS7'),
            ('GAIN0', 'GAIN1', 'GAIN2', 'GAIN3', 'GAIN4', 'GAIN5', 'GAIN6', 'GAIN7'),
            ('CAR0', 'CAR1', 'CAR2', 'CAR3', '', '', '', ''),
            ('TRG0', 'TRG1', 'TRG2', 'TRG3', 'TRG4', 'TRG5', 'TRG6', 'TRG7'),
            ('BID0', 'BID1', 'BID2', 'BID3', 'M/S', 'CLKOEN', 'TRGOEN', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('OC0', 'OC1', 'OC2', 'OC3', 'OC4', 'OC5', 'OC6', 'OC7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('IN1', 'IN2', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', '')
        ),
    )


    bit_flags_out = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15'),
            ('C0', 'C1', 'C2', 'C3', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('MD0', 'MD1', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('TCTRL0', 'TCTRL1', 'TCTRL2', 'TCTRL3', 'TCTRL4', 'TCTRL5', 'TCTRL6', 'TCTRL7'),
            ('TCTRL8', 'TCTRL9', 'TCTRL10', 'TCTRL11', 'TCTRL12', 'TCTRL13', 'TCTRL14', 'TCTRL15'),
            ('TCTRL16', 'TCTRL17', 'TCTRL18', 'TCTRL19', 'TCTRL20', 'TCTRL21', 'TCTRL22', 'TCTRL23'),
            ('', '', '', '', '', '', '', ''),
            ('GATE', '', '', '', '', '', '', ''),
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('TMR', '', 'TRG', '', '', 'SPS', '', ''),
            ('', '', 'EINT', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('MRD', '', '', '', '', '', '', 'MWR'),
            ('OFS0', 'OFS1', 'OFS2', 'OFS3', 'OFS4', 'OFS5', 'OFS6', 'OFS7'),
            ('GAIN0', 'GAIN1', 'GAIN2', 'GAIN3', 'GAIN4', 'GAIN5', 'GAIN6', 'GAIN7'),
            ('CAR0', 'CAR1', 'CAR2', 'CAR3', '', '', '', ''),
            ('TRG0', 'TRG1', 'TRG2', 'TRG3', 'TRG4', 'TRG5', 'TRG6', 'TRG7'),
            ('BID0', 'BID1', 'BID2', 'BID3', 'M/S', 'CLKOEN', 'TRGOEN', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('OC0', 'OC1', 'OC2', 'OC3', 'OC4', 'OC5', 'OC6', 'OC7'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('IN1', 'IN2', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', '')
        ),
    )        


    def get_board_id(self):
        bar = 0
        offset = 0x17
        size = 1


        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]


        return bid




    def _verify_voltage(self, voltage=0.0):
        vol_limit = 10
        if abs(voltage) <= vol_limit: pass
        else:
            msg = 'Voltage must be in -{0}[V] - {1}[V] '.format(-vol_limit, vol_limit)
            msg += 'while {0}[V] is given.'.format(voltage)
            raise InvalidVoltageError(msg)


        return voltage




    def _verify_ch(self, ch=''):
        ch_lim_initial = 1
        ch_lim_final = 16


        if ch.find('-') == -1:
            msg = 'Ch type must be chx-chy absolutelly '
            msg += 'while {0} is given.'.format(ch)
            raise InvalidChTypeError(msg)
        
        ch_ = ch.split('-')
        if len(ch_) == 2: pass
        else :
            msg = 'Ch type must be chx-chy absolutelly '
            msg += 'while {0} is given.'.format(ch)
            raise InvalidChTypeError(msg)
            
        ch_initial, ch_final = int(ch_[0].replace('ch', '')), int(ch_[1].replace('ch', ''))
        if 1 <= ch_initial < ch_final <= 16: pass
        else:
            msg = 'Ch range is in ch{0} - ch{1} '.format(ch_lim_initial, ch_lim_final)
            msg = 'while ch{0} - ch{1} is given.'.format(ch_initial, ch_final)
            raise InvalidChRangeError(msg)
            
        ch = [i for i in range(ch_initial, ch_final+1)]


        return ch




    def _voltage2list(self, voltage=0.0):
        voltage = float(voltage)
        vol_range = 10.0
        res = 12
        res_int = 2**res
        
        if voltage == 10.0: bytes_v = int(res_int - 1)
        else: bytes_v = int(voltage/(vol_range/(res_int)))
        bit_ = bin(bytes_v).replace('0b', '0'*(16-(len(bin(bytes_v))-2)))
        bit_list = [int(bit_[i]) for i in range(len(bit_))]
        bit_list.reverse()


        return bit_list




    def _set_sampling_config(self, mode=''):
        bar = 0
        offset = 0x05


        if mode == 'all_vout_disable': mode = ''
        elif mode == 'all_vout': mode = 'MD0'
        elif mode == 'all_vout_clear': mode = 'MD1'
        elif mode == 'all_vout_enable': mode = 'MD0 MD1'


        flags = mode


        self.set_flag(bar, offset, flags)
        return




    def _ch2bit(self, ch=''):
        if ch == '': return b''
        else:
            ch = int(ch.replace('ch', ''))
            ch = bin(ch-1).replace('0b', '0'*(8-(len(bin(ch-1))-2)))
            bit_list = [int(ch[i]) for i in range(len(ch))]
            bit_list.reverse()


            return bit_list




    def _da_onoff(self, onoff=0):
        bar = 0
        offset = 0x1b


        if onoff == 0: onoff_ = ''
        if onoff == 1: onoff_ = 'OC0 OC1 OC2 OC3 OC4 OC5 OC6 OC7'


        flags = onoff_


        self.set_flag(bar, offset, flags)
        return




    def _da_output(self, ch='', voltage=0.0):
        bar = 0
        size_ch = 1
        size_vol = 2
        offset_ch = 0x02
        offset_vol = 0x00


        data_ch = self._ch2bit(ch=ch)
        new_d_ch = core.list2bytes(data_ch)
        self.write(bar, offset_ch, new_d_ch)


        data_vol = self._voltage2list(voltage=voltage)
        new_d_vol = core.list2bytes(data_vol)
        self.write(bar, offset_vol, new_d_vol)
        return




    def _start_sampling(self):
        self._set_sampling_config(mode='all_vout')


    
    def output_da(self, ch='', voltage=0.0):
        bar = 0
        size = 2
        offset = 0x00


        ch_ = self._verify_ch(ch=ch)
        voltage = self._verify_voltage(voltage=voltage)
        self._set_sampling_config(mode='all_vout_enable')
        self._da_onoff(onoff=1)
        time.sleep(0.01)
        
        for i in range(len(ch_)):
            self._da_output('ch{0}'.format(i+1), voltage)


        self._start_sampling()
        time.sleep(0.01)
        return


    
    def _verify_ch_sim(self, ch=''):
        ch_lim_initial = 1
        ch_lim_final = 16


        if ch in ['ch{}'.format(i) for i in range(ch_lim_initial,ch_lim_final+1)]:
            pass
        else:
            msg = 'Ch range is in ch{0} - ch{1} '.format(ch_lim_initial, ch_lim_final)
            msg = 'while {0} is given.'.format(ch)
            raise InvalidChRangeError(msg)
            
        return ch


    
    def output_da_sim(self, ch='', voltage=0.0):
        bar = 0
        size = 2
        offset = 0x00


        ch_ = self._verify_ch_sim(ch=ch)
        voltage = self._verify_voltage(voltage=voltage)
        self._set_sampling_config(mode='all_vout_enable')
        self._da_onoff(onoff=1)
        time.sleep(0.01)


        self._da_output(ch_, voltage)


        self._start_sampling()
        time.sleep(0.01)
        return


    
    def initialize(self):
        self._da_onoff(onoff=1)
        self._set_sampling_config('all_vout_clear')




    def finalize(self):
        self._set_sampling_config('all_vout_clear')
        self._da_onoff(onoff=0)


# History
# -------
# written by K.Sakasai
