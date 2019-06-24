"""
Solvers for the *hynet*-specific QCQP problem.
"""

import logging
_log = logging.getLogger(__name__)

# Build a list comprising all available solvers. Import in the order of
# preference, as the first element is used as the default solver.
AVAILABLE_SOLVERS = []

try:
    from hynet.solver import ipopt

    AVAILABLE_SOLVERS.append(ipopt.QCQPSolver)
except ImportError:
    pass

try:
    from hynet.solver import cplex

    AVAILABLE_SOLVERS.append(cplex.SOCRSolver)
except ImportError:
    pass

try:
    from hynet.solver import mosek

    AVAILABLE_SOLVERS.append(mosek.SOCRSolver)
    AVAILABLE_SOLVERS.append(mosek.SDRSolver)
except ImportError:
    pass

try:
    from hynet.solver import picos

    AVAILABLE_SOLVERS.append(picos.SOCRSolver)
    AVAILABLE_SOLVERS.append(picos.SDRSolver)
except ImportError:
    pass

try:
    from hynet.solver import pyomo

    AVAILABLE_SOLVERS.append(pyomo.QCQPSolver)
except ImportError:
    pass

if not AVAILABLE_SOLVERS:
    _log.warning("No supported solvers were found.")
