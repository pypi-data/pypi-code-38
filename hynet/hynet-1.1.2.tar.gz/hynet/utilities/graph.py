"""
Graph-related utilities.
"""

import logging
import warnings

import numpy as np
import scipy.sparse
import scipy.sparse.csgraph

from hynet.types_ import hynet_int_
from hynet.utilities.base import (create_sparse_matrix,
                                  create_sparse_zero_matrix)

_log = logging.getLogger(__name__)


def eliminate_parallel_edges(edges):
    """
    Eliminates parallel edges from the graph and returns those edges.

    The edges are considered undirected, i.e., and the source and destination
    node are interchangeable. In the returned edges, the source is set to the
    adjacent node with the higher node number.
    """
    E = np.column_stack((edges[0], edges[1]))
    if E.shape[0] != 0:
        E.sort(axis=1)
        E = np.unique(E, axis=0)
    return E[:, 1], E[:, 0]


def get_adjacency_matrix(edges, num_nodes=None, weights=None):
    """
    Return the adjacency matrix for an undirected graph specified by its edges.

    Parameters
    ----------
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    num_nodes : int, optional
        Number of nodes in the graph. By default, this is set to the maximum
        node number in ``edges`` plus one.
    weights : numpy.ndarray[.hynet_float_], optional
        Edge weights for a *weighted* adjacency matrix.

    Returns
    -------
    A : .hynet_sparse_
        Adjacency matrix of the undirected graph.
    """
    (e_src, e_dst) = edges

    if not e_src.size:
        num_nodes = 0 if num_nodes is None else num_nodes
        return create_sparse_zero_matrix(num_nodes, num_nodes, dtype=hynet_int_)

    if min([e_src.min(), e_dst.min()]) < 0:
        raise ValueError('Negative node numbers are not supported.')

    if np.any(e_src == e_dst):
        raise ValueError('The graph must not contain any self-loops.')

    (e_src, e_dst) = eliminate_parallel_edges((e_src, e_dst))

    max_node = max([e_src.max(), e_dst.max()])
    if num_nodes is None:
        num_nodes = max_node + 1
    elif num_nodes <= max_node:
        raise ValueError('The edges are referencing non-existent nodes.')

    if weights is None:
        weights = np.ones(len(e_src), dtype=hynet_int_)
    else:
        if len(weights) != len(e_src):
            raise ValueError('The number of weights and edges must match.')
        if np.any(weights == 0):
            _log.warning('Some edge weights are zero.')

    A = create_sparse_matrix(e_src, e_dst, weights, num_nodes, num_nodes,
                             dtype=weights.dtype)
    A += A.transpose()
    return A


def get_laplacian_matrix(edges, num_nodes=None):
    """
    Return the Laplacian matrix for an undirected graph specified by its edges.

    Parameters
    ----------
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    num_nodes : int, optional
        Number of nodes in the graph. By default, this is set to the maximum
        node number in ``edges`` plus one.

    Returns
    -------
    L : .hynet_sparse_
        Laplacian matrix of the undirected graph.
    """
    A = get_adjacency_matrix(edges, num_nodes=num_nodes)
    if A.shape == (0, 0):
        return create_sparse_zero_matrix(0, 0, dtype=hynet_int_)
    return scipy.sparse.csgraph.laplacian(A)


def get_minimum_spanning_tree(edges, weights):
    """
    Return the minimum spanning tree in terms of an edges tuple.

    Parameters
    ----------
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    weights : numpy.ndarray[.hynet_float_], optional
        Edge weights.

    Returns
    -------
    mst_edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the minimum spanning tree in terms of node number tuples.
    """
    A = get_adjacency_matrix(edges, weights=weights)
    if A.shape == (0, 0):
        return np.ndarray(0, dtype=hynet_int_), np.ndarray(0, dtype=hynet_int_)
    return scipy.sparse.csgraph.minimum_spanning_tree(A).nonzero()


def get_num_spanning_trees(edges):
    """
    Return the number of spanning trees for the given undirected graph.

    The number of spanning trees is determined using Kirchhoff's matrix tree
    theorem, see e.g. [1]_.

    *Caution:* The vertices must be numbered consecutively starting from zero.
    If the graph is not connected, the number of spanning trees is zero.

    *Remark:* As SciPy does not inherently support the computation of the
    determinant of a sparse matrix, the Laplacian matrix is converted to a
    dense (NumPy) matrix for the computation of a cofactor of the Laplacian.
    Due to this, the performance is potentially poor for large graphs.

    Parameters
    ----------
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.

    Returns
    -------
    numpy.float64
        Number of spanning trees of the undirected graph.

    Raises
    ------
    OverflowError : If the computation results in an overflow.

    References
    ----------
    .. [1] Russell Merris, "Laplacian Matrices of Graphs: A Survey", Linear
           Algebra and its Applications, vol. 197-198, p. 143-176, 1994.
    """
    L = get_laplacian_matrix(edges).toarray()
    with warnings.catch_warnings():
        warnings.filterwarnings('error')  # Treat warnings as errors
        try:
            num_span_trees = np.around(np.linalg.det(L[:-1, :-1]))
        except Warning as warning:
            if 'overflow' in str(warning).lower():
                raise OverflowError('Overflow encountered during the computation '
                                    'of the number of spanning trees.') from None
            else:
                _log.warning(str(warning))
    return num_span_trees


def traverse_graph(nodes, edges, callback, roots=None, auto_root=True):
    """
    Traverse the graph and run a callback at every node.

    The graph is traversed in a depth-first fashion and, at every visited node,
    the provided callback function is called, which must exhibit the signature::

        def callback(node, node_pre, cycle)

    Therein, ``node`` is the currently visited node, ``node_pre`` is the
    previously visited node (or ``numpy.nan`` if the current node is the
    component's root, i.e., the traversal entered a new component), and
    ``cycle`` is ``True`` if the current node was already visited, i.e., the
    edge traversed from the previous to the current node closes a cycle. The
    callback function returns an abort flag, i.e., if the callback returns
    ``True``, the traversal is aborted.

    **Remark:** This function is most efficient if the nodes are numbered
    consecutively from zero to the number of nodes minus one. Negative node
    numbers are not supported.

    Parameters
    ----------
    nodes : numpy.ndarray[.hynet_int_]
        Node numbers of the graph.
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Edges of the graph in terms of node number tuples.
    callback : function
        Node visit callback function.
    roots : numpy.ndarray[.hynet_int_], optional
        Numbers of the root nodes of the graph.
    auto_root : bool, optional
        If True (default), components without a root node are assigned an
        arbitrary node as its root.
    """
    # timer = Timer()
    # debug_message = ("Graph traversal with '"
    #                  + callback.__name__ + "' ({:.3f} sec.)")
    roots = np.ndarray(0) if roots is None else roots

    if not nodes.size:
        return

    (e_src, e_dst) = eliminate_parallel_edges(edges)

    if min(nodes) < 0:
        raise RuntimeError('Negative node numbers are not supported.')

    if not (np.all(np.isin(e_src, nodes)) and np.all(np.isin(e_dst, nodes))):
        raise RuntimeError('The edges are referencing non-existent nodes.')

    if not np.all(np.isin(roots, nodes)):
        raise RuntimeError('The roots are referencing non-existent nodes.')

    # REMARK: As this implementation is robust against duplicate entries in
    # 'nodes', this data validity check is omitted.

    N = max(nodes) + 1
    stack = np.zeros(N, dtype=hynet_int_)  # Stack of nodes to be visited
    visited = np.zeros(N, dtype=bool)      # Indicates if a node was visited
    root_idx = 0                           # Index of the next root to process

    # Set gaps in the node numbering to 'visited'
    visited[np.setdiff1d(range(N), nodes)] = True

    while not np.all(visited):
        # Ignore ambiguous root nodes
        while root_idx < len(roots) and visited[roots[root_idx]]:
            _log.warning("Ambiguous root {} is ignored.".format(roots[root_idx]))
            root_idx += 1

        # Set root node for next component to traverse
        stack_top = 0
        if root_idx < len(roots):
            stack[stack_top] = roots[root_idx]
            root_idx += 1
        elif auto_root:
            stack[stack_top] = np.where(~visited)[0][0]
        else:
            raise RuntimeError('Graph contains components without root nodes.')

        if callback(stack[stack_top], np.nan, False):
            # _log.debug(debug_message.format(timer.total()))
            return

        visited[stack[stack_top]] = True

        # Perform depth-first traversal of this connected component
        while stack_top >= 0:
            # Pop a previously visited node from the stack
            node_pre = stack[stack_top]
            stack_top -= 1

            # Visit all adjacent nodes
            idx_src = e_src == node_pre
            idx_dst = e_dst == node_pre
            adjacent_nodes = np.concatenate((e_dst[idx_src], e_src[idx_dst]))

            for node in adjacent_nodes:
                if callback(node, node_pre, visited[node]):
                    # _log.debug(debug_message.format(timer.total()))
                    return

            # Push previously unvisited adjacent nodes to the top of the stack
            adjacent_nodes = adjacent_nodes[~visited[adjacent_nodes]]
            new_top = stack_top + len(adjacent_nodes)
            stack[(stack_top + 1):(new_top + 1)] = adjacent_nodes[::-1]
            stack_top = new_top
            visited[adjacent_nodes] = True

            # Remove traversed edges
            idx = idx_src | idx_dst
            e_src[idx] = -1
            e_dst[idx] = -1

    # _log.debug(debug_message.format(timer.total()))


def is_acyclic_graph(nodes, edges):
    """Return ``True`` if the graph is acyclic and ``False`` otherwise."""

    # Flag for acyclicity: For the closure to work, we have to avoid a
    # direct assignment in the callback as this causes Python to create a
    # local variable. Due to this, the flag is stored in a list.
    acyclic = [True]

    def detect_cycles(node, node_pre, cycle):  # pylint: disable=unused-argument
        """Callback for the graph traversal to detect cycles."""
        if cycle:
            acyclic[0] = False
            return True  # Abort traversal
        return False

    traverse_graph(nodes, edges, detect_cycles)
    return acyclic[0]


def get_graph_components(nodes, edges, roots=None):
    """
    Return a list of connected components.

    The returned list contains an element for every connected component, where
    the element constitutes an array with all nodes of that component. The
    first element of the array is the root node of the respective component.
    """
    components = []

    def identify_components(node, node_pre, cycle):
        """Callback for the graph traversal to identify components."""
        if np.isnan(node_pre):
            components.append([node])
        elif not cycle:
            components[-1].append(node)

    traverse_graph(nodes, edges, identify_components, roots)
    return [np.array(component) for component in components]
