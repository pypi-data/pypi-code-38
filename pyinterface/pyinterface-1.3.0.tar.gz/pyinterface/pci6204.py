
import struct
from . import core


class InvalidChannelError(Exception):
    pass


class pci6204_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('CD0', 'CD1', 'CD2', 'CD3', 'CD4', 'CD5', 'CD6', 'CD7'),
            ('CD8', 'CD9', 'CD10', 'CD11', 'CD12', 'CD13', 'CD14', 'CD15'),
            ('CD16', 'CD17', 'CD18', 'CD19', 'CD20', 'CD21', 'CD22', 'CD23'),
            ('CD24', 'CD25', 'CD26', 'CD27', 'CD28', 'CD29', 'CD30', 'CD31'),
            ('SEL0', 'SEL1', 'MD0', 'MD1', 'DIR', 'EQS', '', ''),
            ('A', 'B', 'Z', 'L1', 'L2', 'L3', '', ''),
            ('U/D', 'CBF', 'EQ', 'EXLTS', 'EQF', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('CD0', 'CD1', 'CD2', 'CD3', 'CD4', 'CD5', 'CD6', 'CD7'),
            ('CD8', 'CD9', 'CD10', 'CD11', 'CD12', 'CD13', 'CD14', 'CD15'),
            ('CD16', 'CD17', 'CD18', 'CD19', 'CD20', 'CD21', 'CD22', 'CD23'),
            ('CD24', 'CD25', 'CD26', 'CD27', 'CD28', 'CD29', 'CD30', 'CD31'),
            ('SEL0', 'SEL1', 'MD0', 'MD1', 'DIR', 'EQS', '', ''),
            ('A', 'B', 'Z', 'L1', 'L2', 'L3', '', ''),
            ('U/D', 'CBF', 'EQ', 'EXLTS', 'EQF', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
        ),
        (
            ('TD1', 'TD2', 'TD3', 'TD4', '', '', '', ''),
            ('', '', '', '', 'SIGT', '', '', ''),
            ('', '', '', '', 'SIGT', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('BID0', 'BID1', 'BID2', 'BID3', '', '', '', ''),
        )
    )
     
    bit_flags_out = (
        (
            ('WD0', 'WD1', 'WD2', 'WD3', 'WD4', 'WD5', 'WD6', 'WD7'),
            ('WD8', 'WD9', 'WD10', 'WD11', 'WD12', 'WD13', 'WD14', 'WD15'),
            ('WD16', 'WD17', 'WD18', 'WD19', 'WD20', 'WD21', 'WD22', 'WD23'),
            ('WD24', 'WD25', 'WD26', 'WD27', 'WD28', 'WD29', 'WD30', 'WD31'),
            ('SEL0', 'SEL1', 'MD0', 'MD1', 'DIR', 'EQS', '', ''),
            ('P/L', '/EN', '', '', '', '', '', ''),
            ('CC0', 'CC1', '', '', '', '', '', ''),
            ('CLS0', 'CLS1', 'LTS0', 'LTS1', 'ZP', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('WD0', 'WD1', 'WD2', 'WD3', 'WD4', 'WD5', 'WD6', 'WD7'),
            ('WD8', 'WD9', 'WD10', 'WD11', 'WD12', 'WD13', 'WD14', 'WD15'),
            ('WD16', 'WD17', 'WD18', 'WD19', 'WD20', 'WD21', 'WD22', 'WD23'),
            ('WD24', 'WD25', 'WD26', 'WD27', 'WD28', 'WD29', 'WD30', 'WD31'),
            ('SEL0', 'SEL1', 'MD0', 'MD1', 'DIR', 'EQS', '', ''),
            ('P/L', '/EN', '', '', '', '', '', ''),
            ('CC0', 'CC1', '', '', '', '', '', ''),
            ('CLS0', 'CLS1', 'LTS0', 'LTS1', 'ZP', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('L2', 'L3', 'EQ', 'EXLT', 'C/B', 'PERR', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
        ),
        (
            ('TCTRL1', 'TCTRL2', 'TCTRL3', 'TCTRL4', 'SCK1', 'SCK2', 'SCK3', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', 'SIGT', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
        )
    )

    available_ch = [1, 2]
    latch_status = {1: 0, 2: 0}
    comparator = {1: 0, 2: 0}
    
    def get_board_id(self):
        bar = 1
        offset = 0x0f
        size = 1
        
        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]
        return bid
    
    
    def initialize(self):
        self.set_counter(struct.pack('<l', 0), ch=1)
        self.set_counter(struct.pack('<l', 0), ch=2)
        self.set_comparator(struct.pack('<l', -1), ch=1)
        self.set_comparator(struct.pack('<l', -1), ch=2)
        self.set_mode(ch=1)
        self.set_mode(ch=2)
        self.enable_count(ch=1)
        self.enable_count(ch=2)
        self.set_z_mode('', '', '', '', ch=1)
        self.set_z_mode('', '', '', '', ch=2)
        return
    
    
    def _get_offset_for(self, ch, offset):
        ch_offset = {1: 0x00, 2: 0x10}
                
        if ch not in self.available_ch:
            msg = 'ch must be in {1}, not {0}'.format(ch, self.available_ch)
            raise ValueError(msg)
        
        return offset + ch_offset[ch]

        
    def reset(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x06)
        
        flags = 'CC0 CC1'
        self.set_flag(bar, offset, flags)
        return

    
    def set_mode(self, mode='', direction=0, equal=0, latch=0, ch=1):
        last = self.get_mode(ch)
        if mode is None: mode = last['mode']
        if direction is None: direction = last['direction']
        if equal is None: equal = last['equal']
        if latch is None: latch = last['latch']

        self._set_mode(mode, direction, equal, ch)
        self._set_latch(latch, ch)
        return

    
    def _set_mode(self, mode, direction, equal, ch):
        bar = 0
        offset = self._get_offset_for(ch, 0x04)
        
        flags = mode
        if direction == 1: flags += ' DIR'
        if equal == 1: flags += ' EQS'        
        return self.set_flag(bar, offset, flags)

    
    def _set_latch(self, latch, ch):
        self.latch_status[ch] = latch
        return

    
    def get_mode(self, ch=1):
        m = self._get_mode(ch)
        l = self._get_latch(ch)
        ret = {
            'mode': m.to_flags().replace(' DIR', '').replace(' EQS', ''),
            'direction': m['DIR'],
            'equal': m['EQS'],
            'latch': l,
        }
        return ret

    
    def _get_mode(self, ch):
        bar = 0
        offset = self._get_offset_for(ch, 0x04)
        size = 1
        
        return self.read(bar, offset, size)
    

    def _get_latch(self, ch):
        return self.latch_status[ch]
    

    def set_z_mode(self, clear_condition=None, latch_condition=None,
                   z_polarity=None, l_polarity=None, ch=1):
        last = self.get_z_mode(ch)
        if clear_condition is None: clear_condition = last['clear_condition']
        if latch_condition is None: latch_condition = last['latch_condition']
        if z_polarity is None: z_polarity = last['z_polarity']
        if l_polarity is None: l_polarity = last['l_polarity']

        self._set_z_mode(clear_condition, latch_condition,
                         z_polarity, l_polarity, ch)
        return
        
    
    def _set_z_mode(self, clear_condition, latch_condition,
                   z_polarity, l_polarity, ch):
        bar = 0
        offset = self._get_offset_for(ch, 0x07)
        
        flags = ' '.join([clear_condition, latch_condition])
        if z_polarity == 1: flags += ' ZP'
        self.set_flag(bar, offset, flags)
        return


    def get_z_mode(self, ch=1):
        m = self._get_z_mode(ch)
        
        cls = ''
        if m['CLS0']==1: cls = 'CLS0'
        elif m['CLS1']==1: cls = 'CLS1'
        
        lts = ''
        if m['LTS0']==1: lts = 'LTS0'
        elif m['LTS1']==1: lts = 'LTS1'
        
        ret = {
            'clear_condition': cls,
            'latch_condition': lts,
            'z_polarity': m['ZP'],
            'l_polarity': None,
        }
        return ret
    
    
    def _get_z_mode(self, ch):
        bar = 0
        offset = self._get_offset_for(ch, 0x07)
        size = 1

        return self.get_log('out', 0, offset)
        
    
    def enable_count(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x05)
        
        flags = ''        
        self.set_flag(bar, offset, flags)
        return
        
        
    def disable_count(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x05)
        
        flags = '/EN'        
        self.set_flag(bar, offset, flags)
        return
   
        
    def set_counter_mode(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x05)
        
        flags = self.get_log('out', bar, offset).to_flags()
        flags = flags.replace('P/L', '')
        self.set_flag(bar, offset, flags)
        return
    

    def set_comparator_mode(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x05)
        
        flags = self.get_log('out', bar, offset).to_flags()
        flags += ' P/L'
        self.set_flag(bar, offset, flags)
        return
    

    def set_counter(self, count, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x00)
        size = 4
        
        self.set_counter_mode()
        self.write(bar, offset, count)
        return
    
    
    def set_comparator(self, count, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x00)
        size = 4
        
        self.set_comparator_mode()
        self.write(bar, offset, count)
        self.comparator[ch] = count
        return
        
    
    def latch(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x06)
        
        flags = 'CC1'
        self.set_flag(bar, offset, flags)
        return
    
    
    def get_counter(self, ch=1):
        bar = 0
        offset = self._get_offset_for(ch, 0x00)
        size = 4
        
        self.set_counter_mode()
        self.latch(ch)
        return self.read(bar, offset, size)

    
    def get_comparator(self, ch=1):
        return self.comparator[ch]
    
        
    def get_status(self, ch):
        bar = 0
        offset = self._get_offset_for(ch, 0x05)
        size = 2
        
        d = self.read(bar, offset, size)
        return d
    
    
