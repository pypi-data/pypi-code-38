'''Functions to convert ASE Objects to dicts and getting them from dicts'''
import numpy as np

from ase.db.row import atoms2dict as ase_atoms2dict
from ase.db.row import AtomsRow

def atoms2dict(atoms):
    """
    Converts a pAtoms object into a dict
    Args:
        atoms: pAtoms or Atoms object
            The pAtoms or Atoms object to be converted into a dictionary
    Returns: atoms_dict (dict)
        The dictionary of atoms
    """
    if atoms is None:
        return None
    if isinstance(atoms, dict):
        return atoms
    atoms_dict = ase_atoms2dict(atoms)
    if "cell" in atoms_dict:
        try:
            atoms_dict["cell"] = atoms.cell.array
        except AttributeError:
            atoms_dict["cell"] = atoms.cell

    # add information that is missing after using ase.atoms2dict
    atoms_dict["info"] = atoms.info

    # attach calculator
    for key, val in calc2dict(atoms.calc).items():
        atoms_dict[key] = val

    return atoms_dict

def dict2atoms(atoms_dict):
    """
    Converts a dict into a pAtoms object
    Args:
        atoms_dict: dict
            A dictionary representing the pAtoms object
    Returns: pAtoms
        The corresponding pAtoms object
    """
    try:
        atoms = AtomsRow(atoms_dict).toatoms(attach_calculator=True)
    except AttributeError:
        atoms = AtomsRow(atoms_dict).toatoms(attach_calculator=False)

    # Attach missing information
    if "info" in atoms_dict:
        atoms.info = atoms_dict["info"]
    if "command" in atoms_dict:
        atoms.calc.command = atoms_dict["command"]
    if "results" in atoms_dict:
        atoms.calc.results = atoms_dict["results"]

    # attach calculator
    if atoms.calc:
        for key, val in atoms.calc.results.items():
            if isinstance(val, list):
                atoms.calc.results[key] = np.array(val)
    if "use_pimd_wrapper" in atoms.calc.parameters:
        pimd = atoms.calc.parameters["use_pimd_wrapper"]
        if isinstance(pimd, int):
            atoms.calc.parameters["use_pimd_wrapper"] = ("localhost", pimd)

    return atoms

def calc2dict(calc):
    """ Converts an ase calculator calc into a dict"""
    if calc is None:
        return {}
    elif isinstance(calc, dict):
        return calc
    calc_dict = {}
    calc_dict["calculator"] = calc.name.lower()
    calc_dict["calculator_parameters"] = calc.todict()
    try:
        calc_dict["command"] = calc.command
    except AttributeError:
        pass
    calc_dict["results"] = calc.results
    return calc_dict
