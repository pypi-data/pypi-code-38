"""
A leightweight wrapper for Phonopy()
"""

import json
from pathlib import Path
import numpy as np
from phonopy import Phonopy
from hilde import konstanten as const
from hilde.helpers import brillouinzone as bz, talk
from hilde.materials_fp.material_fingerprint import (
    get_phonon_bs_fingerprint_phononpy,
    to_dict,
)
from hilde.structure.convert import to_Atoms, to_phonopy_atoms
from hilde.helpers.numerics import get_3x3_matrix
from hilde.spglib.wrapper import map_unique_to_atoms
from .utils import get_supercells_with_displacements
from ._defaults import defaults


def prepare_phonopy(
    atoms,
    supercell_matrix,
    fc2=None,
    displacement=defaults.displacement,
    symprec=defaults.symprec,
    trigonal=defaults.trigonal,
    is_diagonal=defaults.is_diagonal,
):
    """ Create a Phonopy object """

    ph_atoms = to_phonopy_atoms(atoms, wrap=True)

    supercell_matrix = get_3x3_matrix(supercell_matrix)

    phonon = Phonopy(
        ph_atoms,
        supercell_matrix=np.transpose(supercell_matrix),
        symprec=symprec,
        is_symmetry=True,
        factor=const.omega_to_THz,
    )

    phonon.generate_displacements(
        distance=displacement,
        is_plusminus="auto",
        # is_diagonal=False is chosen to be in line with phono3py, see
        # https://github.com/atztogo/phono3py/pull/15
        is_diagonal=is_diagonal,
        is_trigonal=trigonal,
    )

    if fc2 is not None:
        phonon.set_force_constants(fc2)

    return phonon


def preprocess(
    atoms,
    supercell_matrix,
    displacement=defaults.displacement,
    symprec=defaults.symprec,
    trigonal=defaults.trigonal,
    **kwargs,
):
    """ generate phonopy objects and return displacements as Atoms objects """
    phonon = prepare_phonopy(
        atoms,
        supercell_matrix,
        displacement=displacement,
        symprec=symprec,
        trigonal=trigonal,
    )

    return get_supercells_with_displacements(phonon)


def get_force_constants(phonon, force_sets=None):
    """ Take a Phonopy object, produce force constants from the given forces and
    return in usable shape (3N, 3N) insated of (N, N, 3, 3) """
    n_atoms = phonon.get_supercell().get_number_of_atoms()

    phonon.produce_force_constants(force_sets)

    force_constants = phonon.get_force_constants()

    if force_constants is not None:
        # convert forces from (N, N, 3, 3) to (3*N, 3*N)
        force_constants = (
            phonon.get_force_constants().swapaxes(1, 2).reshape(2 * (3 * n_atoms,))
        )
        return force_constants
    # else
    raise ValueError("Force constants not yet created, specify force_sets.")


def get_dos(
    phonon,
    total=True,
    q_mesh=defaults.q_mesh,
    freq_min=0,
    freq_max="auto",
    freq_pitch=0.1,
    tetrahedron_method=True,
    write=False,
    filename="total_dos.dat",
    force_sets=None,
    direction=None,
    xyz_projection=False,
):
    """ Compute the DOS (and save to file) """

    if force_sets is not None:
        phonon.produce_force_constants(force_sets)

    if total:
        phonon.run_mesh(q_mesh)

        if freq_max == "auto":
            freq_max = phonon.get_mesh()[2].max() * 1.05
        phonon.run_total_dos(
            freq_min=freq_min,
            freq_max=freq_max,
            freq_pitch=freq_pitch,
            use_tetrahedron_method=tetrahedron_method,
        )

        if write:
            phonon.write_total_dos()
            Path("total_dos.dat").rename(filename)

        return phonon.get_total_dos_dict()
    else:
        phonon.run_mesh(q_mesh, is_mesh_symmetry=False, with_eigenvectors=True)

        if freq_max == "auto":
            freq_max = phonon.get_mesh()[2].max() * 1.05

        phonon.run_projected_dos(
            freq_min=freq_min,
            freq_max=freq_max,
            freq_pitch=freq_pitch,
            use_tetrahedron_method=tetrahedron_method,
            direction=direction,
            xyz_projection=xyz_projection,
        )
        if write:
            phonon.write_projected_dos()
            Path("projected_dos.dat").rename(filename)
        return phonon.get_projected_dos_dict()


def get_bandstructure(phonon, paths=None, force_sets=None):
    """
    Compute bandstructure for given path
    Args:
        phonon: phonopy.api_phonopy.Phonopy
        paths: list of str
            e.g. ['GXSYGZURTZ', 'YT', 'UX', 'SR']
    Returns:
        tuple (band_structure_dict, labels)
            band_structure_dict: dict
            labels: list of str
    """
    if force_sets is not None:
        phonon.produce_force_constants(force_sets)

    bands, labels = bz.get_bands_and_labels(to_Atoms(phonon.primitive), paths)

    phonon.run_band_structure(bands, labels=labels)

    return (phonon.get_band_structure_dict(), labels)


def plot_bandstructure(phonon, file="bandstructure.pdf", paths=None, force_sets=None):
    """ Plot bandstructure for given path and save to file """

    _, labels = get_bandstructure(phonon, paths, force_sets)

    plt = phonon.plot_band_structure()

    try:
        plt.savefig(file)
    except FileNotFoundError:
        talk("saving the phonon dispersion not possible, latex probably missing")


def plot_bandstructure_and_dos(
    phonon, q_mesh=defaults.q_mesh, partial=False, file="bands_and_dos.pdf"
):
    """ Plot bandstructure and PDOS """

    _, labels = get_bandstructure(phonon)

    if partial:
        phonon.run_mesh(
            q_mesh,
            with_eigenvectors=True,
            is_mesh_symmetry=False,
        )
        phonon.run_projected_dos(use_tetrahedron_method=True)
        pdos_indices = map_unique_to_atoms(phonon.get_primitive())
    else:
        phonon.run_mesh(q_mesh, with_eigenvectors=True,)
        phonon.run_total_dos(use_tetrahedron_method=True)
        pdos_indices = None

    plt = phonon.plot_band_structure_and_dos(pdos_indices=pdos_indices)
    plt.savefig(file)


def summarize_bandstructure(phonon, fp_file=None):
    """ print a concise symmary of the bandstructure fingerprint """
    from hilde.konstanten.einheiten import THz_to_cm

    get_bandstructure(phonon)

    qpts = np.array(phonon.band_structure.qpoints).reshape(-1, 3)

    freq = np.array(phonon.band_structure.frequencies).reshape(qpts.shape[0], -1)

    gamma_freq = freq[np.where((qpts == np.zeros(3)).all(-1))[0][0]]
    max_freq = np.max(freq.flatten())

    if fp_file:
        print(f"Saving the fingerprint to {fp_file}")
        fp = get_phonon_bs_fingerprint_phononpy(phonon, binning=False)
        fp_dict = to_dict(fp)
        for key, val in fp_dict.items():
            fp_dict[key] = val.tolist()
        with open(fp_file, "w") as outfile:
            json.dump(fp_dict, outfile, indent=4)

    mf = max_freq
    mf_cm = mf * THz_to_cm
    print(f"The maximum frequency is: {mf:.3f} THz ({mf_cm:.3f} cm^-1)")
    print(f"The frequencies at the gamma point are:")
    print(f"              THz |        cm^-1")
    p = lambda ii, freq: print(f"{ii+1:3d}: {freq:-12.5f} | {freq*THz_to_cm:-12.5f}")
    for ii, freq in enumerate(gamma_freq[:6]):
        p(ii, freq)
    for _ in range(3):
        print("  .")
    for ii, freq in enumerate(gamma_freq[-3:]):
        p(len(gamma_freq) - 3 + ii, freq)
    return gamma_freq, max_freq
