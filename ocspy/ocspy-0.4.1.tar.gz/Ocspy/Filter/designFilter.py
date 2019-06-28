import copy

from ..Base.SignalInterface import Signal
from scipy.fftpack import fftfreq
from scipy.fftpack import fft
from scipy.fftpack import ifft
import numpy as np

class LowPassFilter(object):

    @staticmethod
    def inplace_ideal_lowpass(signal, pos_cutoff_frquence, neg_cutoff_frequence, fs_in_fiber=None):
        '''

        :param signal: in place filter
        :return:
        '''
        samples = LowPassFilter.ideal_lowpass(signal, pos_cutoff_frquence, neg_cutoff_frequence, fs_in_fiber)

        if fs_in_fiber is None:
            # means signal is an signal object

            pol_number = signal.pol_number
        else:
            # means signal is a ndarray
            pol_number = signal.shape[0]

        for i in range(pol_number):
            signal[i, :] = samples[i, :]
        # signal.data_sample[0, :] = sample_x
        # signal.data_sample[1, :] = sample_y
        return signal

    @staticmethod
    def ideal_lowpass(signal: Signal, pos_cutoff_frequence, neg_cutoff_frequence, fs_in_fiber=None):
        '''

        :param signal: the  sample will be returned, original sample of signal will not be changed
        :return:
        '''
        if fs_in_fiber is None:
            fs_in_fiber = signal.fs_in_fiber
            pol_number = signal.pol_number
            sample_number_in_fiber = signal.sample_number_in_fiber
        else:
            signal = np.atleast_2d(signal)
            sample_number_in_fiber = signal.shape[1]
            pol_number = signal.shape[0]

        samples = copy.deepcopy(signal[:])

        freq = fftfreq(sample_number_in_fiber, 1 / fs_in_fiber)

        # sample_x_fourier_transform = fft(sample_x)
        # sample_y_fourier_transform = fft(sample_y)
        fft_sample = fft(samples, axis=1)
        # 超过滤波器带宽的频率点直接设置为0
        for i in range(pol_number):
            fft_sample[i, freq > pos_cutoff_frequence] = 0
            fft_sample[i, freq < neg_cutoff_frequence] = 0
        # sample_x_fourier_transform[freq > pos_cutoff_frequence ] = 0
        # sample_x_fourier_transform[freq < neg_cutoff_frequence] = 0
        # sample_y_fourier_transform[abs(freq) > self.bw] = 0
        samples = ifft(fft_sample, axis=1)
        # sample_x = ifft(sample_x_fourier_transform)
        # sample_y = ifft(sample_y_fourier_transform)
        return samples


    @staticmethod
    def bessel_filter(signal:Signal):
        pass

