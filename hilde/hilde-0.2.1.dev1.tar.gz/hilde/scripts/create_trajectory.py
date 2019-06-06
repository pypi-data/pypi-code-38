""" Update trajectory files of old format """

from argparse import ArgumentParser

from ase.io import read
from hilde.trajectory import Trajectory, input2dict


def main():
    """ main routine """
    parser = ArgumentParser(description="Create trajectory file from aims calculations")
    parser.add_argument("output_files", nargs="+", help="aims output files")
    parser.add_argument("-uc", help="Add a (primitive) unit cell")
    parser.add_argument("-sc", help="Add the respective supercell")
    parser.add_argument("--output_format", default="aims-output")
    parser.add_argument("--input_format", default="aims")
    parser.add_argument("-fn", "--filename", default="trajectory.son")
    args = parser.parse_args()

    trajectory = Trajectory()

    # Metadata
    metadata = {}

    # Read the aims calculations
    for p in args.output_files:
        a = read(p, ":", format=args.output_format)
        if not metadata:
            trajectory.metadata = input2dict(a[0])
        trajectory.extend(a)

    if args.uc:
        atoms = read(args.uc, format=args.input_format)
        trajectory.primitive = atoms

    if args.sc:
        atoms = read(args.sc, format=args.input_format)
        trajectory.supercell = atoms

    trajectory.write(file=args.filename)


if __name__ == "__main__":
    main()
