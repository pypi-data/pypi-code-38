"""Functions used to wrap around HiLDe Phonopy/Phono3py functions"""
from pathlib import Path

from ase import units as u
from ase.md.velocitydistribution import PhononHarmonics

from h5py import File

import numpy as np

from hilde import konstanten as const
from hilde.helpers.converters import input2dict
from hilde.phonon_db.ase_converters import dict2atoms
from hilde.phonon_db.row import PhononRow, phonon_to_dict
from hilde.phonopy import displacement_id_str
from hilde.phonopy.workflow import bootstrap
from hilde.phonopy.wrapper import preprocess
from hilde.settings import Settings, AttributeDict
from hilde.structure.convert import to_Atoms_db
from hilde.tasks.calculate import calculate_socket
from hilde.tasks.fireworks.general_py_task import get_func
from hilde.tdep.wrapper import remap_forceconstant
from hilde.trajectory import step2file, metadata2file


def bootstrap_phonon(
    atoms, calc, kpt_density=None, ph_settings=None, ph3_settings=None, fw_settings=None
):
    """
    Creates a Settings object and passes it to the bootstrap function
    Args:
        atoms (ASE Atoms Object): Atoms object of the primitive cell
        calc (ASE Calculator): Calculator for the force calculations
        kpt_density (float): k-point density for the MP-Grid
        ph_settings (dict): kwargs for phonopy setup
        ph3_settings (dict): kwargs for phono3py setup
        fw_settings (dict): FireWork specific settings
    Returns (dict): The output of hilde.phonopy.workflow.bootstrap for phonopy and phono3py
    """
    settings = Settings(settings_file=None)
    settings.atoms = atoms
    if kpt_density:
        settings["control_kpt"] = AttributeDict({"density": kpt_density})
    kwargs_boot = {}
    if calc.name.lower() != "aims":
        kwargs_boot["calculator"] = calc
    else:
        settings["control"] = calc.parameters.copy()
        if "species_dir" in settings.control:
            sd = settings["control"].pop("species_dir")
            settings["basisset"] = AttributeDict({"type": sd.split("/")[-1]})

        if (ph_settings and "use_pimd_wrapper" in ph_settings) or (
            ph3_settings and "use_pimd_wrapper" in ph3_settings
        ):
            settings["socketio"] = AttributeDict(
                {"port": ph_settings.pop("use_pimd_wrapper")}
            )

        if "aims_command" in settings.control:
            del settings.control["aims_command"]

    outputs = []
    at = atoms.copy()
    at.set_calculator(None)
    if ph_settings:
        settings["phonopy"] = ph_settings.copy()
        if "serial" in settings.phonopy:
            del settings.phonopy["serial"]
        ph_out = bootstrap(name="phonopy", settings=settings, **kwargs_boot)
        ph_out["metadata"]["supercell"] = {
            "atoms": ph_out["metadata"]["atoms"],
            "calculator": {},
        }
        ph_out["metadata"]["primitive"] = input2dict(at)
        ph_out["prefix"] = "ph"
        ph_out["settings"] = ph_settings.copy()
        outputs.append(ph_out)
    if ph3_settings:
        settings["phono3py"] = ph3_settings.copy()
        if "serial" in settings.phono3py:
            del settings.phono3py["serial"]
        ph3_out = bootstrap(name="phono3py", settings=settings, **kwargs_boot)
        ph3_out["metadata"]["supercell"] = {
            "atoms": ph3_out["metadata"]["atoms"],
            "calculator": {},
        }
        ph3_out["metadata"]["primitive"] = input2dict(at)
        ph3_out["prefix"] = "ph3"
        ph3_out["settings"] = ph3_settings.copy()
        outputs.append(ph3_out)
    return outputs


def setup_harmonic_analysis(
    atoms,
    calc,
    phonon_dict,
    temperatures=None,
    debye_temp_fact=None,
    n_samples=1,
    deterministic=True,
    fw_settings=None,
    fc_file=None,
    **kwargs,
):
    """
    Initializes harmonic analysis functions
    Args:
        atoms (ASE Atoms Object): Atoms object of the primitive cell
        calc (ASE Calculator): Calculator for the force calculations
        phonon_dict (dict): Dictionary representation of the phonopy object
        temperatures (list): List of temperatures to set up displacements
        debye_temp_fact (list): List of temperatures based on factors of the debye temperature
        n_samples (int): number of samples to calculate
        deterministic (bool): If True use a deterministic model to set up the displacments
        fw_settings (dict): FireWork specific settings
        fc_file (str): force constant file
    Return (dict): Dictionary of the force calculations to run
    """
    if temperatures is None:
        temperatures = list()
    phonon_dict["forces_2"] = np.array(phonon_dict["forces_2"])
    ph = PhononRow(dct=phonon_dict).to_phonon()

    if "supercell_matrix" in kwargs:
        ph_new, sc, _ = preprocess(atoms, kwargs["supercell_matrix"])
    else:
        sc = to_Atoms_db(ph.get_supercell())

    n_atoms = ph.get_supercell().get_number_of_atoms()
    if fc_file:
        if fc_file.split(".")[-1] == "hdf5" or fc_file.split(".")[-1] == "h5":
            fc = np.array(File(fc_file)["fc2"])
        else:
            fc = np.genfromtxt(fc_file).reshape(n_atoms, 3, n_atoms, 3).swapaxes(1, 2)
        ph.set_force_constants(fc)
        phonon_dict = phonon_to_dict(ph, to_mongo=True, add_fc=True)

    if ph.get_force_constants().shape[0] != len(sc.numbers):
        if "remap_wd" in kwargs:
            force_constants = remap_forceconstant(ph, sc, workdir=kwargs["remap_wd"])
        else:
            force_constants = remap_forceconstant(ph, sc)
        n_atoms = ph_new.get_supercell().get_number_of_atoms()
        ph_new.set_force_constants(
            force_constants.reshape(n_atoms, 3, n_atoms, 3).swapaxes(1, 2)
        )
        phonon_dict = phonon_to_dict(ph_new, to_mongo=True, add_fc=True)
    else:
        force_constants = (
            ph.get_force_constants().swapaxes(1, 2).reshape(2 * (3 * n_atoms,))
        )

    if debye_temp_fact is not None:
        ph.set_mesh([51, 51, 51])
        ph.set_total_DOS(freq_pitch=0.01)
        ph.set_Debye_frequency()
        debye_temp = ph.get_Debye_frequency() * const.THzToEv / const.kB
        temperatures += [tt * debye_temp for tt in debye_temp_fact]
    elif temperatures is None:
        raise IOError("temperatures must be given to do harmonic analysis")

    del_keys = [
        "qpoints",
        "phonon_dos_fp",
        "q_points",
        "tp_ZPE",
        "tp_high_T_S",
        "tp_T",
        "tp_A",
        "tp_S",
        "tp_Cv",
        "phonon_bs_fp",
    ]
    for key in del_keys:
        if key in phonon_dict:
            phonon_dict.pop(key)
    ha_metadata = {
        "deterministic": deterministic,
        "n_samples": n_samples,
        # "ph_dict": phonon_dict,
        "supercell": input2dict(sc),
        "primitive": input2dict(to_Atoms_db(ph.get_primitive())),
        **input2dict(sc, calc),
    }

    outputs = []
    for temp in temperatures:
        to_out = dict()
        ha_metadata["temperature"] = temp
        to_out["metadata"] = ha_metadata.copy()
        to_out["prefix"] = "ha_" + str(temp)
        to_out["settings"] = {
            "n_samples": n_samples,
            "deterministic": deterministic,
            **kwargs,
        }
        to_out["settings"]["workdir"] += "/" + str(temp)
        calc_atoms = list()
        for _ in range(n_samples):
            atoms = sc.copy()
            PhononHarmonics(
                atoms,
                force_constants,
                quantum=False,
                temp=temp * u.kB,
                plus_minus=deterministic,
                failfast=True,
            )
            calc_atoms.append(atoms)
        to_out["atoms_to_calculate"] = calc_atoms
        outputs.append(to_out)
    return outputs


def collect_to_trajectory(trajectory, calculated_atoms, metadata):
    """
    Collects forces to a single trajectory file
    Args:
        trajectory (str): file name for the trajectory file
        calculated_atoms (list of ASE Atoms): Results of the force calculations
        metadata (dict): metadata for the phonon calculations
    """
    traj = Path(trajectory)
    traj.parent.mkdir(exist_ok=True, parents=True)
    if "Phonopy" in metadata:
        for el in metadata["Phonopy"]["displacement_dataset"]["first_atoms"]:
            el["number"] = int(el["number"])

    if "Phono3py" in metadata:
        for el1 in metadata["Phono3py"]["displacement_dataset"]["first_atoms"]:
            el1["number"] = int(el1["number"])
            for el2 in el1["second_atoms"]:
                el2["number"] = int(el2["number"])

    metadata2file(metadata, trajectory)
    if isinstance(calculated_atoms[0], dict):
        temp_atoms = [dict2atoms(cell) for cell in calculated_atoms]
    else:
        temp_atoms = calculated_atoms.copy()
    calculated_atoms = sorted(
        temp_atoms,
        key=lambda x: x.info[displacement_id_str] if x else len(calculated_atoms) + 1,
    )
    for atoms in calculated_atoms:
        if atoms:
            step2file(atoms, atoms.calc, trajectory)


def phonon_postprocess(func_path, phonon_times, **kwargs):
    """
    @brief      performs phonon postprocessing steps

    @param      func_path     The path to the postprocessing function
    @param      phonon_times  The time it took to calculate the phonon forces
    @param      kwargs        The keyword arguments for the phonon calculations

    @return     { description_of_the_return_value }
    """
    func = get_func(func_path)
    return func(**kwargs)
