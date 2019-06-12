#!/usr/bin/env python3
# coding: utf-8

"""Hi-C visualization

A lightweight library for quickly parsing, loading and
viewing contact maps in instaGRAAL or csv format.
"""


import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from Bio import SeqIO
import hicstuff.io as hio
from hicstuff.hicstuff import normalize_sparse

SEABORN = False

try:
    import seaborn as sns

    SEABORN = True
except ImportError:
    pass


DEFAULT_DPI = 500
DEFAULT_SATURATION_THRESHOLD = 99


load_sparse_matrix = hio.load_sparse_matrix
raw_cols_to_sparse = hio.raw_cols_to_sparse


def sparse_to_dense(M, remove_diag=True):
    """
    Converts a sparse square matrix into a full dense matrix. Removes the
    diagonal by default.

    Parameters
    ----------
    M : scipy.sparse.coo_matrix
        A sparse representation of the matrix.
    remove_diag : bool
        Whether the diagonal

    Returns
    -------
    numpy.array :
        The matrix in dense format.

    Example
    -------

        >>> import numpy as np
        >>> from scipy.sparse import coo_matrix
        >>> row, col = np.array([1, 2, 3]), np.array([3, 2, 1])
        >>> data = np.array([4, 5, 6])
        >>> S = coo_matrix((data, (row, col)))
        >>> M = sparse_to_dense(S, remove_diag=True)
        >>> for u in M:
        ...     print(u)
        [0 0 0 0]
        [ 0  0  0 10]
        [0 0 0 0]
        [ 0 10  0  0]

    """
    sub_diag = 2 if remove_diag else 1
    D = M.todense()
    E = D + np.transpose(D) - sub_diag * np.diag(np.diag(D))
    return np.array(E)


def plot_matrix(
    array, filename=None, vmin=0, vmax=None, dpi=DEFAULT_DPI, cmap="Reds"
):
    """A function that performs all the tedious matplotlib
    magic to draw a 2D array with as few parameters and
    as little whitespace as possible.

    Adjusted from https://github.com/koszullab/metaTOR
    """

    if vmax is None:
        vmax = np.percentile(array, DEFAULT_SATURATION_THRESHOLD)
    # plt.gca().set_axis_off()
    # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    # plt.margins(0, 0)
    # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    # plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.figure()
    plt.imshow(array, vmin=vmin, vmax=vmax, cmap=cmap, interpolation="none")
    plt.colorbar()
    plt.axis("off")
    if filename:
        plt.savefig(filename, bbox_inches="tight", pad_inches=0.0, dpi=dpi)
        del filename
    else:
        plt.show()


def normalize(M, norm="SCN"):
    """Attempt to normalize if hicstuff is found, does nothing otherwise.
    """
    try:
        return normalize_sparse(M, norm=norm)
    except NameError:
        return M


def scaffold_distribution(genome, threshold=100, plot=True):
    """Visualize scaffold size distribution

    Compute (and optionally display) scaffold size distribution for
    a genome in fasta format.

    Parameters
    ----------
    genome : str, file or pathlib.Path
        The genome scaffold file (or file handle)
    threshold : int, optional
        The size below which scaffolds are discarded, by default 1000000
    plot : bool, optional
        Whether to plot the results

    Returns
    -------
    list :
        The list of scaffold sizes in decreasing order.
    """

    handle = SeqIO.parse(genome, "fasta")
    lengths = sorted(
        (len(u) for u in handle if len(u) > threshold), reverse=True
    )

    if plot:
        x, y = zip(*enumerate(lengths))
        plt.scatter(x=x, y=y)
        plt.show()

    return lengths


def reorder_fasta(genome, output, threshold=100000):
    """Reorder and trim a fasta file

    Sort a fasta file by record lengths, optionally trimming the smallest ones.


    Parameters
    ----------
    genome : str, file or pathlib.Path
        The genome scaffold file (or file handle)
    output : str, file or pathlib.Path
        The output file to write to
    threshold : int, optional
        The size below which scaffolds are discarded, by default 100000
    """

    handle = SeqIO.parse(genome, "fasta")
    handle_to_write = sorted(
        (len(u) for u in handle if len(u) > threshold), reverse=True
    )
    SeqIO.write(handle_to_write, output, "fasta")
