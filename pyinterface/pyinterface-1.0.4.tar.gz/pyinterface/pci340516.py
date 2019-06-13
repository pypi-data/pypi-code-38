

import time
import struct
from . import core


ch_number = 8
outputrange_list = ['DA0_1mA', 'DA0_100mA']


class InvalidChError(Exception):
    pass

class InvalidCurrentError(Exception):
    pass

class InvalidOutputrangeError(Exception):
    pass

class InvalidOnoffError(Exception):
    pass


class pci340516_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'),
            ('B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15'),
            ('C0', 'C1', 'C2', 'C3', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('', '', '', '', '', '', '', ''),
            ('RG', '', '', '', '', '', '', ''),
            ('CH0', 'CH1', 'CH2', '', '', '', '', ''),
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
            ('RG', '', '', '', '', '', '', ''),
            ('CH0', 'CH1', 'CH2', '', '', '', '', ''),
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

    def _select_ch(self, ch=1):
        bar = 0
        offset = 0x07
        flags_list = self.bit_flags_out[bar][offset]

        ch = self._ch2list(ch)[0:3]
        flags_list = [j + ' ' for i, j in zip(ch, flags_list) if i == '1']
        flags = ''.join(map(str, flags_list))[:-1]

        self.set_flag(bar, offset, flags)
        time.sleep(1 * 10 ** (-2))
        return

    def _ch2list(self, ch=1):
        if ch == 0: return []
        else:
            bit_ch = bin(ch-1).replace('0b', '0' * (8 - (len(bin(ch - 1)) - 2)))
            bit_list = [bit_ch[i] for i in range(len(bit_ch))]
            bit_list.reverse()

            return bit_list

    def _current2list(self, current=0., outputrange='DA0_100mA'):
        if outputrange == outputrange_list[0]: current_outputrange = 1.
        elif outputrange == outputrange_list[1]: current_outputrange =100.
        resolution = 16
        resolution_int = 2**resolution

        if current == current_outputrange: bytes_current = int(resolution_int - 1)
        else: bytes_current = int(resolution_int * current / current_outputrange)

        bit = bin(bytes_current).replace('0b', '0'*(16-(len(bin(bytes_current))-2)))
        bit_list = [int(bit[i]) for i in range(len(bit))]
        bit_list.reverse()

        return bit_list

    def _verify_onoff(self, onoff=0):
        if onoff in [0, 1]: pass
        else:
            msg = 'Onoff is 0 or 1, while onoff is given {}.'.format(onoff)
            raise InvalidOnoffError(msg)
        return

    def _verify_ch(self, ch=1):
        if ch in range(1, ch_number + 1): pass
        else:
            msg = 'Ch range is in ch1-ch{},'.format(ch_number)
            msg += ' while ch{} is given.'.format(ch)
            raise InvalidChError(msg)
        return

    def _verify_outputrange(self, outputrange='DA0_100mA'):
        if outputrange in outputrange_list: pass
        else:
            msg = 'Outputrange is {0} or {1}.'.format(*outputrange_list)
            msg = 'Outputrange is {0} or {1}'.format(*outputrange_list)
            raise InvalidOutputrangeError(msg)
        return

    def _verify_current(self, current=0., outputrange='DA0_100mA'):
        if outputrange == outputrange_list[0]:
            if 0. <= current <= 1.: pass
            else:
                msg = 'Output range is {},'.format(outputrange)
                msg += ' while {}mA is given.'.format(current)
                raise InvalidCurrentError(msg)
        elif outputrange == outputrange_list[1]:
            if 0. <= current <= 100.: pass
            else:
                msg = 'Output range is {},'.format(outputrange)
                msg += ' while {}mA is given.'.format(current)
                raise InvalidCurrentError(msg)
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


    def get_outputrange(self, ch=1):
        """電流出力レンジを取得します

        Parameters
        ----------
        ch : int
            取得する電流出力レンジのチャンネルを指定します（範囲: 1 -- 8）

        Returns
        -------
        dict
            指定したチャンネルと電流出力レンジのディクショナリ

        Examples
        --------

        >>> da.get_outputrange()
        {'ch1': 'DA0_100mA'}
        """
        bar = 0
        size = 1
        offset = 0x06

        self._verify_ch(ch)
        self._select_ch(ch)
        status = self.read(bar, offset, size)

        return {'ch{}'.format(ch):outputrange_list[status.to_int()]}


    def set_outputrange(self, ch=1, outputrange='DA0_100mA'):
        """電流出力レンジを設定します

        Parameters
        ----------
        ch : int
            取得する電流出力レンジのチャンネルを指定します（範囲: 1 -- 8）
        outputrange : str
            設定する電流出力レンジを指定します
              - 'DA0_1mA'
              - 'DA0_100mA' (default)
        """
        bar = 0
        offset = 0x06
        flags_list = self.bit_flags_out[bar][offset]

        self._verify_ch(ch)
        self._verify_outputrange(outputrange)
        flags = flags_list[not(outputrange_list.index(outputrange))]

        self._select_ch(ch)
        self.set_flag(bar, offset, flags)
        return


    def get_onoff(self, ch=1):
        """電流出力 接続/遮断を取得します

        Parameters
        ----------
        ch : int
            取得する電流出力 接続/遮断のチャンネルを指定します（範囲: 1 -- 8）

        Returns
        -------
        dict
            指定したチャンネルと電流出力 接続（1）/遮断（0）のディクショナリ

        Examples
        --------

        >>> da.get_onoff()
        {'ch1': 0}
        """
        bar = 0
        size = 1
        offset = 0x1b

        self._verify_ch(ch)
        status = self.read(bar, offset, size)

        return {'ch{}'.format(ch):status.to_list()[ch-1]}


    def set_onoff(self, ch=1, onoff=0):
        """電流出力 接続/遮断を設定します

        Prameters
        ---------
        ch : int
            取得する電流出力 接続/遮断のチャンネルを指定します（範囲: 1 -- 8）
        onoff : int
            0（遮断） or 1（接続）
            設定する電流出力 接続/遮断を指定します
        """
        bar = 0
        size = 1
        offset = 0x1b
        current_onoff = self.read(bar, offset, size).to_list()

        self._verify_ch(ch)
        self._verify_onoff(onoff)

        def calbit(a, b):
            return (not(a) and b) or (a and b)

        change_onoff = current_onoff.copy()
        change_onoff[ch-1] = onoff
        target_onoff = [calbit(i, j) for i, j in zip(current_onoff, change_onoff)]
        self.write(bar, offset, core.list2bytes(target_onoff))
        time.sleep(1 * 10 ** (-2))
        return


    def output_current(self, ch=1, current=0.):
        """電流出力をします （Main Method）

        Prameters
        ---------
        ch : int
            取得する電流出力 接続/遮断のチャンネルを指定します（範囲: 1 -- 8）
        current : float
            出力する電流の値を指定します
              - 'DA0_1mA'   のとき、0. -- 1.
              - 'DA0_100mA' のとき、0. -- 100.
        """
        bar = 0
        offset_ch = 0x02
        offset_current = 0x00

        self._verify_ch(ch)
        outputrange = self.get_outputrange(ch)['ch{}'.format(ch)]
        self._verify_outputrange(outputrange)
        self.set_outputrange(ch, outputrange)
        self._verify_current(current, outputrange)

        self._set_sampling_config('all_output_disable')
        self.set_onoff(ch, 1)
        self.write(bar, offset_ch, core.list2bytes(self._ch2list(ch)))
        self.write(bar, offset_current, core.list2bytes(self._current2list(current, outputrange)))
        self._set_sampling_config('all_output')

        print('[OUTPUT INFO] CH:{ch} Range:{outputrange} Current:{current}mA'.format(**locals()))
        return


    def finalize(self):
        """電流出力を全チャンネル遮断します
        None
        """
        [self.set_onoff(_, 0) for _ in range(1, ch_number + 1)]
        return
