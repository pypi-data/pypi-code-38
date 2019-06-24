"""
PYOMO-based solver for the *hynet*-specific QCQP problem.
"""

import logging

import numpy as np
import pyomo.environ as pe
from pyomo.opt import (SolverStatus as PyomoSolverStatus,
                       TerminationCondition as PyomoTerminationCondition)

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.utilities.base import Timer
from hynet.qcqp.solver import SolverInterface
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.result import QCQPResult

_log = logging.getLogger(__name__)


def parse_status(status, termination):
    """Parse the PYOMO status into a ``SolverStatus``."""
    # Accessing solver status and termination conditions:
    # http://www.pyomo.org/blog/2015/1/8/accessing-solver
    if status == PyomoSolverStatus.ok and \
            termination == PyomoTerminationCondition.optimal:
        return SolverStatus.SOLVED
    if termination == PyomoTerminationCondition.infeasible:
        return SolverStatus.INFEASIBLE
    if termination == PyomoTerminationCondition.unbounded:
        return SolverStatus.UNBOUNDED
    return SolverStatus.FAILED


def _add_lower_bounds(constraint_list, variable, lb):
    """Add variable lower bound constraints and return the resp. indices."""
    index = np.where(~np.isnan(lb))[0]
    for i in index:
        constraint_list.add(variable[i] >= lb[i])
    return index


def _add_upper_bounds(constraint_list, variable, ub):
    """Add variable upper bound constraints and return the resp. indices."""
    index = np.where(~np.isnan(ub))[0]
    for i in index:
        constraint_list.add(variable[i] <= ub[i])
    return index


def _func2pyomo(func, model):
    terms = []
    if func.C is not None:
        if func.C.row.size:
            (v_r, v_i) = (model.v_r, model.v_i)
            terms += [C_ij.real * (v_r[i]*v_r[j] + v_i[i]*v_i[j]) +
                      C_ij.imag * (v_i[i]*v_r[j] - v_r[i]*v_i[j])
                      for C_ij, i, j in zip(func.C.data, func.C.row, func.C.col)]
    if func.c is not None:
        terms += [c_i * model.f[i] for c_i, i in zip(func.c.data, func.c.row)]
    if func.a is not None:
        terms += [a_i * model.s[i] for a_i, i in zip(func.a.data, func.a.row)]
    if func.r is not None:
        terms += [r_i * model.z[i] for r_i, i in zip(func.r.data, func.r.row)]
    return sum(terms)


def _get_result(variable, index):
    return np.array([variable[i].value for i in index], dtype=hynet_float_)


def _get_duals(model, constraint_list, index):
    return np.array([model.dual[constraint_list[i]] for i in index],
                    dtype=hynet_float_)


class QCQPSolver(SolverInterface):
    """
    PYOMO-based solver for the QCQP.

    Parameters
    ----------
    solver_name : str, optional
        Name of the solver, see pyomo.environ.SolverFactory. This solver
        interface was only tested with ``ipopt``, which is set by default.

    See Also
    --------
    hynet.qcqp.solver.SolverInterface : Abstract base class for QCQP solvers.
    """

    def __init__(self, solver_name='ipopt', **kwds):
        super().__init__(**kwds)
        self.solver_name = solver_name

    @property
    def name(self):
        return "PYOMO + " + self.solver_name.upper()

    @property
    def type(self):
        return SolverType.QCQP

    def solve(self, qcqp):
        """
        Solve the given QCQP using PYOMO.

        Parameters
        ----------
        qcqp : QCQP
            Specification of the quadratically-constrained quadratic problem.

        Returns
        -------
        result : QCQPResult
            Solution of the QCQP (typically only a *locally* optimal solution).
        """
        timer = Timer()

        model = pe.ConcreteModel()
        model.dual = pe.Suffix(direction=pe.Suffix.IMPORT)  # For dual variables

        model.range_v = range(qcqp.dim_v)
        model.range_f = range(qcqp.dim_f)
        model.range_s = range(qcqp.dim_s)
        model.range_z = range(qcqp.dim_z)

        if qcqp.initial_point is not None:
            v0 = qcqp.initial_point.v
            f0 = qcqp.initial_point.f
            s0 = qcqp.initial_point.s
            z0 = qcqp.initial_point.z
        else:
            v0 = (qcqp.lb.v + qcqp.ub.v) / 2
            f0 = np.zeros(qcqp.dim_f, dtype=hynet_float_)
            s0 = np.zeros(qcqp.dim_s, dtype=hynet_float_)
            z0 = np.zeros(qcqp.dim_z, dtype=hynet_float_)

        model.v_r = pe.Var(model.range_v,
                           domain=pe.Reals,
                           dense=True,
                           initialize=lambda model, i: v0[i].real)
        model.v_i = pe.Var(model.range_v,
                           domain=pe.Reals,
                           dense=True,
                           initialize=lambda model, i: v0[i].imag)
        model.f = pe.Var(model.range_f,
                         domain=pe.Reals,
                         dense=True,
                         initialize=lambda model, i: f0[i])
        model.s = pe.Var(model.range_s,
                         domain=pe.Reals,
                         dense=True,
                         initialize=lambda model, i: s0[i])
        model.z = pe.Var(model.range_z,
                         domain=pe.Reals,
                         dense=True,
                         initialize=lambda model, i: z0[i])

        model.f_lb = pe.ConstraintList()
        model.s_lb = pe.ConstraintList()
        model.z_lb = pe.ConstraintList()
        model.idx_lb = QCQPPoint(
            v=None,
            f=_add_lower_bounds(model.f_lb, model.f, qcqp.lb.f),
            s=_add_lower_bounds(model.s_lb, model.s, qcqp.lb.s),
            z=_add_lower_bounds(model.z_lb, model.z, qcqp.lb.z)
        )

        model.f_ub = pe.ConstraintList()
        model.s_ub = pe.ConstraintList()
        model.z_ub = pe.ConstraintList()
        model.idx_ub = QCQPPoint(
            v=None,
            f=_add_upper_bounds(model.f_ub, model.f, qcqp.ub.f),
            s=_add_upper_bounds(model.s_ub, model.s, qcqp.ub.s),
            z=_add_upper_bounds(model.z_ub, model.z, qcqp.ub.z)
        )

        # Set phase to zero at root nodes by fixing the imaginary part at zero
        # (This avoids solution ambiguity w.r.t. an absolute phase shift in
        #  ``v`` for those components with a given root node and, therewith,
        #  can improve the solver convergence.)
        if qcqp.roots.size:
            model.root_phase = pe.ConstraintList()
            for root in qcqp.roots:
                model.root_phase.add(model.v_i[root] == 0)

        model.eq_crt = pe.ConstraintList()
        for crt in qcqp.eq_crt:
            model.eq_crt.add(_func2pyomo(crt, model) == crt.b)

        model.ineq_crt = pe.ConstraintList()
        for crt in qcqp.ineq_crt:
            model.ineq_crt.add(_func2pyomo(crt, model) <= crt.b)

        model.objective = pe.Objective(expr=_func2pyomo(qcqp.obj_func, model),
                                       sense=pe.minimize)

        solver = pe.SolverFactory(self.solver_name, tee=self.verbose)

        # Set solver parameters
        for key, value in self.param.items():
            solver.options[key] = value

        _log.debug("QCQP ~ Modeling ({:.3f} sec.)".format(timer.interval()))
        results = solver.solve(model, tee=self.verbose)
        solver_time = timer.interval()
        _log.debug("QCQP ~ Solver ({:.3f} sec.)".format(solver_time))

        status = parse_status(results.solver.status,
                              results.solver.termination_condition)

        if status in [SolverStatus.SOLVED, SolverStatus.INACCURATE]:
            v = _get_result(model.v_r, model.v_r_index) \
                + 1j * _get_result(model.v_i, model.v_i_index)
            optimizer = QCQPPoint(v=self.adjust_absolute_phase(qcqp, v),
                                  f=_get_result(model.f, model.range_f),
                                  s=_get_result(model.s, model.range_s),
                                  z=_get_result(model.z, model.range_z))
            optimal_value = model.objective()

            dv_eq = _get_duals(model, model.eq_crt, model.eq_crt_index)
            dv_ineq = _get_duals(model, model.ineq_crt, model.ineq_crt_index)

            # REMARK: Strangely, in some configurations PYOMO returns the dual
            # variables with their sign flipped. For example, on a Ubuntu
            # machine with PYOMO 5.5.0 and ipopt_bin 3.7.1 (At this date the
            # latest version for Linux) the dual variables were positive, but
            # on MAC OS X with PYOMO 5.5.0 and ipopt_bin 3.11.1 they were
            # negated. As the sign of dual variables of inequality constraints
            # is fixed, we use this to detect this strange behavior.
            if np.all(dv_ineq == 0):
                _log.warning("Dual variable sign detection failed as all "
                             "inequality dual variables are zero.")
            elif np.all(dv_ineq <= 0):
                dv_eq *= -1
                dv_ineq *= -1

            def create_bound_dual(index, dv_f, dv_s, dv_z):
                point = QCQPPoint(
                    v=None,
                    f=np.nan * np.ones(qcqp.dim_f, dtype=hynet_float_),
                    s=np.nan * np.ones(qcqp.dim_s, dtype=hynet_float_),
                    z=np.nan * np.ones(qcqp.dim_z, dtype=hynet_float_))
                point.f[index.f] = np.abs(dv_f)  # See remark above regarding
                point.s[index.s] = np.abs(dv_s)  # the use of the absolute
                point.z[index.z] = np.abs(dv_z)  # value.
                return point

            dv_lb = create_bound_dual(
                index=model.idx_lb,
                dv_f=_get_duals(model, model.f_lb, model.f_lb_index),
                dv_s=_get_duals(model, model.s_lb, model.s_lb_index),
                dv_z=_get_duals(model, model.z_lb, model.z_lb_index)
            )

            dv_ub = create_bound_dual(
                index=model.idx_ub,
                dv_f=_get_duals(model, model.f_ub, model.f_ub_index),
                dv_s=_get_duals(model, model.s_ub, model.s_ub_index),
                dv_z=_get_duals(model, model.z_ub, model.z_ub_index)
            )

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

        _log.debug("QCQP ~ Result creation ({:.3f} sec.)"
                   .format(timer.interval()))
        _log.debug("QCQP ~ Total time for solver ({:.3f} sec.)"
                   .format(timer.total()))
        return result
