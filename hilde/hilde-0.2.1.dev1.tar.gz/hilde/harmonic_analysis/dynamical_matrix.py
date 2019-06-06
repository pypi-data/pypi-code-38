""" Functions related to creation of dynamical matrices """

import numpy as np
from hilde.konstanten import omega_to_THz
from . import get_lattice_points
from .force_constants import reshape_force_constants


def _prefactor(q, r):
    return np.exp(-2j * np.pi * q @ r)


def get_frequencies(dyn_matrix, omega_to_THz=omega_to_THz):
    """ Diagonalize dynamical_matrix and convert to THz """
    evals = np.linalg.eigh(dyn_matrix)[0]
    return np.sign(evals) * np.sqrt(abs(evals)) * omega_to_THz


def get_dynamical_matrix(q, primitive, supercell, force_constants, eps=1e-12):
    """ build the dynamical matrix for one q_point """
    return get_dynamical_matrices([q], primitive, supercell, force_constants, eps)[0]


def get_dynamical_matrices(q_points, primitive, supercell, force_constants, eps=1e-12):
    """ build the dynamical matrix for each q_point """

    lattice_points, _ = get_lattice_points(primitive.cell, supercell.cell)

    force_constants_reshaped = reshape_force_constants(
        primitive, supercell, force_constants, lattice_points=lattice_points
    )

    masses = primitive.get_masses()

    n_prim = len(primitive)

    dyn_matrices = []

    for qq in q_points:
        dyn_matrix = np.zeros([n_prim, n_prim, 3, 3], dtype=complex)

        for LL, lp in enumerate(lattice_points):
            prefactor = _prefactor(qq, lp)
            if np.linalg.norm(prefactor.imag) < eps:
                prefactor = prefactor.real

            for ii in range(n_prim):
                for jj in range(n_prim):
                    dyn_matrix[ii, jj, :, :] += (
                        prefactor * force_constants_reshaped[ii, 0, jj, LL]
                    )

        for ii in range(n_prim):
            for jj in range(n_prim):
                dyn_matrix[ii, jj, :, :] /= np.sqrt(masses[ii] * masses[jj])

        dyn_matrices.append(dyn_matrix.swapaxes(1, 2).reshape(3 * n_prim, 3 * n_prim))

    return dyn_matrices
