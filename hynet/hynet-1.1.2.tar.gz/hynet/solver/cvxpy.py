"""
CVXPY-based solver for the *hynet*-specific QCQP problem (SD and SOC relaxation).

**Caution:** In our experiments, we observed bad performance and, especially
in case of the SDR, convergence issues. Furthermore, we encountered issues
with CVXPY on Windows machines. Due to this, this solver interface is not
supported officially.
"""

import logging
import abc

import cvxpy as cvx
import numpy as np

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.utilities.base import Timer
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

_log = logging.getLogger(__name__)


def parse_status(status):
    """Parse the CVXPY status into a ``SolverStatus``."""
    if status.upper() == 'OPTIMAL':
        return SolverStatus.SOLVED
    if status.upper() in ['OPTIMAL_INACCURATE',
                          'UNBOUNDED_INACCURATE',
                          'INFEASIBLE_INACCURATE']:
        return SolverStatus.INACCURATE
    if status.upper() == 'INFEASIBLE':
        return SolverStatus.INFEASIBLE
    if status.upper() == 'UNBOUNDED':
        return SolverStatus.UNBOUNDED
    return SolverStatus.FAILED


class SolverBase(SolverInterface):
    """Base class for CVXPY-based solvers for a relaxation of the QCQP."""

    def __init__(self, solver_name='CVXOPT', **kwds):
        super().__init__(**kwds)
        self.solver_name = solver_name

        if self.solver_name.upper() == 'CVXOPT':
            if not 'abstol' in self.param:
                self.param['abstol'] = 1e-6
            if not 'reltol' in self.param:
                self.param['reltol'] = 1e-5
            if not 'feastol' in self.param:
                self.param['feastol'] = 1e-6
            if not 'max_iters' in self.param:
                self.param['max_iters'] = 500
            if not 'kktsolver' in self.param:
                # With the default ('chol', i.e., a Cholesky factorization for
                # preprocessing), CVXPY frequently fails with an exception,
                # where the log states "Terminated (singular KKT matrix)."
                self.param['kktsolver'] = 'robust'

    @staticmethod
    @abc.abstractmethod
    def _add_voltage_matrix_constraints(constraint_list, qcqp, x):
        """Add the SOC or PSD constraint(s) on the ``v_tld``-part of ``x``."""

    def solve(self, qcqp):
        """
        Solve the given QCQP via a relaxation using CVXPY.

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
        #
        # For the following code, I used the CVXPY documentation provided at
        # http://www.cvxpy.org/tutorial/index.html

        timer = Timer()
        # ------------------ generate data --------------------------
        (c, A, b, B, d, x_lb, x_ub) = qcqp.get_vectorization()

        # -------------------- size of the data ---------------------
        dim_x = c.shape[0]

        # -------------- create optimization variable ---------------
        x = cvx.Variable(dim_x)

        # ---- convert SciPy sparse matrices to CVXPY constants -----
        # (See the caveat under "Can I use SciPy sparse matrices with CVXPY?"
        #  in the CVXPY FAQ at https://www.cvxpy.org/faq/index.html)
        c = cvx.Constant(c)
        A = cvx.Constant(A)
        B = cvx.Constant(B)

        # ------------------- add the constraints -------------------
        constraint_list = [A * x == b,
                           B * x <= d]

        # Add the specified lower and upper bounds
        idx_lb = ~np.isnan(x_lb)
        constraint_list.append(x[idx_lb] >= x_lb[idx_lb])

        idx_ub = ~np.isnan(x_ub)
        constraint_list.append(x[idx_ub] <= x_ub[idx_ub])

        # Add relaxation-specific constraints on the voltage matrix
        # (This method is overridden appropriately in derived classes)
        self._add_voltage_matrix_constraints(constraint_list, qcqp, x)

        # -------------------- set the objective --------------------
        obj = cvx.Minimize(c.T*x)

        # -------------------- create a problem ---------------------
        prob = cvx.Problem(obj, constraint_list)

        _log.debug(self.type.name + " ~ Modeling ({:.3f} sec.)"
                   .format(timer.interval()))

        # ----------- optimization and solution recovery ------------
        prob.solve(solver=self.solver_name.upper(),
                   verbose=self.verbose,
                   **self.param)
        solver_time = timer.interval()
        _log.debug(self.type.name + " ~ Solver ({:.3f} sec.)"
                   .format(solver_time))

        status = parse_status(prob.status)

        if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
            x = np.asarray(x.value).reshape(dim_x)

            (V, f, s, z) = qcqp.split_vectorization_optimizer(x)
            v = self.rank1approx(V, qcqp.edges, qcqp.roots)
            optimizer = QCQPPoint(v, f, s, z)

            dv_eq = np.asarray(constraint_list[0].dual_value).reshape(-1)
            dv_ineq = np.asarray(constraint_list[1].dual_value).reshape(-1)

            dv_lb = np.nan * np.ones(dim_x, dtype=hynet_float_)
            dv_lb[idx_lb] = constraint_list[2].dual_value
            dv_lb = qcqp.split_vectorization_bound_dual(dv_lb)

            dv_ub = np.nan * np.ones(dim_x, dtype=hynet_float_)
            dv_ub[idx_ub] = constraint_list[3].dual_value
            dv_ub = qcqp.split_vectorization_bound_dual(dv_ub)

            optimal_value = prob.value

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
    CVXPY-based solver for a second-order cone relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_. To retrieve a
    list of available solvers, use

    >>> import cvxpy
    >>> cvxpy.installed_solvers()

    By default, CVXOPT is selected. For appropriate performance in OPF
    calculations, its default parameters are adapted. Access the ``param``
    attribute of an object for their inspection.

    **Caution:** We observed that ECOS sometimes yields inaccurate dual variables.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] http://www.cvxpy.org/tutorial/advanced/index.html#setting-solver-options
    """

    @property
    def name(self):
        return "CVXPY + " + self.solver_name.upper()

    @property
    def type(self):
        return SolverType.SOCR

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its second-order cone relaxation using CVXPY.

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

    @staticmethod
    def _add_voltage_matrix_constraints(constraint_list, qcqp, x):
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
        #      of the considered edge. The latter is implemented below.
        #
        # The rotated SOC specification is not supported by CVXPY. Due to
        # this, we reformulate it as a standard SOC constraint:
        #
        #               V_ij * conj(V_ij) <= V_ii * V_jj
        #
        #                             <=>
        #
        #           || 2 * Re(V_ij) ||^2
        #           || 2 * Im(V_ij) ||   <= (V_ii + V_jj)^2
        #           || V_ii - V_jj  ||_2
        #
        #                             <=> (with (a) satisfied)
        #
        #               [ 2 * Re(V_ij) ]
        #               [ 2 * Im(V_ij) ] <= V_ii + V_jj
        #               [ V_ii - V_jj  ]
        dim_v = qcqp.dim_v
        K = qcqp.num_edges
        (e_src, e_dst) = qcqp.edges

        for k in range(K):
            constraint_list.append(
                cvx.norm(cvx.vstack([2*x[dim_v + k],
                                     2*x[dim_v + k + K],
                                     x[e_src[k]] - x[e_dst[k]]
                                     ]), 2) <= x[e_src[k]] + x[e_dst[k]])


class SDRSolver(SolverBase):
    """
    CVXPY-based solver for a semidefinite relaxation of the QCQP.

    **Caution:** As we experienced convergence and accuracy issues with the
    default solver CVXOPT, we do not include this solver interface officially.

    For information on solver-specific parameters, see e.g. [1]_. To retrieve a
    list of available solvers, use

    >>> import cvxpy
    >>> cvxpy.installed_solvers()

    By default, CVXOPT is selected. For appropriate performance in OPF
    calculations, its default parameters are adapted. Access the ``param``
    attribute of an object for their inspection.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] http://www.cvxpy.org/tutorial/advanced/index.html#setting-solver-options
    """

    @property
    def name(self):
        return "CVXPY + " + self.solver_name.upper()

    @property
    def type(self):
        return SolverType.SDR

    def solve(self, qcqp):  # pylint: disable=useless-super-delegation
        """
        Solve the given QCQP via its semidefinite relaxation using CVXPY.

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
        #   x                   ...and a PSD constraint on the v_tld-part of x
        return super().solve(qcqp)

    @staticmethod
    def _add_voltage_matrix_constraints(constraint_list, qcqp, x):
        """Add the PSD constraint on the ``v_tld``-part of ``x``."""
        # PSD constraint on V
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
        dim_v = qcqp.dim_v
        K = qcqp.num_edges
        (e_src, e_dst) = qcqp.edges

        assert np.all(e_src > e_dst)  # Sparsity pattern of lower-triangular part

        # Note that previous to CVXPY v1.0, the syntax to define a symmetric
        # and positive semidefinite matrix was
        #   V_cr = cvx.Semidef(2 * dim_v)
        # Starting with CVXPY v1.0, it is defined as:
        V_cr = cvx.Variable((2 * dim_v, 2 * dim_v), PSD=True)

        for k in range(K):     # Equating of off-diagonal elements
            i = e_src[k]
            j = e_dst[k]
            constraint_list.append(V_cr[i, j] == x[dim_v + k])
            constraint_list.append(V_cr[i + dim_v, j + dim_v] == x[dim_v + k])
            constraint_list.append(V_cr[i + dim_v, j] == x[dim_v + k + K])
            constraint_list.append(V_cr[j + dim_v, i] == -x[dim_v + k + K])

        for i in range(dim_v):  # Equating of diagonal elements
            constraint_list.append(V_cr[i, i] == x[i])
            constraint_list.append(V_cr[i + dim_v, i + dim_v] == x[i])
            constraint_list.append(V_cr[i + dim_v, i] == 0)
