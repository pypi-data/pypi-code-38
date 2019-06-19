# coding: utf-8

#-------------------------------------------------------------------------------
# Copyright (C) 2018 Maximilian Stahlberg
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
# This file implements the ECOS solver via its official Python interface.
#-------------------------------------------------------------------------------

import cvxopt

from ..expressions import *
from ..constraints import *

from .solver import *

class ECOSSolver(Solver):
    @classmethod
    def test_availability(cls):
        import ecos

    @classmethod
    def supports_integer(cls):
        return True

    @classmethod
    def supported_objectives(cls):
        yield AffinExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield ExpConeConstraint

    def __init__(self, problem):
        super(ECOSSolver, self).__init__(
            problem, "ECOS", "Embedded Conic Solver")

        self._ecosConstraintIndices = dict()
        """Maps a PICOS (multidimensional) constraints to a range of ECOS
        (scalar) constraint indices. Note that equality constraints use a
        different index space."""

        self._ecosModuleCache = None
        """Different versions of ECOS have a different path to the ecos.py
        module, this is a cache of that module to allow for quick access."""

    def reset_problem(self):
        self.int = None
        self._objectiveOffset = 0.0
        self._ecosConstraintIndices.clear()

    @property
    def ecos(self):
        """
        Returns the ECOS core module (found in ecos.py), which is obtained by
        ``import ecos`` up to ECOS 2.0.6 and by ``import ecos.ecos`` starting
        with ECOS 2.0.7.
        """
        if self._ecosModuleCache is None:
            import ecos
            if hasattr(ecos, "ecos"):
                self._ecosModuleCache = ecos.ecos
            else:
                self._ecosModuleCache = ecos
        return self._ecosModuleCache

    @property
    def array(self):
        return self.ecos.np.array

    @property
    def matrix(self):
        return self.ecos.sparse.csc_matrix

    def zeros(self, shape):
        """Creates a zero array or a zero matrix, depending on ``shape``."""
        if isinstance(shape, int) or len(shape) == 1:
            return self.ecos.np.zeros(shape)
        else:
            return self.matrix(shape)

    def stack(self, *args):
        """Stacks vectors or matrices, the latter vertically."""
        # In the case of matrices, stack vertically.
        if isinstance(args[0], self.ecos.sparse.base.spmatrix):
            for i in range(1, len(args)):
                assert isinstance(args[i], self.ecos.sparse.base.spmatrix)
            return self.ecos.sparse.vstack(args, format = "csc")

        # In the case of arrays, append them.
        for i in range(len(args)):
            assert isinstance(args[i], self.ecos.np.ndarray)
        return self.ecos.np.hstack(args)

    def _affineExpressionToGAndH(self, expression):
        assert isinstance(expression, AffinExp)

        length = len(expression)

        # Construct G.
        I, J, V = [], [], []
        for variable in expression.factors:
            factors = expression.factors[variable]

            if not isinstance(factors, cvxopt.base.spmatrix):
                factors = cvxopt.sparse(factors)

            I.extend(factors.I)
            J.extend([variable.startIndex + j for j in factors.J])
            V.extend(factors.V)
        G = self.matrix((V, (I, J)), (length, self.ext.numberOfVars))

        # Construct h.
        if expression.constant is None:
            h = self.zeros(length)
        else:
            # Make sure the constant is passed to self.array as a dense matrix,
            # so that it can be converted properly.
            constant = cvxopt.matrix(expression.constant)
            h = self.array(constant, dtype = float).flatten()
            assert len(h) == length

        return G, h

    def _Gh(self, expression):
        """A shorthand for :meth:`_affineExpressionToGAndH`."""
        return self._affineExpressionToGAndH(expression)

    def _import_problem(self):
        numVars = self.ext.numberOfVars

        # ECOS' internal problem representation is stateless; a number of
        # vectors and matrices is supplied each time a search is started.
        # These vectors and matrices are thus stored in self.int.
        self.int = {
            # Objective function coefficients.
            "c": self.zeros(numVars),

            # Linear equality left hand side.
            "A": self.matrix((0, numVars)),

            # Linear equality right hand side.
            "b": self.array([]),

            # Conic inequality left hand side.
            "G": self.matrix((0, numVars)),

            # Conic inequality right hand side.
            "h": self.array([]),

            # Cone definition: Linear, second order, exponential dimensions.
            "dims": {"l": 0, "q": [], "e": 0},

            # Boolean variable indices.
            "bool_vars_idx": [],

            # Integer variable indices.
            "int_vars_idx": []
        }

        # Import variables, with their bounds as affine constraints.
        for variable in self.ext.variables.values():
            self._import_variable(variable)

        # Import affine constraints.
        for constraint in [
            c for c in self.ext.constraints if isinstance(c, AffineConstraint)]:
            self._ecosConstraintIndices[constraint] = \
                self._import_affine_constraint(constraint)

        # Import second order cone constraints.
        for constraint in [
            c for c in self.ext.constraints if isinstance(c, SOCConstraint)]:
            self._ecosConstraintIndices[constraint] = \
                self._import_socone_constraint(constraint)

        # Import rotated second order cone constraints.
        for constraint in [
            c for c in self.ext.constraints if isinstance(c, RSOCConstraint)]:
            self._ecosConstraintIndices[constraint] = \
                self._import_rscone_constraint(constraint)

        # Import exponential cone constraints.
        for constraint in [c for c in self.ext.constraints
            if isinstance(c, ExpConeConstraint)]:
            self._ecosConstraintIndices[constraint] = \
                self._import_expcone_constraint(constraint)

        # Make sure that no unsupported constraints are present.
        for constraint in self.ext.constraints:
            if  not isinstance(constraint, AffineConstraint) \
            and not isinstance(constraint, SOCConstraint) \
            and not isinstance(constraint, RSOCConstraint) \
            and not isinstance(constraint, ExpConeConstraint):
                raise NotImplementedError(
                    "Constraints of type '{}' are not supported by {}."
                    .format(constraint.__class__.__name__, self.name))

        # Set objective.
        self._import_objective()

    def _import_variable(self, variable):
        varType = variable.vtype
        indices = range(variable.startIndex, variable.endIndex)

        # Mark integer variables.
        if varType is "binary":
            self.int["bool_vars_idx"].extend(indices)
        elif varType is "integer":
            self.int["int_vars_idx"].extend(indices)

        # Import bounds as constraints.
        self._import_affine_constraint(variable.bound_constraint())

    def _append_equality(self, A, b):
        startIndex = len(self.int["b"])
        length     = len(b)

        self.int["A"] = self.stack(self.int["A"], A)
        self.int["b"] = self.stack(self.int["b"], b)

        return range(startIndex, startIndex + length)

    def _append_inequality(self, G, h, typecode):
        assert typecode in self.int["dims"]

        # Make sure constraints are appened in the proper order.
        if typecode is "l":
            assert len(self.int["dims"]["q"]) == 0 \
                and self.int["dims"]["e"] == 0
        elif typecode is "q":
            assert self.int["dims"]["e"] == 0

        startIndex = len(self.int["h"])
        length     = len(h)

        self.int["G"] = self.stack(self.int["G"], G)
        self.int["h"] = self.stack(self.int["h"], h)

        if typecode is "q":
            self.int["dims"][typecode].append(length)
        elif typecode is "e":
            self.int["dims"][typecode] += 1
        else:
            self.int["dims"][typecode] += length

        return range(startIndex, startIndex + length)

    def _import_affine_constraint(self, constraint):
        assert isinstance(constraint, AffineConstraint)

        (G_smaller, h_smaller) = self._Gh(constraint.smaller)
        (G_greater, h_greater) = self._Gh(constraint.greater)
        G = G_smaller - G_greater
        h = h_greater - h_smaller

        if constraint.is_equality():
            return self._append_equality(G, h)
        else:
            return self._append_inequality(G, h, "l")

    def _import_socone_constraint(self, constraint):
        assert isinstance(constraint, SOCConstraint)

        (A, b) = self._Gh(constraint.ne)
        (c, d) = self._Gh(constraint.ub)

        return self._append_inequality(
            self.stack(-c, -A), self.stack(d, b), "q")

    def _import_rscone_constraint(self, constraint):
        assert isinstance(constraint, RSOCConstraint)

        (A,  b ) = self._Gh(constraint.ne )
        (c1, d1) = self._Gh(constraint.ub1)
        (c2, d2) = self._Gh(constraint.ub2)

        return self._append_inequality(
            self.stack(-(c1 + c2), -2.0*A, c2 - c1),
            self.stack(  d1 + d2,   2.0*b, d1 - d2), "q")

    def _import_expcone_constraint(self, constraint):
        assert isinstance(constraint, ExpConeConstraint)

        (Gx, hx) = self._Gh(constraint.x)
        (Gy, hy) = self._Gh(constraint.y)
        (Gz, hz) = self._Gh(constraint.z)

        # ECOS' exponential cone is cl{(x,y,z) | exp(x/z) <= y/z, z > 0},
        # PICOS' is cl{(x,y,z) | x >= y*exp(z/y), y > 0}. Note that given y > 0
        # it is x >= y*exp(z/y) if and only if exp(z/y) <= x/y. Therefor we can
        # transform from our coordinates to theirs with the mapping
        # (x, y, z) ↦ (z, x, y). Further, G and h with G = (Gx, Gy, Gz) and
        # h = (hx, hy, hz) are such that G*X + h = (x, y, z) where X is the
        # row-vectorization of all variables. ECOS however expects G and h such
        # that h - G*X is constrained to be in the exponential cone.
        return self._append_inequality(
            -self.stack(Gz, Gx, Gy), self.stack(hz, hx, hy), "e")

    def _import_objective(self):
        objectiveType, objective = self.ext.objective
        if objectiveType not in ("find", "min", "max"):
            raise NotImplementedError(
                "Objective '{}' not supported by {}."
                .format(objectiveType, self.name))

        if not isinstance(objective, AffinExp):
            raise NotImplementedError(
                "{} does not support nonlinear objectives; try to use an "
                "epigraph reformulation.".format(self.name))

        if objective.constant:
            objectiveOffset = cvxopt.matrix(objective.constant)
            assert len(objectiveOffset) == 1
            objectiveOffset = objectiveOffset[0]
            self._objectiveOffset = objectiveOffset
        else:
            self._objectiveOffset = 0.0

        if objectiveType is not "find":
            # ECOS only supports minimization; flip the sign for maximization.
            sign = 1.0 if objectiveType is "min" else -1.0

            for variable in objective.factors:
                factors = objective.factors[variable]
                for localIndex in range(variable.dim):
                    index = variable.startIndex + localIndex
                    self.int["c"][index] = sign * factors[localIndex]

    def _update_problem(self):
        raise NotImplementedError()

    def _solve(self):
        # An alias to the internal problem instance.
        p = self.int

        ecosOptions = {}

        # Handle "verbose" option.
        beVerbose = self.verbosity() >= 1
        ecosOptions["verbose"]    = beVerbose
        ecosOptions["mi_verbose"] = beVerbose

        # Handle "tol", "feastol", "abstol" and "reltol" options.
        feastol = self.ext.options["feastol"]
        if feastol is None:
            feastol = self.ext.options["tol"]
        abstol = self.ext.options["abstol"]
        if abstol is None:
            abstol = self.ext.options["tol"]
        reltol = self.ext.options["reltol"]
        if reltol is None:
            reltol = self.ext.options["tol"]
        ecosOptions["feastol"] = feastol
        ecosOptions["abstol"]  = abstol
        ecosOptions["reltol"]  = reltol

        # Handle "gaplim" option.
        if self.ext.options["gaplim"] is not None:
            ecosOptions["mi_rel_eps"] = self.ext.options["gaplim"]

        # Handle "maxit" option.
        if self.ext.options["maxit"] is not None:
            ecosOptions["max_iters"]    = self.ext.options["maxit"]
            ecosOptions["mi_max_iters"] = self.ext.options["maxit"]

        # Handle unsupported options.
        self._handle_unsupported_options(
            "lp_root_method", "lp_node_method", "timelimit", "treememory",
            "nbsol", "hotstart")

        # Assemble the solver input.
        arguments = {}
        arguments.update(self.int)
        arguments.update(ecosOptions)

        # Debug print the solver input.
        if self._debug():
            from pprint import pformat
            self._debug("Passing to ECOS:\n" + pformat(arguments))

        # Attempt to solve the problem.
        with self._header(), self._stopwatch():
            solution = self.ecos.solve(**arguments)

        # Debug print the solver output.
        if self._debug():
            from pprint import pformat
            self._debug("Recevied from ECOS:\n" + pformat(solution))

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}

            for var in self.ext.variables.values():
                # HACK: Cast from numpy array to list so that _retrieve_matrix
                #       will respect the target matrix size.
                # TODO: Refactor _retrieve_matrix to handle different input
                #       types consistently.
                value = list(solution["x"][var.startIndex:var.endIndex])
                primals[var.name] = value

        # Retrieve duals.
        if self.ext.options["noduals"]:
            duals = None
        else:
            duals = []

            for constraint in self.ext.constraints:
                dual    = None
                indices = self._ecosConstraintIndices[constraint]

                if isinstance(constraint, AffineConstraint):
                    if constraint.is_equality():
                        dual = list(solution["y"][indices])
                    else:
                        dual = list(solution["z"][indices])
                elif isinstance(constraint, SOCConstraint):
                    dual     = solution["z"][indices]
                    dual[1:] = -dual[1:]
                    dual     = list(dual)
                elif isinstance(constraint, RSOCConstraint):
                    dual     = solution["z"][indices]
                    dual[1:] = -dual[1:]
                    alpha    = dual[0] - dual[-1]
                    beta     = dual[0] + dual[-1]
                    z        = list(2.0 * dual[1:-1])
                    dual     = [alpha, beta] + z
                elif isinstance(constraint, ExpConeConstraint):
                    zxy  = solution["z"][indices]
                    dual = [zxy[1], zxy[2], zxy[0]]
                else:
                    assert False, "Unexpected constraint type."

                if type(dual) is list:
                    if len(dual) == 1:
                        dual = float(dual[0])
                    else:
                        dual = cvxopt.matrix(dual, constraint.size)

                duals.append(dual)

        # Retrieve objective value.
        p = solution["info"]["pcost"]
        d = solution["info"]["dcost"]

        if p is not None and d is not None:
            objectiveValue = 0.5 * (p + d)
        elif p is not None:
            objectiveValue = p
        elif d is not None:
            objectiveValue = d
        else:
            objectiveValue = None

        if objectiveValue is not None:
            objectiveValue += self._objectiveOffset

            if self.ext.objective[0] is "max":
                objectiveValue = -objectiveValue

        # Retrieve solution metadata.
        meta = {"ecos_sol": solution}

        statusCode = solution["info"]["exitFlag"]
        if statusCode is 0:
            meta["status"] = "optimal"
        elif statusCode is 1:
            meta["status"] = "primal infeasible"
        elif statusCode is 2:
            meta["status"] = "dual infeasible"
        elif statusCode is -1:
            meta["status"] = "iteration limit reached"
        elif statusCode is -2:
            meta["status"] = "search direction unreliable"
        elif statusCode is -3:
            meta["status"] = "numerically problematic"
        elif statusCode is -4:
            meta["status"] = "interrupted"
        elif statusCode is -7:
            meta["status"] = "solver error"
        else:
            meta["status"] = "unknown"

        return (primals, duals, objectiveValue, meta)
