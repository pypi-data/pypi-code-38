import math
import typing
from collections import Iterable

import Ocspy.Base as base
import Ocspy.Instrument as instrument
import h5py
import numpy as np
from .Base.SignalInterface import WdmSignalFromArray
from scipy.io import savemat


def calc_sps_in_fiber(nch, spacing, baudrate):
    if divmod(nch, 2)[1] == 0:
        highest = nch / 2 * spacing * 4
        sps_in_fiber = math.ceil(highest / spacing)
    else:
        highest = 4 * ((nch - 1) / 2 * spacing + spacing / 2)
        sps_in_fiber = math.ceil(highest / baudrate)
    if divmod(sps_in_fiber,2)[1]!=0:
        sps_in_fiber+=1
    return sps_in_fiber


def generate_qam_signal(power: typing.Union[typing.List, float], baudrate: typing.Union[float, typing.List],
                        mf='16-qam',
                        symbol_length=2 ** 16, roll_off=0.02, spacing=50e9, unit='Ghz') -> typing.List[base.Signal]:
    signals = []

    if not isinstance(power, list):
        power = [power]
        power = np.array(power)
    if not isinstance(baudrate, float):
        baudrate = [baudrate]
        baudrate = np.array(baudrate)

    if unit.lower() == 'ghz':
        baudrate = baudrate * 1e9

    sps_in_fiber = calc_sps_in_fiber(
        nch=len(power), spacing=spacing, baudrate=np.min(baudrate))

    for p, rate in zip(power, baudrate):
        signal = base.QamSignal(
            rate, sps_in_fiber=sps_in_fiber, mf=mf, symbol_length=symbol_length)
        signal = instrument.AWG(alpha=roll_off)(signal)
        signal.set_signal_power(p, 'dbm')
        signals.append(signal)

    return signals


def to_wdm_array(wdmsignal: base.WdmSignal, signal_under_test_index):
    samples = np.copy(wdmsignal[:])
    if not isinstance(signal_under_test_index, Iterable):
        signal_under_test_index = [signal_under_test_index]
    signal_under_test = []
    for index in signal_under_test_index:
        signal_under_test.append(wdmsignal.signals[index])

    wdm_array_signal = WdmSignalFromArray(field=samples, frequencys=wdmsignal.absolute_frequences,
                                          fs_in_fiber=wdmsignal.fs_in_fiber,
                                          signal_under_study=signal_under_test, signal_index=signal_under_test_index)

    return wdm_array_signal


############should be put into io###########################
def read_matlab_file(matlab_file, key=None, dtype='complex'):
    try:
        from scipy.io import loadmat
        res = loadmat(matlab_file)[key]
    except Exception as e:
        with h5py.File(matlab_file) as f:
            res = f[key][:].T
            if dtype == 'complex':
                res = res['real'] + 1j * res['imag']
    finally:
        return res


def tomat(signal, name):
    samples = signal[:]
    fs = signal.fs_in_fiber
    symbol = signal.symbol
    symbol_rate = signal.symbol_rate
    msg = signal.message
    mf = signal.mf
    savemat(name, dict(sample=samples, fs=fs, symbol=symbol,
                       symbol_rate=symbol_rate, msg=msg, mf=mf))

    # else:


def main():
    signal = generate_qam_signal(0, 35)
    print(isinstance(signal[0], base.QamSignal))


if __name__ == '__main__':
    main()
