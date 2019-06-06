""" Provide a full highlevel phonopy workflow """

from pathlib import Path
import numpy as np
from hilde.helpers.converters import dict2atoms
from hilde.helpers.hash import hash_atoms
from hilde.helpers.pickle import psave
from hilde.phonopy import displacement_id_str
from hilde.structure.convert import to_Atoms
from hilde.trajectory import reader as traj_reader

from hilde.phono3py.wrapper import prepare_phono3py
from hilde.phonopy.postprocess import postprocess as postprocess2
from hilde.io import write


def postprocess(
    trajectory="phono3py/trajectory.son",
    trajectory_fc2="phonopy/trajectory.son",
    pickle_file="phonon3.pick",
    write_files=True,
    verbose=True,
    **kwargs,
):
    """ Phono3py postprocess """

    trajectory3 = Path(trajectory)

    # first run phonopy postprocess
    try:
        phonon = postprocess2(trajectory=trajectory_fc2)
    except FileNotFoundError:
        phonon = None

    # read the third order trajectory
    calculated_atoms, metadata_full = traj_reader(trajectory3, True)
    metadata = metadata_full["Phono3py"]
    primitive = dict2atoms(metadata["primitive"])
    supercell = dict2atoms(metadata_full["atoms"])
    supercell_matrix = metadata["supercell_matrix"]
    supercell.info = {"supercell_matrix": str(supercell_matrix)}

    phono3py_settings = {
        "atoms": primitive,
        "supercell_matrix": supercell_matrix,
        "phonon_supercell_matrix": phonon.get_supercell_matrix() if phonon else None,
        "fc2": phonon.get_force_constants() if phonon else None,
        "cutoff_pair_distance": metadata["displacement_dataset"]["cutoff_distance"],
        "symprec": metadata["symprec"],
        "displacement_dataset": metadata["displacement_dataset"],
        **kwargs,
    }

    phonon3 = prepare_phono3py(**phono3py_settings)
    zero_force = np.zeros([len(calculated_atoms[0]), 3])

    # collect the forces and put zeros where no supercell was created
    force_sets = []
    disp_scells = phonon3.get_supercells_with_displacements()
    hash_dict = dict()
    for nn, scell in enumerate(disp_scells):
        atoms = calculated_atoms[0]
        if scell:
            # This is no longer simply pop since phono3py adds the same supercell multiple times
            if atoms.info[displacement_id_str] == nn:
                hash_dict[hash_atoms(to_Atoms(scell))] = len(force_sets)
                force_sets.append(atoms.get_forces())
                calculated_atoms.pop(0)
            else:
                # This is a repeated supercell, find it using the hash and add the forces
                force_sets.append(force_sets[hash_dict[hash_atoms(to_Atoms(scell))]])
        else:
            # in case the trajectory contains data from higher cutoff calculations
            if atoms.info[displacement_id_str] == nn:
                calculated_atoms.pop(0)
            force_sets.append(zero_force)

    phonon3.produce_fc3(force_sets)

    if pickle_file and write_files:
        psave(phonon3, trajectory3.parent / pickle_file)

    if write_files:
        # Save the supercell
        fname = "geometry.in.supercell3"
        write(supercell, fname)
        if verbose:
            print(f".. Third order supercell written to {fname}")

    return phonon3
