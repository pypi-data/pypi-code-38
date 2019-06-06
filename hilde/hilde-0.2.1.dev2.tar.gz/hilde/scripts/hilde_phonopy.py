""" Summarize output from ASE.md class (in md.log) """

import numpy as np
from argparse import ArgumentParser
from pathlib import Path
from hilde.helpers.pickle import pread
from hilde.phonopy.postprocess import extract_results, postprocess
from hilde.phonopy.wrapper import summarize_bandstructure


def preprocess(args):
    import numpy as np
    from ase.io import read
    from hilde.settings import Settings
    import hilde.phonopy.wrapper as ph

    atoms = read(args.infile, format=args.format)

    _, _, scs_ref = ph.preprocess(atoms, supercell_matrix=1)

    if args.dim is not None:
        phonon, sc, scs = ph.preprocess(atoms, supercell_matrix=args.dim)
    else:
        settings = Settings(args.config_file)
        phonon, sc, scs = ph.preprocess(atoms, **settings.phonopy)
        print("Phonopy settings:")
        settings.print()

    sc_str = np.array2string(phonon.get_supercell_matrix().flatten(), separator=", ")
    print("Phonopy Information")
    print(f"  Supercell matrix:        {sc_str}")
    print(f"  Superlattice:")
    for latvec in sc.cell:
        lv_str = "{:-6.2f} {:-6.2f} {:-6.2f}".format(*latvec)
        print(f"                         {lv_str}")
    print(f"  Number of atoms in SC:   {len(sc)}")
    print(f"  Number of displacements: {len(scs)} ({len(scs_ref)})")


def main():
    """ main routine """
    parser = ArgumentParser(description="information about phonopy task")
    parser.add_argument("infile", help="primitive structure or pickled phonopy")
    parser.add_argument("--dim", type=int, nargs="*", default=None)
    parser.add_argument("--config_file", default="settings.in")
    parser.add_argument("--format", default="aims")
    parser.add_argument("--fp_file", default=None, help="File to store the fingerprint")
    parser.add_argument("--dos", action="store_true")
    parser.add_argument("--pdos", action="store_true")
    parser.add_argument("--tdep", action="store_true")
    parser.add_argument("--born", default=None, help="BORN file")
    parser.add_argument("--full_fc", action="store_true")
    args = parser.parse_args()

    extract_settings = {"plot_dos": args.dos, "plot_pdos": args.pdos, "tdep": args.tdep}

    suffix = Path(args.infile).suffix
    if suffix == ".in":
        preprocess(args)
        return

    elif suffix == ".yaml":
        phonon = postprocess(
            args.infile,
            born_charges_file=args.born,
            calculate_full_force_constants=args.full_fc,
        )
    elif suffix == ".pick" or suffix == ".gz":
        phonon = pread(args.infile)
    else:
        print("*** Nothing happened.")

    extract_results(phonon, **extract_settings)
    summarize_bandstructure(phonon, fp_file=args.fp_file)


if __name__ == "__main__":
    main()
