""" Generate a phonon workflow for Fireworks """
import numpy as np
from fireworks import Workflow
from hilde.fireworks.launchpad import LaunchPadHilde
from hilde.fireworks.workflows.workflow_generator import (
    generate_firework,
    get_phonon_task,
    get_phonon_analysis_task,
    get_time,
    get_aims_task,
    get_kgrid_task,
    get_ha_task,
    to_time_str,
)
from hilde.helpers.hash import hash_atoms_and_calc
from hilde.phonopy.wrapper import defaults as ph_defaults, preprocess
from hilde.phono3py.wrapper import defaults as ph3_defaults


def update_fw_settings(fw_settings, fw_name, queueadapter=None, update_in_spec=True):
    """
    update the fw_settings for the next step
    Args:
        fw_settings(dict): Current fw_settings
        fw_name(str): name of the current step
        queueadapter(dict): dict describing the queueadapter changes for this firework
        update_in_spec(bool): If true move current out_spec to be in_spec
    Returns(dict): The updated fw_settings
    """
    if "out_spec_atoms" in fw_settings and update_in_spec:
        fw_settings["in_spec_atoms"] = fw_settings["out_spec_atoms"]
        fw_settings["in_spec_calc"] = fw_settings["out_spec_calc"]
        fw_settings["from_db"] = True

    fw_settings["out_spec_atoms"] = fw_name + "_atoms"
    fw_settings["out_spec_calc"] = fw_name + "_calc"
    fw_settings["fw_name"] = fw_name
    if "spec" not in fw_settings:
        fw_settings["spec"] = {}
    if queueadapter:
        fw_settings["spec"]["_queueadapter"] = queueadapter
    elif "_queueadapter" in fw_settings["spec"]:
        del fw_settings["spec"]["_queueadapter"]

    return fw_settings


def generate_fw(
    atoms, task_list, fw_settings, qadapter, update_settings=None, update_in_spec=True
):
    """
    Generates a FireWork
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        task_list (list of TaskSpecs): Definitions for the tasks to be run
        fw_settings (dict): FireWork settings for the step
        qadapter (dict): The queueadapter for the step
        update_settings (dict): update calculator settings
        update_in_spec (bool): If True move the current out_spec to be in_spec
    Returns (Firework): A firework for the task
    """
    fw_settings = update_fw_settings(
        fw_settings, fw_settings["fw_name"], qadapter, update_in_spec=update_in_spec
    )
    fw_settings[
        "fw_name"
    ] += f"_{atoms.symbols.get_chemical_formula()}_{hash_atoms_and_calc(atoms)[0]}"
    if not update_settings:
        update_settings = {}
    at = atoms if "in_spec_atoms" not in fw_settings else fw_settings["in_spec_atoms"]
    cl = (
        atoms.calc if "in_spec_calc" not in fw_settings else fw_settings["in_spec_calc"]
    )
    return generate_firework(
        task_list, at, cl, fw_settings, update_calc_settings=update_settings
    )


def generate_kgrid_fw(atoms, wd, fw_settings, qadapter, dfunc_min=1e-12):
    """
    Generate a k-grid optimization Firework
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        wd (str): Workdirectory
        fw_settings (dict): Firework settings for the step
        qadapter (dict): The queueadapter for the step
        dfunc_min (float): minimum value for the change in total energy when converging the k-grid
    Returns (Firework): Firework for the k-grid optimization
    """
    func_kwargs = {
        "workdir": wd + "/" + fw_settings["fw_name"] + "/",
        "trajectory": "kpt_trajectory.son",
        "dfunc_min": dfunc_min,
    }
    if qadapter and "walltime" in qadapter:
        func_kwargs["walltime"] = get_time(qadapter["walltime"])
    else:
        func_kwargs["walltime"] = 1800

    task_spec = get_kgrid_task(func_kwargs)
    return generate_fw(atoms, task_spec, fw_settings, qadapter)


def generate_relax_fw(atoms, wd, fw_settings, qadapter, rel_settings):
    """
    Generates a Firework for the relaxation step
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        wd (str): Workdirectory
        fw_settings (dict): Firework settings for the step
        qadapter (dict): The queueadapter for the step
        rel_settings (dict): kwargs for the relaxation step
    Returns (Firework): Firework for the relaxation step
    """
    fw_settings["fw_name"] = rel_settings["basisset_type"] + "_relax"
    func_kwargs = {"workdir": wd + "/" + fw_settings["fw_name"] + "/"}
    fw_out_kwargs = {"relax_step": 0}
    task_spec = get_aims_task(func_kwargs, fw_out_kwargs)

    if "rel_method" in rel_settings:
        method = func_kwargs.pop("rel_method")
    else:
        method = "ltrm"

    if "conv_crit" in rel_settings:
        force_crit = str(rel_settings.pop("conv_crit"))
    else:
        force_crit = "5e-3"

    update_settings = {
        "relax_geometry": method + " " + force_crit,
        "relax_unit_cell": "full",
        "basisset_type": rel_settings["basisset_type"],
        "scaled": True,
        "use_sym": True,
    }
    return generate_fw(atoms, task_spec, fw_settings, qadapter, update_settings, True)


def generate_phonon_fw(
    atoms, wd, fw_settings, qadapter, ph_settings, update_in_spec=True
):
    """
    Generates a Firework for the phonon initialization
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        wd (str): Workdirectory
        fw_settings (dict): Firework settings for the step
        qadapter (dict): The queueadapter for the step
        ph_settings (dict): kwargs for the phonons
        update_settings (dict): calculator update settings
    Returns (Firework): Firework for the phonon initialization
    """
    if (
        "serial" in ph_settings
        and ph_settings["serial"]
        and "spec" in fw_settings
        and "prev_dos_fp" in fw_settings["spec"]
    ):
        _, _, scs = preprocess(atoms, ph_settings["supercell_matrix"])
        qadapter["walltime"] = to_time_str(get_time(qadapter["walltime"]) * len(scs))

    if qadapter and "walltime" in qadapter:
        ph_settings["walltime"] = get_time(qadapter["walltime"])
    else:
        ph_settings["walltime"] = 1800

    update_settings = {}
    if "basisset_type" in ph_settings:
        update_settings["basisset_type"] = ph_settings.pop("basisset_type")
    if "socket_io_port" in ph_settings:
        update_settings["use_pimd_wrapper"] = ph_settings.pop("socket_io_port")
    elif "use_pimd_wrapper" in ph_settings:
        update_settings["use_pimd_wrapper"] = ph_settings.pop("use_pimd_wrapper")

    typ = ph_settings.pop("type")
    fw_settings["fw_name"] = typ
    ph_settings["workdir"] = wd + "/" + typ + "/"
    func_kwargs = {typ + "_settings": ph_settings.copy()}
    task_spec = get_phonon_task(func_kwargs, fw_settings)
    return generate_fw(
        atoms, task_spec, fw_settings, qadapter, update_settings, update_in_spec
    )


def generate_phonon_postprocess_fw(atoms, wd, fw_settings, ph_settings, wd_init=None):
    """
    Generates a Firework for the phonon analysis
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        wd (str): Workdirectory
        fw_settings (dict): Firework settings for the step
        ph_settings (dict): kwargs for the phonon analysis
        wd_init (str): workdir for the initial phonon force calculations
    Returns (Firework): Firework for the phonon analysis
    """
    if ph_settings.pop("type") == "ph":
        fw_settings["mod_spec_add"] = "ph"
        fw_settings["fw_name"] = "phonopy_analysis"
    else:
        fw_settings["fw_name"] = "phono3py_analysis"
        fw_settings["mod_spec_add"] = "ph3"
    fw_settings["mod_spec_add"] += "_forces"

    func_kwargs = ph_settings.copy()
    if "workdir" in func_kwargs:
        func_kwargs.pop("workdir")
    func_kwargs["analysis_workdir"] = wd + "/" + fw_settings["fw_name"] + "/"
    func_kwargs["init_wd"] = wd_init
    task_spec = get_phonon_analysis_task(
        "hilde." + fw_settings["fw_name"][:-9] + ".postprocess.postprocess",
        func_kwargs,
        fw_settings["mod_spec_add"][:-7] + "_metadata",
        fw_settings["mod_spec_add"],
        fw_settings["mod_spec_add"][:-7] + "_times",
        False,
    )
    fw_settings[
        "fw_name"
    ] += f"_{atoms.symbols.get_chemical_formula()}_{hash_atoms_and_calc(atoms)[0]}"
    return generate_firework(task_spec, None, None, fw_settings=fw_settings.copy())


def generate_ha_fw(atoms, wd, fw_settings, qadapter, ha_settings):
    """
    Generates a Firework for the phonon initialization
    Args:
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        wd (str): Workdirectory
        fw_settings (dict): Firework settings for the step
        qadapter (dict): The queueadapter for the step
        ha_settings (dict): kwargs for the harmonic analysis
    Returns (Firework): Firework for the harmonic analysis initialization
    """
    if qadapter and "walltime" in qadapter:
        ha_settings["walltime"] = get_time(qadapter["walltime"])
    else:
        ha_settings["walltime"] = 1800
    fw_settings["fw_name"] = "harmonic_analysis"
    fw_settings["in_spec_atoms"] = "ph_supercell"
    fw_settings["in_spec_calc"] = "ph_calculator"
    fw_settings.pop("kpoint_density_spec")
    fw_settings["from_db"] = True
    fw_settings["time_spec_add"] = "ha_times"
    ha_settings["workdir"] = wd + "/harmonic_analysis/"
    task_spec = get_ha_task(ha_settings)
    return generate_fw(atoms, task_spec, fw_settings, qadapter, None, False)


def generate_phonon_workflow(workflow, atoms, fw_settings):
    """
    Generates a workflow from given set of steps
    Args
        workflow (list of dicts): List of parameters for all the steps in a given system
        atoms (ASE atoms object, dict): ASE Atoms object to preform the calculation on
        fw_settings (dict): Firework settings for the step
    Returns (Workflow or None):
        Either adds the workflow to the launchpad or returns it
    """
    fw_steps = []
    fw_dep = {}

    fw_settings["fw_name"] = "kgrid_opt"
    fw_settings["out_spec_k_den"] = "kgrid"
    # K-grid optimization
    if "kgrid_qadapter" in workflow:
        qadapter = workflow["kgrid_qadapter"]
    else:
        qadapter = None
    if "kgrid_dfunc_min" in workflow.general:
        dfunc_min = workflow.general.kgrid_dfunc_min
    else:
        dfunc_min = 1e-12
    fw_steps.append(
        generate_kgrid_fw(
            atoms,
            workflow.general.workdir_cluster,
            fw_settings,
            qadapter,
            dfunc_min=dfunc_min,
        )
    )
    # Light Basis Set Relaxation
    fw_settings["kpoint_density_spec"] = "kgrid"
    del fw_settings["out_spec_k_den"]
    fw_settings["from_db"] = True
    # if "basisset" in workflow.general and workflow.general.basisset == "light_intermediate":
    #     light_relax_set = {"basisset_type": workflow.general.basisset}
    # else:
    light_relax_set = {"basisset_type": "light"}
    if "light_rel_qadapter" in workflow:
        qadapter = workflow["light_rel_qadapter"]
    else:
        qadapter = None

    fw_steps.append(
        generate_relax_fw(
            atoms,
            workflow.general.workdir_cluster,
            fw_settings,
            qadapter,
            light_relax_set,
        )
    )
    fw_dep[fw_steps[-2]] = fw_steps[-1]

    # Tighter Basis Set Relaxation
    if "basisset" in workflow.general:
        basis = workflow.general.pop("basisset")
    else:
        basis = None
    use_tight_relax = False
    if "use_tight_relax" in workflow.general and workflow.general["use_tight_relax"]:
        use_tight_relax = True
    if basis != "light" or use_tight_relax:
        if use_tight_relax:
            tighter_relax_set = {"basisset_type": "tight"}
        else:
            tighter_relax_set = {"basisset_type": basis}
        if "tight_rel_qadapter" in workflow:
            qadapter = workflow["tight_rel_qadapter"]
        elif f"{basis}_rel_qadapter" in workflow:
            qadapter = workflow[f"{basis}_rel_qadapter"]
        elif f"light_rel_qadapter":
            qadapter = workflow["light_rel_qadapter"]
        else:
            qadapter = None
        fw_steps.append(
            generate_relax_fw(
                atoms,
                workflow.general.workdir_cluster,
                fw_settings,
                qadapter,
                tighter_relax_set,
            )
        )
        fw_dep[fw_steps[-2]] = fw_steps[-1]

    pre_ph_fw = fw_steps[-1]
    fw_dep[pre_ph_fw] = []

    # Phonon Calculations

    # Second Order
    phonopy_set = ph_defaults.copy()
    del phonopy_set["trigonal"]
    del phonopy_set["q_mesh"]
    phonopy_set["serial"] = True
    phonopy_set["type"] = "ph"
    phonopy_set["basisset_type"] = basis

    if "phonopy_qadapter" in workflow:
        qadapter = workflow["phonopy_qadapter"]
    else:
        qadapter = None
    if "phonopy" in workflow:
        for key, val in workflow.phonopy.items():
            if key != "walltime":
                phonopy_set[key] = val
    if "supercell_matrix" not in phonopy_set:
        phonopy_set["supercell_matrix"] = np.eye(3)
        # phonopy_set["converge_sc"] = True
    fw_steps.append(
        generate_phonon_fw(
            atoms,
            workflow.general.workdir_cluster,
            fw_settings,
            qadapter,
            phonopy_set.copy(),
        )
    )
    fw_dep[pre_ph_fw].append(fw_steps[-1])
    fw_steps.append(
        generate_phonon_postprocess_fw(
            atoms,
            workflow.general.workdir_local,
            fw_settings,
            phonopy_set,
            wd_init=workflow.general.workdir_cluster,
        )
    )
    fw_dep[fw_steps[-2]] = fw_steps[-1]
    if (
        "use_third" in workflow.general and workflow.general.use_third
    ) and "phono3py" in workflow:
        phono3py_set = ph3_defaults.copy()
        phono3py_set["serial"] = True
        phono3py_set["type"] = "ph3"
        phono3py_set["basisset_type"] = basis
        del phono3py_set["displacement"]
        del phono3py_set["cutoff_pair_distance"]
        del phono3py_set["q_mesh"]

        if "phono3py_qadapter" in workflow:
            qadapter = workflow["phono3py_qadapter"]
        else:
            qadapter = None
        if "phono3py" in workflow:
            for key, val in workflow.phono3py.items():
                if key != "walltime":
                    phono3py_set[key] = val
        if "supercell_matrix" not in phono3py_set:
            phono3py_set["supercell_matrix"] = np.eye(3)
            # phono3py_set["converge_sc"] = True
        fw_steps.append(
            generate_phonon_fw(
                atoms,
                workflow.general.workdir_cluster,
                fw_settings,
                qadapter,
                phono3py_set.copy(),
                update_in_spec=False,
            )
        )
        fw_dep[pre_ph_fw].append(fw_steps[-1])
        fw_steps.append(
            generate_phonon_postprocess_fw(
                atoms,
                workflow.general.workdir_local,
                fw_settings,
                phono3py_set,
                wd_init=workflow.general.workdir_cluster,
            )
        )
        fw_dep[fw_steps[-2]] = fw_steps[-1]

    # Harmonic Analysis
    if "harmonic_analysis" in workflow:
        if "harmonic_analysis_qadapter" in workflow:
            qadapter = workflow["harmonic_analysis_qadapter"]
        elif "phonopy_qadapter" in workflow:
            qadapter = workflow["phonopy_qadapter"]
        else:
            qadapter = None

        ha_set = {}
        for key, val in workflow.harmonic_analysis.items():
            if key != "walltime":
                ha_set[key] = val
        fw_steps.append(
            generate_ha_fw(
                atoms,
                workflow.general.workdir_cluster,
                fw_settings,
                qadapter,
                ha_set.copy(),
            )
        )
        fw_dep[fw_steps[-2]] = fw_steps[-1]

    if "launchpad_yaml" in fw_settings:
        launchpad = LaunchPadHilde.from_file(fw_settings["launchpad_yaml"])
    else:
        launchpad = LaunchPadHilde.auto_load()
    launchpad.add_wf(Workflow(fw_steps, fw_dep, name=fw_settings["name"]))
