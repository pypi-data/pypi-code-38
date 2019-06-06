""" Provide a full highlevel phonopy workflow """

from pathlib import Path
import pickle
import numpy as np

from hilde.phonon_db.ase_converters import dict2atoms
from hilde.phonon_db.database_interface import update_phonon_db
from hilde.phonon_db.row import PhononRow
import hilde.phono3py.wrapper as ph3
from hilde.phonopy import displacement_id_str
from hilde.structure.convert import to_Atoms
from hilde.trajectory import reader as traj_reader


def postprocess(
    phonon3,
    calculated_atoms=None,
    trajectory="trajectory.son",
    workdir=".",
    force_constants_file="force_constants.dat",
    displacement=0.03,
    q_mesh=[11, 11, 11],
    cutoff_pair_distance=10.0,
    symprec=1e-5,
    log_level=2,
    pickle_file="phonon3.pick",
    db_path=None,
    fireworks=False,
    **kwargs,
):
    """
    Phono3py postprocess
    Args:
        phonon3 (Phono3py Object or dict): phono3py calculation to post process
        calculated_atoms (list [Atoms object]): A list of all supercells with displacements with the forces calculated
        trajectory (str): Trajectory file path
        workdir (str): work directory path
        force_constants_file (str): Third order force constant output file name
        displacement (float): size of the displacements
        q_mesh (list of ints): size of the qpoint mesh for thermal conductivity calcs
        cutoff_pair_distance (float): cutoff distance for force interactions
        symprec (float): symmetry percison for phono3py
        log_level (int): how much logging should be done
        pickle_file (str): pickle file filename
        db_path (str): Path to database
        fireworks (bool): If True Fireworks was used in the calculation
    """

    if fireworks:
        if isinstance(phonon3, dict):
            phonon3 = PhononRow(dct=phonon3).to_phonon3()
        else:
            phonon3 = PhononRow(phonon3=phonon3).to_phonon3()
        phonon3.generate_displacements(
            distance=displacement,
            cutoff_pair_distance=cutoff_pair_distance,
            is_plusminus="auto",
            is_diagonal=True,
        )
        if not phonon3._mesh:
            phonon3._mesh = np.array(q_mesh, dtype="intc")
    if calculated_atoms:
        if fireworks:
            temp_atoms = [dict2atoms(cell) for cell in calculated_atoms]
        else:
            temp_atoms = calculated_atoms.copy()
        calculated_atoms = sorted(
            temp_atoms,
            key=lambda x: x.info[displacement_id_str] if x else len(disp_cells) + int(1e7),
        )

    elif Path(trajectory).is_file():
        calculated_atoms = traj_reader(trajectory)
    else:
        raise ValueError("Either calculated_atoms or trajectory must be defined")

    fc3_cells = []
    used_forces = 0
    for cell in phonon3.get_supercells_with_displacements():
        if cell is not None:
            fc3_cells.append(calculated_atoms[used_forces])
            used_forces += 1
        else:
            fc3_forces.append(None)
    fc3_forces = ph3.get_forces(fc3_cells)
    phonon3.produce_fc3(fc3_forces)

    phonon3.run_thermal_conductivity(write_kappa=True)

    # compute and save force constants
    n_atoms = phonon3.get_supercell().get_number_of_atoms()
    fc3 = (
        phonon3.get_fc3()
        .swapaxes(4, 3)
        .swapaxes(4, 2)
        .swapaxes(2, 1)
        .reshape(3 * (3 * n_atoms,))
    )
    with open(str(Path(workdir) / force_constants_file), "w") as outfile:
        for i, slice in enumerate(fc3):
            outfile.write(f"# New Slice Number {i}\n")
            np.savetxt(outfile, slice)
    with (Path(workdir) / pickle_file).open("wb") as fp:
        pickle.dump(phonon3, fp)
    if db_path:
        update_phonon3_db(
            db_path,
            to_Atoms(phonon3.get_unitcell()),
            phonon3,
            symprec=phonon3._symprec,
            sc_matrix_3=list(phonon3.get_supercell_matrix().flatten()),
            **kwargs,
        )
