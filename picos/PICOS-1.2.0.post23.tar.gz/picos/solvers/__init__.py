#-------------------------------------------------------------------------------
# Copyright (C) 2017-2018 Maximilian Stahlberg
#
# This file is part of PICOS.
#
# PICOS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PICOS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This file serves as a helper to include all solvers, and to query
# their availability on the user's platform. It is supposed to be
# the only import necessary to get full access to all solvers.
#-------------------------------------------------------------------------------

# Import the solver base class and exceptions (for the API documentation).
from .solver import Solver, SolverError, ProblemUpdateError, \
    InappropriateSolverError, OptionError, UnsupportedOptionError, \
    ConflictingOptionsError, DependentOptionError, OptionValueError

# Import all solvers.
from .solver_cplex  import CPLEXSolver
from .solver_cvxopt import CVXOPTSolver
from .solver_ecos   import ECOSSolver
from .solver_glpk   import GLPKSolver
from .solver_gurobi import GurobiSolver
from .solver_mosek  import MOSEKSolver
from .solver_mskfsn import MOSEKFusionSolver
from .solver_scip   import SCIPSolver
from .solver_smcp   import SMCPSolver

# Map solver names to their implementation classes.
_solvers = {
    "cplex":  CPLEXSolver,
    "cvxopt": CVXOPTSolver,
    "ecos":   ECOSSolver,
    "glpk":   GLPKSolver,
    "gurobi": GurobiSolver,
    "mosek":  MOSEKSolver,
    "mskfsn": MOSEKFusionSolver,
    "scip":   SCIPSolver,
    "smcp":   SMCPSolver
}

# Lift support levels to this module.
from .solver import \
    supportLevelString, \
    SUPPORT_LEVEL_NONE, \
    SUPPORT_LEVEL_LIMITED, \
    SUPPORT_LEVEL_EXPERIMENTAL, \
    SUPPORT_LEVEL_SECONDARY, \
    SUPPORT_LEVEL_NATIVE

# Make sure all solvers inherit from their abstract base class.
from .solver import Solver
assert not False in [issubclass(solver, Solver) for solver in _solvers.values()]

order = [
    "gurobi",
    "cplex",
    "mosek",
    "mskfsn",
    "scip",
    "ecos",
    "glpk",
    "smcp",
    "cvxopt"
]
"""
The default preference list for solver selection. Solvers that do not appear
are appended arbitrarily when selecting a solver.

The order is chosen as follows:

- Commercial solvers appear first as the user has spent money or academic
  licensing effort to make them available and is likely to want them used.
- MOSEK's high level Fusion API was found to be a performance bottleneck
  (2018-10), so it appears at the end of the commercial solver list (so that
  MOSEK's low level Optimizer API takes precedence).
- Commercial solvers are sorted based on LP benchmark results in
  http://plato.asu.edu/talks/informs2017.pdf as LPs are the most basic problem
  type supported by PICOS and the benchmark results appear decisive.
- CVXOPT appears last as it is the only solver that PICOS depends on and thus
  presence on the system is least likely to express user preference.
- The remaining noncommercial solvers are sorted based on the PICOS maintainers'
  subjectively perceived impression of "maintainedness".
"""

class NoAppropriateSolverError(Exception):
    """
    An exception raised when no fitting solver is available.
    """
    pass

def get_solver(name):
    """
    :returns: Implementation class of the solver of the given name.
    """
    return _solvers[name]

def all_solvers():
    """
    :returns: A dictionary mapping solver names to implementation classes.
    """
    return _solvers.copy()

def available_solvers(problem = None):
    """
    :returns: A list of names of available solvers.

    :param picos.Problem problem: Return only solvers that also support this
        problem.
    """
    return [name for name, solver in _solvers.items()
        if solver.available() and (problem is None
            or solver.support_level(problem) > SUPPORT_LEVEL_NONE)]

def potential_solvers(problem):
    """
    :returns: A list of names of solvers that support the given problem.
    """
    return [name for name, solver in _solvers.items()
        if solver.support_level(problem) > SUPPORT_LEVEL_NONE]

def suggested_solver(problem, order = list(order), returnClass = False):
    """
    :returns: The name or class of an available solver that can handle the given
        problem type.

    :param list order: The order in which solvers are considered, as a list of
        solver names. If the list does not contain every solver it will be
        extended arbitrarily to do so.
    :param bool returnClass: Whether to return the solver's class instead of its
        keyword name.
    """
    # Complete the order to contain all solvers.
    for name in _solvers.keys():
        if name not in order:
            order.append(name)

    # Remove solvers that are not available.
    order = [name for name in order if get_solver(name).available()]

    # Retrieve support levels.
    levels = {name: get_solver(name).support_level(problem) for name in order}

    # Remove solvers that don't support the problem.
    order = [name for name in order if levels[name] > SUPPORT_LEVEL_NONE]

    # Stably resort the remaining order according to the support level.
    order = sorted(
        order, key = lambda n: (levels[n], -order.index(n)), reverse = True)

    # Select the first available solver.
    for name in order:
        return get_solver(name) if returnClass else name

    # Inform the user that no fitting solver could be found.
    options = potential_solvers(problem)
    if len(options) == 0:
        raise NoAppropriateSolverError(
            "PICOS does not support a solver that can handle the problem.")
    elif len(options) == 1:
        capableSolvers = options[0]
    else:
        capableSolvers = ", ".join(options[:-1]) + " or " + options[-1]
    raise NoAppropriateSolverError(
        "There appears to be no solver installed that can solve your problem. "
        "Consider installing {}.".format(capableSolvers))
