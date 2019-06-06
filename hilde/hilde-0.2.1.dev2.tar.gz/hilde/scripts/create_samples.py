"""
Script to initialize positions and velocities with force constants.
Similar to canonical_sampling from TDEP.
"""
from argparse import ArgumentParser as argpars
import numpy as np

from ase.io import read
from ase import units as u
import ase.md.velocitydistribution as vd

from hilde.structure.io import inform
from hilde.konstanten.einheiten import omega_to_THz


def main():
    """ main function """
    parser = argpars(description="Read geometry create supercell")
    parser.add_argument("geom", type=str, help="geometry input file")
    parser.add_argument("-T", "--temperature", type=int)
    parser.add_argument("-fc", "--force_constants")
    parser.add_argument("--mc_rattle", nargs="?", type=float, const=0.01, default=None)
    parser.add_argument("-n", "--n_samples", type=int, default=1, help="no. of samples")
    parser.add_argument("--quantum", action="store_true")
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--ignore_negative", action="store_false")
    parser.add_argument("--format", default="aims")
    parser.add_argument("--non_enforced_temp", action="store_true")
    parser.add_argument("--non_stationary", action="store_true")
    parser.add_argument("--random_seed", type=int, default=None)
    args = parser.parse_args()

    atoms = read(args.geom, format=args.format)
    # inform(atoms)

    seed = args.random_seed
    temp = args.temperature
    info_str = []

    if args.mc_rattle:
        try:
            from hiphive.structure_generation import mc_rattle
        except (ModuleNotFoundError, ImportError):
            exit("** hiphive needs to be installed to use mc_rattle.")

    if seed:
        print(f"Random seed is {seed}")
        rng = np.random.RandomState(seed)
        info_str += [f"Random seed: {seed}"]
    else:
        rng = np.random

    if args.force_constants is not None:
        force_constants = np.loadtxt(args.force_constants)

        # Check dyn. matrix
        check_frequencies(atoms, force_constants)

        # collect arguments for PhononHarmonics
        phonon_harmonic_args = {
            "force_constants": force_constants,
            "quantum": args.quantum,
            "temp": temp * u.kB,
            "plus_minus": args.deterministic,
            "failfast": args.ignore_negative,
            "rng": rng,
        }
        info_str += ["created from force constants", f"T = {temp} K"]
        print(f"Use force constants from {args.force_constants} to prepare samples")

    else:
        mb_args = {"temp": temp * u.kB, "rng": rng}
        info_str += ["created from MB distrubtion", f"T = {args.temperature} K"]
        print(f"Use Maxwell Boltzamnn to set up samples")

    for ii in range(args.n_samples):
        print(f"Sample {ii:3d}:")
        sample = atoms.copy()

        if args.force_constants is not None:
            vd.PhononHarmonics(sample, **phonon_harmonic_args)

        elif args.mc_rattle:
            pass

        else:
            vd.MaxwellBoltzmannDistribution(sample, **mb_args)

        if not args.non_enforced_temp:
            force_temperature(sample, temp)

        if not args.non_stationary:
            print(f".. remove net momentum from sample")
            vd.Stationary(sample)
            vd.ZeroRotation(sample)

        filename = f"{args.geom}.{temp}K"
        if args.n_samples > 1:
            filename += f".{ii+1:03d}"

        sample.write(filename, info_str=info_str, velocities=True, format=args.format)

        print(f".. temperature in sample {ii}: {sample.get_temperature():.3f}K")
        print(f".. written to {filename}")


if __name__ == "__main__":
    main()


def get_frequencies(atoms, force_constants):
    """ create dynamical matrix, return frequencies for sanity checks """
    masses = atoms.get_masses()
    # Build dynamical matrix
    rminv = (masses ** -0.5).repeat(3)
    dynamical_matrix = force_constants * rminv[:, None] * rminv[None, :]

    # Solve eigenvalue problem to compute phonon spectrum and eigenvectors
    w2_s, _ = np.linalg.eigh(dynamical_matrix)

    return w2_s * (omega_to_THz) ** 2


def check_frequencies(atoms, force_constants):
    w2 = get_frequencies(atoms, force_constants)
    print("The first 6 frequencies:")
    for ii, freq in enumerate(w2[:6]):
        print(f" {ii + 1:4d}: {np.sign(freq) * np.sqrt(abs(freq))}")

    print("Highest 6 frequencies")
    for ii, freq in enumerate(w2[-6:]):
        print(f" {len(w2) - ii:4d}: {np.sign(freq) * np.sqrt(abs(freq))}")


def force_temperature(atoms, temperature):
    """ force (nucl.) temperature to have a precise value """
    temp0 = atoms.get_kinetic_energy() / len(atoms) / 1.5
    gamma = temperature * u.kB / temp0
    atoms.set_momenta(atoms.get_momenta() * np.sqrt(gamma))

