""" Tools for dealing with force constants """

import numpy as np
from hilde.helpers.numerics import clean_matrix
from hilde.helpers.lattice_points import get_lattice_points, map_I_to_iL


def reshape_force_constants(
    primitive, supercell, force_constants, scale_mass=False, lattice_points=None
):
    """ reshape from (3N x 3N) into 3x3 blocks labelled by (i,L) """

    if lattice_points is None:
        lattice_points, _ = get_lattice_points(primitive.cell, supercell.cell)

    indeces = map_I_to_iL(primitive, supercell, lattice_points=lattice_points)

    n_i = len(primitive)
    n_L = len(lattice_points)

    masses = primitive.get_masses()

    new_force_constants = np.zeros([n_i, n_L, n_i, n_L, 3, 3])

    for n1 in range(len(supercell)):
        for n2 in range(len(supercell)):
            phi = force_constants[3 * n1 : 3 * n1 + 3, 3 * n2 : 3 * n2 + 3]

            i1, L1, i2, L2 = (*indeces[n1], *indeces[n2])

            if scale_mass:
                phi /= np.sqrt(masses[i1] * masses[i2])

            new_force_constants[i1, L1, i2, L2] = clean_matrix(phi)

    return new_force_constants
