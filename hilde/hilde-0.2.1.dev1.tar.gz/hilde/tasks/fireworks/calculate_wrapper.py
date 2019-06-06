from ase.calculators.calculator import CalculationFailed
import os

from hilde.phonon_db.ase_converters import dict2atoms
from hilde.phonopy.wrapper import preprocess
from hilde.settings import Settings
from hilde.tasks.calculate import calculate_socket, calculate

def wrap_calc_socket(
    atoms_dict_to_calculate,
    calc_dict,
    metadata,
    phonon_times=None,
    trajectory="trajectory.son",
    workdir=".",
    backup_folder="backups",
    walltime=1800,
    **kwargs,
):
    """
    Wrapper for the clalculate_socket function
    Args:
        atoms_dict_to_calculate (list of dicts): A list of dicts representing the cells
                                                 to calculate the forces on
        calc_dict (dict): A dictionary representation of the ASE Calculator used to calculate
                          the Forces
        metadata (dict): metadata for the force trajectory file
        phonon_time (list): List of times needed to calculate the supercell forces
        trajectory (str): file name for the trajectory file
        workdir (str): work directory for the force calculations
        backup_folder (str): Directory to store backups
        walltime (int): number of seconds to run the calculation for
    Returns (bool): True if all the calculations completed
    """
    atoms_to_calculate = []
    if calc_dict["calculator"].lower() == "aims":
        settings = Settings(settings_file=None)
        if "species_dir" in calc_dict["calculator_parameters"]:
            from os import path

            species_type = calc_dict["calculator_parameters"]["species_dir"].split("/")[
                -1
            ]
            calc_dict["calculator_parameters"]["species_dir"] = path.join(
                settings.machine.basissetloc, species_type
            )
        calc_dict["command"] = settings.machine.aims_command
        calc_dict["calculator_parameters"]["walltime"] = walltime - 180

    for at_dict in atoms_dict_to_calculate:
        for key, val in calc_dict.items():
            at_dict[key] = val
        atoms_to_calculate.append(dict2atoms(at_dict))
    calculator = dict2atoms(atoms_dict_to_calculate[0]).calc
    try:
        return calculate_socket(
            atoms_to_calculate,
            calculator,
            metadata=metadata,
            trajectory=trajectory,
            workdir=workdir,
            backup_folder=backup_folder,
            walltime=walltime,
            **kwargs,
        )
    except RuntimeError:
        if calc_dict["calculator"].lower() == "aims":
            lines = np.array(open(workdir + "/aims.out").readlines())
            line_sum = np.where(
                lines == "          Detailed time accounting                     :  max(cpu_time)    wall_clock(cpu1)\n"
            )[0]
            sum_present = len(line_sum) > 0
            if not sum_present or float(lines[line_sum[0]+1].split(":")[1].split("s")[1]) / walltime < 0.95:
                raise RuntimeError(
                    "FHI-aims failed to converge, and it is not a walltime issue"
                )
            return True
        else:
            raise RuntimeError("The calculation failed")

def wrap_calculate(
    atoms,
    calc,
    workdir=".",
):
    """
    Wrapper for the clalculate_socket function
    Args:
        atoms (Atoms): Structure.
        calculator (calculator): Calculator.
        workdir (folder): Folder to perform calculation in.

    Returns (bool): True if all the calculations completed
    """
    try:
        return calculate(
            atoms,
            calc,
            workdir
        )
    except RuntimeError:
        if calc.name.lower() == "aims":
            lines = np.array(open(workdir + "/aims.out").readlines())
            line_sum = np.where(
                lines == "          Detailed time accounting                     :  max(cpu_time)    wall_clock(cpu1)\n"
            )[0]
            sum_present = len(line_sum) > 0
            if sum_present and float(lines[line_sum[0]+1].split(":")[1].split("s")[1]) / walltime > 0.95:
                return atoms
            elif "  ** Inconsistency of forces<->energy above specified tolerance.\n" in lines:
                return atoms
            else:
                raise RuntimeError(
                    "FHI-aims failed to converge, and it is not a walltime issue"
                )
        else:
            raise RuntimeError("The calculation failed")
