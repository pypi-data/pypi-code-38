# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from math import log, sqrt

import numpy as np
from scipy.signal import gaussian

from nose.tools import eq_
from numpy.testing import assert_allclose

from eelbrain._data_opt import gaussian_smoother


def test_gaussian_smoother():
    "Test gaussian_kernel function"
    x, y = np.mgrid[:99, :99]
    d = np.abs(x - y, dtype=np.float64)
    d[9, 0] = d[0, 9] = -1
    std = 40. / (2 * (sqrt(2 * log(2))))
    g = gaussian_smoother(d, std)

    # basic properties
    eq_(g.shape, (99, 99))
    # FWHM
    eq_(g[0, 0] / 2, g[0, 20])
    eq_(g[9, 0], 0)
    eq_(g[0, 9], 0)

    # compare with scipy.signal gaussian
    ref = gaussian(99, std)
    ref /= ref.sum()
    assert_allclose(g[49], ref)
