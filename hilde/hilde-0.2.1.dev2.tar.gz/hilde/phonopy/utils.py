""" hilde quality of life """

from phonopy.structure.atoms import PhonopyAtoms
from hilde.structure.convert import to_Atoms
from hilde.helpers.fileformats import last_from_yaml
from hilde.helpers.converters import input2dict
from ._defaults import displacement_id_str


def last_calculation_id(trajectory):
    """ return the id of the last computed supercell """
    disp_id = -1

    try:
        dct = last_from_yaml(trajectory)
        disp_id = dct["info"][displacement_id_str]
    except (FileNotFoundError, KeyError):
        pass

    return disp_id


def to_phonopy_atoms(atoms):
    """ convert ase.Atoms to PhonopyAtoms """
    phonopy_atoms = PhonopyAtoms(
        symbols=atoms.get_chemical_symbols(),
        cell=atoms.get_cell(),
        masses=atoms.get_masses(),
        positions=atoms.get_positions(wrap=True),
    )
    return phonopy_atoms


def enumerate_displacements(cells, info_str=displacement_id_str):
    """ Assign a displacemt id to every atoms obect in cells.

    Args:
        cells (list): atoms objects created by, e.g., phonopy
        info_str (str): how to name the child

    Returns:
        list: cells with id attached to atoms.info (inplace)

    """
    for nn, scell in enumerate(cells):
        if scell is None:
            continue
        scell.info[info_str] = nn


def get_supercells_with_displacements(phonon):
    """ Create a phonopy object and supercells etc. """

    supercell = to_Atoms(
        phonon.get_supercell(),
        info={
            "supercell": True,
            "supercell_matrix": phonon.get_supercell_matrix().T.flatten().tolist(),
        },
    )

    scells = phonon.get_supercells_with_displacements()

    supercells_with_disps = [to_Atoms(cell) for cell in scells]

    enumerate_displacements(supercells_with_disps)

    return phonon, supercell, supercells_with_disps


def metadata2dict(phonon, calculator):
    """ convert metadata information to plain dict """

    atoms = to_Atoms(phonon.get_primitive())

    prim_data = input2dict(atoms)

    phonon_dict = {
        "version": phonon.get_version(),
        "primitive": prim_data["atoms"],
        "supercell_matrix": phonon.get_supercell_matrix().T.astype(int).tolist(),
        "symprec": float(phonon.get_symmetry().get_symmetry_tolerance()),
        "displacement_dataset": phonon.get_displacement_dataset(),
    }

    try:
        displacements = phonon.get_displacements()
        phonon_dict.update({"displacements": displacements})
    except AttributeError:
        pass

    supercell = to_Atoms(phonon.get_supercell())
    supercell_data = input2dict(supercell, calculator)

    return {str(phonon.__class__.__name__): phonon_dict, **supercell_data}

def get_force_constants_from_trajectory(traj, supercell=None, two_dim=False):
    '''
    Remaps the phonopy force constants into an fc matrix for a new structure
    Args:
        traj (Phonopy Object): Phonopy Object with the calculated force constants
        supercell (ASE Atoms): Atoms Object of the new structure to map force constants onto
        two_dim (bool): if True convert to 3*n_atoms x 3*n_atoms matrix
    Returns (np.ndarray): new force constant matrix
    '''
    phonon = postprocess(traj)
    if supercell is None:
        supercell = to_Atoms(phonon.get_supercell())

    n_atoms_new = len(supercell)

    sds = get_symmetry_dataset(supercell)
    map2prim = sds.mapping_to_primitive

    sc = to_Atoms(phonon.get_supercell())
    fc_in = phonon.get_force_constants().copy()

    sc_r = np.zeros((fc_in.shape[0], fc_in.shape[1], 3))
    for aa, a1 in enumerate(phonon.get_primitive().p2s_map):
        sc_r[aa] = sc.get_distances(a1, range(len(sc)), mic=True, vector=True)

    ref_struct_pos = supercell.get_scaled_positions(wrap=True)

    fc_out = np.zeros((n_atoms_new, n_atoms_new, 3, 3))
    for a1 in range(n_atoms_new):
        r0 = supercell.positions[a1]
        uc_index = map2prim[a1]
        for sc_a2, sc_r2 in enumerate(sc_r[uc_index]):
            r_pair = r0 + sc_r2
            r_pair = np.linalg.solve(supercell.get_cell(complete=True).T, r_pair.T).T % 1.0
            for a2 in range(n_atoms_new):
                r_diff = np.abs(r_pair - ref_struct_pos[a2])
                # Integer value is the equivalent of 0.0
                r_diff -= np.floor(r_diff + 1e-13)
                if np.sum(r_diff) < 1e-5:
                    fc_out[a1, a2, :, :] = fc_in[uc_index, sc_a2, :, :]
                    break
    if two_dim:
        fc_out = fc_out.swapaxes(1,2).reshape(2*(3*fc_out.shape[1],))
    return fc_out
