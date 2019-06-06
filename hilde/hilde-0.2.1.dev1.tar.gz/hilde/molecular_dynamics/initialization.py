""" prepare molecular dynamics simulations using the ASE classes """

from pathlib import Path
import numpy as np
from ase import units as u
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, PhononHarmonics

from hilde.helpers.fileformats import last_from_yaml
from hilde.helpers.warnings import warn


def setup_md(
    atoms,
    algorithm="Verlet",
    temperature=None,
    timestep=None,
    friction=None,
    logfile=None,
    workdir=".",
    trajectory=None,
    **kwargs,
):
    """ create and ase.md object with respective settings """

    if trajectory is None:
        trajectory = (Path(workdir) / "trajectory.son").absolute()
    else:
        trajectory = Path(trajectory).absolute()

    if not Path(workdir).is_dir():
        Path(workdir).mkdir()

    dt = timestep * u.fs
    md = None

    if "verlet" in algorithm.lower():
        from ase.md.verlet import VelocityVerlet

        md = VelocityVerlet(atoms, timestep=dt, logfile=logfile)

    elif "langevin" in algorithm.lower():
        from ase.md.langevin import Langevin

        if temperature is None:
            warn("temperature not set", level=2)

        if friction is None:
            warn("Friction not defined, set to 0.01", level=2)

        md = Langevin(
            atoms,
            temperature=temperature * u.kB,
            timestep=dt,
            friction=friction,
            logfile=logfile,
        )

    else:
        raise RuntimeError(f"Molecular dynamics mode {algorithm} is not suppported.")

    prepared = prepare_from_trajectory(atoms, md, trajectory)

    if md is None:
        raise RuntimeError("ASE MD algorithm has to be given")

    return atoms, md, prepared


def prepare_from_trajectory(atoms, md, trajectory="trajectory.son", **kwargs):
    """ Take the last step from trajectory and initialize atoms + md accordingly """

    trajectory = Path(trajectory).absolute()
    if trajectory.exists():
        last_atoms = last_from_yaml(trajectory)
        if "info" in last_atoms["atoms"]:
            md.nsteps = last_atoms["atoms"]["info"]["nsteps"]

            atoms.set_positions(last_atoms["atoms"]["positions"])
            atoms.set_velocities(last_atoms["atoms"]["velocities"])
            print(f"Resume MD from last step in\n  {trajectory}\n")
            return True

    print(f"** {trajectory} does not exist, nothing to prepare")
    return False


def initialize_md(
    atoms,
    temperature=None,
    force_constants=None,
    quantum=False,
    force_temp=True,
    deterministic=True,
    **kwargs,
):
    """ Either use Maxwell Boltzmann or PhononHarmonics to prepare the MD run """

    if temperature is None:
        return atoms

    print(f"Prepare MD run at temperature {temperature}")

    if force_constants is not None:
        print("Initialize positions and velocities using force constants.")
        force_constants = np.loadtxt(force_constants)
        PhononHarmonics(
            atoms,
            force_constants,
            quantum=quantum,
            temp=temperature * u.kB,
            plus_minus=deterministic,
            **kwargs,
        )
        if force_temp:
            temp0 = atoms.get_kinetic_energy() / len(atoms) / 1.5
            gamma = temperature * u.kB / temp0
            atoms.set_momenta(atoms.get_momenta() * np.sqrt(gamma))

    else:
        print("Initialize velocities according to Maxwell-Boltzmann distribution.")
        MaxwellBoltzmannDistribution(
            atoms, temp=temperature * u.kB, force_temp=force_temp
        )

    return atoms
