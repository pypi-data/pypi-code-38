import copy

import numpy as np
from scipy.io import loadmat
from scipy.constants import c
from typing import List
from ..tool.tool import freq2lamb
import os

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Signal(object):
    '''
        Signal:
            This Signal is the base class for single carrier signal, the QamSignal inherit this class:
            the property of Signal:
                1. symbol_rate: GHZ
                2. mf: the modulation format
                3. symbol_length: the length of symbol
                4. signal_power: the launch power of signal,the waveform will be set to this signal,when the signal pass
                laser object
                5. sps: the sample per symbol for dsp
                6. sps in fiber： the sample per symbol for waveform in fiber,because of nonlinear effect of fiber, the sample
                rate shuould greater than 2 time highest frequence of signal.
                7.lam: the wavelength of the signal: [nm]

            @property

    '''

    def __init__(self, **kwargs):
        '''

        :param kwargs: 包含单信道信号的各项参数，包括：
            1. symbol_rate 符号速率 【Hz】
            2. mf 调制格式
            3. symbol length 符号长度
            4. signal_power  信号功率  【dbm】
            5. sps：         发端dsp的采样率
            6. sps_in_fiber: 光纤中采样率
            8. center_frequence: Hz

        property:
            symbol:  the symbol to be sent, can only be accessed but can not be set


        所有单位全部使用国际标准单位

        '''

        self._symbol = None
        self.symbol_rate = kwargs['symbol_rate']
        self.mf = kwargs['mf']
        self.symbol_length = kwargs['symbol_length']
        self.sps_in_fiber = kwargs['sps_in_fiber']
        self.sps = kwargs['sps']
        self.decision_symbol = None
        self.data_sample = None
        self.data_sample_in_fiber = None
        self.center_frequence = kwargs['frequence']

    @property
    def symbol(self):
        return self._symbol

    def inplace_set_signal_power(self,power,unit='dbm'):
        if unit =='dbm':
            pass
        else:
            power = power/10
            power = 10**power
            power = power/1000
        each_pol_power = power/self.pol_number
        self[:] = np.sqrt(each_pol_power)*self[:]

    def set_signal_power(self, power, unit="dbm"):
        if unit == 'dbm':
            power_lin = power / 10
            power_lin = 10 ** power_lin
            power_lin = power_lin / 1000
        else:
            power_lin = power
        self.inplace_normalize_power()
        for i in range(self.pol_number):
            self[i, :] = self[i, :] * np.sqrt(power_lin / self.pol_number)

    @property
    def sample_number_in_fiber(self):
        import warnings
        if self.sps_in_fiber * self.symbol_length != self.data_sample_in_fiber.shape[1]:
            warnings.warn(
                "the sps_in_fiber * symbol length not equal the sample number stored in sample_number_fiber")
            return self.data_sample_in_fiber.shape[1]

        return int(self.sps_in_fiber * self.symbol_length)

    @property
    def sample_number(self):
        return self.sps * self.symbol_length

    @property
    def center_wave_length(self):

        return c / self.center_frequence

    def tonumpy(self):
        '''

        :return: reference to self.data_sample_in_fiber
        if function not return a new ndarrya
        change it outside will change the data_sample_in_fiber property of the object
        '''
        data_sample_in_fiber = copy.deepcopy(self.data_sample_in_fiber)
        return data_sample_in_fiber

    def __getitem__(self, index):
        '''

        :param index: Slice Object
        :return: ndarray of the signal, change this ndarray will change the object

        '''
        assert self.data_sample_in_fiber is not None

        return self.data_sample_in_fiber[index]

    def __setitem__(self, index, value):
        '''

        :param   index: slice Object
        :param   value: the value that to be set,must be ndarray
        :return: None
        '''
        if self.data_sample_in_fiber is None:
            self.data_sample_in_fiber = np.atleast_2d(value)
        else:

            self.data_sample_in_fiber[index] = value

    def measure_power_in_fiber(self, unit='w'):
        '''

        :return: signal power in the fiber, in unit [W]
        '''
        sample_in_fiber = np.atleast_2d(self.data_sample_in_fiber)
        signal_power = 0
        for i in range(sample_in_fiber.shape[0]):
            signal_power += np.mean(np.abs(sample_in_fiber[i, :]) ** 2)
        if unit == "w":
            return signal_power
        else:
            return 10 * np.log10(signal_power * 1000)

    @property
    def fs(self):
        if self.sps is None:
            return 0
        return self.symbol_rate * self.sps

    @property
    def fs_in_fiber(self):
        return self.symbol_rate * self.sps_in_fiber

    def inplace_normalize_power(self):
        '''
            in place operation
        :return:
        '''
        self[:] = self.normalize_power()

    def remove_dc(self):
        for i in range(self.pol_number):
            self[i, :] = self[i, :] - np.mean(self[i, :])

    @property
    def pol_number(self):
        return self.data_sample_in_fiber.shape[0]

    def inplace_normalize_dsp_sample(self):
        temp = self.normalize_dsp_sample()
        self.data_sample = temp

    def normalize_dsp_sample(self):
        temp = np.zeros_like(self.data_sample)
        for i in range(self.pol_number):
            temp[i, :] = self.data_sample[i, :] / \
                np.sqrt(np.mean(np.abs(self.data_sample[i, :]) ** 2))
        return temp

    def normalize_power(self):
        '''

        new ndarray will be returned , the signal object itself is not changed
        :param signal:
        :return: ndarray and signal object will not be changed

        '''
        temp = np.zeros_like(self.data_sample_in_fiber)
        for i in range(self.data_sample_in_fiber.shape[0]):
            temp[i, :] = self.data_sample_in_fiber[i, :] / np.sqrt(
                np.mean(np.abs(self.data_sample_in_fiber[i, :]) ** 2))

        return temp

    def upsample(self, symbol_x, sps):
        '''

        :param symbol_x: 1d array
        :param sps: sample per symbol
        :return: 2-d array after inserting zeroes between symbols
        '''
        assert symbol_x.ndim == 1
        symbol_x.shape = -1, 1
        symbol_x = np.tile(symbol_x, (1, sps))
        symbol_x[:, 1:] = 0
        symbol_x.shape = 1, -1
        return symbol_x

    def __str__(self):
        try:
            string = f'\n\tSymbol rate:{self.symbol_rate / 1e9}[Ghz]\n\tfs_in_fiber:{self.fs_in_fiber / 1e9}[Ghz]\n\t' \
                f'signal_power_in_fiber:{self.measure_power_in_fiber()} [W]\n\t' \
                f'signal_power_in_fiber:{self.measure_power_in_fiber("dbm")} [dbm]\n\t' \
                f'wave_length is {self.center_wave_length * 1e9} [nm]\n\t' \
                f'center_frequence is {self.center_frequence * 1e-12}[Thz]\n\t'

        except Exception as e:
            string = f'\n\tSymbol rate:{self.symbol_rate / 1e9}[Ghz]\n\tfs_in_fiber:{self.fs_in_fiber / 1e9}[Ghz]\n\t' \
                f'wave_length is {self.center_wave_length * 1e9} [nm]\n\t' \
                f'center_frequence is {self.center_frequence * 1e-12}[Thz]\n\t'
        return string

    def __repr__(self):

        return self.__str__()

    @property
    def shape(self):
        return self.data_sample_in_fiber.shape


class SignalFromNumpyArray(Signal):

    def __init__(self, array_sample, symbol_rate, mf, symbol_length, sps_in_fiber, sps, **kwargs):
        '''

        :param array_sample: nd arrary
        :param symbol_rate: [Hz]
        :param mf: modulation format
        :param symbol_length: the length of transimitted symbol
        :param sps_in_fiber: the samples per symbol in fiber
        :param sps: the sampes per symbol in DSP

        This function will read samples from array_sample, the array_sample should be propogated in fiber

        The center frequence is the center frequence, and the absolute frequence is from left to right in wdm comb

        The relative frequence i.e base band equivalent is set a property
        '''
        super(SignalFromNumpyArray, self).__init__(
            **dict(symbol_rate=symbol_rate, mf=mf, symbol_length=symbol_length, sps_in_fiber=sps_in_fiber, sps=sps))
        self.data_sample_in_fiber = array_sample

        if 'tx_symbol' in kwargs:
            self.tx_symbol = kwargs['tx_symbol']
        if 'rx_symbol' in kwargs:
            self.rx_symbol = kwargs['rx_symbol']

        if 'center_frequence' in kwargs:
            self.center_frequence = kwargs['center_frequence']

        if 'aboslute_frequence' in kwargs:
            self.absolute_frequence = kwargs['absolute_frequence']

    @property
    def relative_frequence(self):
        if hasattr(self, 'center_frequence') and hasattr(self, 'absolute_frequence'):
            return self.absolute_frequence - self.center_frequence
        else:
            raise Exception(
                'The frequence not provided enough, please ensure the center_frequency and the absolute_frequenc are all provided')


class WdmSignal(object):
    '''
        WdmSignal Class
    '''

    def __init__(self, signals: List[Signal], grid_size, multiplexed_filed):
        '''

        :param signals: list of signal
        :param grid_size: [Hz],if conventional grid_size,this will be a number or a list of same value
        if the elestical wdm, the grid size of each channel is different.
        :param center_frequence: Hz

        The WdmSignal class should not be used outside usually, in mux function, it will be created automatically.

        '''
        self.signals = signals
        self.grid_size = grid_size
        self.center_frequence = (
            np.min(self.absolute_frequences) + np.max(self.absolute_frequences)) / 2
        self.center_wave_length = freq2lamb(self.center_frequence)
        self.__multiplexed_filed = np.atleast_2d(multiplexed_filed)

    def __setitem__(self, slice, value):

        assert self.__multiplexed_filed is not None
        self.__multiplexed_filed[slice] = value

    def __getitem__(self, slice):
        assert self.__multiplexed_filed is not None
        return self.__multiplexed_filed[slice]

    # @property
    # def center_frequence(self):
    #     frequences = self.absolute_frequences()
    #     return (np.max(frequences)+np.min(frequences))/2

    @property
    def pol_number(self):
        return self.__multiplexed_filed.shape[0]

    @property
    def shape(self):
        return self.__multiplexed_filed.shape

    @property
    def fs_in_fiber(self):
        return self.signals[0].fs_in_fiber

    @property
    def sample_number_in_fiber(self):
        return self.__multiplexed_filed.shape[1]

    @property
    def lam(self):
        lambdas = []
        for signal in self.signals:
            lambdas.append(signal.center_wave_length)
        return lambdas

    @property
    def data_sample_in_fiber(self):
        return self.__multiplexed_filed

    @data_sample_in_fiber.setter
    def data_sample_in_fiber(self, value):
        self.__multiplexed_filed = value

    @property
    def mfs(self):
        mfs = []
        for sig in self.signals:
            mfs.append(sig.mf)
        return mfs

    @property
    def absolute_frequences(self):
        '''

        :return:
        '''
        return np.array([signal.center_frequence for signal in self.signals])

    @property
    def relative_frequences(self):
        '''

        :return: frequences centered in zero frequence , an ndarray
        '''
        return self.absolute_frequences - self.center_frequence

    def __str__(self):

        string = f"center_frequence is {self.center_frequence * 1e-12} [THZ]\t\n" \
            f"power is {self.measure_power_in_fiber()} [dbm] \t\n" \
            f"power is {self.measure_power_in_fiber(unit='w')} [w]\t\n"

        return string

    def measure_power_in_fiber(self, unit='dbm'):

        power = 0
        for i in range(self.pol_number):
            power += np.mean(np.abs(self[i, :]) ** 2)

        if unit == 'dbm':
            power = power * 1000
            power = 10 * np.log10(power)

        return power

class WdmSignalFromArray(object):

    def __init__(self,field,frequencys,fs_in_fiber,signal_under_study,signal_index):
        '''

        :param field:   WDM multiplexed fiedl
        :param center_freq: Hz will be caculated from frequencys
        :param frequencys: Hz each channel's frequencys, the passband frequence
        :param fs_in_fiber: Hz
        '''
        self.__filed = field
        self.fs_in_fiber = fs_in_fiber
        self.frequences = frequencys
        self.center_frequence = np.mean([np.max(frequencys),np.min(frequencys)])
        self.center_wave_length = freq2lamb(self.center_frequence) #m
        self.signal_under_study = signal_under_study
        self.signal_index = signal_index

    def __setitem__(self, slice, value):

        assert self.__filed is not None
        self.__filed[slice] = value

    def __getitem__(self, slice):

        assert self.__filed is not None
        return self.__filed[slice]

    @property
    def pol_number(self):
        return self.__filed.shape[0]

    @property
    def shape(self):
        return self.__filed.shape

    @property
    def sample_number_in_fiber(self):
        return self.__filed.shape[1]

    @property
    def lam(self):
        lambdas = []
        for freq in self.frequences:
            lambdas.append(freq2lamb(freq))
        return lambdas

    @property
    def data_sample_in_fiber(self):
        return self.__filed

    @data_sample_in_fiber.setter
    def data_sample_in_fiber(self, value):
        self.__filed = value

    @property
    def absolute_frequences(self):
        '''

        :return:
        '''
        return self.frequences

    @property
    def relative_frequences(self):
        '''

        :return: frequences centered in zero frequence , an ndarray
        '''
        return self.absolute_frequences - self.center_frequence

    def __str__(self):

        string = f"center_frequence is {self.center_frequence * 1e-12} [THZ]\t\n" \
            f"power is {self.measure_power_in_fiber()} [dbm] \t\n" \
            f"power is {self.measure_power_in_fiber(unit='w')} [w]\t\n"

        return string

    def measure_power_in_fiber(self, unit='dbm'):

        power = 0
        for i in range(self.pol_number):
            power += np.mean(np.abs(self[i, :]) ** 2)

        if unit == 'dbm':
            power = power * 1000 # convert to mw
            power = 10 * np.log10(power)

        return power

class QamSignal(Signal):

    def __init__(self, symbol_rate=35e9, mf="16-qam", symbol_length=2 ** 16, sps=2, sps_in_fiber=4,
                 is_dp=True, frequence=193.1e12, is_from_array=False, is_from_demux=False):
        '''

        :param symbol_rate: [hz]   符号速率
        :param mf: 调制格式,16-qam,32-qam,64-qam,qpsk
        :param signal_power: [dbm] 信号功率
        :param symbol_length:      符号长度
        :param sps: 发端dsp的过采样率
        :param sps_infiber: 在光纤中传输时的过采样率
        '''

        super().__init__(
            **dict(symbol_length=symbol_length, symbol_rate=symbol_rate, mf=mf, sps=sps,
                   sps_in_fiber=sps_in_fiber, frequence=frequence)
        )
        self.is_from_demux = is_from_demux
        if self.mf == 'qpsk':
            order = 4
        else:
            order = self.mf.split('-')[0]
            order = int(order)
        if not is_from_array and not self.is_from_demux:
            if is_dp:

                self.message = np.random.randint(
                    low=0, high=order, size=(2, self.symbol_length))
            else:
                self.message = np.random.randint(
                    low=0, high=order, size=(1, self.symbol_length))

            self.is_dp = is_dp
            # self.symbol = None

            self.init(order)

    def init(self, order):

        qam_data = (f'{base_path}/' + 'qamdata/' + str(order) + 'qam.mat')
        qam_data = loadmat(qam_data)['x']

        symbol = np.zeros(self.message.shape, dtype=np.complex)
        symbol = np.atleast_2d(symbol)
        for i in range(symbol.shape[0]):
            for msg in np.unique(self.message[i, :]):
                symbol[i, self.message[i, :] == msg] = qam_data[0, msg]

        self._symbol = symbol

