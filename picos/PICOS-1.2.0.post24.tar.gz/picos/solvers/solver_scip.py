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
# This file implements the SCIP solver through the PySCIPOpt Python interface.
#-------------------------------------------------------------------------------

import cvxopt

from ..expressions import *
from ..constraints import *

from .solver import *

class SCIPSolver(Solver):
    @classmethod
    def test_availability(cls):
        import pyscipopt

    @classmethod
    def supports_integer(cls):
        return True

    @classmethod
    def supported_objectives(cls):
        yield AffinExp
        yield QuadExp

    @classmethod
    def supported_constraints(cls):
        yield AffineConstraint
        yield SOCConstraint
        yield RSOCConstraint
        yield QuadConstraint

    @classmethod
    def support_level(cls, problem):
        level = super(SCIPSolver, cls).support_level(problem)

        if problem.is_continuous() and not problem.options["noduals"]:
            if problem.type is "LP":
                # LP duals are currently known to have errors.
                level = min(level, SUPPORT_LEVEL_EXPERIMENTAL)
            else:
                # Other duals are not returned.
                level = min(level, SUPPORT_LEVEL_LIMITED)

        return level

    def __init__(self, problem):
        super(SCIPSolver, self).__init__(
            problem, "SCIP", "SCIP Optimization Suite")

        self._scipVar = dict()
        """Maps PICOS variable indices to SCIP variables."""

        self._scipCons = dict()
        """
        Maps PICOS constraints to lists of SCIP constraints.

        For PICOS second order cone constraints, the first entry in the list is
        a SCIP quadratic constraint and the second entry is a SCIP linear
        auxiliary constraint.
        """

        self._scipQuadObjAuxVar = None
        """A SCIP auxiliary variable to support a PICOS quadratic objective."""

        self._scipQuadObjAuxCon = None
        """A SCIP auxiliary constraint to support a PICOS quadr. objective."""

    def reset_problem(self):
        self.int = None

        self._scipVar.clear()
        self._scipCons.clear()

        self._scipQuadObjAuxVar = None
        self._scipQuadObjAuxCon = None

    def _make_scip_var_names(self, picosVar, localIndex = None):
        """
        Converts a PICOS variable to a list of SCIP variable names, each
        corresponding to one scalar variable contained in the PICOS variable.
        If localIndex is given, then only the name of the SCIP variable
        representing the scalar variable with that offset is returned.
        The name format is "picosName[localIndex]".
        """
        # TODO: This function appears in multiple solvers, move it to the Solver
        #       base class as "_make_scalar_var_names".
        if localIndex is not None:
            return "{}[{}]".format(picosVar.name, localIndex)
        else:
            return [
                self._make_scip_var_names(picosVar, localIndex)
                for localIndex in range(len(picosVar))]

    def _import_variable(self, picosVar):
        import pyscipopt as scip
        from math import ceil, floor

        varType = picosVar.vtype
        inf     = self.int.infinity()

        # Retrieve types.
        if varType in ("continuous", "symmetric"):
            scipVarType = "C"
        elif varType == "integer":
            scipVarType = "I"
        elif varType == "binary":
            scipVarType = "I"
        else:
            raise NotImplementedError(
                "Variables of type '{}' are not supported with SCIP."
                .format(varType))

        for localIndex in range(picosVar.dim):
            # Retrieve bounds.
            if varType == "binary":
                lower = 0
                upper = 1
            else:
                bounds = picosVar.bnd.get(localIndex)
                if bounds:
                    lower, upper = bounds
                    if lower is None:
                        lower = -inf
                    elif varType == "integer":
                        lower = int(ceil(lower))
                    if upper is None:
                        upper = inf
                    elif varType == "integer":
                        upper = int(floor(upper))
                else:
                    lower, upper = -inf, inf

            # Give name.
            scipName = self._make_scip_var_names(picosVar, localIndex)

            # Import scalar variable and map its PICOS index to it.
            picosIndex = picosVar.startIndex + localIndex
            self._scipVar[picosIndex] = self.int.addVar(
                name = scipName, vtype = scipVarType, lb = lower, ub = upper)

    def _import_variable_values(self):
        # TODO
        raise NotImplementedError

    def _reset_variable_values(self):
        # TODO
        raise NotImplementedError

    def _affinexp_pic2scip(self, picosExpression):
        """
        Tranforms a PICOS (multidimensional) affine expression into a list of
        SCIP (scalar) expressions.

        :returns: A :class:`list` of :class:`SCIP expressions
            <pyscipopt.scip.Expr>`.
        """
        from pyscipopt.scip import Expr

        if picosExpression is None:
            return [Expr()]

        length = len(picosExpression)

        # Convert linear part.
        scipExpressions = [Expr() for _ in range(length)]
        for picosVar, picosCoefs in picosExpression.factors.items():
            startIndex = picosVar.startIndex
            for localIndex, localVarIndex, coefficient in zip(
                    picosCoefs.I, picosCoefs.J, picosCoefs.V):
                scipVar = self._scipVar[startIndex + localVarIndex]
                scipExpressions[localIndex] += coefficient * scipVar

        # Convert constant part.
        if picosExpression.constant:
            for i in range(length):
                scipExpressions[i] += picosExpression.constant[i]

        return scipExpressions

    def _scalar_affinexp_pic2scip(self, picosExpression):
        """
        Transforms a PICOS scalar affine expression into a SCIP expression.

        :returns: A :class:`SCIP expression <pyscipopt.scip.Expr>`.
        """
        scipExpressions = self._affinexp_pic2scip(picosExpression)
        assert len(scipExpressions) == 1
        return scipExpressions[0]

    def _quadexp_pic2scip(self, picosExpression):
        # Convert affine part.
        scipExpression = self._scalar_affinexp_pic2scip(picosExpression.aff)

        # Convert quadratic part.
        for (pVar1, pVar2), pCoefficients in picosExpression.quad.items():
            for sparseIndex in range(len(pCoefficients)):
                localVar1Index   = pCoefficients.I[sparseIndex]
                localVar2Index   = pCoefficients.J[sparseIndex]
                localCoefficient = pCoefficients.V[sparseIndex]
                scipVar1 = self._scipVar[pVar1.startIndex + localVar1Index]
                scipVar2 = self._scipVar[pVar2.startIndex + localVar2Index]
                scipExpression += localCoefficient * scipVar1 * scipVar2

        return scipExpression

    def _import_linear_constraint(self, picosConstraint):
        assert isinstance(picosConstraint, AffineConstraint)

        scipCons = []
        picosLHS = picosConstraint.lhs - picosConstraint.rhs
        for scipLHS in self._affinexp_pic2scip(picosLHS):
            if picosConstraint.is_increasing():
                scipCons.append(self.int.addCons(scipLHS <= 0.0))
            elif picosConstraint.is_decreasing():
                scipCons.append(self.int.addCons(scipLHS >= 0.0))
            elif picosConstraint.is_equality():
                scipCons.append(self.int.addCons(scipLHS == 0.0))
            else:
                assert False, "Unexpected constraint relation."

        return scipCons

    def _import_quad_constraint(self, picosConstraint):
        assert isinstance(picosConstraint, QuadConstraint)

        scipLHS  = self._quadexp_pic2scip(picosConstraint.le0)
        scipCons = [self.int.addCons(scipLHS <= 0.0)]

        return scipCons

    def _import_socone_constraint(self, picosConstraint):
        scipCons = []
        scipQuadLHS = self._quadexp_pic2scip(
            (picosConstraint.ne | picosConstraint.ne) - \
            (picosConstraint.ub * picosConstraint.ub))
        scipCons.append(self.int.addCons(scipQuadLHS <= 0.0))

        scipAuxLHS = self._scalar_affinexp_pic2scip(picosConstraint.ub)
        if scipAuxLHS.degree() > 0:
            scipCons.append(self.int.addCons(scipAuxLHS >= 0.0))

        return scipCons

    def _import_rscone_constraint(self, picosConstraint):
        scipCons = []
        scipLHS = self._quadexp_pic2scip(
            (picosConstraint.ne | picosConstraint.ne) - \
            (picosConstraint.ub1 * picosConstraint.ub2))
        scipCons.append(self.int.addCons(scipLHS <= 0.0))

        # Make sure that either the RHS is constant, or one of the two
        # expressions is non-negative.
        scipAuxLHS = self._scalar_affinexp_pic2scip(picosConstraint.ub1)
        if scipAuxLHS.degree() > 0:
            scipCons.append(self.int.addCons(scipAuxLHS >= 0.0))
        else:
            scipAuxLHS = self._scalar_affinexp_pic2scip(picosConstraint.ub2)
            if scipAuxLHS.degree() > 0:
                scipCons.append(self.int.addCons(scipAuxLHS >= 0.0))

        return scipCons

    def _import_constraint(self, picosConstraint):
        # Import constraint based on type.
        if isinstance(picosConstraint, AffineConstraint):
            scipCons = self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, QuadConstraint):
            scipCons = self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint):
            scipCons = self._import_socone_constraint(picosConstraint)
        elif isinstance(picosConstraint, RSOCConstraint):
            scipCons = self._import_rscone_constraint(picosConstraint)
        else:
            assert False, "Constraint type belongs to unsupported problem type."

        # Map PICOS constraints to lists of SCIP constraints.
        self._scipCons[picosConstraint] = scipCons

    def _convert_quadratic_objective(self, picosObjective, minimize):
        """Converts a PICOS quadratic objective to an auxiliary variable and an
        auxiliary constraint and returns the variable as the new objective."""
        assert isinstance(picosObjective, QuadExp)

        # Add new or reuse existing auxiliary variable.
        if self._scipQuadObjAuxVar is None:
            inf = self.int.infinity()
            self._scipQuadObjAuxVar = auxVar = self.int.addVar(
                name = "objective", vtype = "C", lb = -inf, ub = inf)

        # Delete an existing auxiliary constraint.
        if self._scipQuadObjAuxCon is not None:
            self.int.delCons(self._scipQuadObjAuxCon)

        # Add a new auxiliary constraint.
        scipObjExpr = self._quadexp_pic2scip(picosObjective)
        if minimize:
            self._scipQuadObjAuxCon = self.int.addCons(auxVar >= scipObjExpr)
        else:
            self._scipQuadObjAuxCon = self.int.addCons(auxVar <= scipObjExpr)

        # Return the auxiliary variable as the new objective function.
        return auxVar

    def _import_objective(self):
        picosSense, picosObjective = self.ext.objective

        # Retrieve objective sense.
        if picosSense in ("find", "min"):
            minimize = True
            scipSense = "minimize"
        elif picosSense == "max":
            minimize = False
            scipSense = "maximize"
        else:
            raise NotImplementedError(
                "Objective sense '{0}' not supported by SCIP."
                .format(picosSense))

        # Import objective function.
        if isinstance(picosObjective, AffinExp):
            scipObjective = self._scalar_affinexp_pic2scip(picosObjective)
        elif isinstance(picosObjective, QuadExp):
            scipObjective = self._convert_quadratic_objective(
                picosObjective, minimize)
        else:
            raise NotImplementedError(
                "Objective of type '{0}' not supported by SCIP."
                .format(type(picosObjective)))

        # HACK: Remove a constant term from the objective as this is not allowed
        #       by SCIP under Python 2. (Not sure if the term is stored or
        #       dropped under Python 3, but no exception is thrown there.)
        from pyscipopt.scip import Term
        constantTerm = Term()
        if constantTerm in scipObjective.terms:
            scipObjective.terms.pop(constantTerm)

        self.int.setObjective(scipObjective, scipSense)

    def _import_problem(self):
        import pyscipopt as scip

        # Create a problem instance.
        self.int = scip.Model()

        # Import variables.
        for variable in self.ext.variables.values():
            self._import_variable(variable)

        # Import constraints.
        for constraint in self.ext.constraints:
            self._import_constraint(constraint)

        # Set objective.
        self._import_objective()

    def _update_problem(self):
        # TODO: Support all problem updates supported by SCIP.
        raise NotImplementedError

    def _solve(self):
        import pyscipopt as scip

        # Reset options.
        self.int.resetParams()

        # Handle "verbose" option.
        picosVerbosity = self.verbosity()
        if picosVerbosity <= -1:
            scipVerbosity = 0
        elif picosVerbosity == 0:
            scipVerbosity = 2
        elif picosVerbosity == 1:
            scipVerbosity = 3
        elif picosVerbosity >= 2:
            scipVerbosity = 5
        self.int.setIntParam("display/verblevel", scipVerbosity)

        # Handle "tol" option.
        if self.ext.options["tol"] is not None:
            tol = self.ext.options["tol"]
            self.int.setRealParam("numerics/feastol", tol)
            self.int.setRealParam("numerics/lpfeastol", tol)
            self.int.setRealParam("numerics/dualfeastol", tol)
            self.int.setRealParam("numerics/barrierconvtol", tol)

        # Handle "gaplim" option.
        if self.ext.options["gaplim"] is not None \
        and not self.ext.is_continuous():
            self.int.setRealParam("limits/gap", self.ext.options["gaplim"])

        # Handle "timelimit" option.
        if self.ext.options["timelimit"] is not None:
            self.int.setRealParam(
                "limits/time", float(self.ext.options["timelimit"]))

        # Handle "treememory" option.
        if self.ext.options["treememory"] is not None:
            self.int.setRealParam(
                "limits/memory", float(self.ext.options["treememory"]))

        # Handle "nbsol" option.
        if self.ext.options["nbsol"] is not None:
            self.int.setRealParam(
                "limits/solutions", float(self.ext.options["nbsol"]))

        # Handle SCIP-specific options.
        for option, value in self.ext.options["scip_params"].items():
            try:
                if isinstance(value, bool):
                    self.int.setBoolParam(option, value)
                elif isinstance(value, str):
                    if len(value) == 1:
                        try:
                            self.int.setCharParam(option, ord(value))
                        except LookupError:
                            self.int.setStringParam(option, value)
                    else:
                        self.int.setStringParam(option, value)
                elif isinstance(value, float):
                    self.int.setRealParam(option, value)
                elif isinstance(value, int):
                    try:
                        self.int.setIntParam(option, value)
                    except LookupError:
                        try:
                            self.int.setLongintParam(option, value)
                        except LookupError:
                            self.int.setRealParam(option, float(value))
            except KeyError:
                self._handle_bad_option_value("scip_params",
                    "SCIP option '{}' does not exist.".format(option))
            except ValueError:
                self._handle_bad_option_value("scip_params",
                    "Invalid value '{}' for SCIP option '{}'."
                    .format(value, option))
            except LookupError:
                self._handle_bad_option_value("scip_params",
                    "Failed to guess type of SCIP option '{}'.".format(option))

        # Handle unsupported options.
        self._handle_unsupported_options(
            "hotstart", "lp_node_method", "lp_root_method", "maxit")

        # In the case of a pure LP, disable presolve to get duals.
        if self.ext.type == "LP" and not self.ext.options["noduals"]:
            self._debug("Disabling SCIP's presolve, heuristics, and propagation"
                " features to allow for LP duals.")

            self.int.setPresolve(scip.SCIP_PARAMSETTING.OFF)
            self.int.setHeuristics(scip.SCIP_PARAMSETTING.OFF)

            # Note that this is a helper to set options, so they get reset at
            # the beginning of the function instead of in the else-scope below.
            self.int.disablePropagation()
        else:
            self.int.setPresolve(scip.SCIP_PARAMSETTING.DEFAULT)
            self.int.setHeuristics(scip.SCIP_PARAMSETTING.DEFAULT)

        # Attempt to solve the problem.
        with self._header(), self._stopwatch():
            self.int.optimize()

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}
            for varName, picosVar in self.ext.variables.items():
                value = []
                for localIndex in range(picosVar.dim):
                    scipVar = self._scipVar[picosVar.startIndex + localIndex]
                    value.append(self.int.getVal(scipVar))

                primals[varName] = value

        # Retrieve duals for LPs.
        if self.ext.options["noduals"] or self.ext.type != "LP":
            duals = None
        else:
            duals = []
            for picosConstraint in self.ext.constraints:
                assert isinstance(picosConstraint, AffineConstraint)

                # Retrieve dual value for constraint.
                scipDuals = []
                for scipCon in self._scipCons[picosConstraint]:
                    scipDuals.append(self.int.getDualsolLinear(scipCon))
                picosDual = cvxopt.matrix(scipDuals, picosConstraint.size)

                # Flip sign based on constraint relation.
                if picosConstraint.is_decreasing():
                    picosDual = -picosDual

                # Flip sign based on objective sense.
                if picosDual and self.ext.objective[0] == "min":
                    picosDual = -picosDual

                duals.append(picosDual)

        # Retrieve objective value.
        objectiveValue = self.int.getObjVal()

        # HACK: Add back the constant objective term; see above.
        picosObjective = self.ext.objective[1]
        picosObjectiveAffinePart = picosObjective.aff \
            if isinstance(picosObjective, QuadExp) else picosObjective
        if picosObjectiveAffinePart.constant:
            objectiveValue += picosObjectiveAffinePart.constant[0]

        # Retrieve solution metadata.
        meta = {}

        # Set common entry "status".
        meta["status"] = self.int.getStatus()

        return (primals, duals, objectiveValue, meta)
