import copy
import os

import numba
import numpy as np
from numba import prange
from scipy.fftpack import fft, ifft, fftfreq
from scipy.io import loadmat
from scipy.signal import correlate, lfilter
from scipy.signal import fftconvolve

from .dsp_tools import cal_scaling_factor_qam
from .dsp_tools import cal_symbols_qam
from .dsp_tools import decision
from .dsp_tools import segment_axis
from .dsp_tools import exp_decision
from ..Base.SignalInterface import Signal
from ..Instrument.ElectricInstrument import PulseShaping


class MatchedFilter(object):

    def __init__(self, roll_off=0.02, span=1024, sps=4):
        self.h = PulseShaping.rcosdesign(int(span * sps), roll_off, 1, int(sps))
        self.delay = int(span / 2 * sps)

    def match_filter(self, signal):
        x = signal.data_sample_in_fiber[0, :]
        y = signal.data_sample_in_fiber[1, :]
        x = fftconvolve(x, self.h)
        y = fftconvolve(y, self.h)

        x = np.roll(x, -self.delay)
        y = np.roll(y, -self.delay)
        x = x[:signal.sample_number_in_fiber]
        y = y[:signal.sample_number_in_fiber]
        return x, y

    def inplace_match_filter(self, signal):
        x, y = self.match_filter(signal)
        signal.data_sample_in_fiber = np.array([x, y])
        return signal

    def __call__(self, signal):
        self.inplace_match_filter(signal)

        return signal


def syncsignal(symbol_tx, sample_rx, sps):
    '''

        :param symbol_tx: 发送符号
        :param sample_rx: 接收符号，会相对于发送符号而言存在滞后
        :param sps: samples per symbol
        :return: 收端符号移位之后的结果

        # 不会改变原信号

    '''
    assert sample_rx.ndim == 1
    assert symbol_tx.ndim == 1
    assert len(sample_rx) >= len(symbol_tx)
    symbol_tx = np.atleast_2d(symbol_tx)[0, :]
    sample_rx = np.atleast_2d(sample_rx)[0, :]

    res = correlate(sample_rx[::sps], symbol_tx)

    index = np.argmax(np.abs(res))

    out = np.roll(sample_rx, sps * (-index - 1 + symbol_tx.shape[0]))
    return out


def cd_compensation(signal: Signal, spans, inplace=False):
    '''

    This function is used for chromatic dispersion compensation in frequency domain.
    The signal is Signal object, and a new sample is created from property data_sample_in_fiber

    :param signal: Signal object
    :param spans: Span object, the signal's has propagated through these spans
    :param inplace: if True, the compensated sample will replace the original sample in signal,or new ndarray will be r
    eturned

    :return: if inplace is True, the signal object will be returned; if false the ndarray will be returned
    '''
    try:
        import cupy as np
    except Exception:
        import numpy as np


    center_wavelength = signal.center_wave_length
    freq_vector = fftfreq(signal[0, :].shape[0], 1 / signal.fs_in_fiber)
    omeg_vector = 2 * np.pi * freq_vector

    sample = np.array(signal[:])

    if not isinstance(spans, list):
        spans = [spans]

    for span in spans:
        beta2 = -span.beta2(center_wavelength)
        dispersion = (-1j / 2) * beta2 * omeg_vector ** 2 * span.length
        dispersion = np.array(dispersion)
        for pol_index in range(sample.shape[0]):
            sample[pol_index, :] = np.fft.ifft(np.fft.fft(sample[pol_index, :]) * np.exp(dispersion))

    if inplace:
        if hasattr(np,'asnumpy'):
            sample = np.asnumpy(sample)
        signal[:] = sample
        return signal
    else:
        if hasattr(np,'asnumpy'):
            sample = np.asnumpy(sample)
        signal = copy.deepcopy(signal)
        signal[:] = sample
        return signal


#     return const[np.argmin(distance)]
def superscalar(symbol_in, training_symbol, block_length, pilot_number, constl, g,filter_n=20):
    # delete symbols to assure the symbol can be divided into adjecent channels
    symbol_in = np.atleast_2d(symbol_in)
    training_symbol =np.atleast_2d(training_symbol)
    constl = np.atleast_2d(constl)
    assert symbol_in.shape[0]==1
    assert training_symbol.shape[0]==1
    assert constl.shape[0]==1
    divided_symbols, divided_training_symbols = __initialzie_superscalar(symbol_in, training_symbol, block_length)
    angle = __initialzie_pll(divided_symbols, divided_training_symbols, pilot_number)

    divided_symbols = divided_symbols * np.exp(-1j * angle)
    divided_symbols = first_order_pll(divided_symbols, (constl), g)
    divided_symbols[0::2, :] = divided_symbols[0::2, ::-1]
    divided_symbols = divided_symbols.reshape((1, -1))
    # ml
    decision_symbols = np.zeros(divided_symbols.shape[1],dtype=np.complex)
    exp_decision(divided_symbols[0,:],constl[0,:],decision_symbols)

    hphase_ml = symbol_in[0,:len(decision_symbols)]/decision_symbols
    hphase_ml = np.atleast_2d(hphase_ml)
    h = np.ones((1,2*filter_n+1))
    hphase_ml = lfilter(h[0,:],1,hphase_ml)
    hphase_ml = np.roll(hphase_ml,-filter_n,axis=1)
    phase_ml = np.angle(hphase_ml)
    divided_symbols = symbol_in[:,:len(decision_symbols)] * np.exp(-1j*phase_ml)
    #ml completed
    divided_training_symbols[0::2, :] = divided_training_symbols[0::2, ::-1]
    divided_training_symbols = divided_training_symbols.reshape((1, -1))
    # scatterplot(divided_symbols,False,'pyqt')

    # filrst order pll

    return divided_symbols, divided_training_symbols


@numba.jit(nopython=True, parallel=True)
def first_order_pll(divided_symbols, constl, g):
    constl = np.atleast_2d(constl)
    phase = np.zeros((divided_symbols.shape[0], divided_symbols.shape[1]))
    for i in prange(divided_symbols.shape[0]):
        signal = divided_symbols[i, :]
        each_error = phase[i, :]
        for point_index, point in enumerate(signal):
            if point_index == 0:
                point = point * np.exp(-1j * 0)
            else:
                point = point * np.exp(-1j * each_error[point_index - 1])
            point_decision = decision(point, constl)
            signal[point_index] = point
            point_decision_conj = np.conj(point_decision)
            angle_difference = np.angle(point * point_decision_conj)

            if point_index > 0:
                each_error[point_index] = angle_difference * g + each_error[point_index - 1]
            else:
                each_error[point_index] = angle_difference * g

    return divided_symbols


def __initialzie_pll(divided_symbols, divided_training_symbols, pilot_number):
    '''
        There are pilot_number symbols of each row,the two adjecnt channel use the same phase,because they are simillar

    '''
    # get pilot symbol
    pilot_signal = divided_symbols[:, : pilot_number]
    pilot_traing_symbol = divided_training_symbols[:, :pilot_number]

    angle = (pilot_signal / pilot_traing_symbol)
    angle = angle.flatten()
    angle = angle.reshape(-1, 2 * pilot_number)
    angle = np.sum(angle, axis=1, keepdims=True)
    angle = np.angle(angle)

    angle_temp = np.zeros((angle.shape[0] * 2, angle.shape[1]), dtype=np.float)
    angle_temp[0::2, :] = angle
    angle_temp[1::2, :] = angle_temp[0::2, :]
    return angle_temp


def __initialzie_superscalar(symbol_in, training_symbol, block_length):
    # delete symbols to assure the symbol can be divided into adjecent channels
    symbol_in = np.atleast_2d(symbol_in)
    training_symbol = np.atleast_2d(training_symbol)
    assert symbol_in.shape[0] == 1
    symbol_length = len(symbol_in[0, :])
    assert divmod(block_length, 2)[1] == 0

    if divmod(symbol_length, 2)[1] != 0:
        # temp_symbol = np.zeros((symbol_in.shape[0], symbol_in.shape[1] - 1), dtype=np.complex)
        # temp_training_symbol = np.zeros((training_symbol.shape[0], training_symbol.shape[1] - 1), dtype=np.complex)
        temp_symbol = symbol_in[:, :-1]
        temp_training_symbol = training_symbol[:, :-1]
    else:
        temp_symbol = symbol_in
        temp_training_symbol = training_symbol

    # divide into channels
    channel_number = int(len(temp_symbol[0, :]) / block_length)
    if divmod(channel_number, 2)[1] == 1:
        channel_number = channel_number - 1
    divided_symbols = np.zeros((channel_number, block_length), dtype=np.complex)
    divided_training_symbols = np.zeros((channel_number, block_length), dtype=np.complex)
    for cnt in range(channel_number):
        divided_symbols[cnt, :] = temp_symbol[0, cnt * block_length:(cnt + 1) * block_length]
        divided_training_symbols[cnt, :] = temp_training_symbol[0, cnt * block_length:(cnt + 1) * block_length]
        if divmod(cnt, 2)[1] == 0:
            divided_symbols[cnt, :] = divided_symbols[cnt, ::-1]
            divided_training_symbols[cnt, :] = divided_training_symbols[cnt, ::-1]
    #             print(divided_training_symbols.shape)
    # First Order PLL

    return divided_symbols, divided_training_symbols


def dual_frequency_lms_equalizer_block(signal, ntaps, sps, constl=None, train_symbol=None, mu=0.001, niter=3):
    pass


@numba.jit(cache=True)
def dual_pol_time_domain_lms_equalizer_pll(signal, ntaps, sps, constl=None, train_symbol=None, mu=0.001,
                                           niter=3, g=0.01, symbol_length=65536):
    weight = __dual_pol_init_lms_weight(ntaps)  # xx xy yx yy
    data_sample_in_fiber = signal[:]
    samplex = segment_axis(data_sample_in_fiber[0, :], ntaps, ntaps - sps)
    sampley = segment_axis(data_sample_in_fiber[1, :], ntaps, ntaps - sps)
    if train_symbol is not None:
        xsymbol = train_symbol[0, ntaps // 2 // sps:]
        ysymbol = train_symbol[1, ntaps // 2 // sps:]
        # xsymbol = np.roll(xsymbol,)

    xsymbols = np.zeros((1, symbol_length), dtype=np.complex128)
    ysymbols = np.zeros((1, symbol_length), dtype=np.complex128)
    errorsx = np.zeros((1, niter * samplex.shape[0]), dtype=np.float64)
    errorsy = np.zeros((1, niter * samplex.shape[0]), dtype=np.float64)
    pll_phase = np.zeros((2, samplex.shape[0]), dtype=np.float64)
    # pll_error = np.zeros((2, samplex.shape[0]), dtype=np.complex128)

    hxx = np.zeros((1, samplex.shape[0]), dtype=np.float64)
    hxy = np.zeros((1, samplex.shape[0]), dtype=np.float64)
    hyx = np.zeros((1, samplex.shape[0]), dtype=np.float64)
    hyy = np.zeros((1, samplex.shape[0]), dtype=np.float64)

    for j in range(niter):
        for i in range(samplex.shape[0]):
            xout = np.sum(samplex[i, ::-1] * weight[0][0]) + np.sum(sampley[i, ::-1] * weight[1][0])
            yout = np.sum(samplex[i, ::-1] * weight[2][0]) + np.sum(sampley[i, ::-1] * weight[3][0])
            if i > 0:
                xout_cpr = xout * np.exp(-1j * pll_phase[0, i - 1])
                yout_cpr = yout * np.exp(-1j * pll_phase[1, i - 1])
            else:
                xout_cpr = xout * np.exp(-1j * 0)
                yout_cpr = yout * np.exp(-1j * 0)

            if train_symbol is not None:
                errorx = __calc_error_train(xout_cpr, symbol=xsymbol[i])
                errory = __calc_error_train(yout_cpr, symbol=ysymbol[i])
                xout_cpr_decision = xsymbol[i]
                yout_cpr_decision = ysymbol[i]
            else:
                assert constl is not None
                # assert constl.ndim ==1

                if constl.ndim != 2:
                    raise Exception("constl must be 2d")
                errorx = __calc_error_dd(xout_cpr, constl)
                errory = __calc_error_dd(yout_cpr, constl)
                xout_cpr_decision = decision(xout_cpr,constl)
                yout_cpr_decision = decision(yout_cpr,constl)

            angle_difference_x = np.angle((xout_cpr * np.conj(xout_cpr_decision)))
            angle_difference_y = np.angle((yout_cpr * np.conj(yout_cpr_decision)))
            if i == 0:
                pll_phase[0, i] = g * angle_difference_x
                pll_phase[1, i] = g * angle_difference_y
                pll_angle_x = 0
                pll_angle_y = 0
            else:
                pll_phase[0, i] = g * angle_difference_x + pll_phase[0, i - 1]
                pll_phase[1, i] = g * angle_difference_y + pll_phase[1, i - 1]
                pll_angle_x = pll_phase[0, i - 1]
                pll_angle_y = pll_phase[1, i - 1]

            weight[0][0] = weight[0][0] + mu * errorx * np.conj(samplex[i, ::-1] * np.exp(-1j * pll_angle_x))
            weight[1][0] = weight[1][0] + mu * errorx * np.conj(sampley[i, ::-1] * np.exp(-1j * pll_angle_y))

            weight[2][0] = weight[2][0] + mu * errory * np.conj(samplex[i, ::-1] * np.exp(-1j * pll_angle_x))
            weight[3][0] = weight[3][0] + mu * errory * np.conj(sampley[i, ::-1] * np.exp(-1j * pll_angle_y))

            if j == niter - 1:
                xsymbols[0, i] = xout_cpr
                ysymbols[0, i] = yout_cpr
                hxx[0, i] = weight[0][0, ntaps // 2 + 1].real
                hxy[0, i] = weight[1][0, ntaps // 2 + 1].real

                hyx[0, i] = weight[2][0, ntaps // 2 + 1].real

                hyy[0, i] = weight[3][0, ntaps // 2 + 1].real

            errorsx[0, i] = np.abs(errorx)
            errorsy[0, i] = np.abs(errory)

    return xsymbols[0, :], ysymbols[0, :], weight, errorsx, errorsy, (hxx, hxy, hyx, hyy)


@numba.jit(cache=True)
def dual_pol_time_domain_lms_equalizer(signal, ntaps, sps, constl=None, train_symbol=None, mu=0.001,
                                       niter=3, symbol_length=65536):
    '''

    :param signal:         signal to be equalized, a numpy array, 2d-array,each row represent a polarizaiton
    :param ntaps:          the tap of the filter
    :param sps:            sample per symbol
    :param constl:         the constellation, used in dd
    :param train_symbol:   symbol to train
    :param mu:             the learning rate, default to 0.001
    :param niter:          the number of equlizeing operation
    :return: equalized symbols, errors
    '''
    data_sample_in_fiber = signal[:]
    samplex = segment_axis(data_sample_in_fiber[0, :], ntaps, ntaps - sps)
    sampley = segment_axis(data_sample_in_fiber[1, :], ntaps, ntaps - sps)

    if train_symbol is not None:
        xsymbol = train_symbol[0, ntaps // 2 // sps:]
        ysymbol = train_symbol[1, ntaps // 2 // sps:]
        # xsymbol = np.roll(xsymbol,)

    weight = __dual_pol_init_lms_weight(ntaps)  # xx xy yx yy
    xsymbols = np.zeros((1, symbol_length), dtype=np.complex128)
    ysymbols = np.zeros((1, symbol_length), dtype=np.complex128)
    errorsx = np.zeros((1, niter * samplex.shape[0]), dtype=np.float64)
    errorsy = np.zeros((1, niter * samplex.shape[0]), dtype=np.float64)

    # hxx = np.zeros((1, samplex.shape[0]))
    # hxy = np.zeros((1, samplex.shape[0]))
    # hyx = np.zeros((1, samplex.shape[0]))
    # hyy = np.zeros((1, samplex.shape[0]))

    for j in range(niter):
        for i in range(samplex.shape[0]):
            xout = np.sum(samplex[i, ::-1] * weight[0][0]) + np.sum(sampley[i, ::-1] * weight[1][0])
            yout = np.sum(samplex[i, ::-1] * weight[2][0]) + np.sum(sampley[i, ::-1] * weight[3][0])

            if train_symbol is not None and j == 0:
                errorx = __calc_error_train(xout, symbol=xsymbol[i])
                errory = __calc_error_train(yout, symbol=ysymbol[i])
            else:
                assert constl is not None
                # assert constl.ndim ==1

                if constl.ndim != 2:
                    raise Exception("constl must be 2d")

                errorx = __calc_error_dd(xout, constl)
                errory = __calc_error_dd(yout, constl)

            weight[0][0] = weight[0][0] + mu * errorx * np.conj(samplex[i, ::-1])
            weight[1][0] = weight[1][0] + mu * errorx * np.conj(sampley[i, ::-1])

            weight[2][0] = weight[2][0] + mu * errory * np.conj(samplex[i, ::-1])
            weight[3][0] = weight[3][0] + mu * errory * np.conj(sampley[i, ::-1])

            if j == niter - 1:
                xsymbols[0, i] = xout
                ysymbols[0, i] = yout
            errorsx[0, i] = np.abs(errorx)
            errorsy[0, i] = np.abs(errory)

    return xsymbols[0,:], ysymbols[0,:], weight, errorsx, errorsy


@numba.jit(cache=True)
def __calc_error_dd(xout, constl):
    '''
        only use in dual_pol_time_domain_lms_equalizer, should not be used outside this file
        xout: a symbol to be decision,one element
        constl: must be 2d array
    '''
    symbol = decision(xout, constl)
    return symbol - xout


@numba.jit(cache=True)
def __calc_error_train(xout, symbol):
    '''
        only use in dual_pol_time_domain_lms_equalizer, should not be used outside this file
        xout: symbol in ,one element
        symbol: True symbol,one element
    '''
    error = symbol - xout
    return error


@numba.jit(cache=True)
def __dual_pol_init_lms_weight(ntaps):
    '''
         only use in dual_pol_time_domain_lms_equalizer, should not be used outside this file
         implement filter taps initialization

        :param ntaps:
        :return:
    '''
    # hxx = np.zeros((1, ntaps), dtype=np.complex128)
    #
    # hxy = np.zeros((1, ntaps), dtype=np.complex128)
    # hyx = np.zeros((1, ntaps), dtype=np.complex128)
    # hyy = np.zeros((1, ntaps), dtype=np.complex128)
    #
    # hxx[0, ntaps // 2] = 1
    # hyy[0, ntaps // 2] = 1

    hxx = np.zeros((1, ntaps), dtype=np.complex128)

    hxy = np.zeros((1, ntaps), dtype=np.complex128)
    hyx = np.zeros((1, ntaps), dtype=np.complex128)
    hyy = np.zeros((1, ntaps), dtype=np.complex128)

    hxx[0, ntaps // 2] = 1
    hyy[0, ntaps // 2] = 1
    return (hxx, hxy, hyx, hyy)


@numba.jit('int32[:](complex128[:],complex128[:],complex128[:])', cache=True)
def __demap_to_msg_jit(symbols, qam_data_in_order, constl):
    msg = np.zeros(len(symbols), dtype=np.int32)

    for index, symbol in enumerate(symbols):
        symbol_decision = decision(symbol, np.atleast_2d(constl))
        distance = np.abs(symbol_decision - qam_data_in_order)
        msg[index] = np.argmin(distance)
    return msg


def demap_to_msg_v2(receive_symbols, order,do_normal=True):
    receive_symbols = np.atleast_2d(receive_symbols)
    assert receive_symbols.shape[0] == 1
    receive_symbols = receive_symbols[0]
    if do_normal:
        receive_symbols = receive_symbols/np.sqrt(np.mean(receive_symbols.real**2+receive_symbols.imag**2))

    base_path = os.path.abspath(__file__)
    base_path = os.path.dirname(os.path.dirname(base_path))

    qam_data_in_order = loadmat(f'{base_path}/qamdata/{order}qam.mat')['x'][0]
    constl = cal_symbols_qam(16) / np.sqrt(cal_scaling_factor_qam(16))
    msg = __demap_to_msg_jit(receive_symbols, qam_data_in_order, constl)

    return msg


def demap_to_msg(rx_symbols, order, do_normal=True):
    '''
    :param rx_symbols:1d array or 2d array if 2d the shape[0] must be 1
    :param do_normal: if True the rx_symbols will be normalized to 1
    :return: 2d array msg, the shape[0] is 1
    '''

    from scipy.io import loadmat

    base_path = os.path.abspath(__file__)
    base_path = os.path.dirname(os.path.dirname(base_path))

    if order == 8:
        raise NotImplementedError('Not implemented yet')

    constl = cal_symbols_qam(order) / np.sqrt(cal_scaling_factor_qam(order))
    rx_symbols = np.atleast_2d(rx_symbols)
    assert rx_symbols.shape[0] == 1
    rx_symbols = rx_symbols[0]

    qam_data = loadmat(f'{base_path}/qamdata/{order}qam.mat')['x'][0]
    msg = np.zeros((1, rx_symbols.shape[0]))
    if do_normal:
        rx_symbols = rx_symbols / np.sqrt(np.mean(rx_symbols.imag ** 2 + rx_symbols.real ** 2))

    for index, symbol in enumerate(rx_symbols):
        decision_symbol = decision(symbol, constl=np.atleast_2d(constl))

        choose = np.abs(decision_symbol - qam_data) < np.spacing(1)
        #         print(choose)
        #         print(np.nonzero(choose)[0])
        msg[0, index] = (np.nonzero(choose)[0])
    #         print(msg[0,index])
    #         break

    return msg.astype(np.int)[0, :]


def main():
    import matplotlib.pyplot as plt
    from scipy.io import loadmat

    cc = loadmat('test2.mat')
    tx = cc['txsymbols']
    sam = cc['rxSignalIn']

    import time

    now = time.time()

    constl = cal_symbols_qam(16)
    constl = constl / np.sqrt(cal_scaling_factor_qam(16))
    constl = np.atleast_2d(constl)
    xsym, ysym, wer, errorsx, errorsy = dual_pol_time_domain_lms_equalizer(sam[:], 13, 2, constl=constl,
                                                                           train_symbol=tx,
                                                                           mu=0.001, niter=3)
    plt.plot(errorsx)
    print(time.time() - now)


if __name__ == '__main__':
    main()
