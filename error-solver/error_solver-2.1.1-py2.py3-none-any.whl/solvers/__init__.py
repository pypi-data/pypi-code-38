"""
==========================================
Error Solver (:mod:`error_solver.solvers`)
==========================================

Solvers
=======
The following classes are available for performing propagation error analysis.

.. autosummary::
    :toctree: generated/

    ErrorSolver
    ErrorSolverPy
    SolverPipeline


Collector
=========
The solvers require that all of the values for a solution be known so that
the partial derivatives of the equations can be evaluated. To assist in
acquiring these values from a program, the :func:`.collect` and
:func:`.fcollect` decorators may be used to wrap class methods and functions,
respectively, to collect their results as they are calculated. Collection
for these functions is performed only while the :class:`.Collector` context
manager is active.

.. autosummary::
    :toctree: generated/

    Collector
    collect
    fcollect
"""

import warnings
from .collector import *
from .error_solver_py import *

# Signal a warning if Sympy is not installed
try:
    from .error_solver import *
except ModuleNotFoundError as error:
    if "'sympy'" in str(error):
        warnings.warn('Sympy not installed. Dependent features will not be available.')
    else:
        raise error
except Exception as error:
    raise error

from .pipeline import *

# Clean up namespace
del warnings
