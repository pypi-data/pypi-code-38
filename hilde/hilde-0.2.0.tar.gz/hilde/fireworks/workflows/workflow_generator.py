"""Functions used to generate a FireWorks Workflow"""
import numpy as np
from ase.io import read
from ase.symbols import symbols2numbers
from fireworks import Workflow, Firework

from hilde.fireworks.launchpad import LaunchPadHilde
from hilde.phonon_db.ase_converters import atoms2dict, calc2dict, dict2atoms
from hilde.helpers.hash import hash_atoms_and_calc
from hilde.helpers.k_grid import update_k_grid, update_k_grid_calc_dict
from hilde.helpers.pickle import pread
from hilde.phonon_db.row import phonon_to_dict
from hilde.phonopy.postprocess import postprocess
from hilde.phonopy.wrapper import preprocess
from hilde.settings import Settings
from hilde.structure.convert import to_Atoms
from hilde.tasks.fireworks.general_py_task import (
    TaskSpec,
    generate_task,
    generate_update_calc_task,
    generate_mod_calc_task,
)
from hilde.tasks.fireworks.utility_tasks import update_calc
from hilde.templates.aims import setup_aims
from hilde.trajectory import reader


def get_time(time_str):
    """Converts a time step to the number of seconds that time stamp represents"""
    time_set = time_str.split(":")
    time = 0
    for ii, tt in enumerate(time_set):
        time += int(round(float(tt))) * 60 ** (len(time_set) - 1 - ii)
    return int(time)


def to_time_str(n_sec):
    """Converts a number of seconds into a time string"""
    secs = int(n_sec % 60)
    mins = int(n_sec / 60) % 60
    hrs = int(n_sec / 3600)
    return f"{hrs}:{mins}:{secs}"


def generate_firework(
    task_spec_list=None,
    atoms=None,
    calc=None,
    fw_settings=None,
    atoms_calc_from_spec=False,
    update_calc_settings=None,
    func=None,
    func_fw_out=None,
    func_kwargs=None,
    func_fw_out_kwargs=None,
    args=None,
    inputs=None,
):
    """
    A function that takes in a set of inputs and returns a Firework to perform that operation
    Args:
        task_spec_list (list of TaskSpecs): list of task specifications to perform
        atoms (ASE Atoms object, dictionary or str):
            If not atoms_calc_from_spec then this must be an ASE Atoms object or a
            dictionary describing it
            If atoms_calc_from_spec then this must be a key str to retrieve the Atoms
            Object from the MongoDB launchpad
        calc (ASE Calculator object, dictionary or str):
            If not atoms_calc_from_spec then this must be an ASE Calculator object or a
            dictionary describing it
            If atoms_calc_from_spec then this must be a key str to retrieve the
            Calculator from the MongoDB launchpad
        fw_settings (dict): Settings used by fireworks to place objects in the right part of
                            the MongoDB
        atoms_calc_from_spec (bool): If True retrieve the atoms/Calculator objects from the
                                     MongoDB launchpad
        update_calc_settings (dict): Used to update the Calculator parameters
        func (str): Function path for the firework
        func_fw_out (str): Function path for the fireworks FWAction generator
        func_kwargs (dict): Keyword arguments for the main function
        func_fw_out_kwargs (dict): Keyword arguments for the fw_out function
        args (list): List of arguments to pass to func
        inputs(list): List of spec to pull in as args from the FireWorks Database
    Returns (Firework):
        A Firework that will perform the desired operation on a set of atoms,
        and process the outputs for Fireworks
    """
    fw_settings = fw_settings.copy()
    if "spec" not in fw_settings:
        fw_settings["spec"] = {}
    if update_calc_settings is None:
        update_calc_settings = {}
    if "spec" in fw_settings and "_queueadapter" in fw_settings["spec"] and "walltime" in fw_settings["spec"]["_queueadapter"]:
        update_calc_settings["walltime"] = get_time(fw_settings["spec"]["_queueadapter"]["walltime"]) - 180
    if func:
        if task_spec_list:
            raise AttributeError(
                "You have defined a task_spec_list and arguments to generate one, please only specify one of these"
            )
        at = atoms is not None
        task_spec_list = [
            TaskSpec(
                func, func_fw_out, at, func_kwargs, func_fw_out_kwargs, args, inputs
            )
        ]
    elif not task_spec_list:
        raise AttributeError(
            "You have not defined a task_spec_list or arguments to generate one, please specify one of these"
        )
    if isinstance(task_spec_list, TaskSpec):
        task_spec_list = [task_spec_list]
    if fw_settings and "from_db" in fw_settings:
        atoms_calc_from_spec = fw_settings["from_db"]
    if "fw_name" not in fw_settings:
        fw_settings["fw_base_name"] = ""
    elif "fw_base_name" not in fw_settings:
        fw_settings["fw_base_name"] = fw_settings["fw_name"]

    setup_tasks = []
    if atoms:
        if not atoms_calc_from_spec:
            at = atoms2dict(atoms)
            if not isinstance(calc, str):
                if "k_grid_density" in update_calc_settings:
                    if not isinstance(calc, dict):
                        update_k_grid(
                            atoms, calc, update_calc_settings["k_grid_density"]
                        )
                    else:
                        recipcell = np.linalg.pinv(at["cell"]).transpose()
                        calc = update_k_grid_calc_dict(
                            calc,
                            recipcell,
                            at["pbc"],
                            update_calc_settings["k_grid_density"],
                        )

                cl = calc2dict(calc)

                for key, val in update_calc_settings.items():
                    if key != "k_grid_density":
                        cl = update_calc(cl, key, val)
                for key, val in cl.items():
                    at[key] = val
            else:
                cl = calc
                setup_tasks.append(
                    generate_update_calc_task(calc, update_calc_settings)
                )
        else:
            at = atoms
            cl = calc
            if update_calc_settings.keys():
                setup_tasks.append(
                    generate_update_calc_task(calc, update_calc_settings)
                )

        if "kpoint_density_spec" in fw_settings:
            setup_tasks.append(
                generate_mod_calc_task(
                    at, cl, "calculator", fw_settings["kpoint_density_spec"]
                )
            )
            cl = "calculator"
    else:
        at = None
        cl = None
    job_tasks = []
    for task_spec in task_spec_list:
        job_tasks.append(generate_task(task_spec, fw_settings, at, cl))
    return Firework(
        setup_tasks + job_tasks, name=fw_settings["fw_name"], spec=fw_settings["spec"]
    )


def get_phonon_task(func_kwargs, fw_settings=None):
    """
    Generate a parallel Phononpy or Phono3py calculation task
    Args:
        func_kwargs (dict): The defined kwargs for func
        fw_settings (dict): Settings used by fireworks to place objects in the right part of
                            the MongoDB
    Return (TaskSpec): The specification object of the task
    """
    if fw_settings is not None:
        fw_settings = fw_settings.copy()
    kwargs_init = {}
    kwargs_init_fw_out = {}
    preprocess_keys = {
        "ph_settings": ["supercell_matrix", "displacement"],
        "ph3_settings": ["supercell_matrix", "displacement", "cutoff_pair_distance"],
    }
    out_keys = ["walltime", "trajectory", "backup_folder", "serial"]
    for set_key in ["ph_settings", "ph3_settings"]:
        if set_key in func_kwargs:
            kwargs_init[set_key] = {}
            if "workdir" in func_kwargs[set_key]:
                wd = func_kwargs[set_key]["workdir"]
            else:
                wd = "."
            kwargs_init_fw_out[set_key] = {"workdir": wd}
            for key, val in func_kwargs[set_key].items():
                if key in preprocess_keys[set_key]:
                    kwargs_init[set_key][key] = val
                if key in out_keys:
                    kwargs_init_fw_out[set_key][key] = val
    if fw_settings and "kpoint_density_spec" in fw_settings:
        inputs = [fw_settings["kpoint_density_spec"]]
        args = []
        if "kpt_density" in func_kwargs:
            del func_kwargs["kpt_density"]
    elif "kpt_density" in func_kwargs:
        inputs = []
        args = [func_kwargs.pop("kpt_density")]
    else:
        inputs = []
        args = [None]

    return TaskSpec(
        "hilde.tasks.fireworks.phonopy_phono3py_functions.bootstrap_phonon",
        "hilde.tasks.fireworks.fw_out.phonons.post_init_mult_calcs",
        True,
        kwargs_init,
        inputs=inputs,
        args=args,
        func_fw_out_kwargs=kwargs_init_fw_out,
        make_abs_path=False,
    )


def get_ha_task(func_kwargs):
    """
    Generate a Harmonic Analysis task
    Args:
        func_kwargs (dict): The defined kwargs for func
    Return (TaskSpec): The specification object of the task
    """
    if "phonon_file" in func_kwargs:
        ph_file = func_kwargs["phonon_file"]
        inputs = list()
        if ph_file.split(".")[-1] == "yaml":
            ph = postprocess(ph_file)
        elif ph_file.split(".")[-1] == "gz" or ph_file.split(".")[-1] == "pick":
            ph = pread(ph_file)
        args = [phonon_to_dict(ph, to_mongo=True)]
    elif "prim_cell_file" in func_kwargs and "fc2_supercell_matrix" in func_kwargs:
        ph, _, _ = preprocess(
            read(func_kwargs["prim_cell_file"]), func_kwargs["fc2_supercell_matrix"]
        )
        func_kwargs["phonon_dict"] = phonon_to_dict(ph, to_mongo=True)
        args = list()
        inputs = list()
    else:
        args = list()
        inputs = ["ph_dict"]
    return TaskSpec(
        "hilde.tasks.fireworks.phonopy_phono3py_functions.setup_harmonic_analysis",
        "hilde.tasks.fireworks.fw_out.phonons.post_init_mult_calcs",
        True,
        func_kwargs,
        args=args,
        inputs=inputs,
        func_fw_out_kwargs=func_kwargs,
        make_abs_path=False,
    )


def get_phonon_analysis_task(func, func_kwargs, metakey, forcekey, timekey, make_abs_path=False):
    """
    Generate a serial Phononpy or Phono3py calculation task
    Args:
        func (str): The function path to the serial calculator
        func_kwargs (dict): The defined kwargs for func
        meta_key (str): Key to find the phonon calculation's metadata to recreate the trajectory
        force_key (str): Key to find the phonon calculation's force data to recreate the trajectory
        make_abs_path (bool): If True make the paths of directories absolute
    Return (TaskSpec): The specification object of the task
    """
    if "workdir" in func_kwargs and "init_wd" not in func_kwargs:
        func_kwargs["init_wd"] = func_kwargs["workdir"]
    if "converge_phonons" in func_kwargs and func_kwargs["converge_phonons"]:
        func_out = "hilde.tasks.fireworks.fw_out.phonons.converge_phonons"
    else:
        func_out = "hilde.tasks.fireworks.fw_out.phonons.add_phonon_to_spec"

    if "workdir" not in func_kwargs:
        func_kwargs["workdir"] = "."

    if "analysis_workdir" in func_kwargs:
        func_kwargs["workdir"] = func_kwargs["analysis_workdir"]

    if "trajectory" in func_kwargs:
        traj = func_kwargs["trajectory"]
    else:
        traj = "trajectory.son"
    func_kwargs["trajectory"] = func_kwargs["workdir"] + "/" + traj
    task_spec_list = []
    task_spec_list.append(
        TaskSpec(
            "hilde.tasks.fireworks.phonopy_phono3py_functions.collect_to_trajectory",
            "hilde.tasks.fireworks.fw_out.general.fireworks_no_mods_gen_function",
            False,
            args=[func_kwargs["trajectory"]],
            inputs=[forcekey, metakey],
            make_abs_path=make_abs_path,
        )
    )
    task_spec_list.append(
        TaskSpec(
            "hilde.tasks.fireworks.phonopy_phono3py_functions.phonon_postprocess",
            func_out,
            False,
            args=[func],
            inputs=[timekey],
            func_kwargs=func_kwargs,
            make_abs_path=make_abs_path,
        )
    )
    return task_spec_list


def get_relax_task(func_kwargs, func_fw_out_kwargs, make_abs_path=False):
    """ Gets the task spec for a relaxation step"""
    return TaskSpec(
        "hilde.relaxation.bfgs.relax",
        "hilde.tasks.fireworks.fw_out.relax.check_relaxation_complete",
        True,
        func_kwargs,
        func_fw_out_kwargs=func_fw_out_kwargs,
        make_abs_path=make_abs_path,
    )


def get_aims_task(func_kwargs, func_fw_out_kwargs, make_abs_path=False):
    """ Gets the task spec for an FHI-aims calculations"""
    return TaskSpec(
        "hilde.tasks.fireworks.calculate_wrapper.wrap_calculate",
        "hilde.tasks.fireworks.fw_out.relax.check_aims_complete",
        True,
        func_kwargs,
        func_fw_out_kwargs=func_fw_out_kwargs,
        make_abs_path=make_abs_path,
    )


def get_kgrid_task(func_kwargs, make_abs_path=False):
    """gets the task spec for a k-grid optimization"""
    return TaskSpec(
        "hilde.k_grid.converge_kgrid.converge_kgrid",
        "hilde.tasks.fireworks.fw_out.optimizations.check_kgrid_opt_completion",
        True,
        func_kwargs,
        make_abs_path=make_abs_path,
    )


def get_step_fw(step_settings, atoms=None, make_abs_path=False):
    """
    Generate a FireWork for the given step
    Args:
        step_settings (dict): parameters describing what the step is
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        make_abs_path (bool): If True make the paths of directories absolute
    Returns (list of Fireworks):
        The list of Fireworks for a given step in a WorkFlow
    """
    calc = setup_aims(settings=step_settings)
    if "control_kpt" in step_settings:
        update_k_grid(atoms, calc, step_settings.control_kpt.density)
    atoms.set_calculator(calc)
    atoms_hash, _ = hash_atoms_and_calc(atoms)
    fw_settings = step_settings.fw_settings.copy()
    if "from_db" not in fw_settings or not fw_settings.from_db:
        at = atoms
        cl = calc
    else:
        at = fw_settings.in_spec_atoms
        cl = fw_settings.in_spec_calc

    if "fw_spec" in step_settings:
        fw_settings["spec"] = step_settings.fw__spec
    else:
        fw_settings["spec"] = {}
    if "fw_spec_qadapter" in step_settings:
        fw_settings["spec"]["_queueadapter"] = dict(step_settings.fw_spec_qadapter)
    if "basisset" in step_settings:
        step_settings.control["basisset_type"] = step_settings.basisset.type
    if "db_storage" in step_settings and "db_path" in step_settings.db_storage:
        db_kwargs = {
            "db_path": step_settings.db_storage.db_path,
            "original_atom_hash": atoms_hash,
        }
    else:
        db_kwargs = None
    task_spec_list = []
    if "relaxation" in step_settings:
        fw_settings["fw_name"] = f"rel_{step_settings.basisset.type[:2]}"
        if db_kwargs:
            db_kwargs["calc_type"] = f"relaxation_{step_settings.basisset.type}"
        task_spec_list.append(
            get_relax_task(step_settings.relaxation, db_kwargs, make_abs_path)
        )
    elif "aims_calculation" in step_settings:
        fw_settings["fw_name"] = f"a_rel_{step_settings.basisset.type[:2]}"
        if db_kwargs:
            db_kwargs["calc_type"] = f"relaxation_{step_settings.basisset.type}"
            fw_out_kwargs = dict(db_kwargs, relax_step=0)
        else:
            fw_out_kwargs = {"relax_step": 0}
        task_spec_list.append(
            get_aims_task(
                step_settings.aims_calculation, fw_out_kwargs, make_abs_path
            )
        )
    elif "kgrid_opt" in step_settings:
        fw_settings["fw_name"] = "k_grid_opt"
        task_spec_list.append(get_kgrid_task(step_settings.kgrid_opt, make_abs_path))
    elif "phonopy" in step_settings or "phono3py" in step_settings:
        func_kwargs = {}
        fw_settings["fw_name"] = "phonon_init"

        if "phonopy" in step_settings:
            func_kwargs["ph_settings"] = step_settings.phonopy
        if "phono3py" in step_settings:
            func_kwargs["ph3_settings"] = step_settings.phono3py
        if (
            "spec" in fw_settings
            and "_queueadapter" in fw_settings["spec"]
            and "walltime" in fw_settings["spec"]["_queueadapter"]
        ):
            if "ph_settings" in func_kwargs and func_kwargs["ph_settings"]["serial"]:
                func_kwargs["ph_settings"]["walltime"] = get_time(
                    fw_settings["spec"]["_queueadapter"]["walltime"]
                )
            if "ph3_settings" in func_kwargs and func_kwargs["ph3_settings"]["serial"]:
                func_kwargs["ph3_settings"]["walltime"] = get_time(
                    fw_settings["spec"]["_queueadapter"]["walltime"]
                )
        if "control_kpt" in step_settings:
            func_kwargs["kpt_density"] = step_settings.control_kpt.density
        task_spec_list.append(get_phonon_task(func_kwargs, fw_settings=fw_settings))
    elif "harmonic_analysis" in step_settings:
        fw_settings["fw_name"] = "harmonic_analysis"
        if "phonon_file" in step_settings.harmonic_analysis:
            ph_file_suff = step_settings.harmonic_analysis.phonon_file.split(".")[-1]
            if ph_file_suff == "yaml":
                _, meta = reader(step_settings.harmonic_analysis.phonon_file, True)
                for key, val in meta["calculator"].items():
                    if key == "calculator":
                        val = val.lower()
                    meta["Phonopy"]["primitive"][key] = val
                meta["Phonopy"]["primitive"]["numbers"] = symbols2numbers(
                    meta["Phonopy"]["primitive"]["symbols"]
                )
                if "cell" in meta["Phonopy"]["primitive"]:
                    meta["Phonopy"]["primitive"]["pbc"] = True
                at = dict2atoms(meta["Phonopy"]["primitive"])
                cl = at.calc
            elif ph_file_suff == "gz" or ph_file_suff == "pick":
                ph = pread(step_settings.harmonic_analysis.phonon_file)
                at = to_Atoms(ph.get_supercell())
                cl = cl
            else:
                raise IOError("File type not supported")
            fw_settings["from_db"] = False
            if "in_spec_atoms" in fw_settings:
                fw_settings.pop("in_spec_atoms")
            if "in_spec_calc" in fw_settings:
                fw_settings.pop("in_spec_calc")
        task_spec_list.append(get_ha_task(step_settings.harmonic_analysis))
    else:
        raise ValueError("Type not defiend")
    fw_settings[
        "fw_name"
    ] += f"_{atoms.symbols.get_chemical_formula()}_{hash_atoms_and_calc(atoms)[0]}"

    fw_list = [
        generate_firework(
            task_spec_list,
            at,
            cl,
            atoms_calc_from_spec=fw_settings.from_db,
            fw_settings=fw_settings.copy(),
            update_calc_settings=step_settings.control,
        )
    ]
    if not ("phonopy" in step_settings or "phono3py" in step_settings):
        return fw_list, {}

    fw_settings = fw_settings.copy()
    task_spec_list = []
    if "phonopy" in step_settings:
        ts_list = get_phonon_analysis_task(
            "hilde.phonopy.postprocess.postprocess",
            step_settings.phonopy,
            "ph_metadata",
            "ph_forces",
            "ph_times",
            make_abs_path,
        )
        for task in ts_list:
            task_spec_list.append(task)
    if "phono3py" in step_settings:
        ts_list = get_phonon_analysis_task(
            "hilde.phono3py.postprocess.postprocess",
            step_settings.phono3py,
            "ph3_metadata",
            "ph3_forces",
            "ph3_times",
            make_abs_path,
        )
        for task in ts_list:
            task_spec_list.append(task)

    fw_settings[
        "fw_name"
    ] = f"phonon_analysis_{atoms.symbols.get_chemical_formula()}_{hash_atoms_and_calc(atoms)[0]}"

    fw_list.append(
        generate_firework(task_spec_list, None, None, fw_settings=fw_settings)
    )
    return fw_list, {fw_list[0]: fw_list[1]}


def generate_workflow(
    steps=Settings(), fw_settings=None, atoms=None, make_abs_path=False, no_dep=False
):
    """
    Generates a workflow from given set of steps
    Args
        steps (list of dicts): List of parameters for all the steps in a given system
        fw_settings (dict): FireWorks settings for the given task
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        make_abs_path (bool): If True make the paths of directories absolute
        no_dep (bool): If True each FireWork in a Workflow is independent
    Returns (Workflow or None):
        Either adds the workflow to the launchpad or returns it
    """
    if not isinstance(steps, list):
        fw_settings = steps.fw_settings
        steps = [steps]
    fw_steps = []
    fw_dep = {}
    for step in steps:
        if "from_db" not in step.fw_settings:
            step.fw_settings["from_db"] = False
        fw_list, step_dep = get_step_fw(step, atoms, make_abs_path)
        if len(fw_steps) != 0:
            for fw in fw_steps[-1]:
                if fw in fw_dep:
                    fw_dep[fw] = [fw_dep[fw]] + fw_list
                else:
                    fw_dep[fw] = fw_list
        for key, val in step_dep.items():
            fw_dep[key] = val
        fw_steps.append(fw_list)
    fws = [fw for step_list in fw_steps for fw in step_list]
    if no_dep:
        fw_dep = {}
    if fw_settings and "to_launchpad" in fw_settings and fw_settings["to_launchpad"]:
        if "launchpad_yaml" in fw_settings:
            launchpad = LaunchPadHilde.from_file(fw_settings["launchpad_yaml"])
        else:
            launchpad = LaunchPadHilde.auto_load()
        launchpad.add_wf(Workflow(fws, fw_dep, name=fw_settings["name"]))
        return None
    return Workflow(fws, fw_dep, name=fw_settings["name"])
