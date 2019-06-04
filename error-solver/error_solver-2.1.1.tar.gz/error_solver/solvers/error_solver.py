"""
Copyright (c) 2019, Matt Pewsey
"""

import sympy
from sympy.parsing.sympy_parser import parse_expr
import datetime
import numpy as np
from ._base_error_solver import _BaseErrorSolver

__all__ = ['ErrorSolver']


class ErrorSolver(_BaseErrorSolver):
    """
    A class for solving systems of equations for their propagation errors
    based on their equation strings.

    Parameters
    ----------
    equations : list
        A list of equation strings or string convertible objects.
    names : dict
        A dictionary of variable name replacements.
    combos : dict
        A dictionary of equation combinations.
    tol : float
        The tolerance used for verifying that values satisfy equations.

    Examples
    --------
    .. literalinclude:: ../../examples/error_solver_ex1.py
    """
    def __init__(self, equations, names={}, combos={}, tol=0.01):
        self.names = names
        self.combos = combos
        self.tol = tol
        self.set_equations(equations)

    def __repr__(self):
        s = (
            ('equations', self._equations),
            ('combos', self.combos),
            ('tol', self.tol),
        )
        s = ', '.join('{}: {!r}'.format(x, y) for x, y in s)
        return '{}({})'.format(type(self).__name__, s)

    @classmethod
    def from_file(cls, path, **kwargs):
        """
        Creates a new object from a specified Error Solver file.

        Parameters
        ----------
        path : str
            The file path.
        kwargs
            Additional arguments accepted by the default initializer.
        """
        data = cls._read_file(path)

        return cls(
            equations=data.get('equations', []),
            names=data.get('names', {}),
            combos=data.get('combos', {}),
            **kwargs
        )

    @staticmethod
    def _read_file(path):
        """
        Reads the specified Error Solver file to a dictionary.

        Parameters
        ----------
        path : str
            The file path.
        """
        data = {}
        section = None

        with open(path, 'rt') as fh:
            for line in fh:
                line = line.split('#')[0].rstrip('\n').strip()

                if line == '':
                    continue

                if line.startswith('[') and line.endswith(']'):
                    section = line.lstrip('[').rstrip(']')

                    if section == 'equations':
                        data[section] = []
                    elif section in ('names', 'combos'):
                        data[section] = {}
                    else:
                        raise ValueError('Invalid section header: {}'.format(section))

                    continue

                if section == 'equations':
                    data[section].append(line)

                elif section == 'names':
                    s = [x.strip() for x in line.split(':')]
                    data[section][s[0]] = s[1]

                elif section == 'combos':
                    s = [x.strip() for x in line.split(':')]
                    v = [int(x.strip()) for x in s[1].split(' ')]
                    data[section][s[0]] = v

        return data

    def _set_equal_to_zero(self, equation):
        """
        Sets the input equation string equal to zero if it isn't already.

        Parameters
        ----------
        equation : str
            The input equation string.
        """
        if not isinstance(equation, str):
            equation = str(equation)

        s = equation.split('=')
        n = len(s)

        if n == 1:
            return equation
        elif n == 2:
            return '({})-({})'.format(s[0], s[1])
        else:
            raise ValueError('Equation has too many equal signs: {}'.format(equation))

    def _parse_equation(self, equation):
        """
        Parses the input equation string to a `sympy` expression.

        Parameters
        ----------
        equation : str
            The input equation string.
        """
        eq = self._set_equal_to_zero(equation)

        try:
            eq = parse_expr(eq)
        except:
            raise ValueError('Failed to parse equation: {}'.format(equation))

        return eq

    def set_equations(self, equations):
        """
        Parses the input equations to `sympy` expressions and sets them to the
        object.

        Parameters
        ----------
        equations : list
            A list of equation strings.
        """
        eqs = []

        for eq in equations:
            eq = self._parse_equation(eq)
            eq = eq.subs(self.names)
            eqs.append(eq)

        self._equations = eqs
        self.set_partials()

    def set_partials(self):
        """
        Calculates the partial derivatives for the equations assigned to the
        object.
        """
        partials = []

        for eq in self._equations:
            p = {k: sympy.diff(eq, k) for k in map(str, eq.free_symbols)}
            partials.append(p)

        self._partials = partials

    def python_str(self):
        """
        Returns a Python module string for the equations and partial derivatives
        assigned to the object.
        """
        def create_header():
            s = '"""\nCreated by Error Solver on {}\n\n{}\n"""\n\nfrom math import *\n\n'
            d = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            n = len(str(len(self._equations)))
            f = '{{:>{}}}: {{}}'.format(n)
            e = '\n'.join(f.format(i, x) for i, x in enumerate(self._equations))
            return s.format(d, e)

        def create_functions():
            e = '# Equation {}\ndef eq{}({}, **kwargs):\n\treturn {}\n\n'
            p = 'def eq{}_{}({}, **kwargs):\n\treturn {}\n\n'
            s = []

            for i, x in enumerate(self._equations):
                args = ', '.join(map(str, x.free_symbols))
                s.append(e.format(i, i, args, x))

                for k, y in self._partials[i].items():
                    s.append(p.format(i, k, args, y))

            return '\n'.join(s)

        def create_equations():
            s = '# Assembled functions\nEQUATIONS = [\n{}\n]\n\n'
            e = ',\n'.join('\teq{}'.format(i) for i in range(len(self._equations)))
            return s.format(e)

        def create_partials():
            s = 'PARTIALS = [\n{}\n]\n\n'
            f = '{!r}: eq{}_{}'
            p = []

            for i, x in enumerate(self._partials):
                e = ', '.join(f.format(y, i, y) for y in x.keys())
                e = '\t{{{}}}'.format(e)
                p.append(e)

            p = ',\n'.join(p)
            return s.format(p)

        def create_combos():
            s = 'COMBOS = {{\n{}\n}}\n'
            p = []

            for k, x in self.combos.items():
                e = ', '.join('{!r}'.format(y) for y in x)
                e = '\t{!r}: [{}]'.format(k, e)
                p.append(e)

            p = ',\n'.join(p)
            return s.format(p)

        func = [
            create_header,
            create_functions,
            create_equations,
            create_partials,
            create_combos,
        ]

        result = '\n'.join(x() for x in func)
        result = result.replace('\t', ' ' * 4)

        return result

    def write_python(self, path):
        """
        Writes a Python module with the equations and partial derivatives
        assigned to the object.

        Parameters
        ----------
        path : str
            The path where the module will be written.
        """
        s = self.python_str()

        with open(path, 'wt') as fh:
            fh.truncate()
            fh.write(s)

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
                jac[i, j] = v.subs(values).evalf()

        return jac

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
            v = eq.subs(values).evalf()

            if v.free_symbols:
                raise ValueError('Values {} missing for equation {}: {}.'
                    .format(v.free_symbols, i, eq))

            v = float(v)

            if abs(v) > self.tol:
                raise ValueError('Equation {}: {} value check tolerance '
                    'exceeded:: |{}| > {}.'.format(i, eq, v, self.tol))

    def _check_restricted_symbols(self, values, errors):
        """
        Checks that the input variables do not include any restricted symbols.

        Parameters
        ----------
        values : dict
            A dictionary mapping variable names to values.
        errors : dict
            A dictionary mapping variable names to errors.
        """
        restr = (sympy.NumberSymbol, sympy.I, sympy.zoo)

        # Input restricted symbols
        inpt = set()
        var = set(values) | set(errors)

        for v in var:
            e = parse_expr(v)
            inpt |= e.atoms(*restr)

        if inpt:
            inpt = sorted(map(str, inpt))
            raise ValueError('Symbols {} in input are restricted and cannot '
                'be used.'.format(inpt))

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
        self._check_restricted_symbols(values, errors)
        self._check_values(values, combo)
        self._check_determinancy(values, errors, combo)
