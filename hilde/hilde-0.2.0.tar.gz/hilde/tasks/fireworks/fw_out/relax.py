"""FWAction generators for relaxations"""
import os
from pathlib import Path

from fireworks import FWAction
from ase.io.aims import read_aims

from hilde.fireworks.workflows.workflow_generator import generate_firework, get_time, to_time_str
from hilde.phonon_db.ase_converters import atoms2dict, calc2dict
from hilde.helpers.fileformats import last_from_yaml
from hilde.helpers.k_grid import k2d


def check_relaxation_complete(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that checks if a relaxation is converged (if outputs is True) and either
    stores the relaxed structure in the MongoDB or appends another Firework as its child
    to restart the relaxation
    Args:
        atoms (ASE Atoms object): The original atoms at the start of this job
        calc (ASE Calculator object): The original calculator
        outputs (bool): The outputs from the function (Is the calc converged)
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_settings (dict): FireWorks specific settings
    Returns (FWAction): The correct action (restart or updated spec) if convergence is reached
    """
    if "trajectory" in func_kwargs:
        last_step_dict = last_from_yaml(func_kwargs["trajectory"])
    elif "workdir" in func_kwargs:
        last_step_dict = last_from_yaml(
            Path(func_kwargs["workdir"] + "/trajectory.son").absolute()
        )
    else:
        last_step_dict = last_from_yaml(Path("./trajectory.son").absolute())

    for key, val in last_step_dict["atoms"].items():
        atoms[key] = val
    calc["results"] = last_step_dict["calculator"]
    for key, val in calc.items():
        atoms[key] = val
    next_step = last_step_dict["info"]["nsteps"] + 1

    if outputs:
        return FWAction(
            update_spec={
                fw_settings["out_spec_atoms"]: atoms,
                fw_settings["out_spec_calc"]: calc,
            }
        )
    del calc["results"]["forces"]
    fw_settings["fw_name"] = fw_settings["fw_base_name"] + str(next_step)
    if "to_launchpad" in fw_settings and fw_settings["to_launchpad"]:
        fw_settings["to_launchpad"] = False
    if "trajectory" in func_kwargs:
        new_traj_list = func_kwargs["trajectory"].split(".")
    elif "workdir" in func_kwargs:
        new_traj_list = str(
            Path(func_kwargs["workdir"] + "/trajectory.son").absolute()
        ).split(".")
    else:
        new_traj_list = str(Path("." + "/trajectory.son").absolute()).split(".")

    try:
        temp_list = new_traj_list[-2].split("_")
        temp_list[-1] = str(int(temp_list[-1]) + 1)
        new_traj_list[-2] = "_".join(temp_list)
        func_kwargs["trajectory"] = ".".join(new_traj_list)
    except ValueError:
        new_traj_list[-2] += "_restart_1"
        func_kwargs["trajectory"] = ".".join(new_traj_list)
    fw = generate_firework(
        func=func,
        func_fw_out=func_fw_out,
        func_kwargs=func_kwargs,
        atoms=atoms,
        calc=calc,
        func_fw_out_kwargs=func_fw_kwargs,
        fw_settings=fw_settings,
    )
    return FWAction(detours=[fw])


def check_aims_complete(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    A function that checks if a relaxation is converged (if outputs is True) and either
    stores the relaxed structure in the MongoDB or appends another Firework as its child
    to restart the relaxation
    Args:
        atoms (ASE Atoms object): The original atoms at the start of this job
        calc (ASE Calculator object): The original calculator
        outputs (ASE Atoms Object): The geometry of the final relaxation step
        func (str): Path to function that performs the MD like operation
        func_fw_out (str): Path to this function
        func_kwargs (dict): keyword arguments for func
        func_fw_kwargs (dict): Keyword arguments for fw_out function
        fw_settings (dict): FireWorks specific settings
    Returns (FWAction): The correct action (restart or updated spec) if convergence is reached
    """
    func_fw_kwargs["relax_step"] += 1
    aims_out = np.array(open(func_kwargs["workdir"] + "/aims.out").readlines())
    completed = "Have a nice day" in aims_out[-2]
    calc = calc2dict(outputs.get_calculator())
    try:
        if "relax_geometry" in calc["calculator_parameters"]:
            new_atoms = read_aims(func_kwargs["workdir"] + "/geometry.in.next_step")
            new_atoms.set_calculator(outputs.get_calculator())
        else:
            new_atoms = atoms.copy()
    except FileNotFoundError:
        if not completed:
            line_sum = np.where(
                aims_out == "          Detailed time accounting                     :  max(cpu_time)    wall_clock(cpu1)\n"
            )[0]
            sum_present = len(line_sum) > 0
            walltime = get_time(fw_settings["spec"]["walltime"])
            if sum_present and float(aims_out[line_sum[0]+1].split(":")[1].split("s")[1]) / walltime > 0.95:
                calc.parameters["walltime"] = 2.0*walltime
                fw_settings["spec"]["walltime"] = to_time_str(2*walltime)
                pass
            else:
                raise IOError(
                    "There was a problem with the FHI Aims calculation stopping program here"
                )
        new_atoms = outputs
    new_atoms_dict = atoms2dict(new_atoms)
    for key, val in atoms["info"].items():
        if key not in new_atoms_dict["info"]:
            new_atoms_dict["info"][key] = val
    update_spec = dict()
    if completed:
        update_spec = {}
        if "out_spec_atoms" in fw_settings:
            update_spec[fw_settings["out_spec_atoms"]] = new_atoms_dict
        if "out_spec_calc" in fw_settings:
            update_spec[fw_settings["out_spec_calc"]] = calc

        return FWAction(
            update_spec=update_spec
        )

    else:
        update_spec = {}
        if "in_spec_atoms" in fw_settings:
            update_spec[fw_settings["in_spec_atoms"]] = new_atoms_dict
        if "in_spec_calc" in fw_settings:
            update_spec[fw_settings["in_spec_calc"]] = calc
        if "kpoint_density_spec" in fw_settings:
            update_spec[fw_settings["kpoint_density_spec"]] = k2d(
                new_atoms, calc["calculator_parameters"]["k_grid"]
            )
        if "relax_geometry" not in calc["calculator_parameters"]:
            calc.parameters["walltime"] = to_time_str(2*get_time(fw_settings["spec"]["walltime"]))
        os.system(f"cp {func_kwargs['workdir']}/aims.out {func_kwargs['workdir']}/aims.out.{func_fw_kwargs['relax_step']}")
    del calc["results"]
    fw_settings["fw_name"] = fw_settings["fw_base_name"] + str(
        func_fw_kwargs["relax_step"]
    )
    fw_settings["spec"].update(update_spec)
    fw_settings["from_db"] = False

    if "to_launchpad" in fw_settings and fw_settings["to_launchpad"]:
        fw_settings["to_launchpad"] = False

    fw = generate_firework(
        func=func,
        func_fw_out=func_fw_out,
        func_kwargs=func_kwargs,
        atoms=new_atoms_dict,
        calc=calc,
        func_fw_out_kwargs=func_fw_kwargs,
        fw_settings=fw_settings,
    )
    return FWAction(detours=[fw], update_spec=update_spec)
