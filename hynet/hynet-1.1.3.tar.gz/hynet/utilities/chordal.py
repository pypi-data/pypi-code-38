"""
Utilities related to chordal matrices.
"""

import logging

import numpy as np
import scipy.sparse
import chompack as cp
import cvxopt.amd

from hynet.types_ import hynet_int_
from hynet.utilities.base import create_sparse_diag_matrix, Timer
from hynet.utilities.cvxopt import scipy2cvxopt, cvxopt2scipy
from hynet.utilities.graph import get_laplacian_matrix
from hynet.utilities.worker import workers

_log = logging.getLogger(__name__)


def _get_graph_sparse_positive_definite_matrix(edges, num_nodes=None):
    """
    Return a positive definite matrix with the graph's sparsity pattern.
    """
    L = get_laplacian_matrix(edges, num_nodes=num_nodes)
    return L + create_sparse_diag_matrix(np.ones(L.shape[0]), dtype=hynet_int_)


def get_chordal_extension_cliques(edges, num_nodes=None, amalgamation_size=None,
                                  amalgamation_fill=None):
    """
    Return a list of cliques of a chordal extension of the given graph.

    This function creates a low fill-in chordal extension of the given
    undirected graph (via a symbolic Cholesky factorization with an approximate
    minimum-degree ordering) and returns the maximal cliques of this
    chordal graph. This function uses CHOMPACK [1]_, a library for chordal
    matrix computations.

    The chordal extension often contains many small cliques, which, when
    utilized in a chordal conversion of a semidefinite program (SDP), can lead
    to the duplication of many variables and a high number of equality
    constraints that link the duplicates [2]_, [3]_. By introducing fewer but
    larger cliques in the chordal extension, a trade-off may be made between
    the size of the PSD matrices (i.e., size of the cliques) and the number of
    variable duplications and additional equality constraints in the chordal
    SDP [2]_, [3]_. This is achieved by creating a chordal extension based on
    the approximate minimum-degree ordering with a low fill-in and,
    subsequently, amalgamating (merging) cliques. This function supports the
    amalgamation heuristic described on page 891 in [3]_, which is provided
    with CHOMPACK [1]_.

    Parameters
    ----------
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    num_nodes : int, optional
        Number of nodes in the graph. By default, this is set to the maximum
        node number in ``edges`` plus one.
    amalgamation_size : int, optional
    amalgamation_fill : int, optional
        Amalgamation of cliques (disabled by default). If ``amalgamation_size``
        and ``amalgamation_fill`` is provided, the amalgamation heuristic
        described on page 891 in [3]_ is applied with ``t_size`` set to
        ``amalgamation_size`` and ``t_fill`` set to ``amalgamation_fill``. If
        either or both are ``None``, the clique amalgamation is disabled.

    Returns
    -------
    cliques : list[numpy.ndarray[.hynet_int_]]
        List of cliques, where a clique is specified by an array of node
        numbers.
    chords : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Chords of the chordal extension in terms of node number tuples.

    References
    ----------
    .. [1] http://chompack.readthedocs.io
    .. [2] Y. Sun, M. S. Andersen, and L. Vandenberghe, "Decomposition in Conic
           Optimization with Partially Separable Structure," SIAM J.
           Optimization 24(2), pp. 873-897, 2014.
    .. [3] M. S. Andersen, A. Hansson, and L. Vandenberghe, "Reduced-Complexity
           Semidefinite Relaxations of Optimal Power Flow Problems," IEEE
           Trans. Power Systems, vol. 29, no. 4, pp. 1855-1863, July 2014.
    """
    timer = Timer()

    if amalgamation_size is not None and amalgamation_fill is not None:
        merge_function = cp.merge_size_fill(tsize=amalgamation_size,
                                            tfill=amalgamation_fill)
    else:
        merge_function = None

    A = _get_graph_sparse_positive_definite_matrix(edges, num_nodes=num_nodes)

    # Find a chordal extension and the maximal cliques with CHOMPACK
    symbolic_factorization = cp.symbolic(scipy2cvxopt(A),
                                         p=cvxopt.amd.order,
                                         merge_function=merge_function)
    cliques = symbolic_factorization.cliques(reordered=False)
    cliques = [np.array(clique, dtype=hynet_int_) for clique in cliques]

    # Identify the introduced chords:
    #  1) Create lower triangular adjacency matrices for the chordal extension
    #     as well as the original graph
    #  2) Subtract the latter from the former to find the chords
    A_chordal = symbolic_factorization.sparsity_pattern(reordered=False,
                                                        symmetric=False)
    A_chordal = cvxopt2scipy(A_chordal, nonzero_only=True).tocoo()
    A_chordal.data[:] = 1  # Just to safeguard against changes in CHOMPACK...

    A = scipy.sparse.tril(A).tocoo()
    A.data[:] = 1

    A_chords = (A_chordal.astype(hynet_int_) - A.astype(hynet_int_)).tocoo()
    mask = (A_chords.data != 0)
    chords = A_chords.row[mask], A_chords.col[mask]

    assert len(chords[0]) == sum(symbolic_factorization.fill)

    _log.debug(("Chordal extension: {:d} cliques with max. order {:d} and "
                "{:d} extension and {:d} amalgamation chords ({:.3f} sec.)")
               .format(len(cliques),
                       int(symbolic_factorization.clique_number),
                       int(symbolic_factorization.fill[0]),
                       int(symbolic_factorization.fill[1]),
                       timer.total()))
    return cliques, chords


def get_clique_graphs(cliques, edges, chords):
    """
    Return the cliques with the associated indices of edges and chords.

    Parameters
    ----------
    cliques : list[numpy.ndarray[.hynet_int_]]
        List of cliques, where a clique is specified by an array of node
        numbers.
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    chords : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Chords of the chordal extension in terms of node number tuples.

    Returns
    -------
    list[tuple[numpy.ndarray[.hynet_int_],
               numpy.ndarray[.hynet_int_],
               numpy.ndarray[.hynet_int_]]]
        List of tuples comprising the following entries (in the same order):

            ``clique`` : (``numpy.ndarray[hynet_int_]``)
                Nodes of the clique, sorted in ascending order.
            ``clique_edges`` : (``numpy.ndarray[hynet_int_]``)
                Indices of the edges in the clique w.r.t. ``edges``.
            ``clique_chords`` : (``numpy.ndarray[hynet_int_]``)
                Indices of the chords in the clique w.r.t. ``chords``.
    """
    return workers.starmap(_get_clique_graph, zip(cliques,
                                                  [edges] * len(cliques),
                                                  [chords] * len(cliques)))


def _get_clique_graph(clique, edges, chords):
    clique = np.sort(clique)
    clique_edges = np.nonzero(np.logical_and(np.isin(edges[0], clique),
                                             np.isin(edges[1], clique)))[0]
    clique_chords = np.nonzero(np.logical_and(np.isin(chords[0], clique),
                                              np.isin(chords[1], clique)))[0]
    return clique, clique_edges, clique_chords
