"""
Rank-1 approximation of a partial Hermitian matrix.
"""

import logging

import numpy as np
import matplotlib.pyplot as plt

from hynet.types_ import hynet_float_, hynet_complex_
from hynet.utilities.base import (create_sparse_matrix,
                                  create_sparse_diag_matrix,
                                  Timer)
from hynet.utilities.graph import traverse_graph, get_graph_components

_log = logging.getLogger(__name__)


def rank1approx_via_traversal(V, edges, roots):
    """
    Return a rank-1 approximation ``vv^H`` of ``V`` based on a graph traversal.

    Assuming that ``V = vv^H`` (i.e., ``rank(V) = 1``), the off-diagonal
    element in row ``i`` and column ``j`` is ``V_ij = v_i*conj(v_j)``. Thus,
    ``|v_j| = sqrt(V_jj)`` and ``arg(v_j) = arg(v_i) - arg(V_ij)``. This is
    utilized to recover ``v`` by setting its element's magnitude to the square
    root of the diagonal elements of ``V`` and reconstructing the angle of its
    elements by accumulating the angle differences from the respective root
    node of in the graph associated with ``V``. The angle at the root node(s)
    is set to zero.
    """
    V = V.tocsr()  # Conversion to CSR for indexing
    dim_v = V.shape[0]
    v = np.zeros(dim_v, dtype=hynet_complex_)
    np.sqrt(V.diagonal().real, out=v)

    def update_angle(node, node_pre, cycle):
        """Callback for the graph traversal to update the angles."""
        if cycle or np.isnan(node_pre):
            return
        angle = np.angle(v[node_pre]) - np.angle(V[node_pre, node])
        v[node] *= np.exp(1j * angle)

    traverse_graph(np.arange(dim_v), edges, update_angle, roots)
    return v


def calc_rank1approx_rel_err(V, v, edges):
    """Calculate the relative reconstruction error for all edges."""
    (e_src, e_dst) = edges
    if not e_src.size:
        return np.ndarray(0, dtype=hynet_float_)
    vv_ = np.multiply(v[e_src], v[e_dst].conj())
    V_ = np.asarray(V.tocsr()[e_src, e_dst])[0]
    return np.true_divide(np.abs(vv_ - V_), np.abs(vv_))


def calc_rank1approx_mse(V, v, edges):
    """
    Calculate the mean squared error for the rank-1 approximation.

    Returns the mean of the squared error of the elements on the diagonal as
    well as those on sparsity pattern defined by ``edges``.
    """
    # ATTENTION: Use caution when modifying this function as the least
    # squares rank-1 approximation depends on this particular MSE calculation.
    (e_src, e_dst) = edges
    vv_ = np.concatenate((np.square(np.abs(v)),
                          np.multiply(v[e_src], v[e_dst].conj()),
                          np.multiply(v[e_dst], v[e_src].conj())))
    # The case distinction is necessary due to inconsistencies of SciPy...
    V = V.tocsr()  # Conversion to CSR for indexing
    V_ = V.diagonal()
    if e_src.size:
        V_ = np.concatenate((V_,
                             np.asarray(V[e_src, e_dst])[0],
                             np.asarray(V[e_dst, e_src])[0]))
    return np.square(np.abs(vv_ - V_)).mean()


def rank1approx_via_least_squares(V, edges, roots, grad_thres=1e-7,
                                  mse_rel_thres=0.002, max_iter=300,
                                  show_convergence_plot=False):
    """
    Return a rank-1 approximation ``vv^H`` of ``V`` by minimizing the squared error.

    The rank-1 approximation may be put as the following optimization problem::

        minimize  ||P(vv^H - V)||_F^2
        v in C^N

    Therein, ``P(X)`` is the projection of the matrix ``X`` onto the sparsity
    pattern defined by ``edges``, i.e., all diagonal elements and the
    off-diagonal elements ``(edges[k][0], edges[k][1])`` and
    ``(edges[k][1], edges[k][0])`` for ``k = 0,...,K-1``, where ``K`` is the
    number of edges. ``||.||_F`` denotes the Frobenius norm. For ``V >= 0``
    (psd) and ``V != 0``, this problem is nonconvex, i.e., the objective is not
    convex over the entire ``C^N``. (If ``rank(V) = 1`` and ``V = xx^H``, then
    the objective is locally convex at ``x``.)

    This function finds a (local) optimizer of this problem using a Wirtinger
    calculus based gradient descent with an Armijo-Goldstein step size control,
    which is initialized with the vector ``v`` obtained from the graph
    traversal rank-1 approximation method. (During the iterations it is ensured
    that the least squares error decreases, otherwise the iterations are
    aborted with a warning. Consequently, in terms of the least squares error,
    this approximation is at least as accurate as the traversal-based
    approximation.)

    Parameters
    ----------
    V : .hynet_sparse_
        Matrix that should be approximated by ``vv^H``.
    edges : (numpy.ndarray[.hynet_int_], numpy.ndarray[.hynet_int_])
        Specification of the sparsity pattern of the matrix ``V``.
    roots : numpy.ndarray[.hynet_int_]
        Root nodes for the graph components of the sparsity pattern. The
        absolute angle in ``v`` is adjusted such that the absolute angle
        at the root nodes is zero.
    grad_thres : .hynet_float_, optional
        Absolute threshold on the 2-norm of the objective's gradient w.r.t.
        ``v`` divided by ``N``. (Termination criterion on the first order
        condition for local optimality.)
    mse_rel_thres : .hynet_float_, optional
        Threshold on the relative improvement of ``||P(vv^H - V)||_F^2 / N``
        from the candidate solution ``v`` in iteration ``i`` to ``v`` in
        iteration ``i + 1``. (Termination criterion on stalling progress.)
    max_iter : .hynet_int_, optional
        Maximum number of iterations. (Fallback in case the other termination
        criteria are not met in a reasonable number of iterations.)
    show_convergence_plot : bool, optional
        If True, a plot is shown to illustrate the convergence behavior.

    Returns
    -------
    v : numpy.ndarray
        Vector ``v``, where  ``vv^H`` approximates ``V`` on the sparsity pattern.
    """
    timer = Timer()
    V = V.tocsr()  # Conversion to CSR for indexing
    (e_src, e_dst) = edges
    N = V.shape[0]
    K = len(e_src)
    f = lambda x: calc_rank1approx_mse(V, x, edges) * (N + 2*K)
    gamma = 0.5
    iteration = 0

    v = rank1approx_via_traversal(V, edges, roots)
    mse = calc_rank1approx_mse(V, v, edges)

    if show_convergence_plot:
        iter_mse = [mse]
        iter_grad = [np.nan]

    vv_offd = np.ones(K, dtype=hynet_complex_)
    P_vv = create_sparse_diag_matrix(np.ones(N)) \
         + create_sparse_matrix(e_src, e_dst, vv_offd, N, N) \
         + create_sparse_matrix(e_dst, e_src, vv_offd.conj(), N, N)

    # The case distinction is necessary due to inconsistencies of SciPy...
    P_V = create_sparse_diag_matrix(V.diagonal())
    if K != 0:
        P_V += create_sparse_matrix(e_src, e_dst,
                                    np.asarray(V[e_src, e_dst])[0], N, N) \
             + create_sparse_matrix(e_dst, e_src,
                                    np.asarray(V[e_dst, e_src])[0], N, N)

    while iteration < max_iter:
        np.multiply(v[e_src], v[e_dst].conj(), out=vv_offd)
        P_vv[range(N), range(N)] = np.square(np.abs(v))
        P_vv[e_src, e_dst] = vv_offd
        P_vv[e_dst, e_src] = vv_offd.conj()
        grad_v = 2 * (P_vv - P_V).dot(v)
        grad_v_mse = np.square(np.abs(grad_v)).mean()

        if grad_v_mse <= grad_thres:
            _log.debug("LS rank-1 approx. ~ Threshold on gradient was reached.")
            break

        gamma = get_armijo_step_size(f, v, grad_v, 2 * gamma)
        v_new = v - gamma * grad_v
        mse_new = calc_rank1approx_mse(V, v_new, edges)

        if mse_new > mse:
            _log.warning(("The gradient descent method was aborted after {0} "
                          "iterations and a gradient 'MSE' of {1:.3g} as the "
                          "objective increased.").format(iteration, grad_v_mse))
            break

        if 1 - mse_new/mse < mse_rel_thres:
            _log.debug("LS rank-1 approx. ~ Progress stalled, iteration aborted.")
            break

        if show_convergence_plot:
            iter_mse.append(mse_new)
            iter_grad.append(grad_v_mse)

        (v, mse) = (v_new, mse_new)
        iteration += 1

    if iteration == max_iter:
        _log.debug("LS rank-1 approx. ~ Maximum number of iterations reached.")

    # Adjust absolute phase in all components
    components = get_graph_components(np.arange(N), edges, roots)
    for component in components:
        v[component] *= np.exp(-1j * np.angle(v[component[0]]))

    if show_convergence_plot:
        fig = plt.figure(figsize=(10, 6))
        fig.suptitle("Least-Squares Rank-1 Approximation via Gradient Descent")
        ax = fig.add_subplot(2, 1, 1)
        ax.plot(iter_mse, color='xkcd:sea blue', linestyle='-', linewidth=1)
        ax.margins(x=0)
        ax.set_xlim(left=0)
        ax.set_title("Reconstruction MSE")
        ax = fig.add_subplot(2, 1, 2)
        ax.plot(iter_grad, color='xkcd:sea blue', linestyle='-', linewidth=1)
        ax.margins(x=0)
        ax.set_xlim(left=0)
        ax.set_title("2-norm of the gradient over the number of dimensions")
        ax.set_xlabel('Iteration')
        fig.subplots_adjust(hspace=0.3)
        fig.show()

    _log.debug("LS rank-1 approx. ~ Ended with gradient 'MSE' of "
               "{0:.3e} after {1} iterations ({2:.3f} sec.)"
               .format(grad_v_mse, iteration, timer.total()))
    return v


def get_armijo_step_size(f, x, grad_fx, gamma=1, epsilon=0.2, alpha=2):
    """
    Return a step size based on the Armijo-Goldstein condition.

    This step size is designed for a Wirtinger calculus based gradient descent
    method that minimizes the function ``f(x)``, where ``x in C^N`` is the
    current candidate solution, ``grad_fx`` is the gradient vector w.r.t.
    ``conj(x)`` evaluated at ``x``, and the step direction ``d = -grad_fx``.
    This function returns a step size ``s in R_(+)``, such that the algorithmic
    map reads ``x -> x + s * d``.
    """
    # LITERATURE:
    # 1) Armijo's rule is described, e.g., in "Nonlinear Programming - Theory
    #    and Algorithms" by Bazaraa, Sherali, and Shetty (3rd ed., ch. 8.3).
    # 2) Relevant aspects of Wirtinger calculus are described, e.g., in
    #    "Complex-Valued Adaptive Signal Processing Using Nonlinear Functions"
    #    by Li and Adali (EURASIP Journal on Advances in Signal Processing)

    fx = f(x)
    dd = -epsilon * 2 * np.sum(np.square(np.abs(grad_fx)))

    theta = lambda gamma: f(x - gamma*grad_fx)
    theta_tld = lambda gamma: fx + gamma * dd

    while gamma > 1e-10:
        delta = theta(gamma) - theta_tld(gamma)
        delta_bar = theta(alpha*gamma) - theta_tld(alpha*gamma)
        if delta <= 0 < delta_bar:
            return gamma
        if delta <= 0:
            gamma *= alpha
        else:
            gamma /= alpha

    _log.warning("The step size is very small.")
    return gamma
