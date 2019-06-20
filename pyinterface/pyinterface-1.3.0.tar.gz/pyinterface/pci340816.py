

import time
import struct
from . import core

 
ch_number = 16


class InvalidChError(Exception):
    pass

class InvalidVoltageError(Exception):
    pass


class pci340816_driver(core.interface_driver):
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
            ('AO', '', '', '', '', '', '', ''),
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
            ('AO', '', '', '', '', '', '', ''),
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

    def _select_ch(self, ch=1):
        bar = 0
        offset = 0x02
        flags_list = self.bit_flags_out[0][offset]

        ch = self._ch2list(ch)[0:4]
        flags_list = [j + ' ' for i, j in zip(ch, flags_list) if i == '1']
        flags = ''.join(map(str, flags_list))[:-1]

        self.set_flag(bar, offset, flags)
        time.sleep(1 * 10 ** (-2))
        return flags

    def _ch2list(self, ch=1):
        if ch == 0: return []
        else:
            bit_ch = bin(ch-1).replace('0b', '0' * (8 - (len(bin(ch - 1)) - 2)))
            bit_list = [bit_ch[i] for i in range(len(bit_ch))]
            bit_list.reverse()

            return bit_list

    def _voltage2list(self, voltage=0.0):
        voltage_outputrange = 10.
        resolution = 16
        resolution_int = 2 ** resolution

        if voltage == voltage_outputrange: bytes_voltage = int(resolution_int - 1)
        else: bytes_voltage = int((voltage + voltage_outputrange) / (voltage_outputrange / (resolution_int / 2)))

        bit = bin(bytes_voltage).replace('0b', '0' * (16 - (len(bin(bytes_voltage)) - 2)))
        bit_list = [int(bit[i]) for i in range(len(bit))]
        bit_list.reverse()

        return bit_list

    def _verify_ch(self, ch=1):
        if ch in range(1, ch_number + 1): pass
        else:
            msg = 'Ch range is in ch1-ch{},'.format(ch_number)
            msg += ' while ch{} is given.'.format(ch)
            raise InvalidChError(msg)
        return

    def _verify_voltage(self, voltage=0.):
        if -10. <= voltage <= 10.: pass
        else:
            msg = 'Output range is -10V -- 10V,'
            msg += ' while {}V is given.'.format(voltage)
            raise InvalidVoltageError(msg)
        return

    def _set_sampling_config(self, config=''):
        bar = 0
        offset = 0x05

        if config == 'all_output_disable': config = ''
        elif config == 'all_output': config = 'MD0'
        elif config == 'all_output_clear': config = 'MD1'
        elif config == 'all_output_enable': config = 'MD0 MD1'

        flags = config
        self.set_flag(bar, offset, flags)
        return

    def _set_onoff(self, onoff=1):
        bar = 0
        offset = 0x1b
        flags_list = self.bit_flags_out[bar][offset]

        flags = flags_list[not(onoff)]

        self.set_flag(bar, offset, flags)
        time.sleep(1 * 10 ** (-2))
        return flags


    def output_voltage(self, ch=1, voltage=0.):
        """電圧出力をします （Main Method）

        Prameters
        ---------
        ch : int
            取得する電流出力 接続/遮断のチャンネルを指定します（範囲: 1 -- 16）
        voltage : float
            出力する電流の値を指定します（範囲: -10. -- 10.）
        """
        bar = 0
        offset = 0x00

        self._verify_ch(ch)
        self._verify_voltage(voltage)

        self._set_sampling_config('all_output_disable')
        self._set_onoff(onoff=1)
        self._select_ch(ch)
        self.write(bar, offset, core.list2bytes(self._voltage2list(voltage)))

        print('[OUTPUT INFO] CH:{ch} Voltage:{voltage:.2f}V'.format(**locals()))
        return


    def finalize(self):
        """電圧出力を全チャンネル遮断します
        None
        """
        self._set_sampling_config('all_output_clear')
        return
