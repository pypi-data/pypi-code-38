"""Utility functions used in for HiLDe"""
from fireworks import FWAction
import numpy as np
from hilde.helpers.k_grid import update_k_grid_calc_dict


def mod_calc(param_key, calc_spec, calc, val, atoms=None, spec_key=None):
    """
    Function to modify a calculator within the MongoDB
    Args:
        param_key (str): key in the calculator dictionary to change
        calc_spec (str): key for the calculator spec
        calc (dict): a dict representing an ASE Calculator
        val: the new value calc[param_key] should be updated to
        atoms (dict): A dict representing an ASE Atoms object
        spec_key (str): The key in the MongoDB to update the val
                        (used to pass the param down the Workflow)
    Returns (FWAction): An FWAction that modifies the calculator inside the spec
    """
    if param_key == "command":
        calc[param_key] = val
    elif param_key == "basisset_type":
        sd = calc["calculator_parameters"]["species_dir"].split("/")
        sd[-1] = val
        calc["calculator_parameters"]["species_dir"] = "/".join(sd)
    elif param_key == "k_grid_density":
        recipcell = np.linalg.pinv(atoms["cell"]).transpose()
        update_k_grid_calc_dict(calc, recipcell, atoms["pbc"], val)
    else:
        calc["calculator_parameters"][param_key] = val
    up_spec = {calc_spec: calc}
    if spec_key:
        up_spec[spec_key] = val
    return FWAction(update_spec=up_spec)


def update_calc(calc_dict, key, val):
    """
    Update the calculator dictionary
    Args:
        calc_dict (dict): The dictionary representation of the ASE Calculator
        key (str): The key string of the parameter to be changed
        val: The updated value associated with the key string
    Returns (dict): The updated clac_dict
    """
    if key == "command":
        calc_dict[key] = val
    elif key == "basisset_type":
        sd = calc_dict["calculator_parameters"]["species_dir"].split("/")
        sd[-1] = val
        calc_dict["calculator_parameters"]["species_dir"] = "/".join(sd)
    elif key == "use_pimd_wrapper" and isinstance(val, int):
        calc_dict["calculator_parameters"][key] = ("localhost", val)
    else:
        if val is None and key in calc_dict["calculator_parameters"]:
            del calc_dict["calculator_parameters"][key]
        elif val is not None:
            calc_dict["calculator_parameters"][key] = val
    return calc_dict


def update_calc_in_db(calc_spec, update_calc_params, calc):
    """
    Updates a calculator in the MongoDB with a new set of parameters
    Args:
        calc_spec (str): spec to store the new calculator
        update_calc_params (dict): A dictionary describing the new parameters to update the calc with
        calc (dict): A dict representing an ASE Calculator
    Returns (FWAction): An FWAction that updates the calculator in the spec
    """
    del_key_list = ["relax_geometry", "relax_unit_cell", "use_sym"]
    for key in del_key_list:
        if key in calc["calculator_parameters"]:
            del calc["calculator_parameters"][key]
    for key, val in update_calc_params.items():
        calc = update_calc(calc, key, val)
    return FWAction(update_spec={calc_spec: calc})
