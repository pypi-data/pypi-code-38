# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
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
# This file implements the representation of an optimization problem.
#-------------------------------------------------------------------------------

from __future__ import print_function, division

import cvxopt as cvx
import numpy as np
import sys
import time

from .tools import *
from .expressions import *
from .constraints import *
from .solvers import *

INFINITY = 1e16


class Problem(object):
    """
    PICOS' representation of an optimization problem.

    :Example:

    >>> import picos
    >>> P = picos.Problem(verbose = 0)
    >>> X = P.add_variable("X", (2,2), lower = 0)
    >>> # 1|X is the dot prouct of X with a matrix of all ones.
    >>> C = P.add_constraint(1|X < 10)
    >>> P.set_objective("max", picos.trace(X))
    >>> # PICOS will select a suitable solver if you don't specify one.
    >>> solution = P.solve(solver = "cvxopt")
    >>> solution["status"]
    'optimal'
    >>> solution["time"] #doctest: +SKIP
    0.00034999847412109375
    >>> round(P.obj_value(), 1)
    10.0
    >>> print(X) #doctest: +SKIP
    [ 0.00e+00  0.00e+00]
    [ 0.00e+00  1.00e+01]
    >>> round(C.dual, 1)
    1.0
    """
    def __init__(self, **options):
        """
        Creates an empty problem and optionally sets initial solver options.

        :param options: A parameter sequence of solver options.
        """
        self.reset(resetOptions = True)

        if options:
            self.update_options(**options)

    def reset(self, resetOptions = False):
        """
        Resets the problem instance to its initial empty state.

        :param bool resetOptions: Whether also solver options should be reset to
            their default values.
        """

        self.objective = ('find', None)
        """Ojective function."""

        self.constraints = []
        """List of all constraints."""

        self._deleted_constraints = []

        self.variables = {}
        """Dictionary of variables indexed by variable names."""

        self.countVar = 0
        """Number of (multidimensional) variables."""

        self.countCons = 0
        """Number of (multidimensional) constraints."""

        self.numberOfVars = 0
        """Total number of (scalar) variables."""

        self.numberAffConstraints = 0
        """Total number of (scalar) affine constraints."""

        self.numberConeVars = 0
        """Number of auxilary variables used for SOC constraints."""

        self.numberConeConstraints = 0
        """Number of SOC constraints"""

        self.numberLSEConstraints = 0
        """Number of LogSumExp constraints (+1 for LogSumExp objective)."""

        self.numberLSEVars = 0
        """Number of vars in LogSumExp expressions."""

        self.numberQuadConstraints = 0
        """Number of quadratic constraints (+1 for quadratic objective)."""

        self.numberQuadNNZ = 0
        """Number of non-zero coefficients of quadratic expressions."""

        self.numberSDPConstraints = 0
        """Number of SDP constraints."""

        self.numberSDPVars = 0
        """Size of the s-vecotrized matrices involved in SDP constraints."""

        self.numberMetaConstraints = 0
        """Number of metaconstraints, such as geomean inequalities."""

        self.longestkey = 0
        """Used for formatting constraint strings."""

        self._status = 'unsolved'
        """Status returned by the solver."""

        self._complex = False
        """Whether the problem has complex coefficients."""

        # TODO: Document these.
        self.groupsOfConstraints = {}
        self.listOfVars = {}
        self.varNames = []
        self.consNumbering = []
        self.number_solutions = 0

        self.solvers = {}
        """The solver instances."""

        for name in all_solvers():
            self.solvers[name] = None

        if resetOptions:
            self._options = NonWritableDict()
            self.set_all_options_to_default()

    def __str__(self):
        probstr = '---------------------\n'
        probstr += 'optimization problem ({0}):\n'.format(self.type)
        probstr += '{0} variables, {1} affine constraints'.format(
            self.numberOfVars, self.numberAffConstraints)

        if self.numberConeVars > 0:
            probstr += ', {0} vars in {1} SO cones'.format(
                self.numberConeVars, self.numberConeConstraints)
        if self.numberLSEConstraints > 0:
            probstr += ', {0} vars in {1} LOG-SUM-EXP'.format(
                self.numberLSEVars, self.numberLSEConstraints)
        if self.numberSDPConstraints > 0:
            probstr += ', {0} vars in {1} SD cones'.format(
                self.numberSDPVars, self.numberSDPConstraints)
        if self.numberQuadConstraints > 0:
            probstr += ', {0} nnz  in {1} quad constraints'.format(
                self.numberQuadNNZ, self.numberQuadConstraints)
        probstr += '\n'

        printedlis = []
        for vkey in sorted(self.variables.keys()):
            if vkey[:4] in (
                '_geo', '_nop', '_ntp', '_ndt', '_nts', '_npq', '_nsk', '_sue'):
                continue
            if '[' in vkey and ']' in vkey:
                lisname = vkey[:vkey.index('[')]
                if lisname not in printedlis:
                    printedlis.append(lisname)
                    var = self.listOfVars[lisname]
                    probstr += '\n' + lisname + ' \t: '
                    probstr += var['type'] + ' of ' + \
                        str(var['numvars']) + ' variables, '
                    if var['size'] == 'different':
                        probstr += 'different sizes'
                    else:
                        probstr += str(var['size'])
                    if var['vtype'] == 'different':
                        probstr += ', different type'
                    else:
                        probstr += ', ' + var['vtype']
                    probstr += var['bnd']
            else:
                var = self.variables[vkey]
                probstr += '\n' + vkey + ' \t: ' + \
                    str(var.size) + ', ' + var.vtype + var._bndtext
        probstr += '\n'
        if self.objective[0] == 'max':
            probstr += '\n\tmaximize ' + self.objective[1].string + '\n'
        elif self.objective[0] == 'min':
            probstr += '\n\tminimize ' + self.objective[1].string + '\n'
        elif self.objective[0] == 'find':
            probstr += '\n\tfind vars\n'
        probstr += 'such that\n'
        if self.countCons == 0:
            probstr += '  []\n'
        k = 0
        while k < self.countCons:
            if k in self.groupsOfConstraints.keys():
                lcur = len(self.groupsOfConstraints[k][2])
                if lcur > 0:
                    lcur += 2
                    probstr += '(' + self.groupsOfConstraints[k][2] + ')'
                if self.longestkey == 0:
                    ntabs = 0
                else:
                    ntabs = int(np.ceil((self.longestkey + 2) / 8.0))
                missingtabs = int(np.ceil(((ntabs * 8) - lcur) / 8.0))
                for i in range(missingtabs):
                    probstr += '\t'
                if lcur > 0:
                    probstr += ': '
                else:
                    probstr += '  '
                probstr += self.groupsOfConstraints[k][1]
                k = self.groupsOfConstraints[k][0] + 1
            else:
                probstr += "  " + self.constraints[k].keyconstring() + '\n'
                k += 1
        probstr += '---------------------'
        return probstr

    def verbosity(self):
        """
        :returns: The problem's current verbosity level.
        """
        return int(self.options["verbose"])

    def _verbosity_printer(self, minLevel, message = None):
        """
        Prints a message, if the verbosity level is not below the given minimum.

        :returns: Whether messages are printed.
        """
        condition = self.verbosity() >= minLevel
        if condition and message is not None:
            print(message)
        return condition

    def _warn(self, message = None):
        """
        Prints a warning message, if the verbosity level allows for it.

        :returns: Whether warning messages are printed.
        """
        return self._verbosity_printer(0, message)

    def _verbose(self, message = None):
        """
        Prints an informative message, if the verbosity level allows for it.

        :returns: Whether informative messages are printed.
        """
        return self._verbosity_printer(1, message)

    def _debug(self, message = None):
        """
        Prints a debug message, if the verbosity level allows for it.

        :returns: Whether debug messages are printed.
        """
        return self._verbosity_printer(2, message)

    def reset_solver_instances(self):
        """
        Resets all solver instances, so that the problem will be reimported and
        solved from scratch.
        """
        for solver in self.solvers.values():
            if solver is not None:
                solver.reset_problem()

    def remove_all_constraints(self):
        """
        Removes all constraints from the problem.

        This function does not remove bounds set directly on variables; use
        :func:`remove_all_variable_bounds <remove_all_variable_bounds>` to do
        so.
        """
        self.numberConeConstraints = 0
        self.numberAffConstraints = 0
        self.numberQuadConstraints = 0
        self.numberSDPConstraints = 0
        self.numberLSEConstraints = 0
        self.numberMetaConstraints = 0
        self.consNumbering = []
        self.groupsOfConstraints = {}
        self.numberConeVars = 0
        self.numberSDPVars = 0
        self.countCons = 0
        self.constraints = []
        self.numberQuadNNZ = 0
        self.numberLSEVars = 0
        if self.objective[0] is not 'find':
            if self.objective[1] is not None:
                expr = self.objective[1]
                if isinstance(expr, QuadExp):
                    self.numberQuadNNZ = expr.nnz()
                if isinstance(expr, LogSumExp):
                    self.numberLSEVars = expr.Exp.size[0] * expr.Exp.size[1]
        self.reset_solver_instances()

    def remove_all_variable_bounds(self):
        """
        Removes all lower and upper bounds from all variables.
        """
        for var in self.variables.values():
            var.bnd._reset()

    def obj_value(self):
        """
        Returns the objective value after the problem was solved.

        :raises: ``AttributeError``, if the problem was not yet solved.
        """
        return self.objective[1].eval()[0]

    def set_objective(self, typ, expr):
        """
        Sets the objective function and optimization direction of the problem.

        :param str typ: Can be either ``'max'``, ``'min'``, or ``'find'``, for a
            maximization, minimization, and feasibility problem, respectively.
        :param expr: The objective function to be minimized or maximized.
            This parameter is ignored if ``typ == 'find'``.
        :type expr: :class:`Expression <picos.expressions.Expression>`
        """
        if typ == 'find':
            self.objective = (typ, None)
            return
        if (isinstance(expr, AffinExp) and expr.size != (1, 1)):
            raise Exception('objective should be scalar')
        if not (isinstance(expr, AffinExp) or isinstance(expr, LogSumExp)
                or isinstance(expr, QuadExp) or isinstance(expr, GeneralFun)):
            raise Exception('unsupported objective')
        if isinstance(self.objective[1], LogSumExp):
            oldexp = self.objective[1]
            self.numberLSEConstraints -= 1
            self.numberLSEVars -= oldexp.Exp.size[0] * oldexp.Exp.size[1]
        if isinstance(self.objective[1], QuadExp):
            oldexp = self.objective[1]
            self.numberQuadConstraints -= 1
            self.numberQuadNNZ -= oldexp.nnz()
        if isinstance(expr, LogSumExp):
            self.numberLSEVars += expr.Exp.size[0] * expr.Exp.size[1]
            self.numberLSEConstraints += 1
        if isinstance(expr, QuadExp):
            self.numberQuadConstraints += 1
            self.numberQuadNNZ += expr.nnz()
        self.objective = (typ, expr)

    def set_var_value(self, name, value, optimalvar=False):
        """
        Sets the :attr:`value <picos.expressions.Expression.value>` of the given
        variable.

        :param str or tuple name: Name of the variable.

        :param value: The value to be set.
        :type value: Anything recognized by :func:`retrieve_matrix
            <picos.tools.retrieve_matrix>`

        :Example:

        >>> prob=picos.Problem()
        >>> x=prob.add_variable('x', 2)
        >>> prob.set_var_value('x', [3,4]) # equivalent to x.value = [3,4]
        >>> abs(x)**2
        <Quadratic Expression: ‖x‖²>
        >>> print(abs(x)**2)
        25.0

        .. note::

            The ``hotstart`` option allows certain solvers to leverage variables
            that were valued manually or by a preceding solution search.
        """
        if isinstance(name, tuple):
            index = name[0]
            name  = name[1]
        else:
            index = None

        try:
            variable = self.variables[name]
        except KeyError:
            raise KeyError("Unknown variable name '{}'.".format(name))

        if index is None:
            variable.value = value

            if optimalvar:
                self.number_solutions = max(self.number_solutions, 1)
        else:
            variable.set_value(value, index = index)

            if optimalvar:
                self.number_solutions = max(self.number_solutions, index + 1)

    def set_all_options_to_default(self):
        """
        Sets all solver options to their default value.
        """
        default_options = {
            'strict_options': False,
            'tol': 1e-8,
            'feastol': None,
            'abstol': None,
            'reltol': None,
            'maxit': None,
            'verbose': 1,
            'allow_license_warnings': True,
            'solver': None,
            'step_sqp': 1,  # undocumented
            'harmonic_steps': 1,  # undocumented
            'noprimals': False,
            'noduals': False,
            'nbsol': None,
            'timelimit': None,
            'acceptable_gap_at_timelimit': None,
            'treememory': None,
            'gaplim': 1e-4,
            'pool_size': None,
            'pool_absgap': None,
            'pool_relgap': None,
            'lp_root_method': None,
            'lp_node_method': None,
            'cplex_params': {},
            'mosek_params': {},
            'gurobi_params': {},
            'scip_params': {},
            'hotstart': False,
            'uboundlimit': None,
            'lboundlimit': None,
            'boundMonitor': False,
            'solve_via_dual': None,
        }

        self._options = NonWritableDict(default_options)

    @property
    def options(self):
        return self._options

    def set_option(self, key, val):
        """
        Sets a single solver option to the given value.

        :param str key: String name of the option, see below for a list.
        :param val: New value for the option.

        The following options are available and are listed with their default
        values.

        * General options common to all solvers:

          * ``strict_options = False`` -- If ``True``, unsupported general
            options will raise an
            :class:`UnsupportedOptionError <picos.solvers.solver.UnsupportedOptionError>`
            exception, instead of printing a warning.

          * ``verbose = 1`` -- Verbosity level.

            * ``-1`` attempts to suppress all output, even errors.
            * ``0`` only outputs warnings and errors.
            * ``1`` generates standard informative output.
            * ``2`` prints all available information for debugging purposes.

          * ``allow_license_warnings = True`` -- Whether solvers are allowed to
            ignore the ``verbose`` option to print licensing related warnings.

            *Using this option to surpress licensing related warnings is done at
            your own legal responsibility.*

          * ``solver = None`` -- Solver to use.

            * ``None`` lets PICOS select a suitable solver for you.
            * ``'cplex'`` for CPLEX.
            * ``'cvxopt'`` for CVXOPT.
            * ``'glpk'`` for GLPK.
            * ``'mosek'`` for MOSEK.
            * ``'gurobi'`` for Gurobi.
            * ``'scip'`` for SCIP (formerly ZIBOpt).
            * ``'smcp'`` for SMCP.

          * ``tol = 1e-8`` -- Relative gap termination tolerance for
            interior-point optimizers (feasibility and complementary slackness).

            *This option is currently ignored by GLPK. SCIP will only lower its
            precision for large values and not increase it for small ones.*

          * ``maxit = None`` -- Maximum number of iterations for simplex or
            interior-point optimizers). *Currently ignored by SCIP.*

          * ``lp_root_method = None`` -- Algorithm used to solve continuous
            linear problems, including the root relaxation of mixed integer
            problems.

            * ``None`` lets PICOS or the solver select it fo you.
            * ``'psimplex'`` for primal Simplex.
            * ``'dsimplex'`` for dual Simplex.
            * ``'interior'`` for the interior point method.

            *This option currently works only with CPLEX, Gurobi and MOSEK. With
            GLPK it works for LPs but not for the MIP root relaxation.*

          * ``lp_node_method = None`` -- Algorithm used to solve subproblems
            at non-root nodes of the branching tree built when solving mixed
            integer programs.

            * ``None`` lets PICOS or the solver select it fo you.
            * ``'psimplex'`` for primal Simplex.
            * ``'dsimplex'`` for dual Simplex.
            * ``'interior'`` for the interior point method.

            *This option currently works only with CPLEX, Gurobi and MOSEK.*

          * ``timelimit = None`` -- Total time limit for the solver, in seconds.
            The default ``None`` means no time limit.

            *This option is not supported by CVXOPT and SMCP*.

          * ``treememory = None`` -- Bound on the memory used by the branch and
            bound tree, in Megabytes.

            *This option currently works only with CPLEX and SCIP.*

          * ``gaplim = 1e-4`` -- For mixed integer problems, the solver returns
            a solution as soon as this value for the relative gap between the
            primal and the dual bound is reached.

          * ``noprimals = False`` -- If ``True``, do not retrieve a primal
            solution from the solver.

          * ``noduals = False`` -- If ``True``, do not retrieve optimal values
            for the dual variables. This can speed up solvers that do not
            produce a dual solution as part of their primal solution process.

          * ``nbsol = None`` -- Maximum number of feasible solution nodes
            visited when solving a mixed integer problem, before returning the
            best one found.

            If you want to obtain all feasible solutions that the solver
            encountered, use ``pool_size`` instead.

          * ``pool_size = None`` -- Maximum number of mixed integer feasible
            solutions returned, instead of just a single one.

            If you merely want to set a limit on the number of feastble solution
            nodes that are visited, use ``nbsol`` instead.

            *This option currently works only with CPLEX.*

          * ``pool_absgap = None`` -- Discards solutions from the solution pool
            as soon as a better solution is found that beats it by the given
            absolute gap tolerance with respect to the objective function.

            *This option currently works only with CPLEX.*

          * ``pool_relgap = None`` -- Discards solutions from the solution pool
            as soon as a better solution is found that beats it by the given
            relative gap tolerance with respect to the objective function.

            *This option currently works only with CPLEX.*

          * ``hotstart = False`` -- If `True`, tells the mixed integer optimizer
            to start from the (partial) solution specified in the variables'
            :attr:`value <picos.expressions.Expression.value>` attributes.

            *This option currently works only with CPLEX, Gurobi and MOSEK.*

          * ``solve_via_dual = None`` -- If set to ``True``, the Lagrangian Dual
            (computed with the function :func:`as_dual <picos.Problem.as_dual>`)
            is passed to the solver, instead of the problem itself. In some
            scenarios this can yield a signficant speed-up. If set to ``None``,
            PICOS chooses automatically whether the problem itself or its dual
            should be passed to the solver.

        * Specific options available for CPLEX:

          * ``cplex_params = {}`` -- A dictionary of
            CPLEX parameters to be set before the CPLEX optimizer is called.

            For example, ``cplex_params = {'mip.limits.cutpasses': 5}`` will
            limit the number of cutting plane passes when solving the root node
            to ``5``.

          * ``uboundlimit = None`` -- Tells CPLEX to stop as soon as an upper
            bound smaller than this value is found.

          * ``lboundlimit = None`` -- Tells CPLEX to stop as soon as a lower
            bound larger than this value is found.

          * ``boundMonitor = True`` -- Tells CPLEX to store information about
            the evolution of the bounds during the solving process. At the end
            of the computation, a list of triples `(time,lowerbound,upperbound)`
            will be provided in the field bounds_monitor` of the dictionary
            returned by :func:`solve <picos.Problem.solve>`.

        * Specific options available for CVXOPT, SMCP and ECOS:

          * ``feastol = None`` -- Feasibility tolerance passed to
            `cvx.solvers.options <http://abel.ee.ucla.edu/cvxopt/userguide/coneprog.html#algorithm-parameters>`_
            If ``None``, then the value of the option ``tol`` is used.

          * ``abstol = None`` -- Absolute tolerance passed to
            `cvx.solvers.options <http://abel.ee.ucla.edu/cvxopt/userguide/coneprog.html#algorithm-parameters>`_
            If ``None``, then the value of the option ``tol`` is used.

          * ``reltol = None`` -- relative tolerance passed to
            `cvx.solvers.options <http://abel.ee.ucla.edu/cvxopt/userguide/coneprog.html#algorithm-parameters>`_
            If ``None``, then **ten times** the value of the option ``tol`` is
            used.

        * Specific options available for Gurobi:

          * ``gurobi_params = {}`` -- A dictionary of
            `Gurobi parameters <http://www.gurobi.com/documentation/5.0/reference-manual/node653>`_
            to be set before the Gurobi optimizer is called.

            For example, ``gurobi_params = {'NodeLimit': 25}`` limits the
            number of nodes visited by the MIP optimizer to 25.

        * Specific options available for MOSEK:

          * ``mosek_params = {}`` -- A dictionary of
            `MOSEK Fusion API parameters <http://docs.mosek.com/8.1/pythonfusion/parameters.html#doc-all-parameter-list>`_
            to be set before the MOSEK optimizer is called.

        * Specific options available for SCIP:

          * ``scip_params = {}`` -- A dictionary of
            `SCIP parameters <http://scip.zib.de/doc-2.0.2/html/PARAMETERS.html>`_
            to be set before the SCIP optimizer is called.

            For example, ``scip_params = {'lp/threads': 4}`` sets the number of
            threads to solve LPs with to ``4``.

        .. note::
            Options can also be passed as a parameter sequence of the form
            ``key = value`` when the :class:`Problem <picos.Problem>` is created
            or later to the function :func:`solve <picos.Problem.solve>`.
        """
        if key not in self.options:
            raise AttributeError('unknown option key :' + str(key))
        self.options._set(key, val)
        if key == 'verbose' and isinstance(val, bool):
            self.options._set('verbose', int(val))

    def update_options(self, **options):
        """
        Sets multiple solver options at once.

        :param options: A parameter sequence of the form ``key = value``.

        For a list of available options and their default values, see the
        documentation of :func:`set_option <picos.Problem.set_option>`.
        """
        for k in options.keys():
            self.set_option(k, options[k])

    def add_variable(self, name, size=1, vtype='continuous', lower=None,
        upper=None):
        """
        Adds a variable to the problem and returns it for use in constraints.

        :param str name: The name of the variable.

        :param size: The size of the variable.
            Can be either

            * an ``int`` :math:`n`, in which case the variable is an
              :math:`n`-dimensional vector,
            * or a ``tuple`` :math:`(n, m)`, in which case the variable is a
              :math:`n × m` matrix.
        :type size: int or tuple

        :param str vtype: Domain of the variable.
            Can be any of

            * ``'continuous'`` -- real valued,
            * ``'binary'`` -- either zero or one,
            * ``'integer'`` -- integer valued,
            * ``'symmetric'`` -- symmetric matrix,
            * ``'antisym'`` -- antisymmetric matrix,
            * ``'complex'`` -- complex matrix,
            * ``'hermitian'`` -- complex hermitian matrix,
            * ``'semicont'`` -- zero or real valued and satisfying its bounds
              (supported by CPLEX and Gurobi only), or
            * ``'semiint'`` -- zero or integer valued and satisfying its bounds
              (supported by CPLEX and Gurobi only).

        :param lower: A lower bound for the variable.

            Can be either a vector or matrix of the same size as the
            variable or a scalar that is then broadcasted so that all
            elements of the variable have the same lower bound.
        :type lower: anything recognized by
            :func:`retrieve_matrix <picos.tools.retrieve_matrix>`

        :param upper: An upper bound for the variable.

            Can be either a vector or matrix of the same size as the
            variable or a scalar that is then broadcasted so that all
            elements of the variable have the same upper bound.
        :type upper: anything recognized by
            :func:`retrieve_matrix <picos.tools.retrieve_matrix>`

        :returns: A :class:`Variable <picos.expressions.Variable>` instance.

        :Example:

        >>> prob=picos.Problem()
        >>> x=prob.add_variable('x',3)
        >>> x
        <3×1 Continuous Variable: x>
        """
        # TODO: tutorial examples with bounds and sparse bounds

        if name in self.variables:
            raise Exception('this variable already exists')
        if isinstance(size, INTEGER_TYPES):
            size = (int(size), 1)
        else:
            size = tuple(int(x) for x in size)
        if len(size) == 1:
            size = (int(size[0]), 1)

        lisname = None
        if '[' in name and ']' in name:  # list or dict of variables
            lisname = name[:name.index('[')]
            ind = name[name.index('[') + 1:name.index(']')]
            if lisname in self.listOfVars:
                oldn = self.listOfVars[lisname]['numvars']
                self.listOfVars[lisname]['numvars'] += 1
                if size != self.listOfVars[lisname]['size']:
                    self.listOfVars[lisname]['size'] = 'different'
                if vtype != self.listOfVars[lisname]['vtype']:
                    self.listOfVars[lisname]['vtype'] = 'different'
                if self.listOfVars[lisname][
                        'type'] == 'list' and ind != str(oldn):
                    self.listOfVars[lisname]['type'] = 'dict'
            else:
                self.listOfVars[lisname] = {
                    'numvars': 1, 'size': size, 'vtype': vtype}
                if ind == '0':
                    self.listOfVars[lisname]['type'] = 'list'
                else:
                    self.listOfVars[lisname]['type'] = 'dict'

        countvar = self.countVar
        numbervar = self.numberOfVars

        if vtype in ('symmetric', 'hermitian'):
            if size[0] != size[1]:
                raise ValueError('symmetric variables must be square')
            s0 = size[0]
            self.numberOfVars += s0 * (s0 + 1) // 2
        elif vtype == 'antisym':
            if size[0] != size[1]:
                raise ValueError('antisymmetric variables must be square')
            s0 = size[0]
            if s0 <= 1:
                raise ValueError('dimension too small')
            if not(lower is None and upper is None):
                raise ValueError(
                    'Variable bounds are not supported for antisymmetric '
                    'variables. Add a constraint instead.')
            idmat = svecm1_identity(vtype, (s0, s0))
            Xv = self.add_variable(name + '_utri',
                                   (s0 * (s0 - 1)) // 2,
                                   vtype='continuous',
                                   lower=None,
                                   upper=None)
            exp = idmat * Xv
            exp.string = name
            exp._size = (s0, s0)
            return exp

        elif vtype == 'complex':
            l = None
            lr, li, ur, ui = None, None, None, None
            if l:
                l = retrieve_matrix(l, size)[0]
                if l.typecode == 'z':
                    lr = l.real()
                    li = l.imag()
                else:
                    lr = l
                    li = None
            u = None
            if u:
                u = retrieve_matrix(u, size)[0]
                if u.typecode == 'z':
                    ur = u.real()
                    ui = u.imag()
                else:
                    ur = u
                    ui = None
            Zr = self.add_variable(
                name + '_RE',
                size,
                vtype='continuous',
                lower=lr,
                upper=ur)
            Zi = self.add_variable(
                name + '_IM',
                size,
                vtype='continuous',
                lower=li,
                upper=ui)
            exp = Zr + 1j * Zi
            exp.string = name
            return exp
        else:
            self.numberOfVars += size[0] * size[1]
        self.varNames.append(name)
        self.countVar += 1

        # svec operation
        idmat = svecm1_identity(vtype, size)

        self.variables[name] = Variable(self, name, size, countvar, numbervar,
            vtype=vtype, lower=lower, upper=upper)
        if lisname is not None:
            if 'bnd' in self.listOfVars[lisname]:
                bndtext = self.listOfVars[lisname]['bnd']
                thisbnd = self.variables[name]._bndtext
                if bndtext != thisbnd:
                    self.listOfVars[lisname]['bnd'] = ', some bounds'
            else:
                self.listOfVars[lisname]['bnd'] = self.variables[name]._bndtext

        return self.variables[name]

    def remove_variable(self, name):
        """
        Removes a variable from the problem.

        :param str name: Name of the variable to remove.

        .. warning::
            This method does not check if some constraint still involves the
            variable to be removed.
        """
        if '[' in name and ']' in name:  # list or dict of variables
            lisname = name[:name.index('[')]
            if lisname in self.listOfVars:
                varattr = self.listOfVars[lisname]
                varattr['numvars'] -= 1
                if varattr['numvars'] == 0:
                    del self.listOfVars[lisname]  # empty list of vars
        if name not in self.variables.keys():
            raise KeyError(
                'Variable {} does not exist. '
                'Maybe you tried to remove some item x[i] of the variable x?'
                .format(name))
        self.countVar -= 1
        var = self.variables[name]
        sz = var.size
        self.numberOfVars -= sz[0] * sz[1]
        self.varNames.remove(name)
        del self.variables[name]
        # FIXME: The following two lines prevent solvers from being updated.
        #        In particular, CPLEX and Gurobi now support variable removal.
        # TODO: Find out if there is any need to recompute the indices. Without
        #       the recomputation, it would seem safe to not reset the solvers.
        self._recompute_start_end_indices()
        self.reset_solver_instances()

    def _recompute_start_end_indices(self):
        ind = 0
        for nam in self.varNames:
            var = self.variables[nam]
            var._startIndex = ind
            if var.vtype in ('symmetric',):
                ind += int((var.size[0] * (var.size[0] + 1)) // 2)
            else:
                ind += var.size[0] * var.size[1]
            var._endIndex = ind

    def copy(self):
        """
        Creates an independent copy of the problem, using new variables.

        .. note ::
            Your existing variable, constraint, and metaconstraint references
            will refer to the original variables, so you cannot query these for
            solution details after solving the copy. Access the copy's
            constraints and variables instead.
        """
        import copy

        newProblem = Problem()
        newVars    = {}

        # Duplicate the variables.
        for _, var in sorted(
            [(var.startIndex, var) for var in self.variables.values()]):
            newVar = newProblem.add_variable(var.name, var.size, var.vtype)
            newVar._bnd = copy.deepcopy(var.bnd)
            # The origin will be adjusted to a copy of the metaconstraint later.
            newVar.origin = var.origin
            newVars[var.name] = newVar

        # Make copies of constraints on top of the new variables.
        newCons = {}
        for constraint in self.constraints:
            newConstraint = constraint.copy_with_new_vars(newVars)
            newProblem.add_constraint(newConstraint, constraint.name)
            newCons[constraint] = newConstraint

        # Make copies of all metaconstraints being referenced by either
        # constraints or variables, on top of the new variables.
        metaMap = {None: None}
        for obj in newProblem.constraints + list(newProblem.variables.values()):
            meta = obj.origin
            if meta in metaMap:
                obj.origin = metaMap[meta]
            else:
                newMeta = meta.copy_with_new_vars(newVars, newCons)
                metaMap[meta] = obj.origin = newMeta

        # Make a copy of the objective on top of the new variables.
        newObjective = copy_exp_to_new_vars(self.objective[1], newVars)
        newProblem.set_objective(self.objective[0], newObjective)

        # Duplicate the problem metadata.
        newProblem.consNumbering = copy.deepcopy(self.consNumbering)
        newProblem.groupsOfConstraints = copy.deepcopy(self.groupsOfConstraints)
        newProblem._options = NonWritableDict(self.options)

        return newProblem

    def add_constraint(self, constraint, key=None):
        """Adds a constraint to the problem.

        :param constraint: The constraint to be added.
        :type constraint: :class:`Constraint <picos.constraints.Constraint>`
        :param str key: Optional name of the constraint.

        :returns: The constraint that was added to the problem, which may be a
            :class:`MetaConstraint <picos.constraints.MetaConstraint>` that contains further
            references to auxiliary constraints that were also added, as well as
            potentially references to new auxiliary variables.
        """
        # Add auxiliary constraints and auxiliary variables for metaconstraints.
        if constraint.is_meta():
            # Add auxiliary variables.
            for auxVarTmpName, auxVar in \
                constraint.tmpProblem.variables.items():
                # Make room for the new variable by adding a named dummy
                # variable of proper size.
                auxVarName = "{}{}_{}".format(constraint.prefix,
                    self.numberMetaConstraints, auxVarTmpName)
                self.add_variable(auxVarName, auxVar.size, auxVar.vtype)

                # Move the temporary auxiliary variable to this problem,
                # replacing its name and indices.
                auxVar.name = auxVarName
                auxVar._startIndex = self.variables[auxVarName].startIndex
                auxVar._endIndex   = self.variables[auxVarName].endIndex
                constraint.auxVars[auxVarName] = auxVar
            self.variables.update(constraint.auxVars)

            # Add auxiliary constraints.
            # Note that in theory, this can add additional auxiliary variables
            # if a metaconstraint is composed of metaconstraints itself.
            newConsStartIndex = self.countCons
            constraint.auxCons.extend(self.add_list_of_constraints(
                constraint.tmpProblem.constraints, key=key))

            assert constraint.auxCons, \
                "A metaconstraint does not add any constraints."

            # Register problem with the metaconstraint and vice versa.
            constraint.problem = self
            self.numberMetaConstraints += 1
            constraintGroup = self.groupsOfConstraints[newConsStartIndex]
            constraintGroup[1] = constraint.constring() + '\n'

            # Register the metaconstraint also with the auxiliary constraints
            # and variables.
            for auxCon in constraint.auxCons:
                auxCon.origin = constraint
            for auxVar in constraint.auxVars.values():
                auxVar.origin = constraint

            # Delete the temporary problem.
            # NOTE: Due to cyclic references between Variable and Problem and
            #       subject to the Python interpreter used, this can only get
            #       cleaned up if neither class defines __del__.
            del constraint.tmpProblem

            if self.options["verbose"] >= 2:
                if constraint.auxVars:
                    print("Adding auxiliary variables for {}: {}."
                        .format(constraint, constraint.auxVars))
                if len(constraint.auxCons) == 1:
                    print("Replacing {} with {}."
                        .format(constraint, constraint.auxCons[0]))
                elif len(constraint.auxCons) >= 2:
                    print("Replacing {} by {} auxiliary constraints: {}."
                        .format(constraint, len(constraint.auxCons),
                        constraint.auxCons))

            # Return only the metaconstraint, which can be queried for further
            # constraints and variables that were added.
            return constraint

        # Name the constraint.
        constraint.name = key
        if key is not None:
            self.longestkey = max(self.longestkey, len(key))

        # Register the problem with the constraint and vice versa.
        constraint.problem = self
        self.constraints.append(constraint)
        self.consNumbering.append(self.countCons)
        self.countCons += 1

        # Look for complex coefficients or constant.
        # FIXME: The lines "exp.factors[variable] = factor.real()" and
        #        "exp.constant = exp.constant.real()" may or may not be executed
        #        depending on iteration order, due to the break statements.
        # TODO: I'm not yet sure if these lines are necessary or even a good
        #       idea, given that the typecode stays "z".
        found = False
        for exp in constraint.expressions():
            if isinstance(exp, QuadExp):
                # A QuadExp should not contain complex coefficients.
                continue

            if not isinstance(exp, AffinExp):
                exp = exp.Exp

            dct_facts = exp.factors

            # Look for complex coefficients.
            for variable, factor in exp.factors.items():
                if factor.typecode == 'z':
                    if factor.imag():
                        self._complex = True
                        found = True
                        # FIXME: See above.
                        break
                    else:
                        exp.factors[variable] = factor.real()

            # Look for a complex constant.
            if exp.constant is not None and exp.constant.typecode == 'z':
                if exp.constant.imag():
                    self._complex = True
                    found = True
                else:
                    exp.constant = exp.constant.real()

            if found:
                # FIXME: See above.
                break

        # Count (scalar) constraints by type.
        if isinstance(constraint, AffineConstraint):
            self.numberAffConstraints += len(constraint.lhs)
        elif isinstance(constraint, SOCConstraint):
            self.numberConeConstraints += 1
            self.numberConeVars += len(constraint.ne) + 1
        elif isinstance(constraint, RSOCConstraint):
            self.numberConeConstraints += 1
            self.numberConeVars += len(constraint.ne) + 2
        elif isinstance(constraint, QuadConstraint):
            self.numberQuadConstraints += 1
            self.numberQuadNNZ += constraint.le0.nnz()
        elif isinstance(constraint, LMIConstraint):
            self.numberSDPConstraints += 1
            n = constraint.lhs.size[0]
            self.numberSDPVars += (n * (n + 1)) // 2

            # If the constraint simply imposes positive semidefiniteness on a
            # single variable, flag the variable accordingly.
            if constraint.semidefVar is not None:
                constraint.semidefVar.semiDef += 1
        elif isinstance(constraint, LSEConstraint):
            self.numberLSEConstraints += 1
            self.numberLSEVars += len(constraint.le0.Exp)

        return constraint

    def add_list_of_constraints(self, lst, it=None, indices=None, key=None):
        """
        Adds a list of constraints to the problem, enabling the use of
        Python list comprehensions (see the example below).

        :param list lst: A list of :class:`constraints <picos.constraints.Constraint>`.
        :param it: DEPRECATED
        :param indices: DEPRECATED
        :param str key: A name describing the list of constraints.

        :returns: A list of all constraints that were added.

        :Example:

        >>> import picos as pic
        >>> import cvxopt as cvx
        >>> from pprint import pprint
        >>> prob=pic.Problem()
        >>> x=[prob.add_variable('x[{0}]'.format(i),2) for i in range(5)]
        >>> pprint(x)
        [<2×1 Continuous Variable: x[0]>,
         <2×1 Continuous Variable: x[1]>,
         <2×1 Continuous Variable: x[2]>,
         <2×1 Continuous Variable: x[3]>,
         <2×1 Continuous Variable: x[4]>]
        >>> y=prob.add_variable('y',5)
        >>> IJ=[(1,2),(2,0),(4,2)]
        >>> w={}
        >>> for ij in IJ:
        ...         w[ij]=prob.add_variable('w[{},{}]'.format(*ij),3)
        ...
        >>> u=pic.new_param('u',cvx.matrix([2,5]))
        >>> C1=prob.add_list_of_constraints([u.T*x[i] < y[i] for i in range(5)])
        >>> C2=prob.add_list_of_constraints([abs(w[i,j])<y[j] for (i,j) in IJ])
        >>> C3=prob.add_list_of_constraints([y[t] > y[t+1] for t in range(4)])
        >>> print(prob) #doctest: +NORMALIZE_WHITESPACE
        ---------------------
        optimization problem (SOCP):
        24 variables, 9 affine constraints, 12 vars in 3 SO cones
        <BLANKLINE>
        w   : dict of 3 variables, (3, 1), continuous
        x   : list of 5 variables, (2, 1), continuous
        y   : (5, 1), continuous
        <BLANKLINE>
            find vars
        such that
          uᵀ·x[i] ≤ y[i] ∀ i ∈ [0…4]
          ‖w[i,j]‖ ≤ y[j] ∀ (i,j) ∈ zip([1,2,4],[2,0,2])
          y[i] ≥ y[i+1] ∀ i ∈ [0…3]
        ---------------------
        """
        if not lst:
            return []

        firstCons = self.countCons
        thisconsnums = []

        newCons = []
        for constraint in lst:
            newCons.append(self.add_constraint(constraint))
            cstnum = self.consNumbering.pop()
            thisconsnums.append(cstnum)

        self.consNumbering.append(thisconsnums)
        lastCons = self.countCons - 1

        key = "" if key is None else key
        self.longestkey = max(self.longestkey, len(key))

        if len(lst) is 1:
            string = str(lst[0])
        else:
            try:
                template, data = parameterized_string([str(con) for con in lst])
            except ValueError:
                string = "[{} constraints (1st: {})]".format(len(lst), lst[0])
            else:
                string = glyphs.forall(template, data)

        self.groupsOfConstraints[firstCons] = [lastCons, string + "\n", key]

        # Remove unwanted subgroup of constraints (which are added when we add
        # a list of metaconstraints).
        goctodel = []
        for goc in self.groupsOfConstraints:
            if goc > firstCons and goc <= lastCons:
                goctodel.append(goc)
        for goc in goctodel:
            del self.groupsOfConstraints[goc]

        return newCons

    def get_valued_variable(self, name):
        """
        Returns the value or values of a variable or of a collection of
        variables with a common base name.

        :param str name: Name of a single variable or of a collection of
            variables (see :func:`get_variable` on how to specify collections).

        :raises: An exception if any of the variables is not valued, in
            particular when the problem was not yet solved.

        :returns: A :func:`CVXOPT matrix <cvxopt:cvxopt.matrix>`, if ``name``
            refers to a single variable, or a list or a dictionary thereof, if
            the collection of variables specified by ``name`` is a list or a
            dictionary, respectively.
        """
        exp = self.get_variable(name)
        if isinstance(exp, list):
            for i in range(len(exp)):
                exp[i] = exp[i].eval()
        elif isinstance(exp, dict):
            for i in exp:
                exp[i] = exp[i].eval()
        else:
            exp = exp.eval()
        return exp

    def get_variable(self, name):
        """
        Returns a single variable with the given name or a list or dictionary of
        variables with the given name as a common base name. In the latter case
        the variables must be named ``name[index]`` or ``name[key]`` with
        ``index`` taken from a set of integer strings and ``key`` taken from a
        set of arbitrary strings.

        :param str name: Name of a single variable or of a collection of
            variables.

        :returns: A :class:`PICOS variable <picos.expressions.Variable>`, if ``name``
            refers to a single variable, or a list or a dictionary thereof, if
            the collection of variables specified by ``name`` is a list or a
            dictionary, respectively.
        """
        var = name
        if var in self.listOfVars.keys():
            if self.listOfVars[var]['type'] == 'dict':
                rvar = {}
            else:
                rvar = [0] * self.listOfVars[var]['numvars']
            seenKeys = []
            for ind in [
                vname[
                    len(var) +
                    1:-
                    1] for vname in self.variables.keys() if (
                    vname[
                        :len(var)] == var and vname[
                    len(var)] == '[')]:
                if ind.isdigit():
                    key = int(ind)
                    if key not in seenKeys:
                        seenKeys.append(key)
                    else:
                        key = ind
                elif ',' in ind:
                    isplit = ind.split(',')
                    if isplit[0].startswith('('):
                        isplit[0] = isplit[0][1:]
                    if isplit[-1].endswith(')'):
                        isplit[-1] = isplit[-1][:-1]
                    if all([i.isdigit() for i in isplit]):
                        key = tuple([int(i) for i in isplit])
                        if key not in seenKeys:
                            seenKeys.append(key)
                        else:
                            key = ind
                    else:
                        key = ind
                else:
                    try:
                        key = float(ind)
                    except ValueError:
                        key = ind
                rvar[key] = self.variables[var + '[' + ind + ']']
            return rvar
        elif var + '_IM' in self.variables and var + '_RE' in self.variables:
            # complex
            exp = self.variables[var + '_RE'] + \
                1j * self.variables[var + '_IM']
            exp.string = var
            return exp
        elif var not in self.variables and var + '_utri' in self.variables:
            # antisym
            vu = self.variables[var + '_utri']
            n = int((1 + (1 + vu.size[0] * 8)**0.5) / 2.)
            idasym = svecm1_identity('antisym', (n, n))
            exp = idasym * vu
            exp.string = var
            exp._size = (n, n)
            return exp
        elif var in self.variables:
            return self.variables[var]
        else:
            raise Exception('no such variable')

    def get_constraint(self, ind):
        u"""
        Returns a constraint of the problem, given its index.

        :param ind: There are three ways to index a constraint:

           * If ``ind`` is an ``int`` :math:`n`, then the :math:`n`-th
             constraint (starting from :math:`0`) is returned, where constraints
             are counted in the order in which they where passed to the problem.
           * if ``ind`` is a ``tuple`` :math:`(k, i)`, then the :math:`i`-th
             constraint from the :math:`k`-th group of constraints is returned
             (both starting from :math:`0`). Here *group of constraints* refers
             to a list of constraints added together via
             :func:`add_list_of_constraints <add_list_of_constraints>`.
           * If ``ind`` is a tuple :math:`(k,)` of length :math:`1`, then the
             :math:`k`-th group of constraints is returned as a list.
        :type ind: int or tuple

        :returns: A :class:`constraint <picos.constraints.Constraint>` or a list thereof.

        :Example:

        >>> import picos as pic
        >>> import cvxopt as cvx
        >>> from pprint import pprint
        >>> prob=pic.Problem()
        >>> x=[prob.add_variable('x[{0}]'.format(i),2) for i in range(5)]
        >>> y=prob.add_variable('y',5)
        >>> Cx=prob.add_list_of_constraints([(1|x[i]) < y[i] for i in range(5)])
        >>> Cy=prob.add_constraint(y>0)
        >>> print(prob) #doctest: +NORMALIZE_WHITESPACE
        ---------------------
        optimization problem (LP):
        15 variables, 10 affine constraints
        <BLANKLINE>
        x   : list of 5 variables, (2, 1), continuous
        y   : (5, 1), continuous
        <BLANKLINE>
            find vars
        such that
          ⟨[1], x[i]⟩ ≤ y[i] ∀ i ∈ [0…4]
          y ≥ 0
        ---------------------
        >>> # Retrieve the 3nd constraint (counted from 0):
        >>> prob.get_constraint(1)
        <1×1 Affine Constraint: ⟨[1], x[1]⟩ ≤ y[1]>
        >>> # Retrieve the 4th consraint from the 1st group:
        >>> prob.get_constraint((0,3))
        <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>
        >>> # Retrieve the unique constraint of the 2nd 'group':
        >>> prob.get_constraint((1,))
        <5×1 Affine Constraint: y ≥ 0>
        >>> # Retrieve the whole 1st group of constraints:
        >>> pprint(prob.get_constraint((0,)))
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[1]⟩ ≤ y[1]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <1×1 Affine Constraint: ⟨[1], x[4]⟩ ≤ y[4]>]
        """
        indtuple = ind
        if isinstance(indtuple, int):
            return self.constraints[indtuple]
        lsind = self.consNumbering
        if not(isinstance(indtuple, tuple) or isinstance(indtuple, list)) or (
                len(indtuple) == 0):
            raise Exception('ind must be an int or a nonempty tuple')

        for k in indtuple:
            if not isinstance(lsind, list):
                if k == 0:
                    break
                else:
                    raise Exception('too many indices')
            if k >= len(lsind):
                raise Exception('index is too large')
            lsind = lsind[k]

        if isinstance(lsind, list):
                # flatten for the case where it is still a list of list
            return [self.constraints[i] for i in flatten(lsind)]
        return self.constraints[lsind]

    # FIXME: Auxiliary variables are not deleted along with metaconstraints.
    # TODO: The method contains redundant code, refactor it.
    def remove_constraint(self, ind):
        """
        Deletes a constraint from the problem.

        :param ind: There are three ways to index a constraint:

           * If ``ind`` is an ``int`` :math:`n`, then the :math:`n`-th
             constraint (starting from :math:`0`) is deleted, where constraints
             are counted in the order in which they where passed to the problem.
           * if ``ind`` is a ``tuple`` :math:`(k, i)`, then the :math:`i`-th
             constraint from the :math:`k`-th group of constraints is deleted
             (both starting from :math:`0`). Here *group of constraints* refers
             to a list of constraints added together via
             :func:`add_list_of_constraints <add_list_of_constraints>`.
           * If ``ind`` is a tuple :math:`(k,)` of length :math:`1`, then the
             whole :math:`k`-th group of constraints is deleted.
        :type ind: int or tuple

        :Example:

        >>> import picos as pic
        >>> import cvxopt as cvx
        >>> from pprint import pprint
        >>> prob=pic.Problem()
        >>> x=[prob.add_variable('x[{0}]'.format(i),2) for i in range(4)]
        >>> y=prob.add_variable('y',4)
        >>> Cxy=prob.add_list_of_constraints([(1|x[i])<y[i] for i in range(4)])
        >>> Cy=prob.add_constraint(y>0)
        >>> Cx0to2=prob.add_list_of_constraints([x[i]<2 for i in range(3)])
        >>> Cx3=prob.add_constraint(x[3]<1)
        >>> pprint(prob.constraints) #doctest: +NORMALIZE_WHITESPACE
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[1]⟩ ≤ y[1]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <4×1 Affine Constraint: y ≥ 0>,
         <2×1 Affine Constraint: x[0] ≤ [2]>,
         <2×1 Affine Constraint: x[1] ≤ [2]>,
         <2×1 Affine Constraint: x[2] ≤ [2]>,
         <2×1 Affine Constraint: x[3] ≤ [1]>]
        >>> # Delete the 2nd constraint (counted from 0):
        >>> prob.remove_constraint(1)
        >>> pprint(prob.constraints) #doctest: +NORMALIZE_WHITESPACE
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <4×1 Affine Constraint: y ≥ 0>,
         <2×1 Affine Constraint: x[0] ≤ [2]>,
         <2×1 Affine Constraint: x[1] ≤ [2]>,
         <2×1 Affine Constraint: x[2] ≤ [2]>,
         <2×1 Affine Constraint: x[3] ≤ [1]>]
        >>> # Delete the 2nd group of constraints, i.e. the constraint y > 0:
        >>> prob.remove_constraint((1,))
        >>> pprint(prob.constraints) #doctest: +NORMALIZE_WHITESPACE
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <2×1 Affine Constraint: x[0] ≤ [2]>,
         <2×1 Affine Constraint: x[1] ≤ [2]>,
         <2×1 Affine Constraint: x[2] ≤ [2]>,
         <2×1 Affine Constraint: x[3] ≤ [1]>]
        >>> # Delete the 3rd remaining group of constraints, i.e. x[3] < [1]:
        >>> prob.remove_constraint((2,))
        >>> pprint(prob.constraints) #doctest: +NORMALIZE_WHITESPACE
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <2×1 Affine Constraint: x[0] ≤ [2]>,
         <2×1 Affine Constraint: x[1] ≤ [2]>,
         <2×1 Affine Constraint: x[2] ≤ [2]>]
        >>> # Delete 2nd constraint of the 2nd remaining group, i.e. x[1] < |2|:
        >>> prob.remove_constraint((1,1))
        >>> pprint(prob.constraints) #doctest: +NORMALIZE_WHITESPACE
        [<1×1 Affine Constraint: ⟨[1], x[0]⟩ ≤ y[0]>,
         <1×1 Affine Constraint: ⟨[1], x[2]⟩ ≤ y[2]>,
         <1×1 Affine Constraint: ⟨[1], x[3]⟩ ≤ y[3]>,
         <2×1 Affine Constraint: x[0] ≤ [2]>,
         <2×1 Affine Constraint: x[2] ≤ [2]>]
        """
        if isinstance(ind, int):  # constraint given with its "raw index"
            constraint = self.constraints[ind]

            # Count down (scalar) constraints by type.
            if isinstance(constraint, AffineConstraint):
                self.numberAffConstraints -= len(constraint)
            elif isinstance(constraint, SOCConstraint):
                self.numberConeConstraints -= 1
                self.numberConeVars -= len(constraint)
            elif isinstance(constraint, RSOCConstraint):
                self.numberConeConstraints -= 1
                self.numberConeVars -= len(constraint)
            elif isinstance(constraint, QuadConstraint):
                self.numberQuadConstraints -= 1
                self.numberQuadNNZ -= constraint.le0.nnz()
            elif isinstance(constraint, LMIConstraint):
                self.numberSDPConstraints -= 1
                n = constraint.size[0]
                self.numberSDPVars -= (n * (n + 1)) // 2

                if constraint.semidefVar:
                    constraint.semidefVar.semiDef -= 1
            elif isinstance(constraint, LSEConstraint):
                self.numberLSEConstraints -= 1
                self.numberLSEVars -= len(constraint.le0.Exp)

            constraint.original_index = ind

            self._deleted_constraints.append(constraint)
            del self.constraints[ind]
            self.countCons -= 1
            if ind in self.consNumbering:  # single added constraint
                self.consNumbering.remove(ind)
                start = ind
                self.consNumbering = offset_in_lil(self.consNumbering, 1, ind)
            else:  # a constraint within a group of constraints
                for i, l in enumerate(self.consNumbering):
                    if ind in flatten([l]):
                        l0 = l[0]
                        while isinstance(l0, list):
                            l0 = l0[0]
                        start = l0
                        remove_in_lil(self.consNumbering, ind)

                self.consNumbering = offset_in_lil(self.consNumbering, 1, ind)
                goc = self.groupsOfConstraints[start]
                self.groupsOfConstraints[start] = [goc[0] - 1,
                                                   goc[1][:-1] + '{-1cons}\n',
                                                   goc[2]]
                if goc[0] == start:
                    del self.groupsOfConstraints[start]

            # offset in subsequent goc
            for stidx in list(self.groupsOfConstraints.keys()):
                if stidx > start:
                    goc = self.groupsOfConstraints[stidx]
                    del self.groupsOfConstraints[stidx]
                    goc[0] = goc[0] - 1
                    self.groupsOfConstraints[stidx - 1] = goc

            return

        indtuple = ind
        lsind = self.consNumbering
        for k in indtuple:
            if not isinstance(lsind, list):
                if k == 0:
                    break
                else:
                    raise Exception('too many indices')
            if k >= len(lsind):
                raise Exception('index is too large')
            lsind = lsind[k]

        # now, lsind must be the index or list of indices to remove
        if isinstance(lsind, list):  # a list of constraints
            # we flatten lsind for the case where it is still a list of lists
            lsind_top = lsind
            lsind = list(flatten(lsind))

            for ind in reversed(lsind):
                constraint = self.constraints[ind]

                # Count down (scalar) constraints by type.
                if isinstance(constraint, AffineConstraint):
                    self.numberAffConstraints -= len(constraint)
                elif isinstance(constraint, SOCConstraint):
                    self.numberConeConstraints -= 1
                    self.numberConeVars -= len(constraint)
                elif isinstance(constraint, RSOCConstraint):
                    self.numberConeConstraints -= 1
                    self.numberConeVars -= len(constraint)
                elif isinstance(constraint, QuadConstraint):
                    self.numberQuadConstraints -= 1
                    self.numberQuadNNZ -= constraint.le0.nnz()
                elif isinstance(constraint, LMIConstraint):
                    self.numberSDPConstraints -= 1
                    n = constraint.size[0]
                    self.numberSDPVars -= (n * (n + 1)) // 2

                    if constraint.semidefVar:
                        constraint.semidefVar.semiDef -= 1
                elif isinstance(constraint, LSEConstraint):
                    self.numberLSEConstraints -= 1
                    self.numberLSEVars -= len(constraint.le0.Exp)

                del self.constraints[ind]

            self.countCons -= len(lsind)
            remove_in_lil(self.consNumbering, lsind_top)
            self.consNumbering = offset_in_lil(
                self.consNumbering, len(lsind), lsind[0])
            # update this group of constraints
            for start, goc in self.groupsOfConstraints.items():
                if lsind[0] >= start and lsind[0] <= goc[0]:
                    break

            self.groupsOfConstraints[start] = [
                goc[0] - len(lsind),
                goc[1][:-1] + '{-%dcons}\n' % len(lsind),
                goc[2]]
            if self.groupsOfConstraints[start][0] < start:
                del self.groupsOfConstraints[start]
            # offset in subsequent goc
            oldkeys = self.groupsOfConstraints.keys()
            for stidx in oldkeys:
                if stidx > start:
                    goc = self.groupsOfConstraints[stidx]
                    del self.groupsOfConstraints[stidx]
                    goc[0] = goc[0] - len(lsind)
                    self.groupsOfConstraints[stidx - len(lsind)] = goc
        elif isinstance(lsind, int):
            self.remove_constraint(lsind)

    def _eval_all(self):
        """
        Returns a big vector of all variable values in the order induced by
        sorted(self.variables.keys()).
        """
        xx = cvx.matrix([], (0, 1))
        for v in sorted(self.variables.keys()):
            xx = cvx.matrix([xx, self.variables[v].valueAsMatrix[:]])
        return xx

    def check_current_value_feasibility(self, tol=1e-5, inttol=1e-3):
        """
        Checks whether all variables that appear in constraints are valued and
        satisfy the constraints up to the given tolerance. In other words,
        checks whether the variables are valued to form a feasible solution.

        :param float tol: Largest tolerated absolute violation of a constraint.
            If ``None``, the ``fesatol`` or ``tol`` solver option is used.
        :param float inttol: Largest tolerated absolute violation of integrality
            of an integral variable.

        :returns: A tuple ``(feasible, violation)`` where ``feasible`` is a bool
            stating whether the solution is feasible and ``violation`` is either
            ``None``, if ``feasible == True``, or the amount of violation,
            otherwise.
        """
        if tol is None:
            if not(self.options['feastol'] is None):
                tol = self.options['feastol']
            else:
                tol = self.options['tol']
        for cs in self.constraints:
            sl = cs.slack
            if not(isinstance(sl, cvx.matrix) or isinstance(sl, cvx.spmatrix)):
                sl = cvx.matrix(sl)
            if isinstance(cs, LMIConstraint):
                # check symmetry
                if min(sl - sl.T) < -tol:
                    return (False, -min(sl - sl.T))
                if min(sl.T - sl) < -tol:
                    return (False, -min(sl.T - sl))
                # check positive semidefiniteness
                if isinstance(sl, cvx.spmatrix):
                    sl = cvx.matrix(sl)
                sl = np.array(sl)
                eg = np.linalg.eigvalsh(sl)
                if min(eg) < -tol:
                    return (False, -float(min(eg)))
            else:
                if min(sl) < -tol:
                    return (False, -float(min(sl)))
        # integer feasibility
        if not(self.is_continuous()):
            for vnam, v in self.variables.items():
                if v.vtype in ('binary', 'integer'):
                    sl = v.valueAsMatrix
                    dsl = [min(s - int(s), int(s) + 1 - s) for s in sl]
                    if max(dsl) > inttol:
                        return (False, max(dsl))

        # so OK, it's feasible
        return (True, None)

    def is_continuous(self):
        """
        :returns: ``True``, if all variables are continuous.
        """
        for variable in self.variables.values():
            if variable.vtype not in [
                    'continuous', 'symmetric', 'hermitian', 'complex']:
                return False
        return True

    def is_pure_integer(self):
        """
        :returns: ``True``, if all variables are integer.
        """
        for variable in self.variables.values():
            if variable.vtype in [
                    'continuous', 'symmetric', 'hermitian', 'complex']:
                return False
        return True

    def is_complex(self):
        """
        :returns: ``True``, if the problem has a complex variable or if there
            is a complex coefficient or constant inside a constraint.
        """
        tps = [x.vtype for x in self.variables.values()]
        if 'hermitian' in tps or 'complex' in tps:
            return True
        else:
            return self._complex

    def minimize(self, obj, **options):
        """
        Sets the objective to minimize the given objective function and calls
        the solver with the given sequence of options.

        :param obj: The objective function to minimize.
        :type obj: :class:`Expression <picos.expressions.Expression>`
        :param options: A sequence of optional solver options.

        :returns: A dictionary, see :func:`solve <picos.Problem.solve>`.

        .. warning::
            This is equivalent to
            :func:`set_objective <picos.Problem.set_objective>`
            followed by :func:`solve <picos.Problem.solve>` and will thus
            override any existing objective function and direction.

            Further, any supplied options will be stored in the problem as if
            they were set via :func:`set_option <picos.Problem.set_option>`.
        """
        self.set_objective('min', obj)
        return self.solve(**options)

    def maximize(self, obj, **options):
        """
        Sets the objective to maximize the given objective function and calls
        the solver with the given sequence of options.

        :param obj: The objective function to maximize.
        :type obj: :class:`Expression <picos.expressions.Expression>`
        :param options: A sequence of optional solver options.

        :returns: A dictionary, see :func:`solve <picos.Problem.solve>`.

        .. warning::
            This is equivalent to
            :func:`set_objective <picos.Problem.set_objective>`
            followed by :func:`solve <picos.Problem.solve>` and will thus
            override any existing objective function and direction.

            Further, any supplied options will be stored in the problem as if
            they were set via :func:`set_option <picos.Problem.set_option>`.
        """
        self.set_objective('max', obj)
        return self.solve(**options)

    def solve(self, **options):
        """
        Hands the problem to a solver.

        You can select the solver manually with the ``solver`` option. Otherwise
        a suitable solver will be selected among those that are available on the
        platform.

        Once the problem has been solved, the optimal solution can be obtained
        by querying the :attr:`value <picos.expressions.Expression.value>` property of the
        variables and the optimal dual values can be accessed via the
        :attr:`dual <picos.constraints.Constraint.dual>` property of the constraints.

        :param options: A sequence of optional solver options. In particular,
            you can use this to select a solver via the ``solver`` option.

        :returns: A dictionary that contains the following common entries, and
            potentially further solver-specific or option-specific fields:

            * ``'status'`` -- The solution status as a human readable string,
              such as ``'optimal'`` or ``'infeasible'``. The exact wording and
              available phrases depend on the solver being used.
            * ``'time'`` -- The time spent searching for a solution in seconds,
              *excluding* any overhead produced by PICOS when exporting the
              problem or configuring the solver.
            * ``'primals'`` -- A dictionary mapping PICOS variables to their
              value in the solution produced by the solver.
            * ``'duals'`` -- A list of dual values produced by the solver, in
              the order in which the constraints were added.

        .. warning ::
            Any supplied options will be stored in the problem as if they were
            set via :func:`set_option <picos.Problem.set_option>`.

        .. note ::
            If the problem is dualized or cast as a SOCP during solution search,
            then it will be solved from scratch upon subsequent searches, even
            if the solver supports problem updates efficiently.
        """
        # Update the solver options.
        # TODO: Consider not storing the passed options permanently. Note that
        #       the _solve_* methods work on problem copies and need to get the
        #       passed options as well.
        if options:
            self.update_options(**options)

        # Select a solver that can handle the problem.
        if self.options["solver"] is None:
            self.set_option("solver", suggested_solver(self))
        solverName = self.options["solver"]
        try:
            solver = get_solver(solverName)
        except:
            raise ValueError("The solver '{}' is unknown to PICOS."
                .format(solverName))
        try:
            solver.test_availability()
        except Exception as error:
            raise ValueError("The solver '{}' does not seem to be available on "
                "your system: {}".format(solverName, error))

        # Produce primals, duals, objective value and solution metadata.
        if self.is_complex():
            # Call solve again on the real version of self and map the results.
            primals, duals, obj, sol = self._solve_complex()
        else:
            quadratic = isinstance(self.objective[1], QuadExp) \
                or any([True for constraint in self.constraints
                    if isinstance(constraint, QuadConstraint)])

            r_socp = any([True for constraint in self.constraints
                if isinstance(constraint, SOCConstraint)
                or isinstance(constraint, RSOCConstraint)])

            solveViaDual    = self.options["solve_via_dual"]
            solverNeedsSOCP = solver.needs_quad_to_socp_cast()
            solverAllowsMix = solver.supports_quad_socp_mix()

            castAsSOCP = quadratic and (solverNeedsSOCP or solveViaDual
                or (r_socp and not solverAllowsMix))

            # Recast the problem as an SOCP if needed either by the solver or
            # for a user request to solve via dual.
            if castAsSOCP:
                if solverNeedsSOCP:
                    reason = "the solver requires this"
                elif solveViaDual:
                    reason = "the problem shall be dualized"
                elif not solverAllowsMix:
                    reason = "the solver does not allow a mix of both"
                else:
                    assert False, "Unknown reason for casting as SOCP."

                self._verbose("Replacing quadratic constraints with second "
                    "order cone constraints as {}.".format(reason))

                problem = self.as_socp()
            else:
                problem = self

            # If the user wants PICOS to decide whether the problem shall be
            # dualized, make that decision now.
            if solveViaDual is None:
                if quadratic and not castAsSOCP:
                    # Don't just cast as SOCP for dualizing, solve the primal
                    # QP/QCQP instead.
                    solveViaDual = False
                else:
                    # Make the decision based on empirical studies.
                    SDPCons = problem.numberSDPConstraints
                    SDPVars = len(
                        [v for v in problem.variables.values() if v.semiDef])
                    solveViaDual = SDPVars < 0.3 * SDPCons

            # First try to dualize, if applicable.
            solvedViaDual = False
            if solveViaDual:
                self._verbose("Dualizing the problem.")

                try:
                    # Dualize the (recast) problem, call solve again on the
                    # dual, and map the results.
                    primals, duals, obj, sol = problem._solve_via_dual(
                        handlePriorCastAsSOCP = castAsSOCP)

                    solvedViaDual = True
                except Exception as error:
                    self._warn("Failed to dualize the problem: {}".format(error))
                    self._verbose("Attempting to solve without dualizing.")

                    # If the problem was cast as SOCP just for the dualization,
                    # resolve the QP/QCQP from scratch, otherwise behave as if
                    # solve_via_dual was False.
                    if castAsSOCP and not solverNeedsSOCP:
                        return self.solve(solve_via_dual = False)
                    else:
                        problem.set_option("solve_via_dual", False)

            # From here on we are working on a primal.
            if solvedViaDual:
                pass
            elif castAsSOCP:
                sol = problem.solve()

                if not sol["primals"]:
                    primals = None
                else:
                    primals = {varName: value
                        for varName, value in sol["primals"].items()
                        if varName in self.variables}

                if not sol["duals"]:
                    duals = None
                else:
                    # TODO: Retrieve the proper dual for quadratic constraints.
                    duals = [
                        None
                        if isinstance(self.constraints[index], QuadConstraint)
                        else dual
                        for index, dual in enumerate(sol["duals"][:-1])
                    ]

                obj = sol["obj"]
            else:
                # This is the base case of solve, it will be entered eventually
                # whenever the method is called.

                # If needed create a new instance of the solver.
                if self.solvers[solverName] is None:
                    self.solvers[solverName] = solver(problem)

                # Call the solver.
                primals, duals, obj, sol = self.solvers[solverName].solve()

        # Extract the primal solution.
        if primals is not None:
            for k in primals:
                if not primals[k] is None:
                    self.set_var_value(k, primals[k], optimalvar=True)

        # Extract the dual solution.
        if duals is not None:
            for i, d in enumerate(duals):
                self.constraints[i].dual = d

        # Extract the solution status.
        self._status = sol["status"]

        # Evaluate the objectiv function if necessary.
        if obj is "toEval" and self.objective[1] is not None:
            obj = self.objective[1].eval()[0]

        # Extend the dictionary returned to the user.
        sol.update({
            "primals": primals,
            "duals":   duals,
            "obj":     obj
        })

        return sol

    def _solve_complex(self):
            if self.options['verbose'] > 0:
                print("Transforming to a real-valued problem.")

            realP = self.as_real()

            sol = realP.solve()
            obj = sol['obj']

            if 'noprimals' in self.options and self.options['noprimals']:
                pass
            else:
                primals = {}
                for var in self.variables.values():
                    if var.vtype == 'hermitian':
                        Zi = realP.get_valued_variable(var.name + '_IM')
                        primals[
                            var.name] = realP.get_valued_variable(
                            var.name + '_RE') + 1j * Zi
                    elif var.vtype == 'complex':
                        Zr = realP.get_valued_variable(var.name + '_RE')
                        Zi = realP.get_valued_variable(var.name + '_IM')
                        primals[var.name] = Zr + 1j * Zi
                    else:
                        primals[var.name] = realP.get_valued_variable(var.name)

            if 'noduals' in self.options and self.options['noduals']:
                pass
            else:
                duals = []
                for cstNum, cst in enumerate(realP.constraints):
                    if self.constraints[cstNum].is_complex():
                        if isinstance(cst, LMIConstraint):
                            n = int(cst.dual.size[0] / 2.)
                            if cst.dual.size[1] != cst.dual.size[0]:
                                raise Exception('Dual must be square matrix')
                            if cst.dual.size[1] != 2 * n:
                                raise Exception('dims must be even numbers')
                            F1 = cst.dual[:n, :n]
                            F1a = cst.dual[n:, n:]
                            F2a = cst.dual[:n, n:]
                            duals.append((F1 + 1j * F2a) + (F1a + 1j * F2a).H)
                        else:
                            if type(cst.dual) is complex:
                                duals.append(cst.dual)
                            else:
                                n = cst.dual.size[1] // 2
                                duals.append(
                                    cst.dual[:, :n] + 1j * cst.dual[:, n:])
                    else:
                        duals.append(cst.dual)

            return primals, duals, obj, sol

    def _solve_via_dual(self, handlePriorCastAsSOCP):
        dual = self.as_dual()

        sol = dual.solve()

        if self.objective[0] == 'min':
            obj = sol['obj']
        else:
            obj = -sol['obj']

        if self.options['noprimals']:
            primals = None
        else:
            primals = {}

            xx = dual.constraints[-1].dual

            if xx is None:
                raise DualizationError(
                    "No primals were retrieved from the dual problem.")

            xx = -xx
            indices = [(v.startIndex, v.endIndex, v)
                       for v in self.variables.values()]
            indices = sorted(indices, reverse=True)

            (start, end, var) = indices.pop()
            varvect = []

            if handlePriorCastAsSOCP:
                xx = xx[:-1]

            for i, x in enumerate(xx):
                if i < end:
                    varvect.append(x)
                else:
                    if var.vtype in ('symmetric',):
                        varvect = svecm1(cvx.matrix(varvect))
                    primals[var.name] = cvx.matrix(
                        varvect, var.size)
                    varvect = [x]
                    (start, end, var) = indices.pop()

            if var.vtype in ('symmetric',):
                varvect = svecm1(cvx.matrix(varvect))

            primals[var.name] = cvx.matrix(varvect, var.size)

        if handlePriorCastAsSOCP:
            # TODO: Is it necessary to set an option here? It shouldn't do much
            #       harm since in this case we are working on a copy, but it
            #       feels odd.
            self.set_option('noduals', True)

        if self.options['noduals']:
            duals = None
        else:
            duals = []

            icone = 0  # cone index
            isdp = 0  # semidef index

            if 'mue' in dual.variables:
                eqiter = iter(dual.get_valued_variable('mue'))

            if 'mul' in dual.variables:
                initer = iter(dual.get_valued_variable('mul'))

            for cons in self.constraints:
                if isinstance(cons, SOCConstraint) \
                or isinstance(cons, RSOCConstraint):
                    z  = dual.get_valued_variable('zs[{0}]'.format(icone))
                    lb = dual.get_valued_variable('lbda[{0}]'.format(icone))
                    d  = cvx.matrix([lb, z])

                    if isinstance(cons, RSOCConstraint):
                        # RSOC constraints were cast as SOC constraints on
                        # import; transform the dual back to an RSOCC dual.
                        alpha = d[0] - d[-1]
                        beta  = d[0] + d[-1]
                        z     = 2.0 * d[1:-1]
                        d     = cvx.matrix([alpha, beta, z])

                    duals.append(d)
                    icone += 1
                elif isinstance(cons, AffineConstraint) and cons.is_equality():
                    szcons = len(cons.lhs)
                    dd = []
                    for i in range(szcons):
                        dd.append(next(eqiter))
                    duals.append(cvx.matrix(dd))
                elif isinstance(cons, AffineConstraint): # inequality
                    szcons = len(cons.lhs)
                    dd = []
                    for i in range(szcons):
                        dd.append(next(initer))
                    duals.append(cvx.matrix(dd))
                elif isinstance(cons, LMIConstraint):
                    X = dual.get_valued_variable('X[{0}]'.format(isdp))
                    duals.append(X)
                    isdp += 1

        return primals, duals, obj, sol

    def _get_type(self, baseOnly = False):
        C = self.constraints

        affine  = any([isinstance(c, AffineConstraint) for c in C])
        soc     = any([isinstance(c, SOCConstraint)
            or isinstance(c, RSOCConstraint) for c in C])
        lmi     = any([isinstance(c, LMIConstraint) for c in C])
        exp     = any([isinstance(c, ExpConeConstraint) for c in C])
        gp      = exp and all([isinstance(c.origin, LSEConstraint)
            for c in C if isinstance(c, ExpConeConstraint)])
        quadObj = isinstance(self.objective[1], QuadExp)
        quadCon = any([isinstance(c, QuadConstraint) for c in C])
        quad    = quadObj or quadCon
        anyCon  = affine or soc or lmi or exp or quadCon

        longPrefix = False
        if affine and not soc and not lmi and not exp and not quad:
            base = "LP"
        elif soc and not lmi and not exp and not quad:
            base = "SOCP"
        elif lmi and not soc and not exp and not quad:
            base = "SDP"
        elif exp and not soc and not lmi and not quad:
            if gp:
                base = "GP"  # Geometric Program
            else:
                base = "ECP" # Exponential Cone Program
        elif quad and not soc and not lmi and not exp:
            if quadObj and not quadCon:
                base = "QP"   # Quadratic Program
            elif quadCon and not quadObj:
                base = "QCP"  # Quadratically Constrained Program
            else:
                base = "QCQP" # Quadratically Constrained Quadratic Program
        elif anyCon and not quad:
            base = "Conic Program"
            longPrefix = True
        elif anyCon:
            base = "CSP" # Constraint Satisfaction Problem
        else:
            base = "Unconstrained Problem"
            longPrefix = True

        if baseOnly:
            complexPrefix = integerPrefix = ""
        else:
            complexPrefix = "Complex " if self.is_complex() else ""

            if self.is_continuous():
                integerPrefix = ""
            elif self.is_pure_integer():
                integerPrefix = "Integer " if longPrefix else "I"
            else: # mixed integer
                integerPrefix = "Mixed-Integer " if longPrefix else "MI"

        return "{}{}{}".format(complexPrefix, integerPrefix, base)

    type = property(_get_type)
    """The problem type as a string, such as 'LP', 'MILP' or 'SOCP'."""

    status = property(lambda self: self._status)
    """The solution status of the problem."""

    def write_to_file(self, filename, writer='picos'):
        """
        Writes the problem to a file.

        :param str filename: Path and name of the output file. The export format
            is inferred from the file extension. Supported extensions and their
            associated format are:

            * ``'.cbf'`` -- Conic Benchmark Format.

              This format is suitable for optimization problems involving second
              order and/or semidefinite cone constraints. This is a standard
              choice for conic optimization problems. Visit the website of
              `The Conic Benchmark Library <http://cblib.zib.de/>`_ or read
              `A benchmark library for conic mixed-integer and continuous optimization <http://www.optimization-online.org/DB_HTML/2014/03/4301.html>`_
              by Henrik A. Friberg for more information.

            * ``'.lp'`` -- `LP format <http://docs.mosek.com/6.0/pyapi/node022.html>`_.

              This format handles only linear constraints, unless the writer
              ``'cplex'`` is used. In the latter case the extended
              `CPLEX LP format <http://pic.dhe.ibm.com/infocenter/cplexzos/v12r4/index.jsp?topic=%2Fcom.ibm.cplex.zos.help%2Fhomepages%2Freffileformatscplex.html>`_
              is used instead.

            * ``'.mps'`` -- `MPS format <http://docs.mosek.com/6.0/pyapi/node021.html>`_.

              As the writer, you need to choose one of ``'cplex'``, ``'gurobi'``
              or ``'mosek'``.

            * ``'.opf'`` -- `OPF format <http://docs.mosek.com/6.0/pyapi/node023.html>`_.

              As the writer, you need to choose ``'mosek'``.

            * ``'.dat-s'`` -- `Sparse SDPA format <http://sdpa.indsys.chuo-u.ac.jp/sdpa/download.html#sdpa>`_.

              This format is suitable for semidefinite programs. Second order
              cone constraints are stored as semidefinite constraints on an
              *arrow shaped* matrix.

        :param str writer: The default ``'picos'`` denotes PICOS' internal
            writer, which can export to *LP*, *CBF*, and *Sparse SDPA* formats.
            If CPLEX, Gurobi or MOSEK is installed, you can choose ``'cplex'``,
            ``'gurobi'``, or ``'mosek'``, respectively, to make use of that
            solver's export function and get access to more formats.

        .. Warning ::
            For problems involving a symmetric matrix variable :math:`X`
            (typically, semidefinite programs), the expressions involving
            :math:`X` are stored in PICOS as a function of :math:`svec(X)`, the
            symmetric vectorized form of :math:`X` (see
            `Dattorro, ch.2.2.2.1 <http://meboo.convexoptimization.com/Meboo.html>`_),
            and are also exported in that form. As a result, using an external
            solver on a problem description file exported by PICOS will also
            yield a solution in this symmetric vectorized form.

            The CBF writer tries to write symmetric variables :math:`X` in the
            section ``PSDVAR`` of the .cbf file. However, this is possible only
            if the constraint :math:`X \succeq 0` appears in the problem, and no
            other LMI involves :math:`X`. If these two conditions are not
            satisfied, then the symmetric vectorization of :math:`X` is used as
            a (free) variable of the section ``VAR`` in the .cbf file, as
            explained in the previous paragraph.
        """
        if self.numberLSEConstraints:
            raise Exception('gp are not supported')
        if not(
                self.objective[1] is None) and isinstance(
                self.objective[1],
                GeneralFun):
            raise Exception('general-obj are not supported')

        # automatic extension recognition
        if not(filename[-4:] in ('.mps', '.opf', '.cbf') or
               filename[-3:] == '.lp' or
               filename[-6:] == '.dat-s'):
            if writer in ('mosek', 'gurobi'):
                if (self.numberSDPConstraints > 0):
                    raise Exception('no SDP with Gurobi or MOSEK')
                if (self.numberConeConstraints +
                        self.numberQuadConstraints) == 0:
                    filename += '.lp'
                else:
                    filename += '.mps'
            elif writer == 'cplex':
                if (self.numberSDPConstraints > 0):
                    raise Exception('no SDP with CPLEX')
                else:
                    filename += '.lp'
            elif writer == 'picos':
                if (self.numberQuadConstraints > 0):
                    pcop = self.copy()
                    pcop.convert_quad_to_socp()
                    pcop.write_to_file(filename, writer)
                    return
                if (self.numberConeConstraints +
                        self.numberSDPConstraints) == 0:
                    filename += '.lp'
                elif self.numberConeConstraints == 0:
                    filename += '.dat-s'
                else:
                    filename += '.cbf'
            else:
                raise Exception('unexpected writer')

        if writer == 'cplex':
            # TODO: Implement problem export via CPLEX.
            raise NotImplementedError(
                "Writing via CPLEX needs to be reimplemented.")
        elif writer == 'mosek':
            # TODO: Implement problem export via MOSEK.
            raise NotImplementedError(
                "Writing via MOSEK needs to be reimplemented.")
        elif writer == 'gurobi':
            # TODO: Implement problem export via Gurobi.
            raise NotImplementedError(
                "Writing via Gurobi needs to be reimplemented.")
        elif writer == 'picos':
            if filename[-3:] == '.lp':
                self._write_lp(filename)
            elif filename[-6:] == '.dat-s':
                self._write_sdpa(filename)
            elif filename[-4:] == '.cbf':
                self._write_cbf(filename)
            else:
                raise Exception('unexpected file extension')
        else:
            raise Exception('unknown writer')

    # HACK: This method abuses the internal problem representation of CVXOPT.
    def _write_lp(self, filename):
        """
        Writes the problem to a file in LP format.
        """
        # add extension
        if filename[-3:] != '.lp':
            filename += '.lp'
        # check lp compatibility
        if (self.numberConeConstraints + self.numberQuadConstraints +
            self.numberLSEConstraints + self.numberSDPConstraints) > 0:
            raise Exception('the picos LP writer only accepts (MI)LP')
        # open file
        f = open(filename, 'w')
        f.write("\\* file " + filename + " generated by picos*\\\n")

        # HACK: See above.
        localCvxoptInstance = CVXOPTSolver(self)
        localCvxoptInstance.import_variable_bounds = False
        localCvxoptInstance._load_problem()
        cvxoptVars = localCvxoptInstance.internal_problem()

        # variable names
        varnames = {}
        for name, v in self.variables.items():
            j = 0
            k = 0
            for i in range(v.startIndex, v.endIndex):
                if v.size == (1, 1):
                    varnames[i] = name
                elif v.size[1] == 1:
                    varnames[i] = name + '(' + str(j) + ')'
                    j += 1
                else:
                    varnames[i] = name + '(' + str(j) + ',' + str(k) + ')'
                    j += 1
                    if j == v.size[0]:
                        k += 1
                        j = 0
                varnames[i] = varnames[i].replace('[', '(')
                varnames[i] = varnames[i].replace(']', ')')
        # affexpr writer

        def affexp_writer(name, indices, coefs):
            s = ''
            s += name
            s += ' : '
            start = True
            for (i, v) in zip(indices, coefs):
                if v > 0 and not(start):
                    s += '+ '
                s += "%.12g" % v
                s += ' '
                s += varnames[i]
                # not the first term anymore
                start = False
            if not(coefs):
                s += '0.0 '
                s += varnames[0]
            return s

        print('writing problem in ' + filename + '...')

        # objective
        if self.objective[0] == 'max':
            f.write("Maximize\n")
            # max handled directly
            cvxoptVars['c'] = -cvxoptVars['c']
        else:
            f.write("Minimize\n")
        I = cvx.sparse(cvxoptVars['c']).I
        V = cvx.sparse(cvxoptVars['c']).V

        f.write(affexp_writer('obj', I, V))
        f.write('\n')

        f.write("Subject To\n")
        bounds = {}
        # equality constraints:
        Ai, Aj, Av = (cvxoptVars['A'].I, cvxoptVars['A'].J, cvxoptVars['A'].V)
        ijvs = sorted(zip(Ai, Aj, Av))
        del Ai, Aj, Av
        itojv = {}
        lasti = -1
        for (i, j, v) in ijvs:
            if i == lasti:
                itojv[i].append((j, v))
            else:
                lasti = i
                itojv[i] = [(j, v)]
        ieq = 0
        for i, jv in itojv.items():
            J = [jvk[0] for jvk in jv]
            V = [jvk[1] for jvk in jv]
            if len(J) == 1:
                # fixed variable
                b = cvxoptVars['b'][i] / V[0]
                bounds[J[0]] = (b, b)
            else:
                # affine equality
                b = cvxoptVars['b'][i]
                f.write(affexp_writer('eq' + str(ieq), J, V))
                f.write(' = ')
                f.write("%.12g" % b)
                f.write('\n')
                ieq += 1

        # inequality constraints:
        Gli, Glj, Glv = (
            cvxoptVars['Gl'].I, cvxoptVars['Gl'].J, cvxoptVars['Gl'].V)
        ijvs = sorted(zip(Gli, Glj, Glv))
        del Gli, Glj, Glv
        itojv = {}
        lasti = -1
        for (i, j, v) in ijvs:
            if i == lasti:
                itojv[i].append((j, v))
            else:
                lasti = i
                itojv[i] = [(j, v)]
        iaff = 0
        for i, jv in itojv.items():
            J = [jvk[0] for jvk in jv]
            V = [jvk[1] for jvk in jv]
            b = cvxoptVars['hl'][i]
            f.write(affexp_writer('in' + str(iaff), J, V))
            f.write(' <= ')
            f.write("%.12g" % b)
            f.write('\n')
            iaff += 1

        # bounds
        #hard-coded
        for varname in self.varNames:
            var = self.variables[varname]
            for ind, (lo, up) in var.bnd.items():
                (clo, cup) = bounds.get(var.startIndex + ind, (None, None))
                if lo is None:
                    lo = -INFINITY
                if up is None:
                    up = INFINITY
                if clo is None:
                    clo = -INFINITY
                if cup is None:
                    cup = INFINITY
                nlo = max(clo, lo)
                nup = min(cup, up)
                bounds[var.startIndex + ind] = (nlo, nup)


        f.write("Bounds\n")
        for i in range(self.numberOfVars):
            if i in bounds:
                bl, bu = bounds[i]
            else:
                bl, bu = -INFINITY, INFINITY
            if bl == -INFINITY and bu == INFINITY:
                f.write(varnames[i] + ' free')
            elif bl == bu:
                f.write(varnames[i] + (" = %.12g" % bl))
            elif bl < bu:
                if bl == -INFINITY:
                    f.write('-inf <= ')
                else:
                    f.write("%.12g" % bl)
                    f.write(' <= ')
                f.write(varnames[i])
                if bu == INFINITY:
                    f.write('<= +inf')
                else:
                    f.write(' <= ')
                    f.write("%.12g" % bu)
            f.write('\n')

        # general integers
        f.write("Generals\n")
        for name, v in self.variables.items():
            if v.vtype == 'integer':
                for i in range(v.startIndex, v.endIndex):
                    f.write(varnames[i] + '\n')
            if v.vtype == 'semiint' or v.vtype == 'semicont':
                raise Exception('semiint and semicont variables not handled by '
                    'this LP writer')
        # binary variables
        f.write("Binaries\n")
        for name, v in self.variables.items():
            if v.vtype == 'binary':
                for i in range(v.startIndex, v.endIndex):
                    f.write(varnames[i] + '\n')
        f.write("End\n")
        print('done.')
        f.close()

    # HACK: This method abuses the internal problem representation of CVXOPT.
    def _write_sdpa(self, filename):
        """
        Writes the problem to a file in Sparse SDPA format.
        """
        # HACK: See above.
        localCvxoptInstance = CVXOPTSolver(self)
        localCvxoptInstance._load_problem()
        cvxoptVars = localCvxoptInstance.internal_problem()

        dims = {}
        dims['s'] = [int(np.sqrt(Gsi.size[0]))
                     for Gsi in cvxoptVars['Gs']]
        dims['l'] = cvxoptVars['Gl'].size[0]
        dims['q'] = [Gqi.size[0] for Gqi in cvxoptVars['Gq']]
        G = cvxoptVars['Gl']
        h = cvxoptVars['hl']

        # handle the equalities as 2 ineq
        if cvxoptVars['A'].size[0] > 0:
            G = cvx.sparse([G, cvxoptVars['A']])
            G = cvx.sparse([G, -cvxoptVars['A']])
            h = cvx.matrix([h, cvxoptVars['b']])
            h = cvx.matrix([h, -cvxoptVars['b']])
            dims['l'] += (2 * cvxoptVars['A'].size[0])

        for i in range(len(dims['q'])):
            G = cvx.sparse([G, cvxoptVars['Gq'][i]])
            h = cvx.matrix([h, cvxoptVars['hq'][i]])

        for i in range(len(dims['s'])):
            G = cvx.sparse([G, cvxoptVars['Gs'][i]])
            h = cvx.matrix([h, cvxoptVars['hs'][i]])

        # Remove the lines in A and b corresponding to 0==0
        JP = list(set(cvxoptVars['A'].I))
        IP = range(len(JP))
        VP = [1] * len(JP)

        # is there a constraint of the form 0==a(a not 0) ?
        if any([b for (i, b) in enumerate(
                cvxoptVars['b']) if i not in JP]):
            raise Exception('infeasible constraint of the form 0=a')

        from cvxopt import sparse, spmatrix
        P = spmatrix(VP, IP, JP, (len(IP), cvxoptVars['A'].size[0]))
        cvxoptVars['A'] = P * cvxoptVars['A']
        cvxoptVars['b'] = P * cvxoptVars['b']
        c = cvxoptVars['c']
        #------------------------------------------------------------#
        # make A,B,and blockstruct.                                  #
        # This code is a modification of the conelp function in SMCP #
        #------------------------------------------------------------#
        Nl = dims['l']
        Nq = dims['q']
        Ns = dims['s']
        if not Nl:
            Nl = 0

        P_m = G.size[1]

        P_b = -c
        P_blockstruct = []
        if Nl:
            P_blockstruct.append(-Nl)
        for i in Nq:
            P_blockstruct.append(i)
        for i in Ns:
            P_blockstruct.append(i)

        # write data
        # add extension
        if filename[-6:] != '.dat-s':
            filename += '.dat-s'
        # check lp compatibility
        if (self.numberQuadConstraints + self.numberLSEConstraints) > 0:
            pcop = self.copy()
            pcop.convert_quad_to_socp()
            pcop._write_sdpa(filename)
            return
        # open file
        f = open(filename, 'w')
        f.write('"file ' + filename + ' generated by picos"\n')
        if self.options['verbose'] >= 1:
            print('writing problem in ' + filename + '...')
        f.write(str(self.numberOfVars) + ' = number of vars\n')
        f.write(str(len(P_blockstruct)) + ' = number of blocs\n')
        # bloc structure
        f.write(str(P_blockstruct).replace('[', '(').replace(']', ')'))
        f.write(' = BlocStructure\n')
        # c vector (objective)
        f.write(str(list(-P_b)).replace('[', '{').replace(']', '}'))
        f.write('\n')
        # coefs
        for k in range(P_m + 1):
            if k != 0:
                v = sparse(G[:, k - 1])
            else:
                v = +sparse(h)

            ptr = 0
            block = 0
            # lin. constraints
            if Nl:
                u = v[:Nl]
                for i, j, value in zip(u.I, u.I, u.V):
                    f.write(
                        '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                            k, block + 1, j + 1, i + 1, -value))
                ptr += Nl
                block += 1

            # SOC constraints
            for nq in Nq:
                u0 = v[ptr]
                u1 = v[ptr + 1:ptr + nq]
                tmp = spmatrix(
                    u1.V, [nq - 1 for j in range(len(u1))], u1.I, (nq, nq))
                if not u0 == 0.0:
                    tmp += spmatrix(u0, range(nq), range(nq), (nq, nq))
                for i, j, value in zip(tmp.I, tmp.J, tmp.V):
                    f.write(
                        '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                            k, block + 1, j + 1, i + 1, -value))
                ptr += nq
                block += 1

            # SDP constraints
            for ns in Ns:
                u = v[ptr:ptr + ns**2]
                for index_k, index in enumerate(u.I):
                    j, i = divmod(index, ns)
                    if j <= i:
                        f.write(
                            '{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
                                k, block + 1, j + 1, i + 1, -u.V[index_k]))
                ptr += ns**2
                block += 1

        f.close()

    def _write_cbf(self, filename, uptri=False):
        """
        Writes the problem to a file in Sparse SDPA format.

        :param bool uptri: Whether upper triangular elements of symmetric
            matrices are specified.
        """
        # write data
        # add extension
        if filename[-4:] != '.cbf':
            filename += '.cbf'
        # check lp compatibility
        if (self.numberQuadConstraints + self.numberLSEConstraints) > 0:
            pcop = self.copy()
            pcop.convert_quad_to_socp()
            pcop._write_cbf(filename)
            return

        # parse variables
        NUMVAR_SCALAR = int(builtin_sum([(var.endIndex - var.startIndex)
                                   for var in self.variables.values()
                                   if not(var.semiDef)]))

        indices = [(v.startIndex, v.endIndex, v)
                   for v in self.variables.values()]
        indices = sorted(indices)
        idxsdpvars = [(si, ei) for (si, ei, v) in indices[::-1] if v.semiDef]
        # search if some semidef vars are implied in other semidef constraints
        PSD_not_handled = []
        for c in self.constraints:
            if isinstance(c, LMIConstraint) and not c.semidefVar:
                for v in (c.lhs - c.rhs).factors:
                    if v.semiDef:
                        idx = (v.startIndex, v.endIndex)
                        if idx in idxsdpvars:
                            PSD_not_handled.append(v)
                            NUMVAR_SCALAR += (idx[1] - idx[0])
                            idxsdpvars.remove(idx)

        barvars = bool(idxsdpvars)

        # find integer variables, put 0-1 bounds on binaries
        ints = []
        for k, var in self.variables.items():
            if var.vtype == 'binary':
                for ind, i in enumerate(range(var.startIndex, var.endIndex)):
                    ints.append(i)
                    (clb, cub) = var.bnd.get(ind, (-INFINITY, INFINITY))
                    lb = max(0., clb)
                    ub = min(1., cub)
                    var.bnd._set(ind, (lb, ub))

            elif self.variables[k].vtype == 'integer':
                for i in range(
                        self.variables[k].startIndex,
                        self.variables[k].endIndex):
                    ints.append(i)

            elif self.variables[k].vtype not in ['continuous', 'symmetric']:
                raise Exception('vtype not handled by _write_cbf()')
        if barvars:
            ints, _, mats = self._separate_linear_cons(
                ints, [0.] * len(ints), idxsdpvars)
            if any([bool(mat) for mat in mats]):
                raise Exception(
                    'semidef vars with integer elements are not supported')

        # open file
        f = open(filename, 'w')
        f.write('#file ' + filename + ' generated by picos\n')
        print('writing problem in ' + filename + '...')

        f.write("VER\n")
        f.write("1\n\n")

        f.write("OBJSENSE\n")
        if self.objective[0] == 'max':
            f.write("MAX\n\n")
        else:
            f.write("MIN\n\n")

        # VARIABLEs

        if barvars:
            f.write("PSDVAR\n")
            f.write(str(len(idxsdpvars)) + "\n")
            for si, ei in idxsdpvars:
                ni = int(((8 * (ei - si) + 1)**0.5 - 1) / 2.)
                f.write(str(ni) + "\n")
            f.write("\n")

        # bounds
        cones = []
        conecons = []
        Acoord = []
        Bcoord = []
        iaff = 0
        offset = 0
        for si, ei, v in indices:
            if v.semiDef and not (v in PSD_not_handled):
                offset += (ei - si)
            else:
                if 'nonnegative' in (v._bndtext):
                    cones.append(('L+', ei - si))
                elif 'nonpositive' in (v._bndtext):
                    cones.append(('L-', ei - si))
                else:
                    cones.append(('F', ei - si))
                if 'nonnegative' not in (v._bndtext):
                    for j, (l, u) in v.bnd.items():
                        if l is not None:
                            Acoord.append((iaff, si + j - offset, 1.))
                            Bcoord.append((iaff, -l))
                            iaff += 1
                if 'nonpositive' not in (v._bndtext):
                    for j, (l, u) in v.bnd.items():
                        if u is not None:
                            Acoord.append((iaff, si + j - offset, -1.))
                            Bcoord.append((iaff, u))
                            iaff += 1
        if iaff:
            conecons.append(('L+', iaff))

        f.write("VAR\n")
        f.write(str(NUMVAR_SCALAR) + ' ' + str(len(cones)) + '\n')
        for tp, n in cones:
            f.write(tp + ' ' + str(n) + '\n')

        f.write('\n')

        # integers
        if ints:
            f.write("INT\n")
            f.write(str(len(ints)) + "\n")
            for i in ints:
                f.write(str(i) + "\n")
            f.write("\n")

        # constraints
        psdcons = []
        isdp = 0
        Fcoord = []
        Hcoord = []
        Dcoord = []
        ObjAcoord = []
        ObjBcoord = []
        ObjFcoord = []
        # dummy constraint for the objective
        if self.objective[1] is None:
            dummy_cons = (AffinExp() > 0)
        else:
            dummy_cons = (self.objective[1] > 0)
        setattr(dummy_cons, "dummycon", None)

        for cons in ([dummy_cons] + self.constraints):
            if isinstance(cons, LMIConstraint):
                v = cons.semidefVar
                if v is not None and v not in PSD_not_handled:
                    continue

            # get sparse indices
            if isinstance(cons, AffineConstraint):
                expcone = cons.lhs - cons.rhs
                if hasattr(cons, "dummycon"):
                    conetype = '0' # Dummy type for the objective function.
                elif cons.is_equality():
                    conetype = 'L='
                elif cons.is_increasing():
                    conetype = 'L-'
                elif cons.is_decreasing():
                    conetype = 'L+'
                else:
                    assert False, "Unexpected constraint relation."
            elif isinstance(cons, SOCConstraint):
                expcone = ((cons.ub) // (cons.ne[:]))
                conetype = 'Q'
            elif isinstance(cons, RSOCConstraint):
                expcone = ((cons.ub1) // (0.5 * cons.ub2) // (cons.ne[:]))
                conetype = 'QR'
            elif isinstance(cons, LMIConstraint):
                if cons.is_increasing():
                    expcone = cons.rhs - cons.lhs
                    conetype = None
                elif cons.is_decreasing():
                    expcone = cons.lhs - cons.rhs
                    conetype = None
                else:
                    assert False, "Unexpected constraint relation."
            else:
                assert False, "Unexpected constraint type."

            ijv = []
            for var, fact in expcone.factors.items():
                if not isinstance(fact, cvx.base.spmatrix):
                    fact = cvx.sparse(fact)
                sj = var.startIndex
                ijv.extend(zip(fact.I, fact.J + sj, fact.V))
            ijvs = sorted(ijv)

            itojv = {}
            lasti = -1
            for (i, j, v) in ijvs:
                if i == lasti:
                    itojv[i].append((j, v))
                else:
                    lasti = i
                    itojv[i] = [(j, v)]

            if conetype:
                if conetype != '0':
                    dim = expcone.size[0] * expcone.size[1]
                    conecons.append((conetype, dim))
            else:
                dim = expcone.size[0]
                psdcons.append(dim)

            if conetype:
                for i, jv in itojv.items():
                    J = [jvk[0] for jvk in jv]
                    V = [jvk[1] for jvk in jv]
                    J, V, mats = self._separate_linear_cons(
                        J, V, idxsdpvars)
                    for j, v in zip(J, V):
                        if conetype != '0':
                            Acoord.append((iaff + i, j, v))
                        else:
                            ObjAcoord.append((j, v))
                    for k, mat in enumerate(mats):
                        for row, col, v in zip(mat.I, mat.J, mat.V):
                            if conetype != '0':
                                Fcoord.append((iaff + i, k, row, col, v))
                            else:
                                ObjFcoord.append((k, row, col, v))
                            if uptri and row != col:
                                if conetype != '0':
                                    Fcoord.append(
                                        (iaff + i, k, col, row, v))
                                else:
                                    ObjFcoord.append((k, col, row, v))
                constant = expcone.constant
                if not(constant is None):
                    constant = cvx.sparse(constant)
                    for i, v in zip(constant.I, constant.V):
                        if conetype != '0':
                            Bcoord.append((iaff + i, v))
                        else:
                            ObjBcoord.append(v)
            else:
                for i, jv in itojv.items():
                    col, row = divmod(i, dim)
                    if not(uptri) and row < col:
                        continue
                    J = [jvk[0] for jvk in jv]
                    V = [jvk[1] for jvk in jv]
                    J, V, mats = self._separate_linear_cons(
                        J, V, idxsdpvars)
                    if any([bool(m) for m in mats]):
                        raise Exception(
                            'SDP cons should not depend on PSD var')
                    for j, v in zip(J, V):
                        Hcoord.append((isdp, j, row, col, v))

                constant = expcone.constant
                if not(constant is None):
                    constant = cvx.sparse(constant)
                    for i, v in zip(constant.I, constant.V):
                        col, row = divmod(i, dim)
                        if row < col:
                            continue
                        Dcoord.append((isdp, row, col, v))

            if conetype:
                if conetype != '0':
                    iaff += dim
            else:
                isdp += 1

        if iaff > 0:
            f.write("CON\n")
            f.write(str(iaff) + ' ' + str(len(conecons)) + '\n')
            for tp, n in conecons:
                f.write(tp + ' ' + str(n))
                f.write('\n')

            f.write('\n')

        if isdp > 0:
            f.write("PSDCON\n")
            f.write(str(isdp) + '\n')
            for n in psdcons:
                f.write(str(n) + '\n')
            f.write('\n')

        if ObjFcoord:
            f.write("OBJFCOORD\n")
            f.write(str(len(ObjFcoord)) + '\n')
            for (k, row, col, v) in ObjFcoord:
                f.write('{0} {1} {2} {3}\n'.format(k, row, col, v))
            f.write('\n')

        if ObjAcoord:
            f.write("OBJACOORD\n")
            f.write(str(len(ObjAcoord)) + '\n')
            for (j, v) in ObjAcoord:
                f.write('{0} {1}\n'.format(j, v))
            f.write('\n')

        if ObjBcoord:
            f.write("OBJBCOORD\n")
            v = ObjBcoord[0]
            f.write('{0}\n'.format(v))
            f.write('\n')

        if Fcoord:
            f.write("FCOORD\n")
            f.write(str(len(Fcoord)) + '\n')
            for (i, k, row, col, v) in Fcoord:
                f.write('{0} {1} {2} {3} {4}\n'.format(i, k, row, col, v))
            f.write('\n')

        if Acoord:
            f.write("ACOORD\n")
            f.write(str(len(Acoord)) + '\n')
            for (i, j, v) in Acoord:
                f.write('{0} {1} {2}\n'.format(i, j, v))
            f.write('\n')

        if Bcoord:
            f.write("BCOORD\n")
            f.write(str(len(Bcoord)) + '\n')
            for (i, v) in Bcoord:
                f.write('{0} {1}\n'.format(i, v))
            f.write('\n')

        if Hcoord:
            f.write("HCOORD\n")
            f.write(str(len(Hcoord)) + '\n')
            for (i, j, row, col, v) in Hcoord:
                f.write('{0} {1} {2} {3} {4}\n'.format(i, j, row, col, v))
            f.write('\n')

        if Dcoord:
            f.write("DCOORD\n")
            f.write(str(len(Dcoord)) + '\n')
            for (i, row, col, v) in Dcoord:
                f.write('{0} {1} {2} {3}\n'.format(i, row, col, v))
            f.write('\n')

        print('done.')
        f.close()

    def _read_cbf(self, filename):
        try:
            f = open(filename, 'r')
        except IOError:
            filename += '.cbf'
            f = open(filename, 'r')
        print('importing problem data from ' + filename + '...')
        self.reset()

        line = f.readline()
        while not line.startswith('VER'):
            line = f.readline()

        ver = int(f.readline())
        if ver != 1:
            print('WARNING, file has version > 1')

        structure_keywords = [
            'OBJSENSE',
            'PSDVAR',
            'VAR',
            'INT',
            'PSDCON',
            'CON']
        data_keywords = ['OBJFCOORD', 'OBJACOORD', 'OBJBCOORD',
                         'FCOORD', 'ACOORD', 'BCOORD',
                         'HCOORD', 'DCOORD']

        structure_mode = True  # still parsing structure blocks
        seen_blocks = []
        parsed_blocks = {}
        while True:
            line = f.readline()
            if not line:
                break
            lsplit = line.split()
            if lsplit and lsplit[0] in structure_keywords:
                if lsplit[0] == 'INT' and ('VAR' not in seen_blocks):
                    raise Exception('INT BLOCK before VAR BLOCK')
                if lsplit[0] == 'CON' and not(
                        'VAR' in seen_blocks or 'PSDVAR' in seen_blocks):
                    raise Exception('CON BLOCK before VAR/PSDVAR BLOCK')
                if lsplit[0] == 'PSDCON' and not(
                        'VAR' in seen_blocks or 'PSDVAR' in seen_blocks):
                    raise Exception('PSDCON BLOCK before VAR/PSDVAR BLOCK')
                if lsplit[0] == 'VAR' and (
                        'CON' in seen_blocks or 'PSDCON' in seen_blocks):
                    raise Exception('VAR BLOCK after CON/PSDCON BLOCK')
                if lsplit[0] == 'PSDVAR' and (
                        'CON' in seen_blocks or 'PSDCON' in seen_blocks):
                    raise Exception('PSDVAR BLOCK after CON/PSDCON BLOCK')
                if structure_mode:
                    parsed_blocks[
                        lsplit[0]] = self._read_cbf_block(
                        lsplit[0], f, parsed_blocks)
                    seen_blocks.append(lsplit[0])
                else:
                    raise Exception('Structure keyword after first data item')
            if lsplit and lsplit[0] in data_keywords:
                if 'OBJSENSE' not in seen_blocks:
                    raise Exception('missing OBJSENSE block')
                if not('VAR' in seen_blocks or 'PSDVAR' in seen_blocks):
                    raise Exception('missing VAR/PSDVAR block')
                if lsplit[0] in (
                        'OBJFCOORD', 'FCOORD') and not(
                        'PSDVAR' in seen_blocks):
                    raise Exception('missing PSDVAR block')
                if lsplit[0] in (
                        'OBJACOORD', 'ACOORD', 'HCOORD') and not(
                        'VAR' in seen_blocks):
                    raise Exception('missing VAR block')
                if lsplit[0] in (
                        'DCOORD', 'HCOORD') and not(
                        'PSDCON' in seen_blocks):
                    raise Exception('missing PSDCON block')
                structure_mode = False
                parsed_blocks[
                    lsplit[0]] = self._read_cbf_block(
                    lsplit[0], f, parsed_blocks)
                seen_blocks.append(lsplit[0])

        f.close()
        # variables
        if 'VAR' in parsed_blocks:
            Nvars, varsz, x = parsed_blocks['VAR']
        else:
            x = None

        if 'INT' in parsed_blocks:
            x = parsed_blocks['INT']

        if 'PSDVAR' in parsed_blocks:
            psdsz, X = parsed_blocks['PSDVAR']
        else:
            X = None

        # objective
        obj_constant = parsed_blocks.get('OBJBCOORD', 0)
        bobj = new_param('bobj', obj_constant)
        obj = new_param('bobj', obj_constant)

        aobj = {}
        if 'OBJACOORD' in parsed_blocks:
            obj_vecs = break_cols(parsed_blocks['OBJACOORD'], varsz)
            aobj = {}
            for k, v in enumerate(obj_vecs):
                if v:
                    aobj[k] = new_param('c[' + str(k) + ']', v)
                    obj += aobj[k] * x[k]

        Fobj = {}
        if 'OBJFCOORD' in parsed_blocks:
            Fbl = parsed_blocks['OBJFCOORD']
            for i, Fi in enumerate(Fbl):
                if Fi:
                    Fobj[i] = new_param('F[' + str(i) + ']', Fi)
                    obj += (Fobj[i] | X[i])

        self.set_objective(self.objective[0], obj)

        # cone constraints
        bb = {}
        AA = {}
        FF = {}
        if 'CON' in parsed_blocks:
            Ncons, structcons = parsed_blocks['CON']
            szcons = [s for tp, s in structcons]

            b = parsed_blocks.get(
                'BCOORD', spmatrix(
                    [], [], [], (Ncons, 1)))
            bvecs = break_rows(b, szcons)
            consexp = []
            for i, bi in enumerate(bvecs):
                bb[i] = new_param('b[' + str(i) + ']', bi)
                consexp.append(new_param('b[' + str(i) + ']', bi))

            A = parsed_blocks.get(
                'ACOORD', spmatrix(
                    [], [], [], (Ncons, Nvars)))
            Ablc = break_rows(A, szcons)
            for i, Ai in enumerate(Ablc):
                Aiblocs = break_cols(Ai, varsz)
                for j, Aij in enumerate(Aiblocs):
                    if Aij:
                        AA[i, j] = new_param('A[' + str((i, j)) + ']', Aij)
                        consexp[i] += AA[i, j] * x[j]

            Fcoords = parsed_blocks.get('FCOORD', {})
            for k, mats in Fcoords.items():
                i, row = block_idx(k, szcons)
                row_exp = AffinExp()
                for j, mat in enumerate(mats):
                    if mat:
                        FF[i, j, row] = new_param(
                            'F[' + str((i, j, row)) + ']', mat)
                        row_exp += (FF[i, j, row] | X[j])

                consexp[i] += (('e_' + str(row) +
                                '(' + str(szcons[i]) + ',1)') * row_exp)

            for i, (tp, sz) in enumerate(structcons):
                if tp == 'F':
                    continue
                elif tp == 'L-':
                    self.add_constraint(consexp[i] < 0)
                elif tp == 'L+':
                    self.add_constraint(consexp[i] > 0)
                elif tp == 'L=':
                    self.add_constraint(consexp[i] == 0)
                elif tp == 'Q':
                    self.add_constraint(abs(consexp[i][1:]) < consexp[i][0])
                elif tp == 'QR':
                    self.add_constraint(abs(
                        consexp[i][2:])**2 < 2 * consexp[i][0] * consexp[i][1])
                else:
                    raise Exception('unexpected cone type')

        DD = {}
        HH = {}
        if 'PSDCON' in parsed_blocks:
            Dblocks = parsed_blocks.get(
                'DCOORD', [spmatrix(
                    [], [], [], (ni, ni)) for ni in parsed_blocks['PSDCON']])
            Hblocks = parsed_blocks.get('HCOORD', {})

            consexp = []
            for i, Di in enumerate(Dblocks):
                DD[i] = new_param('D[' + str(i) + ']', Di)
                consexp.append(new_param('D[' + str(i) + ']', Di))

            for j, Hj in Hblocks.items():
                i, col = block_idx(j, varsz)
                for k, Hij in enumerate(Hj):
                    if Hij:
                        HH[k, i, col] = new_param(
                            'H[' + str((k, i, col)) + ']', Hij)
                        consexp[k] += HH[k, i, col] * x[i][col]

            for exp in consexp:
                self.add_constraint(exp >> 0)

        print('done.')

        params = {'aobj': aobj,
                  'bobj': bobj,
                  'Fobj': Fobj,
                  'A': AA,
                  'b': bb,
                  'F': FF,
                  'D': DD,
                  'H': HH,
                  }

        return x, X, params  # TODO interface + check returned params !

    def _read_cbf_block(self, blocname, f, parsed_blocks):
        if blocname == 'OBJSENSE':
            objsense = f.readline().split()[0].lower()
            self.objective = (objsense, None)
            return None
        elif blocname == 'PSDVAR':
            n = int(f.readline())
            vardims = []
            XX = []
            for i in range(n):
                ni = int(f.readline())
                vardims.append(ni)
                Xi = self.add_variable(
                    'X[' + str(i) + ']', (ni, ni), 'symmetric')
                XX.append(Xi)
                self.add_constraint(Xi >> 0)
            return vardims, XX
        elif blocname == 'VAR':
            Nscalar, ncones = [int(fi) for fi in f.readline().split()]
            tot_dim = 0
            var_structure = []
            xx = []
            for i in range(ncones):
                lsplit = f.readline().split()
                tp, dim = lsplit[0], int(lsplit[1])
                tot_dim += dim
                var_structure.append(dim)
                if tp == 'F':
                    xi = self.add_variable('x[' + str(i) + ']', dim)
                elif tp == 'L+':
                    xi = self.add_variable('x[' + str(i) + ']', dim, lower=0)
                elif tp == 'L-':
                    xi = self.add_variable('x[' + str(i) + ']', dim, upper=0)
                elif tp == 'L=':
                    xi = self.add_variable(
                        'x[' + str(i) + ']', dim, lower=0, upper=0)
                elif tp == 'Q':
                    xi = self.add_variable('x[' + str(i) + ']', dim)
                    self.add_constraint(abs(xi[1:]) < xi[0])
                elif tp == 'QR':
                    xi = self.add_variable('x[' + str(i) + ']', dim)
                    self.add_constraint(abs(xi[2:])**2 < 2 * xi[0] * xi[1])
                xx.append(xi)
            if tot_dim != Nscalar:
                raise Exception('VAR dimensions do not match the header')
            return Nscalar, var_structure, xx
        elif blocname == 'INT':
            n = int(f.readline())
            ints = {}
            for k in range(n):
                j = int(f.readline())
                i, col = block_idx(j, parsed_blocks['VAR'][1])
                ints.setdefault(i, [])
                ints[i].append(col)
            x = parsed_blocks['VAR'][2]
            for i in ints:
                if len(ints[i]) == x[i].size[0]:
                    x[i].vtype = 'integer'
                else:
                    x.append(self.add_variable(
                        'x_int[' + str(i) + ']', len(ints[i]), 'integer'))
                    for k, j in enumerate(ints[i]):
                        self.add_constraint(x[i][j] == x[-1][k])
            return x
        elif blocname == 'CON':
            Ncons, ncones = [int(fi) for fi in f.readline().split()]
            cons_structure = []
            tot_dim = 0
            for i in range(ncones):
                lsplit = f.readline().split()
                tp, dim = lsplit[0], int(lsplit[1])
                tot_dim += dim
                cons_structure.append((tp, dim))
            if tot_dim != Ncons:
                raise Exception('CON dimensions do not match the header')
            return Ncons, cons_structure
        elif blocname == 'PSDCON':
            n = int(f.readline())
            psdcons_structure = []
            for i in range(n):
                ni = int(f.readline())
                psdcons_structure.append(ni)
            return psdcons_structure
        elif blocname == 'OBJACOORD':
            n = int(f.readline())
            J = []
            V = []
            for i in range(n):
                lsplit = f.readline().split()
                j, v = int(lsplit[0]), float(lsplit[1])
                J.append(j)
                V.append(v)
            return spmatrix(
                V, [0] * len(J), J, (1, parsed_blocks['VAR'][0]))
        elif blocname == 'OBJBCOORD':
            return float(f.readline())
        elif blocname == 'OBJFCOORD':
            n = int(f.readline())
            Fobj = [spmatrix([], [], [], (ni, ni))
                    for ni in parsed_blocks['PSDVAR'][0]]
            for k in range(n):
                lsplit = f.readline().split()
                j, row, col, v = (int(lsplit[0]), int(lsplit[1]),
                                  int(lsplit[2]), float(lsplit[3]))
                Fobj[j][row, col] = v
                if row != col:
                    Fobj[j][col, row] = v
            return Fobj
        elif blocname == 'FCOORD':
            n = int(f.readline())
            Fblocks = {}
            for k in range(n):
                lsplit = f.readline().split()
                i, j, row, col, v = (int(lsplit[0]), int(lsplit[1]), int(
                    lsplit[2]), int(lsplit[3]), float(lsplit[4]))
                if i not in Fblocks:
                    Fblocks[i] = [spmatrix([], [], [], (ni, ni))
                        for ni in parsed_blocks['PSDVAR'][0]]
                Fblocks[i][j][row, col] = v
                if row != col:
                    Fblocks[i][j][col, row] = v
            return Fblocks
        elif blocname == 'ACOORD':
            n = int(f.readline())
            J = []
            V = []
            I = []
            for k in range(n):
                lsplit = f.readline().split()
                i, j, v = int(lsplit[0]), int(lsplit[1]), float(lsplit[2])
                I.append(i)
                J.append(j)
                V.append(v)
            return spmatrix(
                V, I, J, (parsed_blocks['CON'][0], parsed_blocks['VAR'][0]))
        elif blocname == 'BCOORD':
            n = int(f.readline())
            V = []
            I = []
            for k in range(n):
                lsplit = f.readline().split()
                i, v = int(lsplit[0]), float(lsplit[1])
                I.append(i)
                V.append(v)
            return spmatrix(
                V, I, [0] * len(I), (parsed_blocks['CON'][0], 1))
        elif blocname == 'HCOORD':
            n = int(f.readline())
            Hblocks = {}
            for k in range(n):
                lsplit = f.readline().split()
                i, j, row, col, v = (int(lsplit[0]), int(lsplit[1]), int(
                    lsplit[2]), int(lsplit[3]), float(lsplit[4]))
                if j not in Hblocks:
                    Hblocks[j] = [spmatrix([], [], [], (ni, ni))
                        for ni in parsed_blocks['PSDCON']]
                Hblocks[j][i][row, col] = v
                if row != col:
                    Hblocks[j][i][col, row] = v
            return Hblocks
        elif blocname == 'DCOORD':
            n = int(f.readline())
            Dblocks = [spmatrix([], [], [], (ni, ni))
                       for ni in parsed_blocks['PSDCON']]
            for k in range(n):
                lsplit = f.readline().split()
                i, row, col, v = (int(lsplit[0]), int(
                    lsplit[1]), int(lsplit[2]), float(lsplit[3]))
                Dblocks[i][row, col] = v
                if row != col:
                    Dblocks[i][col, row] = v
            return Dblocks
        else:
            raise Exception('unexpected block name')

    def convert_quad_to_socp(self):
        """
        Replaces quadratic constraints with equivalent second order cone
        constraints.
        """
        for i, c in enumerate(self.constraints):
            if isinstance(c, QuadConstraint):
                qd = c.le0.quad
                sqnorm = quad2norm(qd)
                self.constraints[i] = sqnorm < -c.le0.aff
                self.numberQuadConstraints -= 1
                self.numberConeConstraints += 1
                szcone = sqnorm.LR[0].size
                self.numberConeVars += (szcone[0] * szcone[1]) + 2

        if isinstance(self.objective[1], QuadExp):
            if '_obj_' not in self.variables:
                obj = self.add_variable('_obj_', 1)
            else:
                obj = self.get_variable('_obj_')

            if self.objective[0] == 'min':
                qd = self.objective[1].quad
                aff = self.objective[1].aff
                sqnorm = quad2norm(qd)
                self.add_constraint(sqnorm < obj - aff)
                self.set_objective('min', obj)
            else:
                qd = (-self.objective[1]).quad
                aff = self.objective[1].aff
                sqnorm = quad2norm(qd)
                self.add_constraint(sqnorm < aff - obj)
                self.set_objective('max', obj)

        # Note that set_objective has numberQuadConstraints if applicable.
        assert self.numberQuadConstraints is 0

        self.numberQuadNNZ = 0

        # Reset all solver instances since a constraint was replaced.
        # TODO: Properly remove and add constraints so solver instances can be
        #       updated.
        self.reset_solver_instances()

    def convert_quadobj_to_constraint(self):
        """
        Replaces a quadratic objective with an equivalent quadratic constraint.
        """
        # TODO: Consider removing this unused method.
        if isinstance(self.objective[1], QuadExp):
            if self.options['verbose'] > 0:
                print('Replacing the quadratic objective with an equivalent '
                    'constraint.')

            if '_obj_' not in self.variables:
                obj = self.add_variable('_obj_', 1)
            else:
                obj = self.get_variable('_obj_')

            if self.objective[0] == 'min':
                self.add_constraint(obj > self.objective[1])
                self.set_objective('min', obj)
            else:
                self.add_constraint(obj < self.objective[1])
                self.set_objective('max', obj)

    def as_socp(self):
        socp = self.copy()
        socp.convert_quad_to_socp()
        return socp

    def as_real(self):
        """
        Returns a modified copy of the problem, where hermitian :math:`n × n`
        matrices are replaced by symmetric :math:`2n × 2n` matrices.
        """
        import copy
        real = Problem()
        cvars = {}
        for (iv, v) in sorted(
            [(v.startIndex, v) for v in self.variables.values()]):
            if v.vtype == 'hermitian':
                cvars[v.name + '_RE'] = real.add_variable(
                    v.name + '_RE', (v.size[0], v.size[1]), 'symmetric')
                cvars[
                    v.name + '_IM_utri'] = list(real.add_variable(
                        v.name + '_IM', (v.size[0], v.size[1]), 'antisym')
                    .factors.keys())[0]
            else:
                cvars[v.name] = real.add_variable(v.name, v.size, v.vtype)

        for c in self.constraints:
            if isinstance(c, LMIConstraint):
                # TODO: Refactor out redundancies in handling of LHS and RHS.
                D = {}
                exp1 = c.lhs
                for var, value in exp1.factors.items():
                    try:
                        if var.vtype == 'hermitian':
                            n = int(value.size[1]**(0.5))
                            idasym = svecm1_identity('antisym', (n, n))

                            D[cvars[var.name + '_RE']] = \
                                cplx_vecmat_to_real_vecmat(
                                    value, sym=True, times_i=False)
                            D[cvars[var.name + '_IM_utri']] = \
                                cplx_vecmat_to_real_vecmat(
                                    value, sym=False, times_i=True) * idasym
                        else:
                            D[cvars[var.name]] = cplx_vecmat_to_real_vecmat(
                                value, sym=False)
                    except Exception as ex:
                        import pdb
                        pdb.set_trace()
                        cplx_vecmat_to_real_vecmat(value, sym=False)
                if exp1.constant is None:
                    cst = None
                else:
                    cst = cplx_vecmat_to_real_vecmat(exp1.constant, sym=False)
                E1 = AffinExp(
                    D, cst, (2 * exp1.size[0], 2 * exp1.size[1]), exp1.string)

                D = {}
                exp2 = c.rhs
                for var, value in exp2.factors.items():
                    if var.vtype == 'hermitian':
                        D[cvars[var.name + '_RE']] = \
                            cplx_vecmat_to_real_vecmat(
                                value, sym=True, times_i=False)
                        D[cvars[var.name + '_IM_utri']] = \
                            cplx_vecmat_to_real_vecmat(
                                value, sym=False, times_i=True)
                    else:
                        D[cvars[var.name]] = cplx_vecmat_to_real_vecmat(
                            value, sym=False)
                if exp2.constant is None:
                    cst = None
                else:
                    cst = cplx_vecmat_to_real_vecmat(exp2.constant, sym=False)
                E2 = AffinExp(
                    D, cst, (2 * exp2.size[0], 2 * exp2.size[1]), exp2.string)

                if c.is_increasing():
                    real.add_constraint(E1 << E2)
                else:
                    real.add_constraint(E1 >> E2)
            elif isinstance(c, AffineConstraint):
                if c.lhs.is_real() and c.rhs.is_real():
                    # If both sides are real, make a proper copy of the
                    # constraint on top of new variables.
                    lhs = copy_exp_to_new_vars(c.lhs, cvars, complex=False)
                    rhs = copy_exp_to_new_vars(c.rhs, cvars, complex=False)
                elif c.is_equality():
                    # At least one side is not real and we have an equality, so
                    # equate both the real and the imaginary part.
                    lhs = copy_exp_to_new_vars(c.lhs, cvars, complex=True)
                    rhs = copy_exp_to_new_vars(c.rhs, cvars, complex=True)
                else:
                    raise Exception('A constraint involves an inequality '
                        'between complex numbers.')
                realConstraint = AffineConstraint(lhs, c.relation, rhs)
                real.add_constraint(realConstraint, c.name)
            elif isinstance(c, SOCConstraint) or isinstance(c, RSOCConstraint):
                if c.ne.is_real():
                    ne = copy_exp_to_new_vars(c.ne, cvars, complex=False)
                else:
                    ne = copy_exp_to_new_vars(c.ne, cvars, complex=True)

                if isinstance(c, SOCConstraint):
                    if not c.ub.is_real():
                        raise Exception('Found a complex expression in the RHS '
                            'of a nonlinear constraint.')
                    ub = copy_exp_to_new_vars(c.ub, cvars, complex=False)
                    realConstraint = SOCConstraint(ne, ub)
                else: # RSOCConstraint
                    if not (c.ub1.is_real() and c.ub2.is_real()):
                        raise Exception('Found a complex expression in the RHS '
                            'of a nonlinear constraint.')
                    ub1 = copy_exp_to_new_vars(c.ub1, cvars, complex=False)
                    ub2 = copy_exp_to_new_vars(c.ub2, cvars, complex=False)
                    realConstraint = RSOCConstraint(ne, ub1, ub2)

                real.add_constraint(realConstraint, c.name)
            elif isinstance(c, QuadConstraint) or isinstance(c, LSEConstraint):
                if c.le0.is_real():
                    le0 = copy_exp_to_new_vars(c.le0, cvars, complex=False)
                else:
                    le0 = copy_exp_to_new_vars(c.le0, cvars, complex=True)

                real.add_constraint(c.__class__(le0), c.name)
            else:
                assert False, "Unexpected constraint type."

        if not(self.objective[1] is None) and not(self.objective[1].is_real()):
            raise Exception('The objective is not real-valued.')

        obj = copy_exp_to_new_vars(self.objective[1], cvars, complex=False)
        real.set_objective(self.objective[0], obj)

        real.consNumbering = copy.deepcopy(self.consNumbering)
        real.groupsOfConstraints = copy.deepcopy(self.groupsOfConstraints)
        real._options = NonWritableDict(self.options)

        return real

    # HACK: This method abuses the internal problem representation of CVXOPT.
    # TODO: Add a proper method that transforms the problem into the canonical
    #       form required here, and, if applicable, make also CVXOPT use it.
    def as_dual(self):
        """
        Returns the Lagrangian dual problem of the problem.

        To this end the problem is put in a canonical primal form (see the
        :ref:`note on dual variables <noteduals>`), and the corresponding dual
        form is returned as a new :class:`Problem <picos.Problem>`.
        """
        if self.numberLSEConstraints > 0:
            raise DualizationError('GP cannot be dualized by PICOS')
        if not self.is_continuous():
            raise DualizationError(
                'Mixed integer problems cannot be dualized by picos')
        if self.numberQuadConstraints > 0:
            raise QuadAsSocpError(
                'try to convert the quads as socp before dualizing')

        if self.is_complex():
            raise Exception(
                'dualization of complex SDPs is not supported (yet).'
                'Try to convert the problem to an equivalent real-valued '
                'problem with as_real() first')

        dual = Problem()

        # HACK: See above.
        localCvxoptInstance = CVXOPTSolver(self)
        localCvxoptInstance._load_problem()
        cvxoptVars = localCvxoptInstance.internal_problem()

        cc = new_param('cc', cvxoptVars['c'])
        lincons = cc
        obj = 0

        # equalities
        Ae = new_param('Ae', cvxoptVars['A'])
        be = new_param('be', -cvxoptVars['b'])
        if Ae.size[0] > 0:
            mue = dual.add_variable('mue', Ae.size[0])
            lincons += (Ae.T * mue)
            obj += be.T * mue

        # inequalities
        Al = new_param('Al', cvxoptVars['Gl'])
        bl = new_param('bl', -cvxoptVars['hl'])
        if Al.size[0] > 0:
            mul = dual.add_variable('mul', Al.size[0])
            dual.add_constraint(mul > 0)
            lincons += (Al.T * mul)
            obj += bl.T * mul

        # soc cons
        i = 0
        As, bs, fs, ds, zs, lbda = [], [], [], [], [], []
        for Gq, hq in zip(cvxoptVars['Gq'], cvxoptVars['hq']):
            As.append(new_param('As[' + str(i) + ']', -Gq[1:, :]))
            bs.append(new_param('bs[' + str(i) + ']', hq[1:]))
            fs.append(new_param('fs[' + str(i) + ']', -Gq[0, :].T))
            ds.append(new_param('ds[' + str(i) + ']', hq[0]))
            zs.append(dual.add_variable('zs[' + str(i) + ']', As[i].size[0]))
            lbda.append(dual.add_variable('lbda[' + str(i) + ']', 1))
            dual.add_constraint(abs(zs[i]) < lbda[i])
            lincons += (As[i].T * zs[i] - fs[i] * lbda[i])
            obj += (bs[i].T * zs[i] - ds[i] * lbda[i])
            i += 1

        # sdp cons
        j = 0
        X = []
        M0 = []
        factors = {}
        for Gs, hs in zip(cvxoptVars['Gs'], cvxoptVars['hs']):
            nbar = int(Gs.size[0]**0.5)
            svecs = [svec(cvx.matrix(Gs[:, k], (nbar, nbar)),
                          ignore_sym=True).T for k in range(Gs.size[1])]
            msvec = cvx.sparse(svecs)
            X.append(
                dual.add_variable(
                    'X[' + str(j) + ']', (nbar, nbar), 'symmetric'))
            factors[X[j]] = -msvec
            dual.add_constraint(X[j] >> 0)
            M0.append(new_param('M0[' + str(j) + ']', -
                                cvx.matrix(hs, (nbar, nbar))))
            obj += (M0[j] | X[j])
            j += 1

        if factors:
            maff = AffinExp(
                factors=factors, size=(
                    msvec.size[0], 1), string='M dot X')
        else:
            maff = 0

        dual.add_constraint(lincons == maff)
        dual.set_objective('max', obj)
        dual._options = NonWritableDict(self.options)

        # Swap noduals and noprimals options.
        tmp = dual.options['noprimals']
        dual.set_option('noprimals', dual.options['noduals'])
        dual.set_option('noduals', tmp)

        # deactivate the solve_via_dual option (to avoid further dualization)
        dual.set_option('solve_via_dual', False)

        return dual
