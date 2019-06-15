"""
Contains the main transmittance/reflectance calculation bits
"""

import numpy as np
import scipy as sp

def rt_amp(index, delta, theta, pol):
    """
    Calculate the reflected and transmitted amplitudes through the
    system.

    Arguments
    ---------
    index : array
        An array of refractive indices, ordered from source layer to
        terminator layer.
    delta : array
        An array of wavenumber offsets.
    theta : array
        An array of angles in radians.
    pol : string
        The polarization of the source wave: 's' or 'p',
        or 'u'.

    Returns
    -------
    r, t : tuple
        A tuple where 'r' is the reflected amplitude, and 't' is the
        transmitted amplitude.
    """
    t_amp, r_amp = make_rt_amp_matrix(index, theta, pol)
    m_mat = make_m_matrix(index, t_amp, r_amp, delta)

    m_prime = make_2x2(1., 0., 0., 1., dtype=complex)
    for i in range(1, len(index)-1):
        m_prime = np.dot(m_prime, m_mat[i])

    C_m = make_2x2(1., r_amp[0, 1], r_amp[0, 1], 1., dtype=complex)
    m_prime = np.dot(C_m / t_amp[0, 1], m_prime)
    trans_amp = 1 / m_prime[0, 0]
    ref_amp = m_prime[1, 0] / m_prime[0, 0]
    return ref_amp, trans_amp

def make_rt_amp_matrix(index, theta, pol):
    """
    Construct reflection and transmission amplitude matrices

    Parameters
    ----------
    index : numpy array
    theta : numpy array
    pol : string

    Returns
    -------
    t_mat, r_mat : tuple
        The t- and r-amplitude matrices.
    """
    t_mat = np.zeros((len(index), len(index)), dtype=complex)
    r_mat = np.zeros((len(index), len(index)), dtype=complex)
    for i in range(len(index) - 1):
        t_mat[i, i+1] = t_interface(index[i], index[i+1], theta[i], theta[i+1], pol)
        r_mat[i, i+1] = r_interface(index[i], index[i+1], theta[i], theta[i+1], pol)
    return t_mat, r_mat

def make_m_matrix(index, t_matrix, r_matrix, delta):
    """
    Construct the M-matrix

    Parameters
    ----------
    index : numpy array
    t_matrix : numpy array
    r_matrix : numpy array
    delta : numpy array

    Returns
    -------
    m_mat : numpy array
    """
    m_mat = np.zeros((len(index), 2, 2), dtype=complex)
    for i in range(1, len(index)-1):
        C_m = make_2x2(np.exp(-1j * delta[i]), 0., 0., np.exp(1j * delta[i]),
                       dtype=complex)
        r_m = make_2x2(1., r_matrix[i, i+1], r_matrix[i, i+1], 1., dtype=complex)
        m_mat[i] = (1 / t_matrix[i, i+1]) * np.dot(C_m, r_m)
    return m_mat

def r_power(r_amp):
    """
    Return the fraction of reflected power.

    Arguments
    ---------
    r_amp : float
        The net reflection amplitude after calculating the transfer
        matrix.
    """
    return np.abs(r_amp)**2

def t_power(t_amp, index_i, index_f, theta_i, theta_f):
    """
    Return the fraction of transmitted power.

    Arguments
    ---------
    t_amp : float
        The net transmission amplitude after calculating the transfer 
        matrix.
    index_i : float
        The index of refraction of the source material.
    index_f : float
        The index of refraction of the terminating material.
    theta_i : float
        The angle of incidence (radians) at the initial interface.
    theta_f : float
        The angle of incidence (radians) at the final interface.
    """
    return np.abs(t_amp**2) * \
           ( (index_f * np.cos(theta_f)) / (index_i * np.cos(theta_i) ) )

def r_interface(index1, index2, theta1, theta2, pol):
    """
    Calculate the reflected amplitude at an interface.

    Arguments
    ---------
    index1 : float
        The index of refraction of the first material.
    index2 : float
        The index of refraction of the second material.
    theta1 : float
        The angle of incidence at interface 1, in radians
    theta2 : float
        The angle of incidence at interface 2, in radians
    pol : string
        The polarization of the source wave (either 's' or 'p').

    Returns
    -------
    reflected amplitude : float
        The amplitude of the reflected power
    """
    if pol == 's':
        numerator = (index1 * np.cos(theta1) - index2 * np.cos(theta2))
        denominator = (index1 * np.cos(theta1) + index2 * np.cos(theta2))
    elif pol == 'p':
        numerator = (index2 * np.cos(theta1) - index1 * np.cos(theta2))
        denominator = (index1 * np.cos(theta2) + index2 * np.cos(theta1))
    else:
        raise ValueError("Polarization must be 's' or 'p'")
    return numerator / denominator

def t_interface(index1, index2, theta1, theta2, pol):
    """
    Calculate the transmission amplitude at an interface.

    Arguments
    ---------
    index1 : float
        The index of refraction of the first material.
    index2 : float
        The index of refraction of the second material.
    theta1 : float
        The angle of incidence at interface 1, in radians
    theta2 : float
        The angle of incidence at interface 2, in radians
    pol : string
        The polarization of the source wave (either 's' or 'p').

    Returns
    -------
    transmitted_amplitude : float
        The amplitude of the transmitted power
    """
    if pol == 's':
        numerator = 2 * index1 * np.cos(theta1)
        denominator = (index1 * np.cos(theta1) + index2 * np.cos(theta2))
    elif pol == 'p':
        numerator = 2 * index1 * np.cos(theta1)
        denominator = (index1 * np.cos(theta2) + index2 * np.cos(theta1))
    else:
        raise ValueError("Polarization must be 's' or 'p'")
    return numerator / denominator

def wavenumber(freq, index, tand, theta):
    """
    Calculate the wavenumber in a material.

    Arguments
    ---------
    freq : float
        The frequency at which to calculate the wavevector, k
    tand : array
        An array of loss tangents, ordered from source to terminating
    index : array
        An array of refractive indices, ordered from source to
        terminating layer
    theta : array
        An array of angles (radians)

    Returns
    -------
    k : array
        The complex wavenumber, k
    """
    k = 2 * np.pi * (freq / 3e8) * np.cos(theta) * index * np.sqrt(1 + 1j * tand)
    return k

#def wavenumber_comp(freq, index, tand, theta):
#    """
#    Calculate the complex wavenumber of a wave in a material.
#    This function is extraneous for now. Please ignore.
#
#    Arguments
#    ---------
#    freq : float
#        The frequency at which to calculate the wavevector, k
#    tand : array
#        An array of loss tangents, ordered from source to terminating
#    index : array
#        An array of refractive indices, ordered from source to
#        terminating layer
#    theta : array
#        An array of angles (radians)
#
#    Returns
#    -------
#    k : array
#        The complex wavenumber, k
#    """
#    extinc_coeff = tand*index/2
#    comp_index = index + 1j*extinc_coeff
#    k = (2*np.pi*comp_index*freq*np.cos(theta)/3e8)
#    return k

def alpha2imagn(freq, a, b, n):
    """
    Convert Halpern's 'a' and 'b' from an absorption coefficient
    of the form `a*freq**b` to a (frequency-dependent) .

    Arguments
    ---------
    freq : array or float
        The frequency (Hz) (or frequencies) at which to calculate the loss
        tangent.
    a : float
        Halpern's 'a' coefficient
    b : float
        Halpern's 'b' coefficient
    n : float
        The real part of the material's refractive index

    Returns
    -------
    imagn : array or float
    """
    nu = freq / 30e9
    # First we need the frequency-dependent absorption coefficient,
    # alpha, which we get from the Halpern fit. From that we will
    # calculate k(appa), the extinction coefficient, for each
    # frequency of interest
    alpha = 2 * a * nu**b

    # This is the absorption-extinction coefficient relation as ~written
    # in Born & Wolf Principles of Optics 1st Ed., 1959, Ch. 13.1,
    # Pg. 614, Eq. 21
    # The factor of 3e10 (c in units of cms^-1) ensures that our k is
    # unitless, as it ought to be.
    imagn = (100 * 3e8 * alpha) / (4 * np.pi * n * freq)
    return imagn

def alpha2tand(freq, a, b, n):
    """
    Convert Halpern's 'a' and 'b' from an absorption coefficient
    of the form `a*freq**b` to a (frequency-dependent) loss tangent.

    Arguments
    ---------
    freq : array or float
        The frequency (Hz) (or frequencies) at which to calculate the loss
        tangent.
    a : float
        Halpern's 'a' coefficient
    b : float
        Halpern's 'b' coefficient
    n : float
        The real part of the material's refractive index

    Returns
    -------
    tand : array
    """
    imagn = alpha2imagn(freq, a, b, n)

    # The complex index of refraction of a material is related to the
    # complex (relative) permittivity by the relation:
    #   e_r = e' + i*e'' = n^2 = (n + i*k)^2 = n^2 - k^2 + i*2nk
    # By equating the real and imaginary parts we are left with:
    #   e' = (n^2 - k^2); e'' = 2nk
    # With this information we can find the loss tangent, which is simply
    # the ratio of the real and imaginary parts of the relative
    # permittivity:
    #   tand = (e''/e')
    ep = n**2 - imagn**2
    epp = 2 * n * imagn
    tand = epp / ep
    return tand


def make_2x2(a11, a12, a21, a22, dtype=float):
    """
    Return a 2x2 array quickly.

    Thanks to Steve Byrnes for this one.

    Arguments
    ---------
    a11 : float
        Array element [0, 0].
    a12 : float
        Array element [0, 1].
    a21 : float
        Array element [1, 0].
    a22 : float
        Array element [1, 1].
    dtype : dtype, optional
        The datatype of the array. Defaults to float.
    """
    array = np.empty((2, 2), dtype=dtype)
    array[0, 0] = a11
    array[0, 1] = a12
    array[1, 0] = a21
    array[1, 1] = a22
    return array

def prop_wavenumber(k, d):
    """
    Calculate the wavenumber offset, delta.

    Note that the distance correction for off-normal incidence is rolled
    into the wavenumber calculation.

    Arguments
    ---------
    k : array
        The wavenumber
    d : array
        An array of distances (thicknesses), ordered from source to
        terminating layer

    Returns
    -------
    delta : array
        The phase difference
    """
    # Turn off 'invalid multiplication' error; it's just the 'inf' boundaries
    olderr = sp.seterr(invalid='ignore')
    delta = k * d
    # Now turn the error back on
    sp.seterr(**olderr)
    return delta

def refract(n, theta0):
    """
    Calculate the angle by which an incident ray is refracted
    """
    # Make a nice pairwise generator so we can avoid playing games with
    # index counting
    thetas = [theta0]
    ngen = zip(n, n[1:])
    for i, rind in enumerate(ngen):
        theta = np.arcsin(np.real_if_close( rind[0] * np.sin(thetas[i]) / rind[1] ))
        thetas.append(theta)
    return np.asarray(thetas)

def replace_tand(freq, tand_array, halpern_dict):
    for k, v in halpern_dict.items():
        tand_array[k] = alpha2tand(freq, v['a'], v['b'], v['n'])
    return tand_array

def main(params):
    """
    Run a transmission/reflection calculation for the given parameters.

    Arguments
    ---------
    params : dict

    Returns
    -------
    result : dict
    """
    rind = params['rind']
    thick = params['thick']
    tand = params['tand']
    pol = params['pol']
    theta0 = params['theta0']
    theta = refract(rind, theta0)
    freq = params['freq']
    halps = params['halpern_layers']

    # Create containers for the reflection/transmission values we calculate
    # at each frequency
    ts = []
    rs = []

    for f in freq:
        if len(halps.keys()) > 0:
            tand = replace_tand(f, tand, halps)
        ks = wavenumber(f, rind, tand, theta)
        delta = prop_wavenumber(ks, thick)
        r_amp, t_amp = rt_amp(rind, delta, theta, pol)
        t_pow = t_power(t_amp, rind[0], rind[-1], theta[0], theta[-1])
        r_pow = r_power(r_amp)
        ts.append(t_pow)
        rs.append(r_pow)

    ts = np.asarray(ts)
    rs = np.asarray(rs)

    results = {'frequency':freq, 'transmission':ts, 'reflection':rs}
    return results
