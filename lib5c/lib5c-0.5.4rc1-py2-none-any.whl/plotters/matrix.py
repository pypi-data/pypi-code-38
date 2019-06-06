"""
Module for simple visualization of matrix data.
"""

import numpy as np
import scipy.sparse as sparse
import matplotlib.pyplot as plt

from lib5c.util.plotting import plotter


@plotter
def plot_matrix(matrix, log=False, pseudocount=0, cmap=None, dpi=800, **kwargs):
    """
    Simple plotter function to quickly visualize a matrix.

    Parameters
    ----------
    matrix : np.ndarray or scipy.sparse.spmatrix
        The matrix to visualize.
    log : bool
        Pass True to log the matrix for visualization.
    pseudocount : int
        Pseudocount to add before logging. Ignored if ``log`` is False.
    cmap : matplotlib colormap, optional
        The colormap to use for visualizing the matrix entries. Default is
        'viridis' with nan's shown in red.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    if isinstance(matrix, sparse.spmatrix):
        matrix = matrix.toarray()
    if log:
        matrix = np.log(matrix + pseudocount)
    if cmap is None:
        cmap = plt.cm.viridis
        cmap.set_bad('red')
    plt.imshow(matrix, cmap=cmap, interpolation='none')
