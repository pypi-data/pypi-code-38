from scipy.signal import convolve, fftconvolve, resample_poly
from scipy.signal import resample
import numpy as np

import numpy as np
import numba


class Quantization(object):

    def __init__(self, clipping_ratio, resolution_bits):
        self.clipping_ratio = clipping_ratio
        self.resolution_bits = resolution_bits

    def __call__(self,signal):
        for i in range(signal.pol_number):
            ibranch = quantization(signal[i, :].real, self.clipping_ratio, self.resolution_bits)
            qbranch = quantization(signal[i, :].imag, self.clipping_ratio, self.resolution_bits)
            signal[i, :] = ibranch + 1j * qbranch
        return signal


def quantization(samples, clipping_ratio, resolution_bits):
    power = np.mean(samples.real ** 2 + samples.imag ** 2)
    A = 10 ** (clipping_ratio / 20) * np.sqrt(power)

    codebook = np.linspace(-A, A, 2 ** resolution_bits, endpoint=True)
    partition = codebook - (codebook[1] - codebook[0]) / 2
    partition = partition[1:]

    _, samples_quan = quantize(samples, partition, codebook)
    #     print(np.array(_))
    return samples_quan


@numba.jit(cache=True)
def quantize(signal, partitions, codebook):
    signal = np.atleast_2d(signal)
    assert signal.shape[0] == 1
    quanta = np.zeros_like(signal, dtype=np.float64)
    indices = np.zeros((1, len(signal[0, :])), dtype=np.int)
    cnt = 0
    for datum in signal[0, :]:
        index = 0
        while index < len(partitions) and datum > partitions[index]:
            index += 1
        indices[0, cnt] = index
        quanta[0, cnt] = codebook[index]
        cnt = cnt + 1
    return indices, quanta


class ADC(object):

    def __call__(self, signal):

        from resampy import resample
        tempx = resample(signal[0], signal.sps_in_fiber, signal.sps, filter='kaiser_fast')
        tempy = resample(signal[1], signal.sps_in_fiber, signal.sps, filter='kaiser_fast')
        new_sample = np.array([tempx, tempy])
        signal.data_sample_in_fiber = new_sample
        signal.sps_in_fiber = signal.sps
        return signal


class DAC(object):

    def __call__(self, signal):

        from resampy import resample
        tempx = resample(signal.data_sample, signal.sps, signal.sps_in_fiber, axis=1, filter='kaiser_fast')
        signal.data_sample_in_fiber = tempx



class PulseShaping(object):
    '''
        Perform Pluse Shaping. need a dict to construct, the construct should contain:
            key:pulse_shaping
                span
                sps
                alpha

    '''

    def __init__(self, **kwargs):
        self.kind = kwargs['kind']
        self.span = kwargs['span']
        self.sps = kwargs['sps']
        self.alpha = kwargs['alpha']
        assert divmod(self.span * self.sps, 2)[1] == 0
        self.number_of_sample = self.span * self.sps
        self.delay = self.span / 2 * self.sps

        self.filter_tap = self.__design_filter()

    def __design_filter(self):
        if self.kind == 'rrc':
            h = PulseShaping.rcosdesign(
                self.number_of_sample, self.alpha, 1, self.sps)
            return np.atleast_2d(h)

        if self.kind == 'rc':
            print(
                'error, why do you want to design rc filter,the practical use should be two rrc filters,on in transimit'
                'side,and one in receiver side, rrc filter will be designed')

    @staticmethod
    def rcosdesign(N, alpha, Ts, Fs):
        """
        Generates a root raised cosine (RRC) filter (FIR) impulse response.
        Parameters
        ----------
        N : int
            Length of the filter in samples.
        alpha : float
            Roll off factor (Valid values are [0, 1]).
        Ts : float
            Symbol period in seconds.
        Fs : float
            Sampling Rate in Hz.
        Returns
        ---------
        time_idx : 1-D ndarray of floats
            Array containing the time indices, in seconds, for
            the impulse response.
        h_rrc : 1-D ndarray of floats
            Impulse response of the root raised cosine filter.
        """

        T_delta = 1 / float(Fs)

        sample_num = np.arange(N + 1)
        h_rrc = np.zeros(N + 1, dtype=float)

        for x in sample_num:
            t = (x - N / 2) * T_delta
            if t == 0.0:
                h_rrc[x] = 1.0 - alpha + (4 * alpha / np.pi)
            elif alpha != 0 and t == Ts / (4 * alpha):
                h_rrc[x] = (alpha / np.sqrt(2)) * (((1 + 2 / np.pi) *
                                                    (np.sin(np.pi / (4 * alpha)))) + (
                                                           (1 - 2 / np.pi) * (np.cos(np.pi / (4 * alpha)))))
            elif alpha != 0 and t == -Ts / (4 * alpha):
                h_rrc[x] = (alpha / np.sqrt(2)) * (((1 + 2 / np.pi) *
                                                    (np.sin(np.pi / (4 * alpha)))) + (
                                                           (1 - 2 / np.pi) * (np.cos(np.pi / (4 * alpha)))))
            else:
                h_rrc[x] = (np.sin(np.pi * t * (1 - alpha) / Ts) +
                            4 * alpha * (t / Ts) * np.cos(np.pi * t * (1 + alpha) / Ts)) / \
                           (np.pi * t * (1 - (4 * alpha * t / Ts)
                                         * (4 * alpha * t / Ts)) / Ts)

        return h_rrc / np.sqrt(np.sum(h_rrc * h_rrc))

    def rrcfilter(self, signal_interface):
        '''

        :param signal_interface: signal object to be pulse shaping,because a reference of signal object is passed
        so the filter is in place
        :return: None

        '''

        # print("---begin pulseshaping ---,the data sample will be set")
        # upsample by insert zeros

        signal_interface.data_sample = np.zeros(
            (signal_interface.symbol.shape[0], signal_interface.sps * signal_interface.symbol_length))
        signal_interface.data_sample = np.asarray(
            signal_interface.data_sample, dtype=np.complex)
        for i in range(signal_interface.symbol.shape[0]):
            signal_interface.data_sample[i, :] = signal_interface.upsample(signal_interface.symbol[i, :],
                                                                           signal_interface.sps)[0, :]

        temp = []
        for i in range(signal_interface.data_sample.shape[0]):
            temp.append(
                fftconvolve(signal_interface.data_sample[i, :], self.filter_tap[0, :], mode='full'))

        # tempy = convolve(self.filter_tap[0, :], signal_interface.data_sample[1, :])
        # temp_signal = np.array([tempx, tempy])
        temp_signal = np.array(temp)
        # compensate group delay
        temp_signal = np.roll(temp_signal, -int(self.delay), axis=1)

        signal_interface.data_sample = temp_signal[:,
                                       :signal_interface.sps * signal_interface.symbol_length]

    def __call__(self, signal):
        self.rrcfilter(signal)


class AWG(object):

    def __init__(self, sps=2, alpha=0.02, span=1024):
        '''

        :param sps: pulse shaping parameters
        :param alpha: reference of the signal object,change signal_interface's property will change all
        :param span

        This function will be used to pulse shaping, the sps is default to 2, it should correspond to signal's sps, then
        the siganl will be resampled to sps_in_fiber automatically

        '''

        # self.signal_interface = signal_interface
        self.roll_off = alpha
        self.span = span
        self.pulse_shaping_filter = PulseShaping(
            kind='rrc', alpha=alpha, sps=sps, span=span)
        self.dac = DAC()

    def __call__(self, signal_interface):
        self.pulse_shaping_filter.rrcfilter(signal_interface)

        self.dac(signal_interface)
        return signal_interface

    def __str__(self):
        string = f"the pulse shaping filter: roll_off:{self.pulse_shaping_filter.alpha}," \
            f" the sps of pulse shaping filter : {self.signal_interface.sps},  the adc sample per symbol: {self.signal_interface.sps_in_fiber} "

        return string

    def __repr__(self):
        return self.__str__()
