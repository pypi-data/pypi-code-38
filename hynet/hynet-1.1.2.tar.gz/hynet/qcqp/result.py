#pylint: disable=too-many-instance-attributes,too-many-arguments
"""
Representation of the result of a *hynet*-specific QCQP.
"""

import logging

import numpy as np
import pandas as pd

from hynet.qcqp.problem import QCQPPoint  # pylint: disable=unused-import
from hynet.utilities.base import Timer

_log = logging.getLogger(__name__)


class QCQPResult:
    """
    Solution of a quadratically constrained quadratic program.

    **Caution:** The constructor adjusts the optimal objective value, the
    optimizer, and the dual variables according to the scaling of the problem,
    i.e., the properties of the result correspond to the *unscaled* QCQP.

    Parameters
    ----------
    qcqp : QCQP
        Problem specification.
    solver : SolverInterface
        Solver object by which the result was obtained.
    solver_status : SolverStatus
        Status reported by the solver after performing the optimization.
    solver_time : float
        Duration of the call to the solver in seconds.
    optimizer : QCQPPoint or None
        Optimal optimization variable ``(v^*, f^*, s^*, z^*)`` or ``None`` if
        the solver failed. In case of a relaxation, ``v^*`` is the rank-1
        approximation of ``V^*``.
    V : .hynet_sparse_ or None
        Optimal optimization variable ``V^*`` in case of a relaxation or
        ``None`` if the solver failed or a nonconvex-QCQP solver was employed.
    optimal_value : float
        Optimal objective value or ``numpy.nan`` if the solver failed.
    reconstruction_mse : float
        The mean squared error of the reconstructed ``v^*`` in case of a
        relaxation or ``numpy.nan`` if the solver failed or a nonconvex-QCQP
        solver was employed.
    dv_lb : QCQPPoint or None
        Optimal dual variables of the lower bounds on ``f``, ``s``, and ``z``
        or ``None`` if the solver failed. The attribute ``v`` is set ``None``
        as these bounds are optional, cf. the QCQP specification.
    dv_ub : QCQPPoint or None
        Optimal dual variables of the upper bounds on ``f``, ``s``, and ``z``
        or ``None`` if the solver failed. The attribute ``v`` is set ``None``
        as these bounds are optional, cf. the QCQP specification.
    dv_eq : numpy.ndarray or None
        Optimal dual variables of the equality constraints or ``None`` if the
        solver failed.
    dv_ineq : numpy.ndarray or None
        Optimal dual variables of the inequality constraints or ``None`` if the
        solver failed.
    """
    def __init__(self, qcqp, solver, solver_status, solver_time,
                 optimizer=None, V=None, optimal_value=None,
                 dv_lb=None, dv_ub=None, dv_eq=None, dv_ineq=None):
        timer = Timer()
        self.qcqp = qcqp
        self.solver = solver
        self.solver_status = solver_status
        self.solver_time = solver_time
        self._optimizer_normalized = optimizer
        self.V = V
        self.optimal_value = optimal_value
        self.dv_lb = dv_lb
        self.dv_ub = dv_ub
        self.dv_eq = dv_eq
        self.dv_ineq = dv_ineq

        # Compensate the scaling of the objective, variables, and constraints
        #
        # REMARK: If a constraint is scaled by s, then the associated dual
        # variable scales by 1/s (cf. the first order optimality conditions).
        # Therefore, to obtain the dual variable of the unscaled constraint,
        # the dual variable of the scaled constraint must be multiplied by s.
        obj_scaling = qcqp.obj_func.scaling

        if self.optimal_value is None:
            self.optimal_value = np.nan
        self.optimal_value /= obj_scaling

        if self._optimizer_normalized is not None:
            scaling = qcqp.normalization.copy().reciprocal()
            self.optimizer = self._optimizer_normalized.copy().scale(scaling)
        else:
            self.optimizer = None

        if self.V is not None:
            self.V = self.V / qcqp.normalization.v ** 2  # New matrix!

        bound_dual_scaling = qcqp.normalization.copy().scale(1 / obj_scaling)
        if self.dv_lb is not None:
            self.dv_lb = self.dv_lb.copy().scale(bound_dual_scaling)

        if self.dv_ub is not None:
            self.dv_ub = self.dv_ub.copy().scale(bound_dual_scaling)

        if self.dv_eq is not None:
            self.dv_eq = self.dv_eq / obj_scaling  # New array!
            for i in range(len(qcqp.eq_crt)):
                self.dv_eq[i] *= qcqp.eq_crt[i].scaling

        if self.dv_ineq is not None:
            self.dv_ineq = self.dv_ineq / obj_scaling  # New array!
            for i in range(len(qcqp.ineq_crt)):
                self.dv_ineq[i] *= qcqp.ineq_crt[i].scaling

        # Calculate the reconstruction error in case of a relaxation
        if self.V is not None:
            self.reconstruction_mse = \
                self.solver.rank1approx.calc_mse(self.V,
                                                 self.optimizer.v,
                                                 qcqp.edges)
        else:
            self.reconstruction_mse = np.nan

        _log.debug("QCQP result creation ({:.3f} sec.)"
                   .format(timer.total()))

    @property
    def empty(self):
        """Return ``True`` if the QCQP result does not contain an optimizer."""
        return self.optimizer is None

    def get_result_tables(self, tables=None,
                          dual_prefix='dv_', value_prefix='cv_'):
        """
        Return a dictionary of data frames with the dual and constraint result.

        According to the table and ID information of the constraint objects,
        a dictionary of data frames is assembled that contains the dual
        variables and the *equality* constraint function values with the right
        hand side subtracted.
        """
        tables = {} if tables is None else tables

        if self.empty:
            return tables

        for crt, dv in zip(self.qcqp.eq_crt, self.dv_eq):
            if crt.table is None:
                continue
            if crt.table not in tables:
                tables[crt.table] = pd.DataFrame()
            tables[crt.table].at[crt.id, dual_prefix + crt.name] = dv
            tables[crt.table].at[crt.id, value_prefix + crt.name] = \
                crt.evaluate(self._optimizer_normalized) / crt.scaling

        for crt, dv in zip(self.qcqp.ineq_crt, self.dv_ineq):
            if crt.table is None:
                continue
            if crt.table not in tables:
                tables[crt.table] = pd.DataFrame()
            tables[crt.table].at[crt.id, dual_prefix + crt.name] = dv

        return tables
