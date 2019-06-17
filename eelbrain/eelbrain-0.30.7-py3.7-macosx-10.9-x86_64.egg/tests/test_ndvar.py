# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from nose.tools import eq_, assert_almost_equal
import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
from scipy import signal

from eelbrain import (
    NDVar, Case, Scalar, UTS, datasets,
    concatenate, convolve, correlation_coefficient, cross_correlation,
    cwt_morlet, find_intervals, find_peaks, frequency_response, psd_welch,
)
from eelbrain.testing import assert_dataobj_equal


def test_concatenate():
    """Test concatenate()

    Concatenation of SourceSpace is tested in .test_mne.test_source_estimate
    """
    ds = datasets.get_uts(True)

    v0 = ds[0, 'utsnd']
    v1 = ds[1, 'utsnd']
    vc = concatenate((v1, v0))
    assert_array_equal(vc.sub(time=(0, 1)).x, v1.x)
    assert_array_equal(vc.sub(time=(1, 2)).x, v0.x)
    assert_array_equal(vc.info, ds['utsnd'].info)

    # scalar
    psd = psd_welch(ds['utsnd'], n_fft=100)
    v0 = psd.sub(frequency=(None, 5))
    v1 = psd.sub(frequency=(45, None))
    conc = concatenate((v0, v1), 'frequency')
    assert_array_equal(conc.frequency.values[:5], psd.frequency.values[:5])
    assert_array_equal(conc.frequency.values[5:], psd.frequency.values[45:])
    conc_data = conc.get_data(v1.dimnames)
    assert_array_equal(conc_data[:, :, 5:], v1.x)


def test_convolve():
    # convolve is also tested in test_boosting.py
    ds = datasets._get_continuous()

    h1 = ds['h1']
    h2 = ds['h2']
    x1 = ds['x1']

    xc = convolve(h1, x1)
    xc_np = np.convolve(h1.x, x1.x)
    assert_array_equal(xc.x, xc_np[:100])

    # add dimension through kernel
    xc = convolve(h2, x1)
    xc_np = np.vstack((np.convolve(h2.x[0], x1.x)[:100],
                       np.convolve(h2.x[1], x1.x)[:100]))
    assert_array_equal(xc.x, xc_np)


def test_correlation_coefficient():
    ds = datasets.get_uts()
    uts = ds['uts']
    uts2 = uts.copy()
    uts2.x += np.random.normal(0, 1, uts2.shape)

    assert_almost_equal(
        correlation_coefficient(uts, uts2),
        np.corrcoef(uts.x.ravel(), uts2.x.ravel())[0, 1])
    assert_allclose(
        correlation_coefficient(uts[:10], uts2[:10], 'time').x,
        [np.corrcoef(uts.x[i], uts2.x[i])[0, 1] for i in range(10)])
    assert_allclose(
        correlation_coefficient(uts[:, :-.1], uts2[:, :-.1], 'case').x,
        [np.corrcoef(uts.x[:, i], uts2.x[:, i])[0, 1] for i in range(10)])


def test_cross_correlation():
    ds = datasets._get_continuous()
    x = ds['x1']

    eq_(cross_correlation(x, x).argmax(), 0)
    eq_(cross_correlation(x[2:], x).argmax(), 0)
    eq_(cross_correlation(x[:9], x).argmax(), 0)
    eq_(cross_correlation(x, x[1:]).argmax(), 0)
    eq_(cross_correlation(x, x[:8]).argmax(), 0)
    eq_(cross_correlation(x[2:], x[:8]).argmax(), 0)


def test_cwt():
    ds = datasets._get_continuous()
    # 1d
    y = cwt_morlet(ds['x1'], [4, 6, 8])
    assert y.ndim == 2
    # 2d
    y = cwt_morlet(ds['x2'], [4, 6, 8])
    assert y.ndim == 3


def test_dot():
    ds = datasets.get_uts(True)

    # x subset of y
    index = ['3', '2']
    utsnd = ds['utsnd']
    topo = utsnd.mean(('case', 'time'))
    y1 = topo.sub(sensor=index).dot(utsnd.sub(sensor=index))
    assert_dataobj_equal(topo[index].dot(utsnd), y1)
    assert_dataobj_equal(topo.dot(utsnd.sub(sensor=index)), y1)


def test_find_intervals():
    time = UTS(-5, 1, 10)
    x = NDVar([0, 1, 0, 1, 1, 0, 1, 1, 1, 0], (time,))
    eq_(find_intervals(x), ((-4, -3), (-2, 0), (1, 4)))
    x = NDVar([0, 1, 0, 1, 1, 0, 1, 1, 1, 1], (time,))
    eq_(find_intervals(x), ((-4, -3), (-2, 0), (1, 5)))
    x = NDVar([1, 1, 0, 1, 1, 0, 1, 1, 1, 1], (time,))
    eq_(find_intervals(x), ((-5, -3), (-2, 0), (1, 5)))


def test_find_peaks():
    scalar = Scalar('scalar', range(9))
    time = UTS(0, .1, 12)
    v = NDVar(np.zeros((9, 12)), (scalar, time))
    wsize = [0, 0, 1, 2, 3, 2, 1, 0, 0]
    for i, s in enumerate(wsize):
        if s:
            v.x[i, 5 - s: 5 + s] += np.hamming(2 * s)

    peaks = find_peaks(v)
    x, y = np.where(peaks.x)
    assert_array_equal(x, [4])
    assert_array_equal(y, [5])


def test_frequency_response():
    b_array = signal.firwin(80, 0.5, window=('kaiser', 8))
    freqs_array, fresp_array = signal.freqz(b_array)
    hz_to_rad = 2 * np.pi * 0.01

    b = NDVar(b_array, (UTS(0, 0.01, 80),))
    fresp = frequency_response(b)
    assert_array_equal(fresp.x, fresp_array)
    assert_array_equal(fresp.frequency.values * hz_to_rad, freqs_array)

    b2d = concatenate((b, b), Case)
    fresp = frequency_response(b2d)
    assert_array_equal(fresp.x[0], fresp_array)
    assert_array_equal(fresp.x[1], fresp_array)
    assert_array_equal(fresp.frequency.values * hz_to_rad, freqs_array)
