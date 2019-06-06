"""
Utility functions for working with Brillouin zones
"""

from ase.dft import kpoints


def get_paths(atoms):
    """ Get recommended path connencting high symmetry points in the BZ.

    Args:
        atoms (Atoms): atoms object

    Returns:
        list: Recommended special points als list
        >>> ['GXL', 'KU']

    """
    cellinfo = kpoints.get_cellinfo(atoms.cell)
    paths = kpoints.special_paths[cellinfo.lattice].split(",")
    return paths


def get_special_points(atoms):
    """ return the high symmetry points of the BZ for atoms """
    return kpoints.get_special_points(atoms.cell)


def get_bands(atoms, paths=None, npoints=50):
    """ Get the recommended BZ path(s) for atoms """
    if paths is None:
        paths = get_paths(atoms)
    bands = []
    for path in paths:
        for ii, _ in enumerate(path[:-1]):
            bands.append(
                kpoints.bandpath(path[ii : ii + 2], atoms.cell, npoints=npoints)[0]
            )
    return bands


def get_labels(paths, latex=True):
    """ Get the labels for a given path for printing them with latex """
    if len(paths) == 1:
        labels = [*paths[0]]
    else:
        labels = [*"|".join(paths)]
    for ii, l in enumerate(labels):
        if l == "|":
            labels[ii] = f"{labels[ii-1]}|{labels[ii+1]}"
            labels[ii - 1], labels[ii + 1] = "", ""
        if l == "G" and latex:
            labels[ii] = "\\Gamma"
    labels = [l for l in labels if l]

    latexify = lambda sym: "$\\mathrm{\\mathsf{" + str(sym) + "}}$"
    if latex:
        return [latexify(sym) for sym in labels]
    return labels


def get_bands_and_labels(atoms, paths=None, npoints=50, latex=True):
    """ Combine get_bands() and get_labels() """
    if paths is None:
        paths = get_paths(atoms)
    return get_bands(atoms, paths, npoints=npoints), get_labels(paths, latex=latex)
