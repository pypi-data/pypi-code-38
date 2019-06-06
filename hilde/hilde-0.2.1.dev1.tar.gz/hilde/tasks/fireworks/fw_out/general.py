"""General purpose FWAction Generators"""
from fireworks import FWAction
from hilde.phonon_db.ase_converters import atoms2dict


def mod_spec_add(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that appends the current results to a specified spec in the MongoDB
    Args:
        atoms (ASE Atoms object): The original atoms at the start of this job
        calc (ASE Calculator object): The original calculator
        outputs (ASE Atoms Object): The atoms with attached calculator to be added to the spec
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_settings (dict): FireWorks specific settings
    Returns (FWAction): Action to added the calculated atoms to the spec
    """
    atoms_dict = atoms2dict(outputs)
    return FWAction(mod_spec=[{"_push": {fw_settings["mod_spec_add"]: atoms_dict}}])


def fireworks_no_mods(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that does not change the FireWorks Workflow upon completion
    Args:
        atoms (ASE Atoms object): The original atoms at the start of this job
        calc (ASE Calculator object): The original calculator
        outputs (general): The outputs from the function (assumes to be a single bool output)
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_settings (dict): FireWorks specific settings
    Returns (FWAction): An empty FWAction
    """
    return FWAction()


def fireworks_no_mods_gen_function(
    func, func_fw_out, *args, fw_settings=None, **kwargs
):
    """
    A function that does not change the FireWorks Workflow upon completion
    Args:
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        args (list): List of arguments to pass to func
        fw_settings (dict): FireWorks specific settings
        kwargs (dict): keyword arguments for func
    Returns (FWAction): An empty FWAction
    """
    return FWAction()
