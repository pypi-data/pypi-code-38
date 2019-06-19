#-------------------------------------------------------------------------------
# Copyright (C) 2012-2017 Guillaume Sagnol
# Copyright (C)      2017 Maximilian Stahlberg
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
# This file implements the CVXOPT solver.
# Currently, it also implements the similar SMCP solver.
#-------------------------------------------------------------------------------

import numpy
import cvxopt as cvx

from ..expressions import *
from ..constraints import *
from ..tools import spmatrix, builtin_sum

from .solver import *

class CVXOPTSolver(Solver):
    @classmethod
    def test_availability(cls):
        # CVXOPT is a dependency of PICOS, so it is always available.
        pass

    @classmethod
    def supports_integer(cls):
        return False

    @classmethod
    def supported_objectives(cls):
        yield AffinExp
        yield LogSumExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield LMIConstraint
        yield ExpConeConstraint

    @classmethod
    def support_level(cls, problem):
        # CVXOPT only supports exponential cone constraints generated from
        # posynomial inequalities, that are logarithm of sum of exponentials
        # expressions with an upper bound of zero.
        for constraint in problem.constraints:
            if isinstance(constraint, ExpConeConstraint):
                if not isinstance(constraint.origin, LSEConstraint):
                    return SUPPORT_LEVEL_NONE

        return super(CVXOPTSolver, cls).support_level(problem)

    def __init__(self, problem):
        super(CVXOPTSolver, self).__init__(
            problem, "CVXOPT", "Python Convex Optimization Solver")

        # HACK: Setting this to false would result in variable bounds to be
        #       ignored, instead of added to the linear inequalities matrix.
        #       This is used by a Problem method that prints the problem to a
        #       file using a CVXOPTSolver instance.
        self.import_variable_bounds = True

        # SMCP currently offers no option reset, so keep a backup.
        try:
            import smcp
            self._smcp_default_options = smcp.solvers.options.copy()
        except ImportError:
            pass

    def reset_problem(self):
        self.int = None

    def _is_geometric_program(self):
         return any([True for constraint in self.ext.constraints
            if isinstance(constraint.origin, LSEConstraint)])

    # TODO: Document this function better. What exactly does it do? Example?
    def _make_gandh(self, affExpr):
        """if affExpr is an affine expression,
        this method creates a bloc matrix G to be multiplied by the large
        vectorized vector of all variables,
        and returns the vector h corresponding to the constant term.
        """
        n1 = affExpr.size[0] * affExpr.size[1]
        # matrix G
        I = []
        J = []
        V = []
        for var in affExpr.factors:
            si = var.startIndex
            facvar = affExpr.factors[var]
            if not isinstance(facvar, cvx.base.spmatrix):
                facvar = cvx.sparse(facvar)
            I.extend(facvar.I)
            J.extend([si + j for j in facvar.J])
            V.extend(facvar.V)
        G = spmatrix(V, I, J, (n1, self.ext.numberOfVars))

        # is it really sparse ?
        # if cvx.nnz(G)/float(G.size[0]*G.size[1])>0.5:
        #       G=cvx.matrix(G,tc='d')
        # vector h
        if affExpr.constant is None:
            h = cvx.matrix(0, (n1, 1), tc='d')
        else:
            h = affExpr.constant
        if not isinstance(h, cvx.matrix):
            h = cvx.matrix(h, tc='d')
        if h.typecode != 'd':
            h = cvx.matrix(h, tc='d')
        return G, h

    def _import_problem(self):
        numVars = self.ext.numberOfVars
        isGP    = self._is_geometric_program()

        # CVXOPT's internal problem representation is stateless; a number of
        # matrices are supplied to the appropriate solver function each time a
        # search is started. These matrices are thus stored in self.int.
        p = self.int = {
            # Objective function coefficients.
            'c'  : None,
            # Linear equality left hand side.
            'A'  : spmatrix([], [], [], (0, numVars), tc='d'),
            # Linear equality right hand side.
            'b'  : cvx.matrix([], (0, 1), tc='d'),
            # Linear inequality left hand side.
            'Gl' : spmatrix([], [], [], (0, numVars), tc='d'),
            # Linear inequality right hand side.
            'hl' : cvx.matrix([], (0, 1), tc='d'),
            # Second order cone inequalities left hand sides.
            'Gq' : [],
            # Second order cone inequalities right hand sides.
            'hq' : [],
            # Semidefinite cone inequalities left hand sides.
            'Gs' : [],
            # Semidefinite cone inequalities right hand sides.
            'hs' : [],

            # Used for the objective function of geometric programs.
            'F' : None,
            'g' : None,
            'K' : None,

            # HACK: This is not used by CVXOPT, but by functions abusing its
            #       internal problem representation.
            'quadcons' : []
        }

        # Sanity check objective type.
        objectiveType, objective = self.ext.objective
        if objectiveType not in ('find', 'min', 'max'):
            raise NotImplementedError(
                "Objective '{}' not supported by {}."
                .format(objectiveType, self.name))

        # (?)
        if isinstance(objective, QuadExp):
            # HACK: See above.
            p['quadcons'].append(('_obj', -1))
            objective = objective.aff
        elif isinstance(objective, LogSumExp):
            objective = objective.Exp

        # Set the objective.
        if not isGP:
            if objectiveType == 'find':
                p['c'] = cvx.matrix(0, (numVars, 1), tc='d')
            else:
                (c, _) = self._make_gandh(objective)
                if objectiveType == 'min':
                    p['c'] = cvx.matrix(c, tc='d').T
                elif objectiveType == 'max':
                    p['c'] = -cvx.matrix(c, tc='d').T
        else:
            if objectiveType == 'find':
                p['F'] = cvx.matrix(0, (1, numVars), tc='d')
                p['K'] = [0]
            else:
                (F, g) = self._make_gandh(objective)
                p['K'] = [F.size[0]]
                if objectiveType == 'min':
                    p['F'] = cvx.matrix(F, tc='d')
                    p['g'] = cvx.matrix(g, tc='d')
                elif objectiveType == 'max':
                    p['F'] = -cvx.matrix(F, tc='d')
                    p['g'] = -cvx.matrix(g, tc='d')

        # LSE constraints are imported directly even though they are
        # metaconstraints within PICOS. Keep track of them so we don't import
        # them multiple times for each auxilary constraint we visit.
        seenLSEConstraints = []

        # Add constraints.
        for constraintNum, constraint in enumerate(self.ext.constraints):
            self._debug("Importing {}.".format(constraint))
            if isinstance(constraint.origin, LSEConstraint):
                if constraint.origin not in seenLSEConstraints:
                    (F, g) = self._make_gandh(constraint.origin.le0Exponents)
                    p['F'] = cvx.sparse([p['F'], F])
                    p['g'] = cvx.matrix([p['g'], g])
                    p['K'].append(F.size[0])

                    seenLSEConstraints.append(constraint.origin)

                # HACK: Add the affine auxiliary constraints as otherwise the
                #       variables that they use are unused, and CVXOPT doesn't
                #       like unused variables at all.
                if not isinstance(constraint, AffineConstraint):
                    continue

            # HACK: This is intentionally no 'elif', see above.
            if isinstance(constraint, AffineConstraint):
                (G_smaller, h_smaller) = self._make_gandh(constraint.smaller)
                (G_greater, h_greater) = self._make_gandh(constraint.greater)
                G = G_smaller - G_greater
                h = h_greater - h_smaller
                if constraint.is_equality():
                    p['A'] = cvx.sparse([p['A'], G])
                    p['b'] = cvx.matrix([p['b'], h])
                else:
                    p['Gl'] = cvx.sparse([p['Gl'], G])
                    p['hl'] = cvx.matrix([p['hl'], h])
            elif isinstance(constraint, SOCConstraint):
                (A, b) = self._make_gandh(constraint.ne)
                (c, d) = self._make_gandh(constraint.ub)
                p['Gq'].append(cvx.sparse([-c, -A]))
                p['hq'].append(cvx.matrix([d, b]))
            elif isinstance(constraint, RSOCConstraint):
                (A,  b)  = self._make_gandh(constraint.ne)
                (c1, d1) = self._make_gandh(constraint.ub1)
                (c2, d2) = self._make_gandh(constraint.ub2)
                p['Gq'].append(cvx.sparse([-c1 - c2, -2 * A, c2 - c1]))
                p['hq'].append(cvx.matrix([d1 + d2, 2 * b, d1 - d2]))
            elif isinstance(constraint, QuadConstraint):
                # HACK: Currently, problems with quadratic constriants are cast
                #       as SOCP before solution, but the constraints need to be
                #       handled here anyway because some functions abuse the
                #       internal problem representation of CVXOPT and expect
                #       quadcons to be set.
                p['quadcons'].append((constraintNum, p['Gl'].size[0]))
                (G_lhs, h_lhs) = self._make_gandh(constraint.le0.Exp.aff)
                p['Gl'] = cvx.sparse([p['Gl'], G_lhs])
                p['hl'] = cvx.matrix([p['hl'], -h_lhs])
            elif isinstance(constraint, LMIConstraint):
                (G_smaller, h_smaller) = self._make_gandh(constraint.smaller)
                (G_greater, h_greater) = self._make_gandh(constraint.greater)
                p['Gs'].append(G_smaller - G_greater)
                p['hs'].append(h_greater - h_smaller)
            else:
                raise NotImplementedError(
                    "Constraints of type '{}' are not supported by {}."
                    .format(constraint.__class__.__name__, self.name))

        # Add variable bounds as additional constraints.
        # HACK: See __init__. (Assume this condition to be True.)
        if self.import_variable_bounds:
            self._debug("Importing variable bounds.")
            # I, J, V represent a left hand side sparse matrix L where each
            # row identifies a scalar variable to be bounded, R represents
            # the right hand side vector of bounds.
            I, J, V, R = [], [], [], []
            constraintIndex = 0
            for variable in self.ext.variables.values():
                for localIndex, (lower, upper) in variable.bnd.items():
                    if lower is not None:
                        I.append(constraintIndex)
                        J.append(variable.startIndex + localIndex)
                        V.append(-1.0)
                        R.append(-lower)
                        constraintIndex += 1
                    if upper is not None:
                        I.append(constraintIndex)
                        J.append(variable.startIndex + localIndex)
                        V.append(1.0)
                        R.append(upper)
                        constraintIndex += 1
            L = cvx.spmatrix(V, I, J, (constraintIndex, numVars))
            R = cvx.matrix(R)
            p['Gl'] = cvx.sparse([p['Gl'], L])
            p['hl'] = cvx.matrix([p['hl'], R])

    def _update_problem(self):
        raise NotImplementedError()

    def _solve(self):
        # An alias to the internal problem instance.
        p = self.int

        # This class doubles as an implementation for the SMCP solver.
        solver = self.ext.options['solver'].lower()
        assert solver in ("cvxopt", "smcp")

        isGP = self._is_geometric_program()

        # Check if the problem type is supported.
        # TODO: Check if general-obj problems are properly handled.
        if solver == 'smcp':
            # SMCP is a standalone solver made available through the SMCPSolver
            # class. However, since SMCP both depends on CVXOPT and has a
            # similar interface, its logic is implemented inside CVXOPTSolver,
            # and SMCPSolver subclasses it. Ensure that self is indeed a
            # SMCPSolver instance.
            assert self.__class__.__name__ == "SMCPSolver", \
                "SMCP needs to be used through the SMCPSolver class."
            import smcp

        # Clear all options set previously. This is necessary because CVXOPT
        # options are global, and might be changed even by another problem.
        cvx.solvers.options.clear()

        # Handle "verbose" option.
        cvx.solvers.options['show_progress'] = (self.verbosity() >= 1)

        # Handle "tol", "feastol", "abstol" and "reltol" options.
        feastol = self.ext.options['feastol']
        if feastol is None:
            feastol = self.ext.options['tol']
        abstol = self.ext.options['abstol']
        if abstol is None:
            abstol = self.ext.options['tol']
        reltol = self.ext.options['reltol']
        if reltol is None:
            reltol = 10 * self.ext.options['tol']
        cvx.solvers.options['feastol'] = feastol
        cvx.solvers.options['abstol'] = abstol
        cvx.solvers.options['reltol'] = reltol

        # Handle "maxit" option.
        maxit = self.ext.options['maxit']
        if maxit is None:
            maxit = int(1e6)
        cvx.solvers.options['maxiters'] = maxit

        # Allow solving GPs that are not strictly feasible.
        # TODO: Turn this into a proper option?
        cvx.solvers.options['kktreg'] = 1e-6

        # Handle unsupported options.
        self._handle_unsupported_options(
            'lp_root_method', 'lp_node_method', 'timelimit', 'treememory',
            'nbsol', 'hotstart')

        # TODO: Add CVXOPT-sepcific options. Candidates are:
        #       - refinement

        # Set options for SMCP.
        if solver == 'smcp':
            # Restore default options.
            smcp.solvers.options = self._smcp_default_options.copy()

            # Copy options also used by CVXOPT.
            smcp.solvers.options.update(cvx.solvers.options)

            # Further handle "verbose" option.
            smcp.solvers.options['debug'] = (self.verbosity() >= 2)

            # TODO: Add SMCP-sepcific options.

        if self._debug():
            from pprint import pformat
            if solver == 'smcp':
                options = smcp.solvers.options
            else:
                options = cvx.solvers.options
            self._debug("Setting options:\n{}\n".format(pformat(options)))

        # Print a header.
        if solver == 'smcp':
            subsolverText = None
        else:
            if isGP:
                subsolverText = 'internal GP solver'
            else:
                subsolverText = 'internal CONELP solver'

        # Further prepare the problem for the CVXOPT/SMCP CONELP solvers.
        # TODO: This should be done during import.
        if not isGP:
            # Retrieve the structure of the cone, which is a cartesian product
            # of the non-negative orthant of dimension l, a number of second
            # order cones with dimensions in q and a number of positive
            # semidefinite cones with dimensions in s.
            dims = {
                'l': p['Gl'].size[0],
                'q': [Gqi.size[0] for Gqi in p['Gq']],
                's': [int(numpy.sqrt(Gsi.size[0])) for Gsi in p['Gs']]
            }

            # Construct G and h to contain all conic inequalities, starting with
            # those with respect to the non-negative orthant.
            G = p['Gl']
            h = p['hl']

            # SMCP's ConeLP solver does not handle (linear) equalities, so cast
            # them as inequalities.
            if solver == 'smcp':
                if p['A'].size[0] > 0:
                    G = cvx.sparse([G, p['A']])
                    G = cvx.sparse([G, -p['A']])
                    h = cvx.matrix([h, p['b']])
                    h = cvx.matrix([h, -p['b']])
                    dims['l'] += (2 * p['A'].size[0])

            # Add second-order cone inequalities.
            for i in range(len(dims['q'])):
                G = cvx.sparse([G, p['Gq'][i]])
                h = cvx.matrix([h, p['hq'][i]])

            # Add semidefinite cone inequalities.
            for i in range(len(dims['s'])):
                G = cvx.sparse([G, p['Gs'][i]])
                h = cvx.matrix([h, p['hs'][i]])

            # Remove zero lines from linear equality constraint matrix, as
            # CVXOPT expects this matrix to have full row rank.
            JP = list(set(p['A'].I))
            IP = range(len(JP))
            VP = [1] * len(JP)
            if any([b for (i, b) in enumerate(p['b']) if i not in JP]):
                raise SolverError(
                    'Infeasible constraint of the form 0 = a with a != 0.')
            P = spmatrix(VP, IP, JP, (len(IP), p['A'].size[0]))
            A = P * p['A']
            b = P * p['b']

        # Attempt to solve the problem.
        with self._header(subsolverText), self._stopwatch():
            if solver == 'smcp':
                if self._debug():
                    self._debug("Calling smcp.solvers.conelp(c, G, h, dims) "
                        "with\nc:\n{}\nG:\n{}\nh:\n{}\ndims:\n{}\n"
                        .format(p['c'], G, h, dims))
                try:
                    result = smcp.solvers.conelp(p['c'], G, h, dims)
                except TypeError:
                    # HACK: Work around "'NoneType' object is not subscriptable"
                    #       exception with infeasible/unbounded problems.
                    result = None
            else:
                if isGP:
                    result = cvx.solvers.gp(p['K'], p['F'], p['g'], p['Gl'],
                        p['hl'], p['A'], p['b'], kktsolver = 'ldl')
                else:
                    result = cvx.solvers.conelp(p['c'], G, h, dims, A, b)

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        elif result is None or result["x"] is None:
            primals = None
        else:
            primals = {}

            # Retrieve values for all but LSE auxiliary variables.
            for var in self.ext.variables.values():
                # Auxiliary variables for LSE metaconstraints have no
                # meaningful value at this point.
                if isinstance(var.origin, LSEConstraint):
                    continue

                # HACK: Cast from numpy array to list so that _retrieve_matrix
                #       will respect the target matrix size.
                # TODO: Refactor _retrieve_matrix to handle different input
                #       types consistently.
                value = list(result["x"][var.startIndex:var.endIndex])

                primals[var.name] = value

            # Give auxiliary variables added for an LSE metaconstraint a
            # solution value.
            for var in self.ext.variables.values():
                if isinstance(var.origin, LSEConstraint):
                    value = []
                    for i, exponent in enumerate(var.origin.le0Exponents):
                        value.append(cvx.matrix(exponent.constant
                            if exponent.constant else 0.0))
                        for v, factor in exponent.factors.items():
                            value[i] += factor * cvx.matrix(primals[v.name])
                        value[i] = cvx.exp(value[i])[0,0]
                    primals[var.name] = cvx.matrix(value, var.size)

        # Retrieve duals.
        if self.ext.options["noduals"]:
            duals = None
        elif result is None:
            duals = None
        else:
            duals = []
            (indy, indzl, indzq, indznl, indzs) = (0, 0, 0, 0, 0)

            if isGP:
                zkey = 'zl'
                zqkey = 'zq'
                zskey = 'zs'
            else:
                zkey = 'z'
                zqkey = 'z'
                zskey = 'z'
                indzq = dims['l']
                indzs = dims['l'] + builtin_sum(dims['q'])

            if solver == 'smcp':
                # Equality constraints were cast as two inequalities.
                ieq = p['Gl'].size[0]
                neq = (dims['l'] - ieq) // 2
                soleq = result['z'][ieq:ieq + neq]
                soleq -= result['z'][ieq + neq:ieq + 2 * neq]
            else:
                soleq = result['y']

            seenLSEConstraints = []

            for constraint in self.ext.constraints:
                dual   = None
                consSz = len(constraint)

                if isinstance(constraint.origin, LSEConstraint):
                    # We are looking at an auxiliary constraint for a
                    # metaconstraint that was imported directly.

                    # We don't get any duals:
                    # - The affine constraint was imported for technical reasons
                    #   and all variables used in it are irrelevant to the
                    #   objective function. Hence the dual will always be 0.
                    #   We don't store it since that could produce a bad result
                    #   when querying the LSE metaconstraint for its dual.
                    # - The exponential cone constraints were never imported.
                    #   Instead, a single LSE constraint was imported.
                    if isinstance(constraint, AffineConstraint):
                        assert constraint.is_inequality()
                        indzl += len(constraint) # = 1
                    else:
                        assert isinstance(constraint, ExpConeConstraint)
                        if constraint.origin not in seenLSEConstraints:
                            indznl += len(constraint.origin) # = 1
                            seenLSEConstraints.append(constraint.origin)
                elif isinstance(constraint, AffineConstraint):
                    if constraint.is_equality():
                        if soleq is not None:
                            dual = (P.T * soleq)[indy:indy + consSz]
                            indy += consSz
                    else:
                        if result[zkey] is not None:
                            dual = result[zkey][indzl:indzl + consSz]
                            indzl += consSz
                elif isinstance(constraint, SOCConstraint) \
                or isinstance(constraint, RSOCConstraint):
                    if result[zqkey] is not None:
                        if isGP:
                            dual = result[zqkey][indzq]
                            dual[1:] = -dual[1:]
                            indzq += 1
                        else:
                            dual = result[zqkey][indzq:indzq + consSz]
                            # Swap the sign of the SOcone's Lagrange multiplier,
                            # as PICOS wants it the other way round.
                            # Note that this also affects RScone constraints
                            # which were cast as SOcone constraints on import.
                            dual[1:] = -dual[1:]
                            if isinstance(constraint, RSOCConstraint):
                                # RScone were cast as a SOcone on import, so
                                # transform the dual to a proper RScone dual.
                                alpha = dual[0] - dual[-1]
                                beta  = dual[0] + dual[-1]
                                z     = 2.0 * dual[1:-1]
                                dual  = cvx.matrix([alpha, beta, z])
                            indzq += consSz
                elif isinstance(constraint, LMIConstraint):
                    if result[zskey] is not None:
                        matSz = constraint.size[0]
                        if isGP:
                            dual = cvx.matrix(
                                result[zskey][indzs], (matSz, matSz))
                            indzs += 1
                        else:
                            dual = cvx.matrix(
                                result[zskey][indzs:indzs + consSz],
                                (matSz, matSz))
                            indzs += consSz

                duals.append(dual)

        # Retrieve objective value.
        if result is None:
            objectiveValue = None
        elif isGP:
            objectiveValue = 'toEval'
        else:
            p = result['primal objective']
            d = result['dual objective']
            if p is not None and d is not None:
                objectiveValue = 0.5 * (p + d)
            elif p is not None:
                objectiveValue = p
            elif d is not None:
                objectiveValue = d
            else:
                objectiveValue = None
            if self.ext.objective[0] == 'max' and objectiveValue is not None:
                objectiveValue = -objectiveValue

        # Retrieve solution metadata.
        meta = {
            'cvxopt_sol' : result,
            'status'     : result['status'] if result else "unavailable"
        }

        return (primals, duals, objectiveValue, meta)
