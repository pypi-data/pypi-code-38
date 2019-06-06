from argparse import ArgumentParser as argpars

import numpy as np

from hilde.io import read, write, inform
from hilde.helpers import warn, bold
from hilde.spglib.wrapper import refine_cell, standardize_cell


def main():
    parser = argpars(description="Read geometry and use spglib to refine")
    parser.add_argument("geometry")
    parser.add_argument("--prim", action="store_true", help="store primitive cell")
    parser.add_argument("--conv", action="store_true", help="store conventional cell")
    parser.add_argument("-t", "--tolerance", type=float, default=1e-5)
    parser.add_argument("--format", default="aims")
    parser.add_argument("--cart", action="store_true")
    parser.add_argument("--center", action="store_true", help="center average position")
    parser.add_argument("--origin", action="store_true", help="first atom to origin")
    args = parser.parse_args()

    ### Greet
    fname = args.geometry

    atoms = read(fname)

    print(f"Perfom geometry refinement for")
    inform(atoms, symprec=args.tolerance)

    if args.prim:
        atoms = standardize_cell(atoms, to_primitve=True, symprec=args.tolerance)
        outfile = f"{args.geometry}.primitive"
    elif args.conv:
        atoms = standardize_cell(atoms, to_primitve=False, symprec=args.tolerance)
        outfile = f"{args.geometry}.conventional"
    elif args.center:
        atoms = center_atoms(atoms)
        outfile = f"{args.geometry}.center"
    elif args.origin:
        atoms = center_atoms(atoms, origin=True)
        outfile = f"{args.geometry}.origin"
    else:
        atoms = refine_cell(atoms, symprec=args.tolerance)
        outfile = f"{args.geometry}.refined"

    write(atoms, outfile, format=args.format, spacegroup=True, scaled=not args.cart)

    coords = "fractional coordinates"
    if args.cart:
        coords = "cartesian coordinates"

    print()
    print(f"New structure written in {bold(coords)} and {args.format} format to")
    print(f"  {bold(outfile)}")


if __name__ == "__main__":
    main()


def center_com(atoms):
    """ centre the center of mass """
    midpoint = atoms.cell.sum(axis=0) / 2
    atoms.positions -= atoms.get_center_of_mass()
    atoms.positions += midpoint

    return atoms


def center_pos(atoms):
    """ centre the average position"""
    midpoint = atoms.cell.sum(axis=0) / 2
    atoms.positions -= atoms.positions.mean(axis=0)
    atoms.positions += midpoint

    return atoms


def center_atoms(atoms, origin=False):
    """ Center atoms: Move center of mass, then average position to cell midpoint """

    # 0) move 1. atom to origin
    atoms.positions -= atoms[0].position
    atoms.wrap()

    # i) move center of mass to midpoint
    atoms = center_com(atoms)
    for ii in range(10):
        temp_pos = atoms.positions.copy()
        atoms.wrap()
        if np.linalg.norm(temp_pos - atoms.positions) > 1e-12:
            atoms = center_com(atoms)
            continue
        else:
            break
        # if we end up here, this was not succesful
        warn("FIXME", level=2)

    # ii) move average position to midpoint
    atoms = center_pos(atoms)
    for ii in range(10):
        temp_pos = atoms.positions.copy()
        atoms.wrap()
        if np.linalg.norm(temp_pos - atoms.positions) > 1e-12:
            atoms = center_pos(atoms)
            continue
        else:
            break
        # if we end up here, this was not succesful
        warn("FIXME", level=2)

    if origin:
        atoms.positions -= atoms[0].position
        atoms.wrap()

    return atoms
