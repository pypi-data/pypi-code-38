from ase.atoms import Atoms
import numpy as np

def to_phonopy_atoms(structure, wrap=False):
    from phonopy.structure.atoms import PhonopyAtoms
    phonopy_atoms = PhonopyAtoms(
        symbols=structure.get_chemical_symbols(),
        cell=structure.get_cell(),
        masses=structure.get_masses(),
        positions=structure.get_positions(wrap=wrap),
    )
    return phonopy_atoms


def to_spglib_cell(structure):
    lattice = structure.cell
    positions = structure.get_scaled_positions()
    number = structure.get_atomic_numbers()
    return (lattice, positions, number)

def to_Atoms_db(structure, info={}, pbc=True):
    """ convert structure to ase.Atoms without masses """
    if structure is None:
        return None

    atoms_dict = {
        "symbols": structure.get_chemical_symbols(),
        "cell": np.round(structure.get_cell(), 14),
        "positions": np.round(structure.get_positions(), 14),
        "pbc": pbc,
        "info": info,
    }

    atoms = Atoms(**atoms_dict)

    return atoms

def to_Atoms(structure, info={}, pbc=True):
    """ convert structure to ase.Atoms """

    if structure is None:
        return None

    atoms_dict = {
        "symbols": structure.get_chemical_symbols(),
        "cell": structure.get_cell(),
        "masses": structure.get_masses(),
        "positions": structure.get_positions(),
        "pbc": pbc,
        "info": info,
    }

    atoms = Atoms(**atoms_dict)

    return atoms
