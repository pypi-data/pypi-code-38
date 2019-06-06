""" helpers to deal with structures (as represented by ase.Atoms) """

import numpy as np
from ase.geometry import cell_to_cellpar, cellpar_to_cell
from hilde.helpers.numerics import clean_matrix

# no ase
def clean_atoms(input_atoms, align=False, tolerance=1e-9):
    """Objective: Put position of atom 0 to origin,
    align 1. lattice vector with x axis, 2. to xy plane
    rotation: change lattice via rotations, else: change via cellpars
    """

    atoms = input_atoms.copy()

    # this had unwanted side effects:
    # atoms.positions -= atoms.positions[0]
    # atoms.wrap()

    scaled_pos = atoms.get_scaled_positions()

    old_lattice = atoms.cell

    if align:
        cell_params = cell_to_cellpar(old_lattice)
        new_lattice = clean_matrix(cellpar_to_cell(cell_params))
    else:
        new_lattice = clean_matrix(old_lattice)

    # Sanity check
    vol0 = np.linalg.det(old_lattice)
    vol1 = np.linalg.det(new_lattice)
    assert abs(vol0 - vol1) / vol0 < tolerance, (vol0, vol1)

    atoms.cell = new_lattice
    atoms.set_scaled_positions(scaled_pos)

    atoms.positions = clean_matrix(atoms.positions)

    return atoms
