"""FWAction generators for optimizations"""
from pathlib import Path

from fireworks import FWAction

from hilde.fireworks.workflows.workflow_generator import generate_firework
from hilde.phonon_db.ase_converters import calc2dict
from hilde.helpers.fileformats import last_from_yaml


def check_kgrid_opt_completion(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that checks if an MD like calculation is converged (if outputs is True)
    and either stores the relaxed structure in the MongoDB or appends another Firework
    as its child to restart the MD
    Args:
        atoms (ASE Atoms object): The original atoms at the start of this job
        calc (ASE Calculator object): The original calculator
        outputs (list (bool, float, ASE Calculator): (Converged?, current k-point density,
                                                      current ASE Calculator)
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_setstings (dict): FireWorks specific settings
    Returns (FWAction): Either another k-grid optimization step, or an updated spec
    """
    trajectory = Path(func_kwargs["workdir"]) / func_kwargs["trajectory"]
    last_step_dict = last_from_yaml(trajectory)
    for key, val in last_step_dict["atoms"].items():
        atoms[key] = val
    calc["results"] = last_step_dict["calculator"]
    for key, val in calc.items():
        atoms[key] = val
    if outputs[0]:
        up_spec = {
            fw_settings["out_spec_k_den"]: outputs[1],
            fw_settings["out_spec_atoms"]: atoms,
            fw_settings["out_spec_calc"]: calc2dict(outputs[2]),
        }
        return FWAction(update_spec=up_spec)

    fw_settings["fw_name"] = fw_settings["fw_base_name"]
    if fw_settings["to_launchpad"]:
        fw_settings["to_launchpad"] = False
    new_traj_list = trajectory.split(".")
    try:
        temp_list = new_traj_list[-2].split("_")
        temp_list[-1] = str(int(temp_list[-1]) + 1)
        new_traj_list[-2] = "_".join(temp_list)
        trajectory = ".".join(new_traj_list)
    except ValueError:
        new_traj_list[-2] += "_restart_1"
        trajectory = ".".join(new_traj_list)

    fw = generate_firework(
        func=func,
        func_fw_out=func_fw_out,
        func_kwargs=func_kwargs,
        atoms=atoms,
        calc=outputs[2],
        func_fw_out_kwargs=func_fw_kwargs,
        fw_settings=fw_settings,
    )
    return FWAction(detours=[fw])
