"""Functions that generate FWActions after performing Aims Calculations"""
from pathlib import Path

from fireworks import FWAction

import numpy as np

from hilde.fireworks.workflows.workflow_generator import generate_firework
from hilde.phonon_db.ase_converters import atoms2dict
from hilde.trajectory import reader as traj_reader


def mod_spec_add(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that appends the current results to a specified spec in the MongoDB
    Args:
        atoms (ASE Atoms): The original atoms at the start of this job
        calc (ASE Calculator): The original calculator
        outputs (dict): The outputs from the function (assumes to be a single bool output)
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_settings (dict): FireWorks specific settings
    Returns (FWAction): Modifies the spec to add the current atoms list to it
    """
    atoms_dict = atoms2dict(outputs)
    mod_spec = [{"_push": {fw_settings["mod_spec_add"]: atoms_dict}}]
    if "time_spec_add" in fw_settings:
        mod_spec[0]["_push"][fw_settings["time_spec_add"]] = func_fw_kwargs.pop(
            "run_time"
        )

    return FWAction(mod_spec=mod_spec)

def socket_calc_check(func, func_fw_out, *args, fw_settings=None, **kwargs):
    """
    A function that checks if a socket calculation is done, and if not restarts
    Args:
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        args (list): Arguments passed to the socket calculator function
        fw_settings (dict): FireWorks specific settings
        kwargs (dict): Key word arguments passed to the socket calculator function
    Returns (FWAction): Either a new Firework to restart the calculation or an updated
                        spec with the list of atoms
    """
    if len(args) > 3 and isinstance(args[3], list):
        times = args[3].copy()
    else:
        times = list()
    if "workdir" in kwargs:
        watchdog_log = Path(kwargs["workdir"]) / "calculations" / "watchdog.log"
    else:
        watchdog_log = Path(".") / "calculations" / "watchdog.log"
    if watchdog_log.exists():
        cur_times = np.genfromtxt(str(watchdog_log))
        if len(cur_times.shape) == 1:
            cur_times = [cur_times[3]]
        else:
            cur_times = list(cur_times[:, 3])
    else:
        cur_times = []
    update_spec = {
        fw_settings["calc_atoms_spec"]: args[0],
        fw_settings["calc_spec"]: args[1],
        fw_settings["metadata_spec"]: args[2],
        fw_settings["time_spec_add"]: times + cur_times,
    }
    inputs = [
        fw_settings["calc_atoms_spec"],
        fw_settings["calc_spec"],
        fw_settings["metadata_spec"],
        fw_settings["time_spec_add"],
    ]
    if kwargs["outputs"]:
        wd = Path(kwargs.get("workdir", "."))
        traj = kwargs.get("trajectory", "trajectory.son")
        ca = traj_reader(str((wd / traj).absolute()), False)
        update_spec[fw_settings["mod_spec_add"]] = [atoms2dict(at) for at in ca]
        return FWAction(update_spec=update_spec)
    fw_settings["spec"].update(update_spec)
    fw = generate_firework(
        func="hilde.tasks.fireworks.calculate_wrapper.wrap_calc_socket",
        func_fw_out="hilde.tasks.fireworks.fw_out.calculate.socket_calc_check",
        func_kwargs=kwargs,
        atoms_calc_from_spec=False,
        inputs=inputs,
        fw_settings=fw_settings,
    )
    return FWAction(update_spec=update_spec, detours=[fw])
