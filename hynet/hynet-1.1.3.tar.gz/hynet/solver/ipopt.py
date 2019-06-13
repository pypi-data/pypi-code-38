#pylint: disable=unused-argument,anomalous-backslash-in-string
"""
IPOPT-based solver for the *hynet*-specific QCQP problem.
"""

import logging

import numpy as np
import scipy.sparse
import ipopt

from hynet.types_ import (hynet_int_,
                          hynet_float_,
                          hynet_complex_,
                          SolverType,
                          SolverStatus)
from hynet.utilities.worker import workers
from hynet.utilities.base import partition_iterable, Timer
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

_log = logging.getLogger(__name__)


def parse_status(status):
    """
    Parse the IPOPT status into a ``SolverStatus``.

    *Remark:* The interpretation of the status values can be deduced from
    the CyIPOPT code in [1]_.

    References
    ----------
    .. [1] https://github.com/matthias-k/cyipopt/blob/master/src/cyipopt.pyx
    """
    if status == 0:
        return SolverStatus.SOLVED
    if status == 1:
        return SolverStatus.INACCURATE
    if status == 2:
        return SolverStatus.INFEASIBLE
    return SolverStatus.FAILED


class QCQPSolver(SolverInterface):
    """
    IPOPT-based solver for the QCQP.

    This interface is based on CyIPOPT [1]_, a Python wrapper for IPOPT [2]_.

    For information on solver-specific parameters, see e.g. [3]_.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://github.com/matthias-k/cyipopt
    .. [2] https://projects.coin-or.org/Ipopt
    .. [3] https://www.coin-or.org/Ipopt/documentation/node40.html
    """

    def __init__(self, **kwds):
        super().__init__(**kwds)
        # REMARK: Experimentally, we found that this default setting provides a
        # good compromise between accuracy and performance.
        if 'tol' not in self.param:
            self.param['tol'] = 1e-6

    @property
    def name(self):
        return "IPOPT"

    @property
    def type(self):
        return SolverType.QCQP

    def solve(self, qcqp):
        """
        Solve the given QCQP using IPOPT.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the QCQP (in general only a *locally* optimal solution).
        """
        timer = Timer()

        problem = IPOPTProblem(qcqp, options=self)
        _log.debug("QCQP ~ Modeling ({:.3f} sec.)".format(timer.interval()))

        status, optimizer, dv_lb, dv_ub, dv_eq, dv_ineq, optimal_value = problem.solve()
        solver_time = timer.interval()
        _log.debug("QCQP ~ Solver ({:.3f} sec.)".format(solver_time))

        if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
            optimizer.v[:] = self.adjust_absolute_phase(qcqp, optimizer.v)
            result = QCQPResult(qcqp, self, status, solver_time,
                                optimizer=optimizer,
                                V=None,
                                optimal_value=optimal_value,
                                dv_lb=dv_lb,
                                dv_ub=dv_ub,
                                dv_eq=dv_eq,
                                dv_ineq=dv_ineq)
        else:
            result = QCQPResult(qcqp, self, status, solver_time)

        _log.debug("QCQP ~ Total time for solver ({:.3f} sec.)"
                   .format(timer.total()))
        return result


class IPOPTProblem(ipopt.problem):
    """
    Specification and solution of the QCQP via IPOPT.
    """
    # The following documents were helpful to understand the interface of (Cy)IPOPT:
    #   https://www.coin-or.org/Ipopt/documentation/node22.html
    #   https://github.com/matthias-k/cyipopt/blob/master/test/examplehs071.py
    #   https://github.com/matthias-k/cyipopt/blob/master/test/lasso.py
    #   https://pythonhosted.org/ipopt/tutorial.html
    #   https://pythonhosted.org/ipopt/reference.html

    def __init__(self, qcqp, options):
        """
        Initialize the problem formulation and prepare for the solution process.
        """
        (e_src, e_dst) = qcqp.edges
        assert np.all(e_src > e_dst)  # Sparsity pattern of lower-triangular part

        self.qcqp = qcqp
        UNBOUNDED = 2.0e19  # Bounds are ignored if larger/smaller than +/- 10^19

        # Partitioning: x = [Re(v)^T, Im(v)^T, f^T, s^T, z^T]^T
        self._ofs_v_i = qcqp.dim_v
        self._ofs_f = self._ofs_v_i + qcqp.dim_v
        self._ofs_s = self._ofs_f + qcqp.dim_f
        self._ofs_z = self._ofs_s + qcqp.dim_s
        self._dim_x = self._ofs_z + qcqp.dim_z

        # Variable bounds
        x_lb = np.concatenate((-qcqp.ub.v,
                               -qcqp.ub.v,
                               qcqp.lb.f,
                               qcqp.lb.s,
                               qcqp.lb.z))
        x_ub = np.concatenate((qcqp.ub.v,
                               qcqp.ub.v,
                               qcqp.ub.f,
                               qcqp.ub.s,
                               qcqp.ub.z))
        self._idx_lb_nan = np.isnan(x_lb)
        self._idx_ub_nan = np.isnan(x_ub)
        x_lb[self._idx_lb_nan] = -UNBOUNDED
        x_ub[self._idx_ub_nan] = UNBOUNDED

        # Set phase to zero at root nodes by fixing the imaginary part at zero
        # (This avoids solution ambiguity w.r.t. an absolute phase shift in
        #  ``v`` for those components with a given root node and, therewith,
        #  can improve the solver convergence.)
        if qcqp.roots.size:
            idx_v_i_root = qcqp.roots + qcqp.dim_v
            x_lb[idx_v_i_root] = 0
            x_ub[idx_v_i_root] = 0

        # Initial point
        if qcqp.initial_point is not None:
            self._x0 = np.concatenate((qcqp.initial_point.v.real,
                                       qcqp.initial_point.v.imag,
                                       qcqp.initial_point.f,
                                       qcqp.initial_point.s,
                                       qcqp.initial_point.z))
        else:
            self._x0 = np.zeros(self._dim_x, dtype=hynet_float_)
            self._x0[:self._ofs_v_i] = (qcqp.lb.v + qcqp.ub.v) / 2

        # Objective: Part of gradient related to f, s, and z
        self._grad_f_fsz = scipy.sparse.vstack((qcqp.obj_func.c,
                                                qcqp.obj_func.a,
                                                qcqp.obj_func.r)
                                               ).toarray().reshape(1, -1)[0]

        # Objective: Hessian
        self._hessian_idx = self._get_hessian_index(qcqp)
        self._hessian_obj = self._get_hessian_data(qcqp, qcqp.obj_func)

        # Constraints and their upper and lower bounds:
        #  (1) Vectorize the constraints for efficient evaluation in the callback
        #  (2) Stack the equality and inequality constraints
        A, b, B, d = qcqp.get_constraint_vectorization()
        self._A = scipy.sparse.vstack((A, B)).tocsr()  # CSR for slicing & mat. prod.
        crt_b = np.concatenate((b, d))
        constraints = np.concatenate((qcqp.eq_crt, qcqp.ineq_crt))
        crt_ub = crt_b
        crt_lb = np.array(crt_b)
        crt_lb[len(qcqp.eq_crt):] = -UNBOUNDED

        # Column offsets in A with respect to the variables (vectorization!)
        ofs_A_v_real = qcqp.dim_v
        ofs_A_v_imag = ofs_A_v_real + qcqp.num_edges
        ofs_A_f = ofs_A_v_imag + qcqp.num_edges

        # Constraints: Jacobian
        #  (1) Create the stacking of c, a, and r for all constraints
        #  (2) Prepare the computation of the part of the gradient related to v
        #  (3) Stack the index data from (1) and (2) to defined the sparsity
        #      pattern of the Jacobian
        jac_fsz_mtx = self._A[:, ofs_A_f:].tocoo()
        jac_fsz_idx = (jac_fsz_mtx.row, jac_fsz_mtx.col + self._ofs_f)
        self._jacobian_fsz = jac_fsz_mtx.data
        jac_v_idx, self._jacobian_C = \
            self._get_jacobian_v(constraints, qcqp.dim_v)
        self._jacobian_idx = (np.concatenate((jac_v_idx[0], jac_fsz_idx[0])),
                              np.concatenate((jac_v_idx[1], jac_fsz_idx[1])))

        # Constraints: Hessian
        #   The following code performs the same as _get_hessian_data (cf.
        #   its application to the objective function above), as if it were
        #   applied to all constraints and the resulting Hessian data vectors
        #   were stacked horizontally. However, for performance reasons this
        #   implementation utilizes the precomputed stacking of the constraint
        #   vectorization above. Note that during the vectorization the
        #   off-diagonal elements are already multiplied by 2, thus only the
        #   diagonal elements need to be scaled.
        C_diag = 2*self._A[:, :ofs_A_v_real]
        C_offd_real = self._A[:, ofs_A_v_real:ofs_A_v_imag]
        C_offd_imag = self._A[:, ofs_A_v_imag:ofs_A_f]
        self._hessian_crt = scipy.sparse.hstack((C_diag,
                                                 C_diag,
                                                 C_offd_real,
                                                 C_offd_real,
                                                 C_offd_imag,
                                                 -C_offd_imag)).transpose().tocsr()

        # Initialize base class
        # (REMARK: This calls ``jacobianstructure`` and ``hessianstructure``)
        super().__init__(n=self._dim_x,
                         m=len(constraints),
                         problem_obj=self,
                         lb=x_lb,
                         ub=x_ub,
                         cl=crt_lb,
                         cu=crt_ub)

        # Set options
        self.addOption(b'sb', b'yes')  # Suppress the IPOPT banner
        self.addOption(b'print_level', 5 if options.verbose else 0)
        # self.addOption(b'print_options_documentation', b'yes')
        for key, value in options.param.items():
            self.addOption(key.encode(encoding='utf-8'),
                           value.encode(encoding='utf-8')
                           if isinstance(value, str) else value)

    def _split(self, x):
        """
        Split ``x = [Re(v)^T, Im(v)^T, f^T, s^T, z^T]^T`` into ``p = (v, f, s, z)``.

        Parameters
        ----------
        x : numpy.ndarray
            Optimization variable.

        Returns
        -------
        p : QCQPPoint
            Corresponding QCQP point ``p = (v, f, s, z)``.
        """
        return QCQPPoint(v=x[:self._ofs_v_i] + 1j*x[self._ofs_v_i:self._ofs_f],
                         f=x[self._ofs_f:self._ofs_s],
                         s=x[self._ofs_s:self._ofs_z],
                         z=x[self._ofs_z:])

    @staticmethod
    def _get_jacobian_v(constraints, dim_v):
        """
        Return the Jacobian sparsity pattern and evaluation support w.r.t. v.

        The gradient of the function
        ::
            v_cr^T C_cr v_cr + c^T f + a^T s + r^T z

        reads
        ::
            [ (2*C_cr v_cr)^T, c^T, a^T, r^T ]^T

        which considers the vectorization ``x = [v_cr^T, f^T, s^T, z^T]^T``
        and the composite real representation
        ::
            v_cr = [ Re(v)^T  Im(v)^T ]^T

        and
        ::
            C_cr = [ Re(C)  -Im(C) ]
                   [ Im(C)   Re(C) ]

        For the following discussion, it shall also be noted that
        ::
            (2*C_cr v_cr)^T = [ 2*Re(Cv)^T, 2*Im(Cv)^T ]

        The Jacobian of the vector-valued constraint function as queried by
        IPOPT is the vertical stacking of the transpose of the individual
        constraint function gradients. Let the constraint ``i`` have the
        parameters ``C_i``, ``c_i``, ``a_i``, and ``r_i``. Then, the Jacobian
        comprises the following blocks::

            [ 2*Re(C_1 v)^T  |  2*Im(C_1 v)^T  |  c_1^T  a_1^T  r_1^T ]
            [      ...       |       ...       |         ...          ]
            [ 2*Re(C_N v)^T  |  2*Im(C_N v)^T  |  c_N^T  a_N^T  r_N^T ]

            \_______________/ \_______________/ \____________________/
                   (1)               (2)                 (3)

        Block (3) remains constant for all iterations and is precomputed during
        initialization, while this method considers block (1) and (2). In row
        ``i``, the sparsity pattern in (1) and (2) is defined by the *nonzero
        rows* of ``C_i``. This method determines this sparsity pattern for all
        constraints and, alongside, returns a stacking of the row-reduced
        (i.e., only nonzero rows) constraint matrices ``C_i`` for an efficient
        evaluation of the nonzero elements in (1) and (2) during the callback.
        """
        timer = Timer()

        result_list = workers.map(_get_sparsity_and_row_reduction, constraints)

        list_row = []
        list_col = []
        list_jacobian_C = []
        for n, result in enumerate(result_list):
            if result is None:
                continue
            col, jacobian_C = result
            list_row.append(n + np.zeros(len(col), dtype=hynet_int_))
            list_col.append(col)
            list_jacobian_C.append(jacobian_C)

        row = np.concatenate(list_row)
        row = np.concatenate((row, row))          # For grad. w.r.t. v_r and v_i

        col = np.concatenate(list_col)
        col = np.concatenate((col, col + dim_v))  # For grad. w.r.t. v_r and v_i

        # Stacking is slow: Use multiprocessing to prestack, if available...
        if workers.is_multiprocessing and \
                len(list_jacobian_C) >= workers.num_workers:
            list_jacobian_C = workers.map(scipy.sparse.vstack,
                                          partition_iterable(list_jacobian_C,
                                                             workers.num_workers)
                                          )
        jacobian_C = scipy.sparse.vstack(list_jacobian_C).tocsr()

        _log.debug("QCQP ~ Preparation of v-part in Jacobian ({:.3f} sec.)"
                   .format(timer.total()))
        return (row, col), jacobian_C

    @staticmethod
    def _get_hessian_index(qcqp):
        """
        Returns the row and column index tuple for the Hessian sparsity pattern.

        This method defines the sparsity pattern for ``_get_hessian_data``.

        **Remark:** IPOPT requires that *only the lower left triangular part*
        (or, alternatively, the upper triangular part) is specified.

        **Remark:** This method as well as ``_get_hessian_data`` assumes that
        ``e_src > e_dst``, where ``(e_src, e_dst) = qcqp.edges``. This is
        asserted during initialization.
        """
        (e_src, e_dst) = qcqp.edges
        range_v = np.arange(qcqp.dim_v)

        row = np.concatenate((range_v,               # Diag. top-left
                              range_v + qcqp.dim_v,  # Diag. bottom-right
                              e_src,                 # Off-diag. top-left LT
                              e_src + qcqp.dim_v,    # Off-diag. bottom-right LT
                              e_src + qcqp.dim_v,    # Off-diag. bottom-left LT
                              e_dst + qcqp.dim_v))   # Off-diag. bottom-left UT

        col = np.concatenate((range_v,               # Diag. top-left
                              range_v + qcqp.dim_v,  # Diag. bottom-right
                              e_dst,                 # Off-diag. top-left LT
                              e_dst + qcqp.dim_v,    # Off-diag. bottom-right LT
                              e_dst,                 # Off-diag. bottom-left LT
                              e_src))                # Off-diag. bottom-left UT
        return row, col

    @staticmethod
    def _get_hessian_data(qcqp, func):
        """
        Returns the Hessian as a data vector for the given function.

        The Hessian of the function
        ::
            v_cr^T C_cr v_cr + c^T f + a^T s + r^T z

        comprises ``2*C_cr`` in the top-left block considering the vectorization
        ``x = [v_cr^T, f^T, s^T, z^T]^T`` and the composite real representation
        ::
            v_cr = [ Re(v)^T  Im(v)^T ]^T

        and
        ::
            C_cr = [ Re(C)  -Im(C) ]
                   [ Im(C)   Re(C) ]

        The data is returned w.r.t. the sparsity pattern for the Hessian matrix
        as defined by ``_get_hessian_index``, i.e., the diagonal followed by
        the elements of the top-left, bottom-right, and bottom-left block of
        ``C_cr``. The block off-diagonal elements consider the sparsity pattern
        of the constraint matrix.
        """
        list_data = []
        (e_src, e_dst) = qcqp.edges

        C_diag = func.C.diagonal().real
        if e_src.size:
            C_offd = np.asarray(func.C.tocsr()[e_src, e_dst])[0]
        else:
            C_offd = np.ndarray(0, dtype=hynet_complex_)
        C_offd_real = C_offd.real
        C_offd_imag = C_offd.imag

        # REMARK: The real part of C is symmetric, while the imaginary part
        # of C is skew-symmetric.

        # Diagonal of top-left and bottom-right block
        list_data.append(C_diag)
        list_data.append(C_diag)

        # Off-diagonal elements (lower triangular part) of top-left block
        list_data.append(C_offd_real)

        # Off-diagonal elements (lower triangular part) of bottom-right block
        list_data.append(C_offd_real)

        # Off-diagonal elements of bottom-left block
        # (REMARK: The diagonal of the bottom-left block is zero)
        list_data.append(C_offd_imag)
        list_data.append(-C_offd_imag)

        return 2*np.concatenate(list_data)

    def solve(self):
        """Execute the interior-point solver."""
        logger = logging.getLogger()  # Root logger
        logger_disabled = logger.disabled
        logger.disabled = True  # CyIPOPT spams the log, so disable temporarily
        x, info = super().solve(self._x0)
        logger.disabled = logger_disabled
        status = parse_status(info['status'])

        if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
            optimizer = self._split(x)

            dv_lb = info['mult_x_L']
            dv_lb[self._idx_lb_nan] = np.nan
            dv_lb = self._split(dv_lb)
            dv_lb.v = None

            dv_ub = info['mult_x_U']
            dv_ub[self._idx_ub_nan] = np.nan
            dv_ub = self._split(dv_ub)
            dv_ub.v = None

            dv = info['mult_g']
            dv_eq = dv[:len(self.qcqp.eq_crt)]
            dv_ineq = dv[len(self.qcqp.eq_crt):]
            optimal_value = info['obj_val']
        else:
            optimizer = dv_lb = dv_ub = dv_eq = dv_ineq = optimal_value = None

        return status, optimizer, dv_lb, dv_ub, dv_eq, dv_ineq, optimal_value

    def objective(self, x):
        """
        Callback for the calculation of the objective function.
        """
        return self.qcqp.obj_func.evaluate(self._split(x))

    def gradient(self, x):
        """
        Callback for the calculation of the gradient of the objective function.
        """
        p = self._split(x)
        grad_f_v = 2*self.qcqp.obj_func.C.dot(p.v)
        return np.concatenate((grad_f_v.real, grad_f_v.imag, self._grad_f_fsz))

    def constraints(self, x):
        """Callback for the calculation of the constraints."""
        (e_src, e_dst) = self.qcqp.edges
        p = self._split(x)
        V_diag = np.square(np.abs(p.v))
        V_offd = np.multiply(p.v[e_src], p.v[e_dst].conj())
        x_tld = np.concatenate((V_diag, V_offd.real, V_offd.imag, p.f, p.s, p.z))
        return self._A.dot(x_tld)

    def jacobianstructure(self):
        """Definition of the sparsity structure of the Jacobian."""
        return self._jacobian_idx

    def jacobian(self, x):
        """Callback for the calculation of the Jacobian."""
        p = self._split(x)
        sparse_grad_g_v = 2*self._jacobian_C.dot(p.v)
        return np.concatenate([sparse_grad_g_v.real,
                               sparse_grad_g_v.imag,
                               self._jacobian_fsz])

    def hessianstructure(self):
        """
        Definition of the sparsity structure of the Hessian.

        *Remark:* If ``hessianstructure`` and ``hessian`` is *not* overridden,
        the Hessian is approximated.
        """
        return self._hessian_idx

    def hessian(self, x, lagrange, obj_factor):
        """Callback for the calculation of the Hessian."""
        return obj_factor * self._hessian_obj + self._hessian_crt.dot(lagrange)

    def intermediate(self, alg_mod, iter_count, obj_value, inf_pr, inf_du, mu,
                     d_norm, regularization_size, alpha_du, alpha_pr, ls_trials):
        """Intermediate callback."""
        return True  # Keep iterating...


def _get_sparsity_and_row_reduction(crt):
    """
    Return the index of nonzero rows and the row reduction of ``crt.C``.

    See Also
    --------
    hynet.solver.ipopt.IPOPTProblem._get_jacobian_v
    """
    if crt.C is not None:
        nonzero_rows = np.unique(crt.C.row)
        return nonzero_rows, crt.C.tocsr()[nonzero_rows, :]
    else:
        return None
