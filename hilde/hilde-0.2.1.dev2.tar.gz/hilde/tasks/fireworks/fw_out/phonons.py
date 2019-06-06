"""Generate FWActions after setting Phonon Calculations"""
from ase.symbols import Symbols

from fireworks import FWAction, Workflow

from phonopy import Phonopy

import numpy as np

from hilde.fireworks.workflows.workflow_generator import (
    generate_firework,
    get_time,
    to_time_str,
)
from hilde.fireworks.workflows.phonon_wf import (
    generate_phonon_fw,
    generate_phonon_postprocess_fw,
)
from hilde.phonon_db.ase_converters import calc2dict, atoms2dict
from hilde.helpers.k_grid import k2d
from hilde.helpers.supercell import make_cubic_supercell
from hilde.materials_fp.material_fingerprint import (
    get_phonon_dos_fingerprint_phononpy,
    fp_tup,
    scalar_product,
)
from hilde.phonon_db.row import phonon_to_dict, phonon3_to_dict
from hilde.structure.convert import to_Atoms
from hilde.trajectory import reader


def post_init_mult_calcs(
    atoms, calc, outputs, func, func_fw_out, func_kwargs, func_fw_kwargs, fw_settings
):
    """
    @brief      postprocessing for initializing parallel force calculaitons

    @param      atoms           The ASE atoms object
    @param      calc            The ASE calculate
    @param      outputs         The outputs after setting up claculations
    @param      func            The function used to initialize the calculations
    @param      func_fw_out     The path to this function
    @param      func_kwargs     The kwargs for the initializer
    @param      func_fw_kwargs  The kwargs for this function
    @param      fw_settings     The FireWorks settings

    @return     FWAction that will run all force calculations
    """
    if fw_settings is None:
        fw_settings = dict()
    update_spec = dict()
    detours = []
    for out in outputs:
        prefix = out["prefix"]
        fw_set = fw_settings.copy()
        func_set = out["settings"]
        if prefix + "_settings" in func_fw_kwargs:
            func_set = dict(func_set, **func_fw_kwargs[prefix + "_settings"])
        if "serial" not in func_set:
            func_set["serial"] = True
        update_spec[prefix + "_metadata"] = out["metadata"]
        if "spec" in fw_set:
            fw_set["spec"].update(update_spec)
        else:
            fw_set["spec"] = update_spec.copy()
        fw_set["mod_spec_add"] = prefix + "_forces"
        fw_set["metadata_spec"] = prefix + "_metadata"
        if "calculator" in out:
            calc_dict = calc2dict(out["calculator"])
        else:
            calc_dict = calc.copy()
        if (
            "prev_dos_fp" in fw_set
            and "walltime" in fw_set
            and "serial" in func_set
            and func_set["serial"]
        ):
            fw_set["walltime"] = to_time_str(
                get_time(fw_set["walltime"]) * len(out["atoms_to_calculate"])
            )
        detours = get_detours(
            out["atoms_to_calculate"],
            calc_dict,
            prefix,
            func_set,
            fw_set,
            update_spec,
            atoms,
            detours,
        )
    return FWAction(update_spec=update_spec, detours=detours)


def get_detours(
    atoms_to_calculate,
    calc_dict,
    prefix,
    calc_kwargs,
    fw_settings,
    update_spec,
    atoms=None,
    detours=None,
):
    """
    Add a set of detours for force calculations
    Args:
        atoms_to_calculate (list of ASE Atoms objects): List of structures to calculate forces for
        calc_dict (dict): Dictionary representation of the ASE Calculator Object
        prefix (str): prefix to add to force calculations
        calc_kwargs (dict): A set of kwargs for the Force calculations
        fw_settings (dict): A dictionary describing all FireWorks settings
        update_spec (dict): Parmeters to be added to the FireWorks spec
        atoms (ASE Atoms Object): Initial ASE Atoms object representation of the structure
        detours (list of Fireworks): Current list of force calculations to perform
    Returns (list of Fireworks): The updated detours object
    """
    if detours is None:
        detours = []
    fw_settings["time_spec_add"] = prefix + "_times"
    if "walltime" in calc_kwargs:
        if "spec" in fw_settings and "_queueadapter" in fw_settings["spec"]:
            if "walltime" in fw_settings["spec"]["_queueadapter"]:
                calc_kwargs["walltime"] = get_time(fw_settings["spec"]["_queueadapter"]["walltime"]) - 120
            else:
                fw_settings["spec"]["_queueadapter"]["walltime"] = to_time_str(calc_kwargs["walltime"]) + 120
        else:
            if "spec" not in fw_settings:
                fw_settings["spec"] = dict()
            fw_settings["spec"]["_queueadapter"] = {
                "walltime": to_time_str(calc_kwargs["walltime"] + 120)
            }

    if calc_kwargs["serial"]:
        update_spec[prefix + "_calculated_atoms"] = [
            atoms2dict(at) for at in atoms_to_calculate
        ]
        update_spec[prefix + "_calculator"] = calc_dict
        fw_settings["spec"].update(update_spec)
        fw_settings["calc_atoms_spec"] = prefix + "_calculated_atoms"
        fw_settings["calc_spec"] = prefix + "_calculator"
        return add_socket_calc_to_detours(detours, atoms, calc_kwargs, fw_settings, prefix)
    return add_single_calc_to_detours(
        detours, calc_kwargs, atoms, atoms_to_calculate, calc_dict, fw_settings, prefix
    )


def add_socket_calc_to_detours(detours, atoms, func_kwargs, fw_settings, prefix):
    """
    Generates a Firework to run a socket calculator and adds it to the detours
    Args:
        detours (list of Fireworks): Current list of detours
        atoms (ASE Atoms Object): Initial ASE Atoms object representation of the structure
        func_kwargs (dict): kwargs needed to do the socket I/O calculation
        fw_settings (dict): FireWorks settings
        prefix (str): ph for phonopy and ph3 for phono3py calculations
    Returns (list of Fireworks): an updated detours list
    """
    calc_kwargs = {}
    calc_keys = ["trajectory", "workdir", "backup_folder", "walltime"]
    for key in calc_keys:
        if key in func_kwargs:
            calc_kwargs[key] = func_kwargs[key]
    fw_set = fw_settings.copy()
    fw_set["fw_name"] = (
            prefix + f"_serial_forces_{Symbols(atoms['numbers']).get_chemical_formula()}"
        )
    fw = generate_firework(
        func="hilde.tasks.fireworks.calculate_wrapper.wrap_calc_socket",
        func_fw_out="hilde.tasks.fireworks.fw_out.calculate.socket_calc_check",
        func_kwargs=calc_kwargs,
        atoms_calc_from_spec=False,
        inputs=[
            prefix + "_calculated_atoms",
            prefix + "_calculator",
            prefix + "_metadata",
        ],
        fw_settings=fw_set.copy(),
    )
    detours.append(fw)
    return detours


def add_single_calc_to_detours(
    detours, func_fw_kwargs, atoms, atoms_list, calc_dict, fw_settings, prefix
):
    """
    Adds a group of Fireworks to run as single calculations
    Args:
        detours (list of Fireworks): Current list of detours
        func_kwargs (dict): kwargs needed to do the socket I/O calculation
        atoms (dict): Dictionary representing the ASE Atoms object of theprimitive cell
        atoms_list (list of Atoms): List of supercells to perform force calculations on
        calc_dict (dict): Dictionary representing the ASE Calculator for the force calculations
        fw_settings (dict): FireWorks settings
        prefix (str): ph for phonopy and ph3 for phono3py calculations
    Returns (list of Fireworks): an updated detours list
    """
    for i, sc in enumerate(atoms_list):
        if not sc:
            continue
        fw_settings = fw_settings.copy()
        fw_settings["from_db"] = False
        if "kpoint_density_spec" in fw_settings:
            del fw_settings["kpoint_density_spec"]
        sc.info["displacement_id"] = i
        sc_dict = atoms2dict(sc)
        for key, val in calc_dict.items():
            sc_dict[key] = val
        calc_kwargs = {"workdir": func_fw_kwargs["workdir"] + f"/{i:05d}"}
        fw_settings["fw_name"] = (
            prefix + f"forces_{Symbols(sc_dict['numbers']).get_chemical_formula()}_{i}"
        )
        detours.append(
            generate_firework(
                func="hilde.tasks.fireworks.calculate_wrapper.wrap_calculate",
                func_fw_out="hilde.tasks.fireworks.fw_out.calculate.mod_spec_add",
                func_kwargs=calc_kwargs,
                atoms=sc_dict,
                calc=calc_dict,
                atoms_calc_from_spec=False,
                fw_settings=fw_settings,
            )
        )
    return detours


def add_phonon_to_spec(func, func_fw_out, *args, fw_settings=None, **kwargs):
    """
    Add the phonon_dict to the spec
    Args:
        func (str): Path to the phonon analysis function
        func_fw_out (str): Path to this function
        args (list): list arguments passed to the phonon analysis
        fw_settings (dict): Dictionary for the FireWorks specific systems
        kwargs (dict): Dictionary of keyword arguments
            Mandatory Keys:
                outputs: The Phonopy object from post-processing
    Returns (FWAction): FWAction that adds the phonon_dict to the spec
    """
    _, metadata = reader(kwargs["trajectory"], True)
    calc_dict = metadata["calculator"]
    calc_dict["calculator"] = calc_dict["calculator"].lower()
    if "phono3py" in args[0]:
        update_spec = {
            "ph3_dict": phonon3_to_dict(kwargs["outputs"]),
            "ph3_calculator": calc_dict,
            "ph3_supercell": atoms2dict(to_Atoms(kwargs["outputs"].get_primitive())),
        }
    else:
        update_spec = {
            "ph_dict": phonon_to_dict(kwargs["outputs"]),
            "ph_calculator": calc_dict,
            "ph_supercell": atoms2dict(to_Atoms(kwargs["outputs"].get_primitive())),
        }
    return FWAction(update_spec=update_spec)


def converge_phonons(func, func_fw_out, *args, fw_settings=None, **kwargs):
    """
    Check phonon convergence and set up future calculations after a phonon calculation
    Args:
        func (str): Path to the phonon analysis function
        func_fw_out (str): Path to this function
        args (list): list arguments passed to the phonon analysis
        fw_settings (dict): Dictionary for the FireWorks specific systems
        kwargs (dict): Dictionary of keyword arguments
            Mandatory Keys:
                outputs: The Phonopy object from post-processing
                serial (bool): If True use a serial calculation
                init_wd (str): Path to the base phonon force calculations
                trajectory (str): trajectory file name
    Returns (FWAction): Increases the supercell size or adds the phonon_dict to the spec
    """
    calc_time = np.max(args[1])

    if fw_settings:
        fw_settings["from_db"] = False
        if "in_spec_calc" in fw_settings:
            fw_settings.pop("in_spec_calc")
        if "in_spec_atoms" in fw_settings:
            fw_settings.pop("in_spec_atoms")
    _, metadata = reader(kwargs["trajectory"], True)
    calc_dict = metadata["calculator"]
    calc_dict["calculator"] = calc_dict["calculator"].lower()
    ph = kwargs["outputs"]
    prev_dos_fp = None
    if isinstance(ph, Phonopy):
        ph.set_mesh([51, 51, 51])
        if "prev_dos_fp" in kwargs:
            prev_dos_fp = kwargs["prev_dos_fp"].copy()
            de = prev_dos_fp[0][0][1] - prev_dos_fp[0][0][0]
            min_f = prev_dos_fp[0][0][0] - 0.5 * de
            max_f = prev_dos_fp[0][0][-1] + 0.5 * de
            ph.set_total_DOS(freq_min=min_f, freq_max=max_f, tetrahedron_method=True)
        else:
            ph.set_total_DOS(tetrahedron_method=True)
        dos_fp = get_phonon_dos_fingerprint_phononpy(ph, nbins=201)
        conv_crit = 0.95 if "conv_crit" not in kwargs else kwargs["conv_crit"]
        if prev_dos_fp is not None and check_phonon_conv(
            dos_fp, prev_dos_fp, conv_crit
        ):
            update_spec = {
                "ph_dict": phonon_to_dict(ph),
                "ph_calculator": calc_dict,
                "ph_supercell": atoms2dict(to_Atoms(ph.get_primitive())),
            }
            return FWAction(update_spec=update_spec)
        # Reset dos_fp to include full Energy Range for the material
        ph.set_total_DOS(tetrahedron_method=True)
        dos_fp = get_phonon_dos_fingerprint_phononpy(ph, nbins=201)

        # If Not Converged update phonons
        pc = to_Atoms(ph.get_primitive())
        # if "add_atoms" in kwargs and kwargs["add_atoms"]:
        _, sc_mat = make_cubic_supercell(
            pc,
            len(pc.numbers) * np.linalg.det(ph.get_supercell_matrix()) + 50,
            deviation=0.4,
        )
        # else:
        #     sc_mat = ph.get_supercell_matrix()
        #     sc_mat[0] += 1
        #     sc_mat[4] += 1
        #     sc_mat[8] += 1
        fw_settings["in_spec_calc"] = "calculator"
        update_spec = {"calculator": calc_dict, "prev_dos_fp": dos_fp}
        if "kpoint_density_spec" not in fw_settings:
            fw_settings["kpoint_density_spec"] = "kgrid"
        update_spec[fw_settings["kpoint_density_spec"]] = k2d(
            pc, calc_dict["calculator_parameters"]["k_grid"]
        )
        if "spec" in fw_settings:
            fw_settings["spec"].update(update_spec)
        else:
            fw_settings["spec"] = update_spec.copy()
        displacement = ph._displacement_dataset["first_atoms"][0]["displacement"]
        disp_mag = np.linalg.norm(displacement)
        func_kwargs = {
            "type": "ph",
            "displacement": disp_mag,
            "supercell_matrix": sc_mat,
            "serial": kwargs["serial"],
            "converge_phonons": True,
        }
        kwargs.update(func_kwargs)

        if "spec" in fw_settings:
            fw_settings["spec"]["prev_dos_fp"] = dos_fp
        else:
            fw_settings["spec"] = {"prev_dos_fp": dos_fp}

        if "spec" in fw_settings and "_queueadapter" in fw_settings["spec"]:
            time_scaling = (
                np.linalg.det(sc_mat) / np.linalg.det(ph.get_supercell_matrix())
            ) ** 3.0
            fw_settings["spec"]["_queueadapter"]["walltime"] = to_time_str(
                calc_time * time_scaling
            )
            fw_settings["spec"]["_queueadapter"]["nodes"] = 1
            qadapter = fw_settings["spec"]["_queueadapter"]
        else:
            qadapter = None

        init_wd = kwargs["init_wd"].split("/")

        while "" in init_wd:
            init_wd.remove("")
        if kwargs["init_wd"][0] == "/":
            init_wd = [""] + init_wd

        if len(init_wd[-1]) > 9 and init_wd[-1][:9] == "sc_natoms_":
            wd = "/".join(init_wd[:-1])
        else:
            wd = "/".join(init_wd)
        workdir_init = (
            wd
            + f"/sc_natoms_{int(np.round(np.linalg.det(sc_mat)*len(pc.numbers))+0.5)}"
        )
        init_fw = generate_phonon_fw(
            pc, workdir_init, fw_settings, qadapter, func_kwargs, update_in_spec=False
        )

        analysis_wd = kwargs["workdir"].split("/")

        while "" in analysis_wd:
            analysis_wd.remove("")

        while "phonopy_analysis" in analysis_wd:
            analysis_wd.remove("phonopy_analysis")

        while "phono3py_analysis" in analysis_wd:
            analysis_wd.remove("phono3py_analysis")

        if kwargs["workdir"][0] == "/":
            analysis_wd = [""] + analysis_wd

        if "sc_natoms" in analysis_wd[-1]:
            a_wd = "/".join(analysis_wd[:-1])
        else:
            a_wd = "/".join(analysis_wd)

        a_wd += f"/sc_natoms_{int(np.linalg.det(sc_mat)*len(pc.numbers)+0.5)}"

        kwargs["prev_dos_fp"] = dos_fp
        kwargs["trajectory"] = kwargs["trajectory"].split("/")[-1]

        analysis_fw = generate_phonon_postprocess_fw(
            pc, a_wd, fw_settings, kwargs, wd_init=wd
        )

        analysis_fw.parents = [init_fw]
        detours = [init_fw, analysis_fw]
        wf = Workflow(detours, {init_fw: [analysis_fw]})
        return FWAction(detours=wf, update_spec={"prev_dos_fp": dos_fp})

    from phono3py.phonon3 import Phono3py

    return FWAction()


def check_phonon_conv(dos_fp, prev_dos_fp, conv_crit):
    """ Checks if the density of state finger prints are converged """
    for ll in range(4):
        prev_dos_fp[ll] = np.array(prev_dos_fp[ll])
    prev_dos_fp = fp_tup(prev_dos_fp[0], prev_dos_fp[1], prev_dos_fp[2], prev_dos_fp[3])
    return scalar_product(dos_fp, prev_dos_fp, col=1, pt=0, normalize=False, tanimoto=True) >= conv_crit
