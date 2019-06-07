"""
IBM-CPLEX-based solver for the *hynet*-specific QCQP problem (SOC relaxation).
"""

import logging
import sys
import re

import numpy as np
import cplex

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.utilities.base import Timer
from hynet.utilities.worker import workers
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

_log = logging.getLogger(__name__)


def parse_status(status):
    """Parse the CPLEX status into a ``SolverStatus``."""
    # The information on the status codes was extracted from:
    # - http://www.ibm.com/support/knowledgecenter/SSSA5P_12.6.3/ilog.odms.cplex.help/refpythoncplex/html/cplex._internal._subinterfaces.SolutionStatus-class.html
    # - http://www.ibm.com/support/knowledgecenter/SSSA5P_12.6.3/ilog.odms.cplex.help/refcallablelibrary/macros/Solution_status_codes.html
    # - http://www-eio.upc.edu/lceio/manuals/cplex-11/html/overviewcplex/statuscodes.html
    cplex_status = cplex.Cplex().solution.status
    if status == cplex_status.optimal:
        return SolverStatus.SOLVED
    if status == cplex_status.unbounded:
        return SolverStatus.UNBOUNDED
    if status == cplex_status.infeasible:
        return SolverStatus.INFEASIBLE
    if status == cplex_status.num_best:
        return SolverStatus.INACCURATE
    return SolverStatus.FAILED


def _set_cplex_parameters(prob, param):
    """
    Set the parameters of the CPLEX problem.

    *Remark:* This is a workaround to support the key-value parameter
    interface as generally used in *hynet*, cf. ``SolverInterface``.

    Parameters
    ----------
    prob : cplex.Cplex
        CPLEX problem object.
    param : dict[str, object]
        Dictionary of numeric parameters (``{'parameter_name': value}``).
    """
    pattern_param = re.compile(r"([a-z]+[.]?)+")
    for key, value in param.items():
        pattern_match = pattern_param.match(key)
        if pattern_match is None or pattern_match.group() != key:
            _log.warning("Ignoring invalid parameter '{:s}'.".format(key))
            continue
        try:
            if isinstance(value, str):  # For a string, check if it's a number
                value = float(value)
            value = "{:g}".format(value)  # Convert the number to a string
        except ValueError:
            _log.warning("Ignoring non-numeric parameter '{:s}' = {:s}"
                         .format(key, str(value)) + " (not supported).")
            continue
        try:
            # Yes, I totally agree, that's a cheesy solution... ;D
            eval("prob.parameters." + key + ".set(" + value + ")")
        except Exception as exception:
            _log.warning("Failed to set parameter '{:s}': {:s}"
                         .format(key, str(exception)))


def _get_cplex_crt_row(row, mtx):
    row = mtx[row, :]
    return [list(map(int, row.indices)), row.data]


class SOCRSolver(SolverInterface):
    """
    CPLEX-based solver for a second-order cone relaxation of the QCQP.

    For information on solver-specific parameters, see e.g. [1]_. The
    parameters of the CPLEX problem object in its attribute ``parameters`` can
    be set by specifying the respective sub-attributes and parameter values in
    the solver parameter dictionary. For example, to set the convergence
    tolerance to ``1e-9`` for the *hynet* CPLEX SOCR solver object ``solver``,
    call

    >>> solver.param['barrier.qcpconvergetol'] = 1e-9

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.

    References
    ----------
    .. [1] https://www.ibm.com/support/knowledgecenter/SSSA5P_12.6.3/ilog.odms.cplex.help/CPLEX/Parameters/topics/introListAlpha.html
    """

    @property
    def name(self):
        return "CPLEX"

    @property
    def type(self):
        return SolverType.SOCR

    @staticmethod
    def _add_voltage_matrix_constraints(prob, qcqp):
        """Add the SOC constraints on the ``v_tld``-part of ``x``."""
        # PSD constraint on 2x2 principal submatrix =>
        #  (a) diagonal is nonnegative -> ensured by LB on voltage mag.
        #  (b) determinant is nonnegative -> rotated SOC:
        #
        #               V_ij * conj(V_ij) <= V_ii * V_jj
        #                             <=>
        #          real(V_ij)^2 + imag(V_ij)^2 <= V_ii * V_jj
        #
        if not qcqp.num_edges:
            return
        (e_src, e_dst) = qcqp.edges
        e_src = list(map(int, e_src))
        e_dst = list(map(int, e_dst))
        ofs_v_real = int(qcqp.dim_v)
        ofs_v_imag = int(qcqp.dim_v + qcqp.num_edges)
        for k in range(qcqp.num_edges):
            prob.quadratic_constraints.add(
                quad_expr=[[e_src[k], ofs_v_real + k, ofs_v_imag + k],
                           [e_dst[k], ofs_v_real + k, ofs_v_imag + k],
                           [-1.0, 1.0, 1.0]],
                sense='L',
                rhs=0.0)

    def solve(self, qcqp):
        """
        Solve the given QCQP via its second-order cone relaxation using CPLEX.

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
        timer = Timer()
        (c, A, b, B, d, x_lb, x_ub) = qcqp.get_vectorization()
        dim_x = c.shape[0]

        # Convert from the COO to the CSR sparse matrix format: Sum up
        # duplicate entries (i.e., if there are more than one value for the
        # same element in the COO matrix) and convert to the compressed sparse
        # row format to be prepared for the row slicing.
        A = A.tocsr()
        B = B.tocsr()

        x_lb[np.isnan(x_lb)] = -cplex.infinity
        x_ub[np.isnan(x_ub)] = +cplex.infinity

        # The following code is based on the CPLEX documentation provided by
        # the example "socpex1.py" of CPLEX as well as the "CPLEX Python API
        # Reference Manual" available at
        #   http://www.ibm.com/support/knowledgecenter/SSSA5P_12.6.3/ilog.odms.cplex.help/refpythoncplex/html/frames.html
        prob = cplex.Cplex()

        # Manage the CPLEX output
        if self.verbose:
            output_stream = sys.stdout
        else:
            output_stream = None
        prob.set_log_stream(output_stream)
        prob.set_results_stream(output_stream)
        prob.set_warning_stream(output_stream)
        prob.set_error_stream(output_stream)

        # Variable definition and bounds
        #
        # Remark: By default, CPLEX sets the lower bounds to zero and the
        # upper bounds to cplex.infinity.
        var_idx = prob.variables.add(lb=x_lb, ub=x_ub)
        assert var_idx == range(dim_x)

        # Objective
        prob.objective.set_sense(prob.objective.sense.minimize)
        c = c.transpose().tocsr()
        assert len(c.indptr) == 2 and all(c.indptr == [0, len(c.data)])
        prob.objective.set_linear(zip(map(int, c.indices), c.data))

        # Equality constraints
        N = A.shape[0]
        A_crt = workers.starmap(_get_cplex_crt_row, zip(range(N), [A] * N))
        prob.linear_constraints.add(lin_expr=A_crt,
                                    senses=['E'] * N,  # 'E' = "equals"
                                    rhs=b)

        # Inequality constraints
        M = B.shape[0]
        B_crt = workers.starmap(_get_cplex_crt_row, zip(range(M), [B] * M))
        prob.linear_constraints.add(lin_expr=B_crt,
                                    senses=['L'] * M,  # 'L' = "less than"
                                    rhs=d)

        # Add the SOC constraints on the voltage matrix
        self._add_voltage_matrix_constraints(prob, qcqp)

        # Set solver parameters
        _set_cplex_parameters(prob, self.param)

        # Optimization and solution recovery
        _log.debug(self.type.name + " ~ Modeling ({:.3f} sec.)"
                   .format(timer.interval()))
        prob.solve()
        solver_time = timer.interval()
        _log.debug(self.type.name + " ~ Solver ({:.3f} sec.)"
                   .format(solver_time))

        status = parse_status(prob.solution.get_status())

        if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
            x = np.array(prob.solution.get_values(0, dim_x - 1), hynet_float_)
            (V, f, s, z) = qcqp.split_vectorization_optimizer(x)
            v = self.rank1approx(V, qcqp.edges, qcqp.roots)
            optimizer = QCQPPoint(v, f, s, z)

            # Unfortunately, I found the CPLEX documentation on the dual
            # variables of the variable bounds to be rather vague. The dual
            # variable of the active bound is provided as the reduced cost,
            # while the different signs suggest that the sign encodes the
            # information of the type of bound, i.e., the upper or lower bound.
            # I verified this educated guess by comparing the dual variables
            # for the hynet.test.system.TEST_SYSTEM with the result of MOSEK,
            # particularly considering
            #   result.converter[['dv_cap_src_q_max', 'dv_cap_src_q_min',
            #                     'dv_cap_dst_q_max', 'dv_cap_dst_q_min']]
            #   result.injector[['dv_cap_p_min', 'dv_cap_p_max',
            #                    'dv_cap_q_min', 'dv_cap_q_max']])
            # In case that we find an official documentation of this in the
            # CPLEX docs, it would be great if we can add a reference here.
            dv_xb = np.array(prob.solution.get_reduced_costs(0, dim_x - 1),
                             hynet_float_)

            dv_lb = np.zeros(dim_x, dtype=hynet_float_)
            idx_lb = dv_xb > 0
            dv_lb[idx_lb] = dv_xb[idx_lb]
            dv_lb[x_lb == -cplex.infinity] = np.nan
            dv_lb = qcqp.split_vectorization_bound_dual(dv_lb)

            dv_ub = np.zeros(dim_x, dtype=hynet_float_)
            idx_ub = dv_xb < 0
            dv_ub[idx_ub] = -dv_xb[idx_ub]
            dv_ub[x_ub == cplex.infinity] = np.nan
            dv_ub = qcqp.split_vectorization_bound_dual(dv_ub)

            # The sign of the dual variables is flipped. I could not find
            # anything in the CPLEX documentation on this. It may be explained
            # by the switch from maximization (default) to minimization.
            dv_eq = -np.array(prob.solution.get_dual_values(0, N - 1),
                              hynet_float_)
            dv_ineq = -np.array(prob.solution.get_dual_values(N, N + M - 1),
                                hynet_float_)

            optimal_value = prob.solution.get_objective_value()

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
