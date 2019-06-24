

import struct
from . import core




class InvalidChError(Exception):
    pass




class InvalidModeError(Exception):
    pass




class pci3165_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B8', 'B9', 'B10', 'B11', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', 'BUSY'),
            ('CA0', 'CA1', 'CA2', 'CA3', 'CA4', 'CA5', '', ''),
            ('SD0', 'SD1', 'SD2', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('GATE', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('TMR', 'BSY', 'TRG', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('TMR', 'BSY', 'TRG', '', '', '', '', ''),
            ('EXTG', 'EINT', '', '', '', '', '', 'DITG'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('BID0', 'BID1', 'BID2', 'BID3', 'M/S', 'CLKOEN', 'TRGOEN', ''),
            ('', '', '', '', '', '', 'SMD0', 'SMD1'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('IN1', 'IN2', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', '')
        ),
        (
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', '')
        )
    )
    
    bit_flags_out = (
        (
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('CA0', 'CA1', 'CA2', 'CA3', 'CA4', 'CA5', 'MA', 'MB'),
            ('SD0', 'SD1', 'SD2', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('GATE', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('DITG', 'TMR', 'BSY', 'TRG', '', '', '', ''),
            ('', 'EXTG', 'EINT', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('SMD1', '', '', '', '', 'M/S', 'CLKOEN', 'TRGOEN'),
            ('', '', '', '', '', '', '', 'SMD0'),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', 'OUT1', 'OUT2', '', '', '', '', ''),
            ('', '', '', '', '', '', '')
        ),
        (
            ('', '', '', '', '', '', '', ''),
            ('U/D', 'INC', 'CS', '', '', '', '', ''),
            ('U/D', 'INC', 'CS', '', '', '', '', ''),
            ('U/D', 'INC', 'CS', '', '', '', '', '')
        )
    )




    def get_board_id(self):
        bar = 0
        offset = 0x17
        size = 1


        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]


        return bid




    def _verify_mode(self, mode):
        mode_list = ['single', 'diff']
        if mode in mode_list: pass
        else:
            msg = 'Mode must be single or diff mode '
            msg += 'while {0} mode is given.'.format(mode)
        return


    
    def _verify_ch(self, ch='', mode=''):
        ch_limit_single = 64
        ch_limit_diff = 32


        if mode == 'single':
            if ch in ['ch{0}'.format(i) for i in range(1, ch_limit_single+1)]: pass
            else:
                msg = 'Ch must be in 1ch-{0}ch with {1} mode '.format(ch_limit_single, mode)
                msg += 'while {0}ch is given.'.format(ch)
                raise InvalidChError(msg)
            return
        
        if mode == 'diff':
            if ch in ['ch{0}'.format(i) for i in range(1,ch_limit_diff+1)]: pass
            else:
                msg = 'Ch must be in 1ch-{0}ch with {1} mode'.format(ch_limit_diff, mode)
                msg += 'while {0}ch is given.'.format(ch)
                raise InvalidChError(msg)
            return




    def _set_sampling_config(self, mode='single'):
        bar = 0
        offset = 0x05


        if mode == 'single': mode_ = ''
        elif mode == 'diff': mode_ = 'SD0'
        
        flags = mode_


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




    def _list2voltage(self, vol_list=[]):
        vol_range = 10
        res = 16
        res_int = 2**16
        
        bytes_v = int.from_bytes(core.list2bytes(vol_list), 'little')
        vol = -vol_range + (vol_range/(res_int/2))*bytes_v


        return vol




    def _start_sampling(self, data):
        bar = 0
        offset = 0x04
        size = 1
        
        num = len(data)
        new_d = core.list2bytes(data)
        self.write(bar, offset, new_d)
        self._busy()
        return




    def _busy(self):
        bar = 0
        size = 1
        offset = 0x03


        busy = self.read(bar, offset, size)
        while busy.to_list()[7]==0:
            busy = self.read(bar, offset, size)
        return


    
    def set_sampling_config(self, singlediff=''):
        self._verify_mode(mode=singlediff)
        self._set_sampling_config(mode=singlediff)
        return


    
    def get_sampling_config(self):
        bar = 0
        offset = 0x05
        size = 1


        return self.read(bar, offset, size).print()




    def input_ad(self, ch='', singlediff='diff'):
        bar = 0
        size = 2
        offset = 0x00


        self._verify_mode(mode=singlediff)
        self._verify_ch(ch=ch, mode=singlediff)
        self._set_sampling_config(mode=singlediff)
        ch = self._ch2bit(ch)
        self._start_sampling(ch)


        ret = self.read(bar, offset, size)
        ret = self._list2voltage(ret.to_list())


        return ret


    
    def input_ad_master(self, singlediff='diff'): # for Mr.Inaba
        self._verify_mode(singlediff)
        mode = singlediff


        if mode == 'single': ch = 'ch1-ch16'
        elif mode == 'diff': ch = 'ch1-ch8'
        
        ch_ = ch.replace('ch', '').split('-')
        ch_initial, ch_final = int(ch_[0]), int(ch_[1])
        ch = [self.input_ad('ch{0}'.format(i)) for i in range(ch_initial, ch_final+1)]
        
        return ch


# History
# -------
# written by K.Sakasai
