""" a light wrapper for spglib """

import numpy as np
import spglib as spg
from ase.atoms import Atoms
from hilde.structure.convert import to_spglib_cell
from hilde.konstanten.symmetry import symprec as default_symprec
from hilde.helpers.attribute_dict import AttributeDict


def cell_to_Atoms(lattice, scaled_positions, numbers, info=None):
    """ convert from spglib cell to Atoms """
    atoms_dict = {
        "cell": lattice,
        "scaled_positions": scaled_positions,
        "numbers": numbers,
        "pbc": True,
        "info": info,
    }

    return Atoms(**atoms_dict)


def get_symmetry_dataset(atoms, symprec=default_symprec):
    """ return the spglib symmetry dataset """

    dataset = spg.get_symmetry_dataset(to_spglib_cell(atoms), symprec=symprec)

    uwcks, count = np.unique(dataset["wyckoffs"], return_counts=True)
    dataset["wyckoffs_unique"] = [(w, c) for (w, c) in zip(uwcks, count)]

    ats, count = np.unique(dataset["equivalent_atoms"], return_counts=True)
    dataset["equivalent_atoms_unique"] = zip(uwcks, count)

    return AttributeDict(dataset)


def map_unique_to_atoms(atoms, symprec=default_symprec):
    """ map each symmetry unique atom to other atoms as used by phonopy PDOS """

    ds = get_symmetry_dataset(atoms, symprec=symprec)

    uniques = np.unique(ds.equivalent_atoms)

    mapping = [[] for _ in range(len(uniques))]

    for ii, index in enumerate(ds.equivalent_atoms):
        for jj, unique in enumerate(uniques):
            if index == unique:
                mapping[jj].append(ii)

    return mapping


def get_spacegroup(atoms, symprec=default_symprec):
    """ return spglib spacegroup """

    return spg.get_spacegroup(to_spglib_cell(atoms), symprec=symprec)


def refine_cell(atoms, symprec=default_symprec):
    """ refine the structure """
    lattice, scaled_positions, numbers = spg.refine_cell(to_spglib_cell(atoms), symprec)

    return cell_to_Atoms(lattice, scaled_positions, numbers)


def standardize_cell(
    atoms, to_primitve=False, no_idealize=False, symprec=default_symprec
):
    """ wrap spglib.standardize_cell """

    cell = to_spglib_cell(atoms)
    args = spg.standardize_cell(cell, to_primitve, no_idealize, symprec)

    return cell_to_Atoms(*args)
