""" Creation of BTD matrices from a sparse matrix """

from .sparse import SparseCSR


class BlockTriDiagonal(object):
    r""" A block-tri-diagonal (BTD) matrix format with arbitrary block sizes

    The block-tri-diagonal matrix format is a dense format made up in chunks of

    .. math::
        \mathbf M = 
           \begin{bmatrix}
             \mathbf A_1 & \mathbf C_1 & \dots
             \\
             \mathbf B_2 & \mathbf A_2 & \mathbf C_2 & \dots
             \\
             \mathbf 0   & \mathbf B_3 & \mathbf A_3 & \mathbf C_3
             \\
             \vdots & & \ddots &
           \end{bmatrix}

    It will allow one to solve particular problems more efficiently, as well as
    handling larger matrices due to the smaller memory footprint.

    Notes
    -----
    The BTD matrix requires a square matrix, the indices for the matrix will be ensured symmetric.

    This matrix format is different from `scipy.sparse.bsr_matrix` since each block
    need not have the same size.

    Parameters
    ----------
    sparse : scipy.sparse.*_matrix
        sparse matrix to create the BTD from
    blocks : array_like, optional
        user-defined block sizes, if not supplied a subsequent `finalize` call
        must be made to determine the block sizes.
    pivot : array_like, optional
        pivot table for the matrix elements in `sparse`. They are used as
        ``pivot[0] == row``user-defined block sizes, if not supplied a subsequent `finalize` call
        must be made to determine the block sizes.
    """

    def __init__(self, sparse, blocks=None, pivot=None):
        csr = sparse.tocsr()
        if csr.shape[0] != csr.shape[1]:
            raise ValueError(self.__class__.__name__ + ' cannot initialize a BTD matrix with a non-square matrix.')

        # Save the sparse pattern internally, but with a small data-type
        sym = csr + csr.transpose()
        self._indices = sym.indices[:]
        self._indptr = sym.indptr[:]
        del sym

        # Save blocks
        self._blocks = blocks

    @property
    def blocks(self):
        """ Block sizes used in algorithms """
        return self._blocks
