"""
Script to compute supercells from inputself.
Similar to generate_structure from TDEP.
"""
from argparse import ArgumentParser as argpars
import numpy as np
from hilde.io import read, get_info_str
from hilde.structure.io import inform
from hilde.helpers.supercell import make_cubic_supercell, make_supercell
from hilde.helpers.geometry import get_cubicness
from hilde.helpers.numerics import get_3x3_matrix
from hilde.helpers.structure import clean_atoms
from hilde.spglib.wrapper import get_spacegroup
from hilde.helpers import Timer


def print_matrix(matrix, indent=2):
    ind = indent * " "
    rep = [" [{}, {}, {}]".format(*elem) for elem in matrix]
    # join to have a comma separated list
    rep = f",\n{ind}".join(rep)
    # add leading [ and trailing ]
    rep = f"{ind}[{rep[1:]}"
    rep += "]"
    print(rep)


def main():
    parser = argpars(description="Read geometry create supercell")
    parser.add_argument("geom", type=str, help="geometry input file")
    parser.add_argument("-n", type=int, help="target size")
    parser.add_argument("-d", "--dim", type=int, nargs="+", help="supercell matrix")
    parser.add_argument("--deviation", type=float, default=0.2)
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--dry", action="store_true", help="Do not write output file")
    parser.add_argument("--format", default="aims")
    parser.add_argument("--frac", action="store_true")
    args = parser.parse_args()

    timer = Timer()
    fname = args.geom
    print(f"Find supercell for")
    cell = read(fname, format=args.format)
    inform(cell)

    if args.n:
        print("\nSettings:")
        print(f"  Target number of atoms: {args.n}")
        supercell, smatrix = make_cubic_supercell(
            cell, args.n, deviation=args.deviation, limit=args.limit
        )
    elif args.dim:
        smatrix = get_3x3_matrix(args.dim)
        supercell = make_supercell(cell, smatrix)
    else:
        exit("Please specify either a target cell size or a supercell matrix")

    print(f"\nSupercell matrix:")
    print(" python:  {}".format(np.array2string(smatrix.flatten(), separator=", ")))
    print(" cmdline: {}".format(" ".join([f"{el}" for el in smatrix.flatten()])))
    print(" 2d:")
    print_matrix(smatrix, indent=0)

    print(f"\nSuperlattice:")
    print(supercell.cell.array)
    print(f"\nNumber of atoms:  {len(supercell)}")
    print(
        "Cubicness:        {:.3f} ({:.3f})".format(
            get_cubicness(supercell.cell), get_cubicness(supercell.cell) ** 3
        )
    )

    if not args.dry:
        spacegroup = get_spacegroup(cell)
        output_filename = f"{args.geom}.supercell_{len(supercell)}"
        info_str = get_info_str(supercell, spacegroup)
        info_str += [f"Supercell matrix:    {smatrix.flatten()}"]
        supercell.write(
            output_filename, format=args.format, scaled=args.frac, info_str=info_str
        )
        print(f"\nSupercell written to {output_filename}")

    timer()


if __name__ == "__main__":
    main()
