"""
MOSEK-based solver for the *hynet*-specific QCQP problem (SD and SOC relaxation).
"""

import logging
import sys
import abc

import numpy as np
import mosek

from hynet.types_ import hynet_int_, hynet_float_, SolverType, SolverStatus
from hynet.utilities.base import Timer
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

try:
    from hynet.utilities.chordal import (get_chordal_extension_cliques,
                                         get_clique_graphs)
    CHORDAL_MODULE = True
except ImportError:
    CHORDAL_MODULE = False

_log = logging.getLogger(__name__)


def _validate_mosek_license():
    """
    Raise an ``ImportError`` if the MOSEK installation has no valid license.
    """
    try:
        with mosek.Env() as env:
            with env.Task() as task:
                task.optimize()
    except mosek.Error as exception:
        raise ImportError("MOSEK is not properly installed: " + str(exception))


# Abort the import if MOSEK has no valid license:
_validate_mosek_license()


def parse_status(status):
    """Parse the MOSEK status into a ``SolverStatus``."""
    if status == mosek.solsta.optimal:
        return SolverStatus.SOLVED
    if status in [mosek.solsta.prim_infeas_cer,
                  mosek.solsta.dual_infeas_cer]:
        return SolverStatus.INFEASIBLE

    # The following status codes are only available prior to MOSEK v9.0.
    if hasattr(mosek.solsta, 'near_optimal') and \
            status == mosek.solsta.near_optimal:
        return SolverStatus.INACCURATE
    if hasattr(mosek.solsta, 'near_prim_infeas_cer') and \
            status == mosek.solsta.near_prim_infeas_cer:
        return SolverStatus.INFEASIBLE
    if hasattr(mosek.solsta, 'near_dual_infeas_cer') and \
            status == mosek.solsta.near_dual_infeas_cer:
        return SolverStatus.INFEASIBLE

    return SolverStatus.FAILED


class SolverBase(SolverInterface):
    """
    Base class for MOSEK-based solvers for a relaxation of the QCQP.

    **Caution:** Before MOSEK 9.0, the dual variables were observed to be
    inaccurate at times. Due to this, if an older version than 9.0 is employed,
    the default tolerance on dual feasibility is tightened (cf. the ``param``
    attribute of the solver interface after the instantiation).
    """

    def __init__(self, **kwds):
        super().__init__(**kwds)
        if mosek.Env.getversion() < (9,):
            if not 'MSK_DPAR_INTPNT_CO_TOL_DFEAS' in self.param:
                self.param['MSK_DPAR_INTPNT_CO_TOL_DFEAS'] = 1e-9

    # REMARK concerning the logger callback:
    #   Originally, the class accepted an argument ``log_stream`` of type
    #   ``io.TextIOBase`` for the object initialization, which was set to
    #   ``sys.stdout`` by default and used as the output stream for the logging
    #   information in verbose mode. However, as a consequence of the solver
    #   object containing an open stream as an attribute, it was rendered
    #   non-serializable with pickle. As a customization of the logging output
    #   stream is typically not needed, this implementation hard-wires the
    #   logging to ``sys.stdout`` to render the solver objects 'pickleable'.
    def _logger(self, message):
        """Logger callback for MOSEK"""
        sys.stdout.write(message)
        sys.stdout.flush()

    @abc.abstractmethod
    def _add_voltage_matrix_constraints(self, task, qcqp, dim_x, ofs,
                                        x_lb, x_ub, x_bnd, coupling_emphasis):
        """Add the SOC or PSD constraint(s) on the ``v_tld``-part of ``x``."""

    def solve(self, qcqp):
        """
        Solve the given QCQP via a relaxation using MOSEK.

        The relaxation-specific constraints on the bus voltage matrix are
        added via the (abstract) method ``_add_voltage_matrix_constraints``,
        which must be implemented in a derived class.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the relaxed problem associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                ...and SOC or PSD constraint(s) on v_tld-part of x
        timer = Timer()
        (c, A, b, B, d, x_lb, x_ub) = qcqp.get_vectorization()
        dim_x = c.shape[0]

        # Voltage matrix coupling constraint emphasis: The implementation of
        # the constraints on the v_tld-part, i.e., the PSD or SOC constraints,
        # utilizes auxiliary variables that are coupled to v_tld via equality
        # constraints. We observed that, especially in case of the chordal SDR,
        # an unscaled implementation of these coupling constraints leads to an
        # insufficiently accurate coupling that considerably impedes the
        # accuracy of the solution. Due to this, we introduce a scaling of the
        # coupling constraints to enforce a more accurate coupling, where the
        # scaling is selected as the maximum sensitivity within the other
        # constraints.
        coupling_emphasis = max(abs(A).max(), abs(B).max())

        # Convert from the COO to the CSR sparse matrix format: In the COO
        # format, there can be duplicate entries (i.e., more than one value for
        # the same element in the matrix, which are to be added), but this is
        # not supported by MOSEK's ``putaijlist``. To this end, the matrices
        # are converted to the CSR format, which sums up the duplicate entries.
        c = c.tocsr()
        A = A.tocsr()
        B = B.tocsr()

        x_lb_is_nan = np.isnan(x_lb)
        x_ub_is_nan = np.isnan(x_ub)
        x_bnd = np.array([mosek.boundkey.ra] * dim_x)
        x_bnd[np.logical_and(x_lb_is_nan, x_ub_is_nan)] = mosek.boundkey.fr
        x_bnd[np.logical_and(~x_lb_is_nan, x_ub_is_nan)] = mosek.boundkey.lo
        x_bnd[np.logical_and(x_lb_is_nan, ~x_ub_is_nan)] = mosek.boundkey.up
        x_bnd[x_lb == x_ub] = mosek.boundkey.fx

        # For the following code, I used the MOSEK documentation provided at
        #  1) http://docs.mosek.com/8.1/pythonapi.pdf
        #  2) https://docs.mosek.com/8.1/pythonapi/optimizer-task.html
        with mosek.Env() as env:
            if self.verbose:
                env.set_Stream(mosek.streamtype.log, self._logger)

            with env.Task() as task:
                if self.verbose:
                    task.set_Stream(mosek.streamtype.log, self._logger)

                # Variable definition and bounds
                task.appendvars(dim_x)
                task.putvarboundlist(range(dim_x), x_bnd, x_lb, x_ub)

                # Objective
                task.putobjsense(mosek.objsense.minimize)
                idx_nz = c.nonzero()[0]
                task.putclist(idx_nz, c[idx_nz].toarray()[:, 0])

                # Equality constraints
                ofs = 0
                N = b.shape[0]
                task.appendcons(N)
                idx_nz = A.nonzero()
                task.putaijlist(ofs + idx_nz[0], idx_nz[1],
                                np.asarray(A[idx_nz[0], idx_nz[1]])[0])
                task.putconboundlist(range(ofs, ofs + N),
                                     [mosek.boundkey.fx] * N, b, b)
                ofs += N

                # Inequality constraints
                M = d.shape[0]
                task.appendcons(M)
                idx_nz = B.nonzero()
                task.putaijlist(ofs + idx_nz[0], idx_nz[1],
                                np.asarray(B[idx_nz[0], idx_nz[1]])[0])
                task.putconboundlist(range(ofs, ofs + M),
                                     [mosek.boundkey.up] * M, np.zeros(M), d)
                ofs += M

                # Add relaxation-specific constraints on the voltage matrix
                # (This method is overridden appropriately in derived classes)
                self._add_voltage_matrix_constraints(task, qcqp, dim_x, ofs,
                                                     x_lb, x_ub, x_bnd,
                                                     coupling_emphasis)

                # Set solver parameters
                for key, value in self.param.items():
                    task.putparam(key, str(value))

                # Optimization and solution recovery
                _log.debug(self.type.name + " ~ Modeling ({:.3f} sec.)"
                           .format(timer.interval()))
                task.optimize()
                solver_time = timer.interval()
                _log.debug(self.type.name + " ~ Solver ({:.3f} sec.)"
                           .format(solver_time))

                if self.verbose:
                    task.solutionsummary(mosek.streamtype.log)

                status = parse_status(task.getsolsta(mosek.soltype.itr))

                if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
                    x = np.ndarray(dim_x, hynet_float_)
                    task.getxxslice(mosek.soltype.itr, 0, dim_x, x)
                    (V, f, s, z) = qcqp.split_vectorization_optimizer(x)
                    v = self.rank1approx(V, qcqp.edges, qcqp.roots)
                    optimizer = QCQPPoint(v, f, s, z)

                    dv_lb = np.ndarray(dim_x, dtype=hynet_float_)
                    task.getslxslice(mosek.soltype.itr, 0, dim_x, dv_lb)
                    dv_lb[np.isnan(x_lb)] = np.nan
                    dv_lb = qcqp.split_vectorization_bound_dual(dv_lb)

                    dv_ub = np.ndarray(dim_x, dtype=hynet_float_)
                    task.getsuxslice(mosek.soltype.itr, 0, dim_x, dv_ub)
                    dv_ub[np.isnan(x_ub)] = np.nan
                    dv_ub = qcqp.split_vectorization_bound_dual(dv_ub)

                    dv_eq_lb = np.ndarray(N, dtype=hynet_float_)
                    task.getslcslice(mosek.soltype.itr, 0, N, dv_eq_lb)
                    dv_eq_ub = np.ndarray(N, dtype=hynet_float_)
                    task.getsucslice(mosek.soltype.itr, 0, N, dv_eq_ub)
                    dv_eq = dv_eq_ub - dv_eq_lb

                    dv_ineq = np.ndarray(M, dtype=hynet_float_)
                    task.getsucslice(mosek.soltype.itr, N, N + M, dv_ineq)

                    optimal_value = task.getprimalobj(mosek.soltype.itr)

                    result = QCQPResult(qcqp, self, status, solver_time,
                                        optimizer=optimizer,
                                        V=V,
                                        optimal_value=optimal_value,
                                        dv_lb=dv_lb,
                                        dv_ub=dv_ub,
                                        dv_eq=dv_eq,
                                        dv_ineq=dv_ineq)
                else:
                    result = QCQPResult(qcqp, self, status, solver_time)

        _log.debug(self.type.name + " ~ Result creation ({:.3f} sec.)"
                   .format(timer.interval()))
        _log.debug(self.type.name + " ~ Total time for solver ({:.3f} sec.)"
                   .format(timer.total()))
        return result


class SOCRSolver(SolverBase):
    """
    MOSEK-based solver for a second-order cone relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_, [2]_.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://docs.mosek.com/9.0/opt-server/param-groups.html
    .. [2] https://docs.mosek.com/9.0/pythonapi/solving-conic.html
    """

    @property
    def name(self):
        return "MOSEK"

    @property
    def type(self):
        return SolverType.SOCR

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its second-order cone relaxation using MOSEK.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the SOCR associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                   ...and SOC constraints on v_tld-part of x
        return super().solve(qcqp)

    def _add_voltage_matrix_constraints(self, task, qcqp, dim_x, ofs,
                                        x_lb, x_ub, x_bnd, coupling_emphasis):
        """Add the SOC constraints on the ``v_tld``-part of ``x``."""
        # Second-order cone constraints on V (cf. QCQP.get_vectorization)
        #
        # PSD constraint on 2x2 principal submatrix =>
        #  (a) diagonal is nonnegative -> ensured by LB on voltage mag.
        #  (b) determinant is nonnegative -> rotated SOC:
        #
        #               V_ij * conj(V_ij) <= V_ii * V_jj
        #                             <=>
        #          real(V_ij)^2 + imag(V_ij)^2 <= V_ii * V_jj
        #
        #      where i is the source bus and j is the destination bus
        #      of the considered edge. Note that MOSEK requires
        #      rotated second-order cones to be specified as
        #
        #              2 * x_0 * x_1 >= x_2^2 + x_3^2
        #
        #      i.e., there is an additional scaling factor of 2.
        #
        # MOSEK limits variables to being a member of only one cone. If
        # multiple edges connect to a bus, the corresponding diagonal
        # element is a member of more than one cone. Due to this, the
        # diagonal elements V_ii and V_jj are duplicated for every
        # second-order cone, i.e., for every edge k with source node i
        # and destination node j an additional variable
        # w_k = [V_ii/2, V_jj]^T is introduced. Thus, the augmented
        # optimization variable x' is
        #
        #            x' = [x^T, w_0^T, ..., w_(K-1)^T]^T
        #
        # where K is the number of edges.

        # Add the variables w_k. Note that the diagonal elements of V
        # are at the "beginning" of x and the bounds can be reused.
        (e_src, e_dst) = qcqp.edges
        K = qcqp.num_edges
        task.appendvars(2*K)
        idx_w_src = range(dim_x, dim_x + 2*K, 2)
        idx_w_dst = range(dim_x + 1, dim_x + 2*K, 2)
        task.putvarboundlist(idx_w_src, x_bnd[e_src],
                             x_lb[e_src]/2, x_ub[e_src]/2)
        task.putvarboundlist(idx_w_dst, x_bnd[e_dst],
                             x_lb[e_dst], x_ub[e_dst])

        task.appendcons(2*K)
        idx_crt_w_src = range(ofs, ofs + 2*K, 2)
        idx_crt_w_dst = range(ofs + 1, ofs + 2*K, 2)
        task.putaijlist(idx_crt_w_src, e_src, 0.5 * np.ones(K) * coupling_emphasis)
        task.putaijlist(idx_crt_w_src, idx_w_src, -np.ones(K) * coupling_emphasis)
        task.putaijlist(idx_crt_w_dst, e_dst, np.ones(K) * coupling_emphasis)
        task.putaijlist(idx_crt_w_dst, idx_w_dst, -np.ones(K) * coupling_emphasis)
        task.putconboundlist(range(ofs, ofs + 2*K),
                             [mosek.boundkey.fx] * 2*K,
                             np.zeros(2*K), np.zeros(2*K))
        ofs += 2*K

        for k in range(K):
            task.appendcone(mosek.conetype.rquad, 0,
                            [idx_w_src[k], idx_w_dst[k],
                             qcqp.dim_v + k, qcqp.dim_v + K + k])


class SDRSolver(SolverBase):
    """
    MOSEK-based solver for a semidefinite relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_.

    Parameters
    ----------
    chordal : bool
        If ``True``, a chordal conversion of the semidefinite program (SDP) is
        solved [2]_, while the original ("full") SDP is solved otherwise. For
        the solution of the SDR for medium- and large-scale systems, the
        chordal conversion is essentially necessary to attain an acceptable
        solution time. The chordal conversion requires CHOMPACK [3]_ and
        CVXOPT [4]_, which can be installed using Python's package management
        system ("pip install chompack cvxopt"). By default, the chordal SDR is
        enabled if these packages are installed and disabled otherwise.
    amalgamation_size : int, optional
    amalgamation_fill : int, optional
        Amalgamation of cliques for the chordal SDR. If ``amalgamation_size``
        (default ``1``) and ``amalgamation_fill`` (default ``0``) is provided,
        the amalgamation heuristic described on page 891 in [5]_ is applied
        with ``t_size`` set to ``amalgamation_size`` and ``t_fill`` set to
        ``amalgamation_fill``. If either or both are ``None``, the clique
        amalgamation is disabled. Please note that, due to the particular
        implementation approach in this solver interface that introduces two
        auxiliary variables for every chord, only amalgamations with a low
        additional fill-in are recommended.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://docs.mosek.com/9.0/opt-server/param-groups.html
    .. [2] M. Fukuda, M. Kojima, K. Murota, and K. Nakata, "Exploiting Sparsity
           in Semidefinite Programming via Matrix Completion I: General
           Framework" SIAM J. Optimization 11(3), pp. 647-674, 2001.
    .. [3] http://chompack.readthedocs.io
    .. [4] http://cvxopt.org
    .. [5] Y. Sun, M. S. Andersen, and L. Vandenberghe, "Decomposition in Conic
           Optimization with Partially Separable Structure," SIAM J.
           Optimization 24(2), pp. 873-897, 2014.
    """
    def __init__(self, chordal=CHORDAL_MODULE, amalgamation_size=1,
                 amalgamation_fill=0, **kwds):
        super().__init__(**kwds)
        self.chordal = chordal
        self.amalgamation_size = amalgamation_size
        self.amalgamation_fill = amalgamation_fill

    @property
    def name(self):
        return "MOSEK"

    @property
    def type(self):
        return SolverType.SDR

    def __str__(self):
        sdr_type = 'chordal' if self.chordal else 'full'
        return self.name + ' (' + sdr_type + ' ' + self.type.value + ')'

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its semidefinite relaxation using MOSEK.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the SDR associated with the QCQP.
        """
        # We solve the following problem:
        #
        #  min   c^T x   s.t.   Ax == b,  Bx <= d,  x_lb <= x <= x_ub
        #   x                   ...and PSD constraint(s) on the v_tld-part of x
        return super().solve(qcqp)

    def _add_voltage_matrix_constraints(self, task, qcqp, dim_x, ofs,
                                        x_lb, x_ub, x_bnd, coupling_emphasis):
        (e_src, e_dst) = qcqp.edges
        assert np.all(e_src > e_dst)  # Sparsity pattern of lower-triangular part

        if self.chordal:
            if not CHORDAL_MODULE:
                raise RuntimeError("Chordal matrix module not loaded. Please "
                                   "install CHOMPACK and CVXOPT "
                                   "(\"pip install chompack cvxopt\").")

            # Get cliques and chords of a chordal extension the sparsity graph
            cliques, chords = get_chordal_extension_cliques(
                qcqp.edges,
                num_nodes=qcqp.dim_v,
                amalgamation_size=self.amalgamation_size,
                amalgamation_fill=self.amalgamation_fill
            )
            assert np.all(chords[0] > chords[1])  # Sparsity of lower-tri. part
            setattr(qcqp, 'chords', chords)  # Dynamically add the chords
            num_chords = len(qcqp.chords[0])

            # Add variables for the off-diagonal elements related to the chords
            #
            # Up to now, the optimization variable x comprises the stacking
            #
            #   x = [v_tld^T, f^T, s^T, z^T]^T
            #
            # Analogous to the edges of the sparsity graph in the v_tld-part,
            # we append the elements for to the chords, i.e.,
            #
            #   x = [v_tld^T, f^T, s^T, z^T, v_crd^T]^T
            #
            # with
            #
            #    v_crd = [real(V_{c_src(1),c_dst(1)}    ^
            #             ...                           | L = Num. of chords
            #             real(V_{c_src(L),c_dst(L)}    v
            #             imag(V_{c_src(1),c_dst(1)}    ^
            #             ...                           | L = Num. of chords
            #             imag(V_{c_src(L),c_dst(L)}]   v
            #
            if num_chords:
                task.appendvars(2 * num_chords)
                task.putvarboundlist(range(dim_x, dim_x + 2 * num_chords),
                                     [mosek.boundkey.fr] * 2 * num_chords,
                                     [np.nan] * 2 * num_chords,
                                     [np.nan] * 2 * num_chords)

            # Add PSD constraints on all principal submatrices associated with
            # maximal cliques of a chordal extension of the sparsity graph
            ofs_crt = ofs
            ofs_psd = 0
            for clique, clique_edges, clique_chords in \
                    get_clique_graphs(cliques, qcqp.edges, qcqp.chords):
                ofs_crt, ofs_psd = \
                    self._add_psd_constraint(task, qcqp, coupling_emphasis,
                                             ofs_crt=ofs_crt,
                                             ofs_psd=ofs_psd,
                                             nodes=clique,
                                             edges=clique_edges,
                                             chords=clique_chords,
                                             ofs_chords=dim_x)
        else:
            # Add a PSD constaint on the entire bus voltage matrix
            self._add_psd_constraint(task, qcqp, coupling_emphasis,
                                     ofs_crt=ofs,
                                     ofs_psd=0,
                                     nodes=np.arange(qcqp.dim_v,
                                                     dtype=hynet_int_),
                                     edges=np.arange(qcqp.num_edges,
                                                     dtype=hynet_int_))

    def _add_psd_constraint(self, task, qcqp, coupling_emphasis, ofs_crt, ofs_psd,
                            nodes, edges, chords=None, ofs_chords=np.nan):
        """
        Add a PSD constraint on the ``v_tld``-part of ``x``.

        This function adds a positive semidefiniteness constraint on the
        principal submatrix related to the rows and columns specified by
        ``nodes``, where ``edges`` defines the sparsity pattern thereof.
        The ``edges`` are a list of **edge numbers** that reference the edges
        in ``qcqp``.

        Parameters
        ----------
        task : mosek.Task
            MOSEK optimization task object.
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.
        coupling_emphasis : float
            Scaling factor for the coupling constraints (see also the remark
            in the code of ``SolverBase.solve``).
        ofs_crt : int
            Offset for the next constraint.
        ofs_psd : int
            Offset for the next PSD variable.
        nodes : numpy.ndarray[.hynet_int_]
            Nodes that specify the principal submatrix.
        edges : numpy.ndarray[.hynet_int_]
            Edges (in terms of indices to the edges in ``qcqp``) that specify
            the sparsity pattern in the principal submatrix.
        chords : numpy.ndarray[.hynet_int_], optional
            Chords (in terms of indices to the chords in ``qcqp``) that specify
            the chordal extension pattern in the principal submatrix.
        ofs_chords : int, optional
            Offset of the variables in the optimization variable ``x`` for the
            off-diagonal elements related to the chords.

        Returns
        -------
        ofs_crt : int
            New offset for the next constraint.
        ofs_psd : int
            New offset for the next PSD variable.
        """
        # Remark to the implementation of the PSD constraint on the complex-
        # valued principal submatrix. Below, we refer to the latter as ``V``.
        #
        # Consider the splitting of the Hermitian matrix V into its
        # real and imaginary part, i.e., V = V_r + j*V_i. Then,
        #
        #       V is PSD    <=>    V_cr = [ V_r  -V_i ] is PSD
        #                                 [ V_i   V_r ]
        #
        # This code implements the real-valued equivalent of V >= 0,
        # i.e., V_cr >= 0. To this end, a semidefinite matrix variable
        # V_cr is added and all relevant elements are equated to v_tld.
        # Note the following particularities:
        #
        #  1) MOSEK considers *symmetric* coefficient matrices and
        #     requires the specification of the *lower* triangular part.
        #  2) When equating the off-diagonal elements of V_cr to v_tld,
        #     the respective element of V_cr is taken twice (due to the
        #     sym. coeff. matrix), which explains the factor of 2 for
        #     the corresponding element in v_tld.
        #  3) As V is Hermitian, V_r is symmetric and V_i is skew-symmetric.
        #     Thus, the diagonal of V_i is zero and the respective elements
        #     in V_cr are fixed at zero.
        #
        num_nodes = len(nodes)
        num_edges = len(edges)
        num_chords = 0 if chords is None else len(chords)
        dim_V_cr = 2*num_nodes

        nodes_mapped = np.arange(num_nodes, dtype=hynet_int_)
        node_map = -np.ones(qcqp.dim_v, dtype=hynet_int_)
        node_map[nodes] = nodes_mapped

        # Add the symmetric matrix V_cr
        task.appendbarvars([dim_V_cr])

        # Add constraints to equate v_tld and v_crd to V_cr
        num_crt_V_cr = 3*num_nodes + 4*(num_edges + num_chords)
        task.appendcons(num_crt_V_cr)
        task.putconboundlist(range(ofs_crt, ofs_crt + num_crt_V_cr),
                             [mosek.boundkey.fx] * num_crt_V_cr,
                             np.zeros(num_crt_V_cr),
                             np.zeros(num_crt_V_cr))

        # Diagonal of V_r in top-left block
        for n, n_mapped in zip(nodes, nodes_mapped):
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [n_mapped],
                                             [n_mapped],
                                             [-1.0 * coupling_emphasis])
            task.putaij(ofs_crt, n, 1.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Diagonal of V_r in bottom-right block
        for n, n_mapped in zip(nodes, nodes_mapped):
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [n_mapped + num_nodes],
                                             [n_mapped + num_nodes],
                                             [-1.0 * coupling_emphasis])
            task.putaij(ofs_crt, n, 1.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Diagonal of V_i in bottom-right block (fixed at zero)
        for n, n_mapped in zip(nodes, nodes_mapped):
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [n_mapped + num_nodes],
                                             [n_mapped],
                                             [1.0 * coupling_emphasis])
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Lower-triangular off-diagonal elements
        if num_edges:
            ofs_crt = self._add_off_diag_equalities(task, ofs_crt, ofs_psd,
                                                    coupling_emphasis,
                                                    ofs_in_x=qcqp.dim_v,
                                                    edges=qcqp.edges,
                                                    edge_indices=edges,
                                                    dim_V_cr=dim_V_cr,
                                                    node_map=node_map)
        if num_chords:
            ofs_crt = self._add_off_diag_equalities(task, ofs_crt, ofs_psd,
                                                    coupling_emphasis,
                                                    ofs_in_x=ofs_chords,
                                                    edges=qcqp.chords,
                                                    edge_indices=chords,
                                                    dim_V_cr=dim_V_cr,
                                                    node_map=node_map)
        return ofs_crt, ofs_psd + 1

    def _add_off_diag_equalities(self, task, ofs_crt, ofs_psd, coupling_emphasis,
                                 ofs_in_x, edges, edge_indices, dim_V_cr, node_map):

        (e_src, e_dst) = edges
        num_edges = len(e_src)
        ofs_block = int(dim_V_cr/2)

        assert np.all(node_map[e_src[edge_indices]] > node_map[e_dst[edge_indices]])

        # Lower-triangular off-diagonal elements of V_r in top-left block
        for k in edge_indices:
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [node_map[e_src[k]]],
                                             [node_map[e_dst[k]]],
                                             [-1.0 * coupling_emphasis])
            task.putaij(ofs_crt, k + ofs_in_x, 2.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Lower-triangular off-diagonal elements of V_r in bottom-right block
        for k in edge_indices:
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [node_map[e_src[k]] + ofs_block],
                                             [node_map[e_dst[k]] + ofs_block],
                                             [-1.0 * coupling_emphasis])
            task.putaij(ofs_crt, k + ofs_in_x, 2.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Lower-triangular part of V_i in bottom-left block
        for k in edge_indices:
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [node_map[e_src[k]] + ofs_block],
                                             [node_map[e_dst[k]]],
                                             [-1.0 * coupling_emphasis])
            task.putaij(ofs_crt, k + ofs_in_x + num_edges, 2.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        # Upper-triangular part of V_i in bottom-left block (skew-symmetry!)
        for k in edge_indices:
            mtx_id = task.appendsparsesymmat(dim_V_cr,
                                             [node_map[e_dst[k]] + ofs_block],
                                             [node_map[e_src[k]]],
                                             [1.0 * coupling_emphasis])
            task.putaij(ofs_crt, k + ofs_in_x + num_edges, 2.0 * coupling_emphasis)
            task.putbaraij(ofs_crt, ofs_psd, [mtx_id], [1.0])
            ofs_crt += 1

        return ofs_crt
