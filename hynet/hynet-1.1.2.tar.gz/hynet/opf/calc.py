"""
Calculation of the optimal power flow.
"""

import logging

from hynet.types_ import SolverType
from hynet.solver import AVAILABLE_SOLVERS
from hynet.data.connection import DBConnection
from hynet.data.interface import load_scenario
from hynet.scenario.representation import Scenario
from hynet.model.steady_state import SystemModel
from hynet.qcqp.solver import SolverInterface
from hynet.opf.initial_point import CopperPlateInitialPointGenerator
from hynet.utilities.base import Timer

_log = logging.getLogger(__name__)


def get_default_initial_point_generator():
    """
    Return the default initial point generator for the current system.

    If a sufficiently efficient SOCR solver is available, the utilization of a
    copper plate based initial point for the solution of the nonconvex QCQP
    typically improves the overall performance, i.e., that the reduced number
    of iterations of the QCQP solver outweighs the computational cost for the
    initial point.
    """
    socr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SOCR]

    def find_solver(solver_name):
        for SolverClass in socr_solvers:
            if SolverClass().name == solver_name:
                return SolverClass
        return None

    # Prioritized search for a suitable SOCR solver
    for solver_name in ['MOSEK', 'CPLEX']:
        SolverClass = find_solver(solver_name)
        if SolverClass is not None:
            return CopperPlateInitialPointGenerator(SolverClass())
    return None


def calc_opf(data, scenario_id=0, solver=None, solver_type=None,
             initial_point_generator=get_default_initial_point_generator()):
    """
    Calculate the optimal power flow.

    This function formulates and solves the optimal power flow (OPF) problem.
    The solver or solver type may be specified explicitly, otherwise an
    appropriate solver is selected automatically.

    **Custom OPF Formulations:** For a customization of the standard OPF
    formulation, please refer to the docstring of ``SystemModel``.

    **Copper Plate Models:** *hynet* supports the simulation of "copper plate
    models", i.e., when the grid model is neglected all injectors and
    loads are connected to a single bus. As such models exhibit the *hybrid
    architecture*, all solver types (QCQP, SDR, and SOCR) are applicable. The
    grid model of a scenario can be reduced to a copper plate using
    ``reduce_to_copper_plate``.

    Parameters
    ----------
    data : DBConnection or Scenario or SystemModel
        Connection to a *hynet* grid database, a ``Scenario`` object, or a
        ``SystemModel`` object.
    scenario_id : .hynet_id_, optional
        Identifier of the scenario. This argument is ignored if ``data`` is a
        ``Scenario`` or ``SystemModel`` object.
    solver : SolverInterface, optional
        Solver for the QCQP problem; the default selects an appropriate
        solver of those available.
    solver_type : SolverType, optional
        Optional solver type for the QCQP problem, i.e., if passed it restricts
        the automatic solver selection to this type. It is ignored if
        ``solver`` is not ``None``.
    initial_point_generator : InitialPointGenerator or None, optional
        Initial point generator for QCQP solvers (ignored for relaxation-based
        solvers). By default, an appropriate initial point generator is
        selected if a computationally efficient SOCR solver is installed.
        Set to ``None`` to skip the initial point generation.

    Returns
    -------
    result : OPFResult
        Optimal power flow solution.

    See Also
    --------
    hynet.scenario.representation.Scenario
    hynet.opf.result.OPFResult
    hynet.types_.SolverType
    hynet.model.steady_state.SystemModel
    hynet.reduction.copper_plate.reduce_to_copper_plate
    hynet.opf.initial_point : Initial point generators.
    """
    timer = Timer()
    if isinstance(data, SystemModel):
        model = data
    elif isinstance(data, Scenario):
        model = SystemModel(data)
    elif isinstance(data, DBConnection):
        model = SystemModel(load_scenario(data, scenario_id))
    else:
        raise ValueError(("The argument 'data' must be a database file name, "
                          "a Scenario object, or a SystemModel object."))

    if solver is None:
        solver = select_solver(model, solver_type)()
    elif not isinstance(solver, SolverInterface):
        raise ValueError("The solver must be a SolverInterface-derived object.")

    _log.debug("Calculate OPF ~ Loading, verification, and solver selection "
               "({:.3f} sec.)".format(timer.interval()))
    timer.reset()

    qcqp = model.get_opf_problem()

    if solver.type == SolverType.QCQP and \
            initial_point_generator is not None and \
            model.dim_v > len(model.islands):
        # Support the solver with an appropriate initial point
        qcqp.initial_point = initial_point_generator(model, qcqp)

    _log.debug("Calculate OPF ~ QCQP creation ({:.3f} sec.)"
               .format(timer.interval()))

    result = solver.solve(qcqp)
    return model.create_opf_result(result, total_time=timer.total())


def select_solver(model, solver_type=None):
    """
    Return the most appropriate solver of those available for the given conditions.

    Parameters
    ----------
    model : SystemModel
        Steady state model for which the OPF shall be calculated.
    solver_type : SolverType, optional
        Specification of the solver type. By default, the most appropriate
        among all available solver types is selected.

    Returns
    -------
    solver : SolverInterface
        Selected solver interface *class*.

    Raises
    ------
    RuntimeError
        In case no appropriate solver was found.
    """
    if not AVAILABLE_SOLVERS:
        raise RuntimeError("No supported solvers were found.")

    qcqp_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.QCQP]
    sdr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SDR]
    socr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SOCR]

    if solver_type is not None:
        if solver_type == SolverType.QCQP:
            if qcqp_solvers:
                solver = qcqp_solvers[0]
            else:
                raise RuntimeError("No supported QCQP solvers were found.")
        elif solver_type == SolverType.SDR:
            if sdr_solvers:
                solver = sdr_solvers[0]
            else:
                raise RuntimeError("No supported SDR solvers were found.")
        elif solver_type == SolverType.SOCR:
            if socr_solvers:
                solver = socr_solvers[0]
            else:
                raise RuntimeError("No supported SOCR solvers were found.")
        else:
            raise ValueError("The solver type must be a SolverType member.")
    else:
        if model.has_hybrid_architecture:
            # For the hybrid architecture, choose the most efficient solver
            if socr_solvers:
                solver = socr_solvers[0]
            elif sdr_solvers:
                solver = sdr_solvers[0]
            else:
                solver = qcqp_solvers[0]
        else:
            if qcqp_solvers:
                solver = qcqp_solvers[0]
            else:
                raise RuntimeError("Please install a QCQP solver to reliably "
                                   "solve the OPF for systems without the "
                                   "hybrid architecture.")
    return solver
