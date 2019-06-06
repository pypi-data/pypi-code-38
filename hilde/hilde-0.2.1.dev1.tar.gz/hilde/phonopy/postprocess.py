""" Provide a full highlevel phonopy workflow """
from pathlib import Path

import numpy as np

from phonopy.file_IO import write_FORCE_CONSTANTS

from hilde.helpers.converters import dict2atoms
from hilde.helpers import Timer
from hilde.helpers.paths import cwd
from hilde.phonopy.wrapper import(
    prepare_phonopy,
    get_force_constants,
    plot_bandstructure as plot_bs,
    get_bandstructure,
    plot_bandstructure_and_dos
)
from hilde.phonopy import defaults
from hilde.structure.convert import to_Atoms, to_Atoms_db
from hilde.trajectory import reader
from hilde.helpers.pickle import psave
from hilde.io import write
from hilde.helpers import warn

from . import displacement_id_str


def postprocess(
    trajectory="phonopy/trajectory.son",
    calculate_full_force_constants=False,
    born_charges_file=None,
    verbose=True,
    **kwargs,
):
    """ Phonopy postprocess """

    timer = Timer()
    trajectory = Path(trajectory)
    if verbose:
        print("Start phonopy postprocess:")

    calculated_atoms, metadata = reader(trajectory, True)

    # make sure the calculated atoms are in order
    for nn, atoms in enumerate(calculated_atoms):
        atoms_id = atoms.info[displacement_id_str]
        if atoms_id == nn:
            continue
        warn(f"Displacement ids are not in order. Inspect {trajectory}!", level=2)

    for disp in metadata["Phonopy"]["displacement_dataset"]["first_atoms"]:
        disp["number"] = int(disp["number"])
    primitive = dict2atoms(metadata["Phonopy"]["primitive"])
    supercell = dict2atoms(metadata["atoms"])
    supercell_matrix = metadata["Phonopy"]["supercell_matrix"]
    supercell.info = {"supercell_matrix": str(supercell_matrix)}
    symprec = metadata["Phonopy"]["symprec"]

    phonon = prepare_phonopy(primitive, supercell_matrix, symprec=symprec)
    phonon._displacement_dataset = metadata["Phonopy"]["displacement_dataset"].copy()

    force_sets = [atoms.get_forces() for atoms in calculated_atoms]

    phonon.produce_force_constants(
        force_sets, calculate_full_force_constants=calculate_full_force_constants
    )

    # born charges?
    if born_charges_file:
        from phonopy.file_IO import get_born_parameters

        prim = phonon.get_primitive()
        psym = phonon.get_primitive_symmetry()
        if verbose:
            print(f".. read born effective charges from {born_charges_file}")
        nac_params = get_born_parameters(open(born_charges_file), prim, psym)
        phonon.set_nac_params(nac_params)


    if calculate_full_force_constants:
        phonon.produce_force_constants(force_sets, calculate_full_force_constants=True)

        # force_constants = get_force_constants(phonon)
        # fname = "force_constants.dat"
        # np.savetxt(fname, force_constants)
        # print(f".. Force constants saved to {fname}.")

    if verbose:
        timer("done")
    return phonon

def extract_results(
    phonon,
    write_geometries=True,
    write_force_constants=True,
    write_thermal_properties=False,
    write_bandstructure=False,
    write_dos=False,
    write_pdos=False,
    plot_bandstructure=True,
    plot_dos=False,
    plot_pdos=False,
    q_mesh=None,
    output_dir="phonopy_output",
    tdep=False,
    tdep_reduce_fc=True,
):
    """ Extract results from phonopy object and present them.
        With `tdep=True`, the necessary input files for TDEP's
          `convert_phonopy_to_forceconstant`
        are written. """
    if q_mesh is None:
        q_mesh = defaults.q_mesh.copy()
    Path.mkdir(Path(output_dir), exist_ok=True)
    with cwd(output_dir):
        if write_geometries:
            write(to_Atoms(phonon.get_supercell()), "geometry.in.supercell")
            write(to_Atoms(phonon.get_primitive()), "geometry.in.primitive")

        if write_force_constants:
            write_FORCE_CONSTANTS(
                phonon.get_force_constants(),
                filename="FORCE_CONSTANTS",
                p2s_map=phonon.get_primitive().get_primitive_to_supercell_map(),
            )

        if write_thermal_properties:
            phonon.run_mesh(q_mesh)
            phonon.run_thermal_properties()
            phonon.write_yaml_thermal_properties()

        if plot_bandstructure:
            plot_bs(phonon, file="bandstructure.pdf")
        if write_bandstructure:
            get_bandstructure(phonon)
            phonon.write_yaml_band_structure()

        if plot_dos:
            plot_bandstructure_and_dos(phonon, file="bands_and_dos.pdf")
        if write_dos:
            phonon.run_mesh(q_mesh, with_eigenvectors=True)
            phonon.run_total_dos(use_tetrahedron_method=True)
            phonon.write_total_dos()

        if plot_pdos:
            plot_bandstructure_and_dos(phonon, partial=True, file="bands_and_pdos.pdf")
        if write_pdos:
            phonon.run_mesh(q_mesh, with_eigenvectors=True, is_mesh_symmetry=False)
            phonon.run_projected_dos(
                use_tetrahedron_method=True,
            )
            phonon.write_projected_dos()

    primitive = to_Atoms_db(phonon.get_primitive())
    supercell = to_Atoms_db(phonon.get_supercell())

    if tdep:
        write_settings = {"format": "vasp", "direct": True, "vasp5": True}
        fnames = {"primitive": "infile.ucposcar", "supercell": "infile.ssposcar"}

        # reproduce reduces force constants
        if tdep_reduce_fc:
            phonon.produce_force_constants(calculate_full_force_constants=False)

    else:
        write_settings = {"format": "aims", "scaled": True}
        fnames = {
            "primitive": "geometry.in.primitive",
            "supercell": "geometry.in.supercell",
        }

    fname = fnames["primitive"]
    primitive.write(fname, **write_settings)
    print(f"Primitive cell written to {fname}")

    fname = fnames["supercell"]
    supercell.write(fname, **write_settings)
    print(f"Supercell cell written to {fname}")

    # # save as force_constants.dat
    # if tdep_reduce_fc:
    #     phonon.produce_force_constants()
    # n_atoms = phonon.get_supercell().get_number_of_atoms()

    # force_constants = (
    #     phonon.get_force_constants().swapaxes(1, 2).reshape(2 * (3 * n_atoms,))
    # )

    # fname = "force_constants.dat"
    # np.savetxt(fname, force_constants)
    # print(f"Full force constants as numpy matrix written to {fname}.")
