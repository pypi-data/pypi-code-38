"""
Utilities related to CVXOPT.
"""

import logging

import numpy as np
import cvxopt

from hynet.types_ import hynet_int_, hynet_float_, hynet_complex_
from hynet.utilities.base import create_sparse_matrix

_log = logging.getLogger(__name__)


def scipy2cvxopt(matrix):
    """
    Return the SciPy sparse matrix as a CVXOPT sparse matrix.

    Parameters
    ----------
    matrix : .hynet_sparse_
        Matrix that shall be converted.
    Returns
    -------
    cvxopt.spmatrix
        Input matrix in CVXOPT's sparse format.
    """
    A = matrix.tocoo()
    return cvxopt.spmatrix(A.data.tolist(), A.row.tolist(), A.col.tolist(), A.shape)


def cvxopt2scipy(matrix, nonzero_only=False):
    """
    Return the CVXOPT sparse matrix as a SciPy sparse matrix.

    Parameters
    ----------
    matrix : cvxopt.spmatrix
        Matrix that shall be converted.
    nonzero_only : bool, optional
        If ``False`` (default), all entries are transferred, regardless of
        their value. If ``True``, the data is checked and only nonzero entries
        are transferred.
    Returns
    -------
    .hynet_sparse_
        Input matrix as a SciPy sparse matrix.
    """
    if matrix.typecode == 'i':
        dtype = hynet_int_
    elif matrix.typecode == 'd':
        dtype = hynet_float_
    elif matrix.typecode == 'z':
        dtype = hynet_complex_
    else:
        raise ValueError("Unknown CVXOPT typecode '{:s}'."
                         .format(matrix.typecode))

    row = np.array(matrix.I.T)[0]
    col = np.array(matrix.J.T)[0]
    data = np.array(matrix.V.T)[0]

    if nonzero_only:
        mask = (data != 0)
        row = row[mask]
        col = col[mask]
        data = data[mask]

    return create_sparse_matrix(row, col, data,
                                matrix.size[0], matrix.size[1], dtype=dtype)
