
import time
import struct
from . import core


ad_mode = {'single':64, 'diff':32}
inputrange_list = ['AD0_5V', 'AD0_10V', 'AD-2.5_2.5V', 'AD-5_5V', 'AD-10_10V']


class InvalidChError(Exception):
    pass

class InvalidModeError(Exception):
    pass

class InvalidInputrangeError(Exception):
    pass


class pci3177_driver(core.interface_driver):
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

    def _ch2list(self, ch=1):
        if ch == 0: return []
        else:
            bit_ch = bin(ch-1).replace('0b', '0' * (8 - (len(bin(ch - 1)) - 2)))
            bit_list = [bit_ch[i] for i in range(len(bit_ch))]
            bit_list.reverse()

            return bit_list

    def _verify_mode(self, mode):
        mode_list = list(ad_mode.keys())
        if mode in mode_list: pass
        else:
            msg = 'Mode must be single or diff,'
            msg += ' while {0} is given.'.format(mode)
            raise InvalidModeError(msg)
        return

    def _verify_ch(self, ch=1, mode='single'):
        if ch in [_ for _ in range(1, ad_mode['{}'.format(mode)] + 1)]: pass
        else:
            msg = 'Ch range is in ch1 -- ch{},'.format(ad_mode['{}'.format(mode)])
            msg += ' while ch{} is given.'.format(ch)
            raise InvalidChError(msg)
        return

    def _verify_mode(self, mode):
        mode_list = ['single', 'diff']
        if mode in mode_list: pass

    def _verify_inputrange(self, inputrange='DA-10_10V'):
        if inputrange in inputrange_list: pass
        else:
            msg = 'Inputrange is {0}.'.format(inputrange_list)
            raise InvalidInputrangeError(msg)
        return

    def _list2voltage(self, voltage_list, inputrange):
        voltage_range = float(inputrange.split('_')[-1].replace('V', ''))
        resolution = 12
        resolution_int = 2 ** resolution

        if inputrange[2] == '0':
            voltage_int = int.from_bytes(core.list2bytes(voltage_list), 'little')
            voltage = voltage_range / resolution_int * voltage_int

            return voltage

        else:
            voltage_int = int.from_bytes(core.list2bytes(voltage_list), 'little')
            voltage = -voltage_range + (voltage_range / (resolution_int / 2)) * voltage_int

            return voltage
        return

    def _is_busy(self):
        bar = 0
        size = 1
        offset = 0x03

        while not(self.read(bar, offset, size)[7]): pass
        return

    def _set_sampling_mode(self, mode='single'):
        bar = 0
        offset = 0x05

        if mode == 'single': mode = ''
        elif mode == 'diff': mode = 'SD0'

        flags = mode
        self.set_flag(bar, offset, flags)
        return

    def _start_sampling(self, ch=1):
        bar = 0
        size = 1
        offset = 0x04

        self.write(bar, offset, core.list2bytes(self._ch2list(ch)))
        time.sleep(60 * 10 ** (-6))
        self._is_busy()
        return

    def input_voltage(self, ch=1, mode='single', inputrange='AD-10_10V'):
        """電圧入力をします （Main Method）

        Parameters
        ----------
        ch : int
            取得する電圧入力のチャンネルを指定します（範囲: 1 -- 16）
        mode : str
            電圧入力方式を指定します
              - 'single'   のとき、シングルエンド入力
              - 'diff'     のとき、差動入力
        inputrange : str
            電圧入力レンジを指定します
              - 'DA0_5V'
              - 'DA0_10V'
              - 'DA-2.5_2.5V'
              - 'DA-5_5V'
              - 'DA-10_10V'（default）

        Returns
        -------
        float（単位 : V）
            指定したチャンネルの電圧入力の値

        Examples
        --------
        ch1 -- ch8 の電圧入力を取得します
        （差動入力、AD-5_5V）

        >>> [ad.input_voltage(_, 'diff', 'AD-5_5V') for _ in range(1, 9)]
        [-0.003662109375,
        -0.006103515625,
        -0.00244140625,
        0.0,
        0.0048828125,
        0.00244140625,
        -0.001220703125,
        0.0]
        """
        bar = 0
        size = 2
        offset = 0x00

        self._verify_mode(mode)
        self._verify_ch(ch, mode)
        self._verify_inputrange(inputrange)

        self._set_sampling_mode(mode)
        self._start_sampling(ch)
        voltage = self._list2voltage(self.read(bar, offset, size).to_list(), inputrange)

        if mode == 'single': pass
        elif mode == 'diff': voltage = voltage / 2

        return voltage
