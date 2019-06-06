""" a wrapper for TDEP """
from ase.io.aims import read_aims
from subprocess import run
from pathlib import Path

import numpy as np

from hilde.helpers.paths import cwd
from hilde.helpers import Timer
from hilde.phonopy.postprocess import extract_results
from hilde.trajectory import reader

def remap_forceconstant(
    ph, new_supercell, workdir='tdep', logfile="rempa_fc.log"
):
    command = ["remap_forceconstant"]
    with cwd(workdir, mkdir=True), open(logfile, "w") as file:
        convert_phonopy_to_dep(ph, ".", False)
        new_supercell.write("infile.newposcar", format="vasp", vasp5=True, direct=True)
        run(command, stdout=file)
        return parse_tdep_forceconstant("outfile.forceconstant_remapped")

def convert_phonopy_to_dep(
    ph, workdir="tdep", reduce_ph_fc=True, logfile="convert_phonopy_to_dep.log"
):
    command = ["convert_phonopy_to_forceconstant", "--truncate"]
    with cwd(workdir, mkdir=True), open(logfile, "w") as file:
        extract_results(ph, tdep=True, tdep_reduce_fc=reduce_ph_fc)
        run(command, stdout=file)
        outfile = Path("outfile.converted_forceconstant")
        infile = Path("infile.forceconstant")
        if infile.exists():
            infile.unlink()
        infile.symlink_to(outfile)
        print(f".. Symlink {infile} created.")

def canonical_configuration(
     ph=None, workdir="tdep", temperature=300, n_sample=5, quantum=False, logfile="canon_conf.log"
):
    if ph:
        convert_phonopy_to_dep(ph, workdir)
    command = ["canonical_configuration"]
    if quantum:
        command.append(f"--quantum")
    command.extend("-of 4".split())
    command.extend(f"-n {n_sample}".split())
    command.extend(f"-t {temperature}".split())
    with cwd(workdir, mkdir=True), open(logfile, "w") as file:
        run(command, stdout=file)
    outfiles = Path(workdir).glob("aims_conf*")
    return [read_aims(of) for of in outfiles]

def extract_forceconstants_from_trajectory(
    trajectory_file, workdir="tdep", rc2=10, remapped=True, logfile="fc.log", **kwargs
):
    trajectory = reader(trajectory_file)
    if "skip" in kwargs:
        skip = kwargs["skip"]
    else:
        skip = 0
    trajectory.to_tdep(folder=workdir, skip=0)
    extract_forceconstants(workdir, rc2, remapped, logfile, **kwargs)

def parse_tdep_forceconstant(fname="infile.forceconstant", force_remap=False):
    """ parse the remapped forceconstants from TDEP """
    timer = Timer()

    remapped = force_remap
    if "remap" in str(fname):
        remapped = True

    print(f"Parse force constants from\n  {fname}")
    print(f".. remap representation for supercell: ", remapped)

    with open(fname) as fo:
        n_atoms = int(next(fo).split()[0])
        cutoff = float(next(fo).split()[0])

        print(f".. Number of atoms:   {n_atoms}")
        print(rf".. Real space cutoff: {cutoff:.3f} \AA")

        # Not yet clear how many lattice points / force constants we will get
        lattice_points = []
        force_constants = []

        for i1 in range(n_atoms):
            n_neighbors = int(next(fo).split()[0])
            for _ in range(n_neighbors):
                fc = np.zeros([n_atoms, 3, n_atoms, 3])

                # neighbour index
                i2 = int(next(fo).split()[0]) - 1

                # lattice vector
                lp = np.array(next(fo).split(), dtype=float)

                # the force constant matrix for pair (i1, i2)
                phi = np.array([next(fo).split() for _ in range(3)], dtype=float)

                fc[i1, :, i2, :] = phi

                lattice_points.append(lp)
                # force_constants.append(fc.reshape((3 * n_atoms, 3 * n_atoms)))
                force_constants.append(fc)

        n_unique = len(np.unique(lattice_points, axis=0))
        print(f".. Number of lattice points: {len(lattice_points)} ({n_unique} unique)")

    timer()

    if remapped:
        force_constants = np.sum(force_constants, axis=0)
        return force_constants.reshape(2 * (3 * n_atoms,))

    return np.array(force_constants), np.array(lattice_points)


def extract_forceconstants(
    workdir="tdep", rc2=10, remapped=True, logfile="fc.log", **kwargs
):
    """ run tdep's extract_forceconstants in the working directory """

    timer = Timer()

    print(f"Extract force constants with TDEP from input files in\n  {workdir}")

    command = ["extract_forceconstants", "--verbose"]

    command.extend(f"-rc2 {rc2}".split())

    if remapped:
        command.append("--printfc2remapped")

    with cwd(workdir), open(logfile, "w") as file:
        run(command, stdout=file)
        timer()

        # create the symlink of force constants
        print(f".. Create symlink to forceconstant file")
        outfile = Path("outfile.forceconstant")
        infile = Path("infile" + outfile.suffix)

        if infile.exists():
            proceed = input(f"Symlink {infile} exists. Proceed? (y/n) ")
            if proceed.lower() == "y":
                infile.unlink()
            else:
                print(".. Symlink NOT created.")
                return

        infile.symlink_to(outfile)
        print(f".. Symlink {infile} created.")


def phonon_dispersion_relations(workdir="tdep", gnuplot=True, logfile="dispersion.log"):
    """ run tdep's phonon_dispersion_relations in working directory """

    timer = Timer(f"Run TDEP phonon_dispersion_relations in {workdir}")

    with cwd(workdir):
        # check if input files are present
        for file in ("forceconstant", "ucposcar", "ssposcar"):
            path = Path("infile." + file)
            if not path.exists():
                raise FileNotFoundError(f"{path} missing in ./{workdir}.")

        # plot if ipnut files are present
        command = "phonon_dispersion_relations -p".split()

        with open(logfile, "w") as file:
            run(command, stdout=file)

            if gnuplot:
                print(f".. use gnuplot to plot dispersion to pdf")
                command = "gnuplot -p outfile.dispersion_relations.gnuplot_pdf".split()
                run(command, stdout=file)

    timer()
