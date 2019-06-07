"""
Rank-1 approximation of partial Hermitian matrices.

This module provides an object-oriented representation of the rank-1
approximation functionality provided in *hynet*'s utilities.

See Also
--------
hynet.utilities.rank1approx
hynet.qcqp.solver
"""

import logging
import abc

from hynet.utilities.rank1approx import (rank1approx_via_traversal,
                                         rank1approx_via_least_squares,
                                         calc_rank1approx_rel_err,
                                         calc_rank1approx_mse)

_log = logging.getLogger(__name__)


class Rank1Approximator(abc.ABC):
    """
    Abstract base class for rank-1 approximators for partial Hermitian matrices.

    Derived classes implement a rank-1 approximation for partial Hermitian
    matrices, where the sparsity pattern of the latter is defined by its
    associated undirected graph.
    """
    @abc.abstractmethod
    def __call__(self, V, edges, roots):
        """
        Return a vector ``v`` such that ``vv^H`` approximates ``V``.

        Parameters
        ----------
        V : .hynet_sparse_
        edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
            Specification of the sparsity pattern of the matrix ``V`` via the
            edges ``(edge_src, edge_dst)`` of an undirected graph. The matrix
            ``V`` may only have nonzero/relevant entries in row/column
            ``edge_src[i]`` and column/row ``edge_dst[i]``, with
            ``i in range(K)`` where ``K = len(edge_src) = len(edge_dst)``, as
            well as on the diagonal. The edges specified in ``edges`` must be
            *unique*, i.e., there must not exist any parallel or anti-parallel
            edges.
        roots : numpy.ndarray[.hynet_int_]
            Root nodes of the undirected graph defined by ``edges`` that
            specifies the sparsity pattern. At these root nodes the absolute
            angle of the vector ``v`` is set to zero.

        Returns
        -------
        v : numpy.ndarray[.hynet_complex_]
        """

    @staticmethod
    def calc_mse(V, v, edges):
        """Calculate the mean squared error for the rank-1 approximation."""
        return calc_rank1approx_mse(V, v, edges)

    @staticmethod
    def calc_rel_err(V, v, edges):
        """Calculate the relative reconstruction error for all edges."""
        return calc_rank1approx_rel_err(V, v, edges)


class GraphTraversalRank1Approximator(Rank1Approximator):
    """
    Graph traversal based rank-1 approximation of partial Hermitian matrices.

    Please refer to ``rank1approx_via_traversal`` for more details.

    See Also
    --------
    hynet.utilities.rank1approx.rank1approx_via_traversal
    """
    def __call__(self, V, edges, roots):
        return rank1approx_via_traversal(V, edges, roots)


class LeastSquaresRank1Approximator(Rank1Approximator):
    """
    Graph traversal based rank-1 approximation of partial Hermitian matrices.

    Please refer to ``rank1approx_via_least_squares`` for more details.

    Parameters
    ----------
    grad_thres : .hynet_float_
    mse_rel_thres : .hynet_float_
    max_iter : .hynet_int_
    show_convergence_plot : bool

    See Also
    --------
    hynet.utilities.rank1approx.rank1approx_via_least_squares
    """
    def __init__(self, grad_thres=1e-7, mse_rel_thres=0.002, max_iter=300,
                 show_convergence_plot=False):
        self.grad_thres = grad_thres
        self.mse_rel_thres = mse_rel_thres
        self.max_iter = max_iter
        self.show_convergence_plot = show_convergence_plot

    def __call__(self, V, edges, roots):
        return rank1approx_via_least_squares(
            V, edges, roots,
            grad_thres=self.grad_thres,
            mse_rel_thres=self.mse_rel_thres,
            max_iter=self.max_iter,
            show_convergence_plot=self.show_convergence_plot
        )
