""" Update trajectory files of old format """

from argparse import ArgumentParser
import shutil

from hilde.io import read
from hilde.trajectory import reader


def main():
    """ main routine """
    parser = ArgumentParser(description="Update trajectory file")
    parser.add_argument("trajectory")
    parser.add_argument("-uc", help="Add a (primitive) unit cell")
    parser.add_argument("-sc", help="Add the respective supercell")
    parser.add_argument("--format", default="aims")
    args = parser.parse_args()

    trajectory = reader(args.trajectory)
    new_trajectory = "temp.yaml"

    if args.uc:
        atoms = read(args.uc, format=args.format)
        trajectory.primitive = atoms

    if args.sc:
        atoms = read(args.sc, format=args.format)
        trajectory.supercell = atoms

    trajectory.write(file=new_trajectory)

    shutil.copy(args.trajectory, f"{args.trajectory}.bak")
    shutil.move(new_trajectory, args.trajectory)


if __name__ == "__main__":
    main()
