"""
Copyright (c) 2019, Matt Pewsey
"""

import numpy as np
from ._base_error_solver import _BaseErrorSolver

__all__ = ['ErrorSolverPy']


class ErrorSolverPy(_BaseErrorSolver):
    """
    A class for solving systems of equations for their propagation errors
    using Python functions.

    Parameters
    ----------
    equations : list
        A list of equation functions.
    partials : list
        A list of dictionaries of partial derivative functions.
    combos : dict
        A dictionary of equation combinations.
    tol : float
        The tolerance used for verifying that values satisfy equations.

    Examples
    --------
    .. literalinclude:: ../../examples/error_solver_py_ex1.py

    In lieu of defining the equation methods manually, the :class:`.ErrorSolver`
    class may be used to automatically calculate the partial derivatives
    from an input system of equations and write methods to a Python module
    for use by :class:`ErrorSolverPy`. This can be done as follows:

    .. literalinclude:: ../../examples/error_solver_py_ex2.py
    """
    def __init__(self, equations, partials, combos={}, tol=0.01):
        self._equations = equations
        self._partials = partials
        self.combos = combos
        self.tol = tol

    def __repr__(self):
        s = (
            ('equations', self._equations),
            ('combos', self.combos),
            ('tol', self.tol),
        )
        s = ', '.join('{}: {!r}'.format(x, y) for x, y in s)
        return '{}({})'.format(type(self).__name__, s)

    @classmethod
    def from_module(cls, module, **kwargs):
        """
        Initializes an object from an imported Error Solver Python module.

        Parameters
        ----------
        module
            An imported Python module with the requisite EQUATIONS, PARTIALS,
            and COMBOS global variables.
        kwargs
            Additional arguments accepted by the default initializer.
        """
        return cls(
            equations=module.EQUATIONS,
            partials=module.PARTIALS,
            combos=module.COMBOS,
            **kwargs
        )

    def _check_values(self, values, combo):
        """
        Checks that the input values satisfy all equations within the
        specified tolerances.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        combo : str
            The name of the equation combination to be applied.
        """
        for i, eq in enumerate(self.get_equations(combo)):
            v = eq(**values)

            if abs(v) > self.tol:
                raise ValueError('Equation {}: {} value check tolerance '
                    'exceeded:: |{}| > {}.'.format(i, eq, v, self.tol))

    def check(self, values, errors, combo=None):
        """
        Checks that the input parameters are correct to carry out a solution.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        combo : str
            The name of the equation combination to be applied.
        """
        self._check_values(values, combo)
        self._check_determinancy(values, errors, combo)

    def equation_vars(self, combo=None):
        """
        Returns a set of all variables in the equations.

        Parameters
        ----------
        combo : str
            The name of the equation combination to be applied.
        """
        var = set()

        for p in self.get_partials(combo):
            var |= p.keys()

        return var

    def jacobian(self, values, errors, combo=None):
        """
        Returns the Jacobian matrix for the system of equations.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        combo : str
            The name of the equation combination to be applied.
        """
        partials = self.get_partials(combo)
        val, err = self.used_vars(values, errors, combo)
        var = {x: i for i, x in enumerate(val + err)}

        n, m = len(partials), len(var)
        jac = np.zeros((n, m), dtype='float')

        for i, p in enumerate(partials):
            for k, v in p.items():
                j = var[k]
                jac[i, j] = v(**values)

        return jac
