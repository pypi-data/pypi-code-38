"""Defines conversions between various anomalies.
"""

from math import pi, atan2, sin, cos, tan

def mean2ecc(M_rad, e):
    """Converts a mean (constant time-rate projection) anomaly into eccentric.
       This is the only non-procedural conversion (i.e., it is computed by
       numerical iteration), necessary to solve the transcendental Kepler's
       equation for eccentric anomaly (M = E + e * sin(E)).
    """
    E_rad = M_rad + 0.5 * e
    if M_rad > pi:
        E_rad = M_rad - 0.5 * e
    r = 1
    tol = 1e-8
    n = 0
    max = 1e3
    while abs(r) > tol and n < max:
        n = n + 1
        f = E_rad - e * sin(E_rad) - M_rad
        df = 1 - e * cos(E_rad)
        r = f / df
        E_rad = E_rad - r
    if abs(r) > tol:
        raise Exception('Failed to converge within %u iterations' % n)
    return E_rad

def ecc2true(E_rad, e):
    """Converts an eccentric anomaly into true (angle from perigee in cartesian
       space).
    """
    n = (1 + e)**0.5 * tan(0.5 * E_rad)
    d = (1 - e)**0.5
    return 2 * atan2(n, d)
    
def true2ecc(tht_rad, e):
    """Converts a true (angle from perigee in cartesian space) into eccentric.
    """
    n = (1 - e)**0.5 * tan(0.5 * tht_rad)
    d = (1 + e)**0.5
    return 2 * atan2(n, d)
    
def ecc2mean(E_rad, e):
    """Converts an eccentric anomaly into mean (constant time-rate projection).
    """
    return E_rad - e * sin(E_rad)
    
def true2mean(tht_rad, e):
    """Converts a true (angle from perigee in cartesian space) into mean
       (constant time-rate projection) by chaining *true2ecc* and *ecc2mean*.
    """
    E_rad = true2ecc(tht_rad, e)
    return ecc2mean(E_rad, e)

def mean2true(M_rad, e):
    """Converts a mean (constant time-rate projection) into true (angle from
       perigee in cartesian space) by chaining *true2ecc* and *ecc2mean*.
    """
    E_rad = mean2ecc(M_rad, e)
    return ecc2true(E_rad, e)
