""" deal with displacements in supercells """

import numpy as np
from hilde.helpers.numerics import clean_matrix
from hilde.konstanten import v_unit


def get_dR(atoms, atoms0, wrap_tol=1e-5):
    """ Compute and return dR = R - R^0 respecting possibly wrapped atoms """

    # get fractional coordinates
    fR0 = atoms0.get_scaled_positions()
    fR = atoms.get_scaled_positions()

    fdR = fR - fR0

    # wrap too large displacements
    fdR = (fdR + 0.5 + wrap_tol) % 1 - 0.5 - wrap_tol

    # displacement in cartesian coordinates
    dR = clean_matrix(fdR @ atoms0.cell, eps=1e-12)

    return dR


def get_U(atoms, atoms0, masses=None, wrap_tol=1e-5):
    """ Compute dR = R - R^0 and return U = sqrt(M) . dR """

    dR = get_dR(atoms0, atoms, wrap_tol=wrap_tol)

    # mass scaling
    if masses is None:
        masses = atoms.get_masses()

    dU = dR * np.sqrt(masses[:, None])

    return dU


def get_dUdt(atoms, masses=None, wrap_tol=1e-5):
    """ Compute V and return dU/dt = sqrt(M) . V """

    V = atoms.get_velocities()  # / v_unit

    if V is None:
        V = np.zeros_like(atoms.positions)

    # mass scaling
    if masses is None:
        masses = atoms.get_masses()

    dUdt = V * np.sqrt(masses[:, None])

    return dUdt
