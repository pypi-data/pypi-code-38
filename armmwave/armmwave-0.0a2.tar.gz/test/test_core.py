"""
Contains tests for the core.py module.
"""

import pytest
import numpy as np
import numpy.testing as npt
from armmwave import core

@pytest.mark.parametrize('test_n, test_delta, test_theta, expected_r, expected_t',
    [(np.array([1., 1., 1.]), np.array([0., 0., 0.]), np.array([0., 0., 0.]),
      (0., 0.), (1., 1.)),
    ])
@pytest.mark.parametrize('test_pol', ['s', 'p'])
def test_rt_amp(test_n, test_delta, test_theta, test_pol, expected_r, expected_t):
    """Check that the correct r- and t-amplitudes are returned"""
    if test_pol == 's':
        expected_r = expected_r[0]
        expected_t = expected_t[0]
    if test_pol == 'p':
        expected_r = expected_r[1]
        expected_t = expected_t[1]
    r, t = core.rt_amp(test_n, test_delta, test_theta, test_pol)
    npt.assert_allclose(r, expected_r)
    npt.assert_allclose(t, expected_t)

@pytest.mark.parametrize('test_n, test_theta, expected_r, expected_t',
    [(np.array([1., 1., 1.]), np.array([0., 0., 0.]),
     (np.array([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]]),
      np.array([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])),
     (np.array([[0., 1., 0.], [0., 0., 1.], [0., 0., 0.]]),
      np.array([[0., 1., 0.], [0., 0., 1.], [0., 0., 0.]]))),
    ])
@pytest.mark.parametrize('test_pol', ['s', 'p'])
def test_make_rt_amp_matrix(test_n, test_theta, test_pol, expected_r, expected_t):
    """
    Check that the r- and t-amplitude matrices are properly constructed.
    """
    if test_pol == 's':
        expected_r = expected_r[0]
        expected_t = expected_t[0]
    if test_pol == 'p':
        expected_r = expected_r[1]
        expected_t = expected_t[1]
    t, r = core.make_rt_amp_matrix(test_n, test_theta, test_pol)
    npt.assert_allclose(t, expected_t)
    npt.assert_allclose(r, expected_r)

@pytest.mark.parametrize('test_n, test_tmat, test_rmat, test_delta, expected',
    [(np.array([1., 1., 1.]),
      np.array([[0., 1., 0.], [0., 0., 1.], [0., 0., 0.]]),
      np.array([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]]),
      np.array([0., 0., 0.]),
      np.array([[[0., 0.], [0., 0.]],
                [[1., 0.], [0., 1.]],
                [[0., 0.], [0., 0.]]])),
    ])
def test_make_m_matrix(test_n, test_tmat, test_rmat, test_delta, expected):
    """
    Check that the M-matrix is properly constructed.
    """
    npt.assert_allclose(core.make_m_matrix(test_n, test_tmat, test_rmat, test_delta),
                        expected)

def test_r_power():
    """Check reflected power for vacuum-material"""
    testval = np.array([-2., 0., 2.])
    n = np.array([1., 2.])
    expected = np.array([4., 0., 4.])
    npt.assert_allclose(core.r_power(testval), expected)

@pytest.mark.parametrize('test_angle, expected',
    [(np.array([0., 0.]), np.array([8., 0., 8])),
     (np.array([0.52359878, 0.25268026]), np.array([8.944271921510557, 0., 8.944271921510557])),
    ])
def test_t_power(test_angle, expected):
    """
    Check the transmitted amplitude --> power conversion for normal
    incidence, 30 degree incidence.
    """
    amplitude = np.array([-2., 0., 2.])
    n = np.array([1., 2.])
    angle = test_angle
    npt.assert_allclose(core.t_power(amplitude, n[0], n[1], angle[0],
                        angle[1]), expected)

@pytest.mark.parametrize('test_input, expected',
    [(np.array([0., 0.]), (-0.3333333333333333, 0.3333333333333333 )),
     (np.array([0.52359878, 0.25268026]), (-0.38196601179972556, 0.2828596521354057)),
    ])
@pytest.mark.parametrize('test_pol', ['s', 'p', 'q'])
def test_r_interface(test_input, test_pol, expected):
    """
    Check the reflected amplitude at an interface for normal incidence
    and 30 degree incidence for both 's'- and 'p'-polarizations. If the
    polarization is neither 's' nor 'p', then a ValueError should be
    raised.
    """
    n = np.array([1., 2.])
    angle = test_input
    pol = test_pol
    if pol == 's':
        expected = expected[0]
    if pol == 'p':
        expected = expected[1]
    if pol != 's' and pol != 'p':
        pytest.raises(ValueError, core.r_interface, n[0], n[1],
                      angle[0], angle[1], pol)
        return
    npt.assert_allclose(core.r_interface(n[0], n[1], angle[0], angle[1],
                        pol), expected)

@pytest.mark.parametrize('test_input, expected',
    [(np.array([0., 0.]), (0.6666666666666666, 0.6666666666666666 )),
     (np.array([0.52359878, 0.25268026]), (0.6180339882002746, 0.6414298260677028)),
    ])
@pytest.mark.parametrize('test_pol', ['s', 'p', 'q'])
def test_t_interface(test_input, test_pol, expected):
    """
    Check the transmitted amplitude at an interface for normal incidence
    and 30 degree incidence for both 's'- and 'p'-polarizations. If the
    polarization is neither 's' nor 'p', then a ValueError should be
    raised.
    """
    n = np.array([1., 2.])
    angle = test_input
    pol = test_pol
    if pol == 's':
        expected = expected[0]
    if pol == 'p':
        expected = expected[1]
    if pol != 's' and pol != 'p':
        pytest.raises(ValueError, core.t_interface, n[0], n[1],
                      angle[0], angle[1], pol)
        return
    npt.assert_allclose(core.t_interface(n[0], n[1], angle[0], angle[1],
                        pol), expected)

@pytest.mark.parametrize('test_freq, test_n, test_tand, test_angle, expected',
    [(100., 1., 0., 0., 2.0943951023931953e-06 + 0j),
     (100., 2., 0.05, 0.52359878, 3.628731468587418e-06 + 9.066165854860358e-08j),
    ])
def test_wavenumber(test_freq, test_n, test_tand, test_angle, expected):
    """
    Check the wavenumber at normal incidence and 30 deg incidence. Check
    an absorptive medium and a non-absorptive medium.
    """
    npt.assert_allclose(core.wavenumber(test_freq, test_n, test_tand, test_angle),
                        expected)

@pytest.mark.parametrize('test_freq, test_a, test_b, test_n, expected',
    [(100., 0., 0., 1., 0.),
     (100., 1., 0., 1., 47746482.9275686),
    ])
def test_alpha2imagn(test_freq, test_a, test_b, test_n, expected):
    """
    Check conversion of Halpern a/b coefficients to the imaginary component
    of the refractive index. If the `a` coefficient is zero, then we should
    get zero back.
    """
    npt.assert_allclose(core.alpha2imagn(test_freq, test_a, test_b, test_n),
                        expected)

@pytest.mark.parametrize('test_freq, test_a, test_b, test_n, expected',
    [(100., 0., 0., 1., 0.),
     (100., 1., 0., 1., -4.188790204786393e-08),
    ])
def test_alpha2tand(test_freq, test_a, test_b, test_n, expected):
    """
    Check conversion of Halpern a/b coefficients to the imaginary component
    of the refractive index. If the `a` coefficient is zero, then we should
    get zero back.
    """
    npt.assert_allclose(core.alpha2tand(test_freq, test_a, test_b, test_n),
                        expected)

@pytest.mark.parametrize('test_a11, test_a12, test_a21, test_a22, expected',
    [(1, 2, 3, 4, np.array([[1, 2], [3, 4]]))])
def test_make_2x2(test_a11, test_a12, test_a21, test_a22, expected):
    """Check that array elements wind up in the correct places"""
    npt.assert_equal(core.make_2x2(test_a11, test_a12, test_a21, test_a22),
                     expected)

@pytest.mark.parametrize('test_k, test_d, expected',
    [(np.array([1e8, 15e-6, 1e8]), np.array([np.inf, 100, np.inf]),
      np.array([np.inf, 15e-4, np.inf])),
    ])
def test_prop_wavenumber(test_k, test_d, expected):
    """
    Check that we can multiply and get infinite boundaries without raising
    errors through scipy.
    """
    npt.assert_allclose(core.prop_wavenumber(test_k, test_d), expected)

@pytest.mark.parametrize('test_n, test_theta0, expected',
    [(np.array([1., 1.5, 1.]), 0., np.array([0, 0, 0])),
     (np.array([1., 1.5, 1.]), 0.5235987755982988,
      np.array([0.5235987755982988, 0.33983690945412187, 0.5235987755982988])),
    ])
def test_refract(test_n, test_theta0, expected):
    """
    Check Snell angles at normal incidence and 30 deg incidence for a
    vacuum-glass-vacuum interface.
    """
    npt.assert_allclose(core.refract(test_n, test_theta0), expected)

@pytest.mark.skip(reason='no way of currently testing this')
def test_replace_tand():
    """This will function will be incorporated into the integration tests."""
    pass

@pytest.mark.skip(reason='no way of currently testing this')
def test_main():
    """This will function will be incorporated into the integration tests."""
    pass
