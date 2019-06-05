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
# This file implements the Gurobi solver through its official Python interface.
#-------------------------------------------------------------------------------

import cvxopt
from collections import namedtuple

from ..expressions import *
from ..constraints import *
from ..tools import NonConvexError, svec

from .solver import *

class GurobiSolver(Solver):
    @classmethod
    def test_availability(cls):
        import gurobipy

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

    GurobiSOCC = namedtuple("SOCC",
        ("LHSVars", "RHSVar", "LHSCons", "RHSCon", "quadCon"))

    GurobiRSOCC = namedtuple("RSOCC",
        ("LHSVars", "RHSVars", "LHSCons", "RHSCons", "quadCon"))

    def __init__(self, problem):
        super(GurobiSolver, self).__init__(
            problem, "Gurobi", "Gurobi Optimizer")

        self._gurobiVar = dict()
        """Maps PICOS variable indices to Gurobi variables."""

        self._gurobiLinearConstraints = dict()
        """Maps a PICOS (multidimensional) linear constraint to a collection of
        Gurobi (scalar) linear constraints."""

        self._gurobiQuadConstraint = dict()
        """Maps a PICOS quadratic constraint to a Gurobi quadr. constraint."""

        self._gurobiSOCC = dict()
        """Maps a PICOS second order cone constraint to its Gurobi
        representation involving auxiliary variables and constraints."""

        self._gurobiRSOCC = dict()
        """Maps a PICOS rotated second order cone constraint to its Gurobi
        representation involving auxiliary variables and constraints."""

    def reset_problem(self):
        self.int = None

        self._gurobiVar.clear()
        self._gurobiLinearConstraints.clear()
        self._gurobiQuadConstraint.clear()
        self._gurobiSOCC.clear()
        self._gurobiRSOCC.clear()

    def _import_variable(self, picosVar):
        import gurobipy as gurobi

        varDim  = picosVar.dim
        varType = picosVar.vtype

        # Retrieve types.
        if varType in ("continuous", "symmetric"):
            gurobiVarType = gurobi.GRB.CONTINUOUS
        elif varType == "integer":
            gurobiVarType = gurobi.GRB.INTEGER
        elif varType == "binary":
            gurobiVarType = gurobi.GRB.BINARY
        elif varType == "semiint":
            gurobiVarType = gurobi.GRB.SEMIINT
        elif varType == "semicont":
            gurobiVarType = gurobi.GRB.SEMICONT
        else:
            raise NotImplementedError(
                "Variables of type '{}' are not supported with Gurobi."
                .format(varType))

        # Retrieve bounds.
        lowerBounds = []
        upperBounds = []
        for localIndex in range(varDim):
            bounds = picosVar.bnd.get(localIndex)
            if bounds:
                lower, upper = bounds
                if lower is None:
                    lowerBounds.append(-gurobi.GRB.INFINITY)
                else:
                    lowerBounds.append(lower)
                if upper is None:
                    upperBounds.append(gurobi.GRB.INFINITY)
                else:
                    upperBounds.append(upper)
            else:
                lowerBounds.append(-gurobi.GRB.INFINITY)
                upperBounds.append(gurobi.GRB.INFINITY)

        # Import variable.
        # Note that Gurobi allows importing the objective function coefficients
        # for the new variables here, but that is done later to streamline
        # updates to the objective.
        gurobiVars = self.int.addVars(varDim, lb=lowerBounds, ub=upperBounds,
            vtype=gurobiVarType, name=picosVar.name)

        # Map PICOS variable indices to Gurobi variables.
        for localIndex in range(varDim):
            picosIndex = picosVar.startIndex + localIndex
            gurobiVar = gurobiVars[localIndex]
            self._gurobiVar[picosIndex] = gurobiVar

    def _remove_variable(self, picosVar):
        gurobiVars = []
        for localIndex in range(picosVar.dim):
            picosIndex = picosVar.startIndex + localIndex
            gurobiVars.append(self._gurobiVar.pop(picosIndex))
        self.int.remove(gurobiVars)

    def _import_variable_values(self):
        for picosVar in self.ext.variables.values():
            if picosVar.is_valued():
                value = picosVar.valueAsMatrix

                # TODO: Allow accessing the "internal" value of a variable, i.e.
                #       the value in svec representation for symmetric ones.
                if picosVar.vtype is "symmetric":
                    value = svec(value)

                for localIndex in range(picosVar.dim):
                    picosIndex = picosVar.startIndex + localIndex
                    gurobiVar = self._gurobiVar[picosIndex]
                    gurobiVar.Start = value[localIndex]

    def _reset_variable_values(self):
        import gurobipy as gurobi

        for gurobiVar in self._gurobiVar.values():
            gurobiVar.Start = gurobi.GRB.UNDEFINED

    def _affinexp_pic2grb(self, picosExpression):
        import gurobipy as gurobi
        for gurobiVars, coefficients, constant in picosExpression.sparse_rows(
                None, indexFunction = lambda picosVar, localIndex:
                self._gurobiVar[picosVar.startIndex + localIndex]):
            gurobiExpression = gurobi.LinExpr(coefficients, gurobiVars)
            gurobiExpression.addConstant(constant)
            yield gurobiExpression

    def _scalar_affinexp_pic2grb(self, picosExpression):
        """
        Tranforms a PICOS scalar affine expression into a Gurobi (scalar) affine
        expression.

        :returns: A :class:`LinExpr <gurobipy.LinExpr>`.
        """
        assert len(picosExpression) is 1
        return next(self._affinexp_pic2grb(picosExpression))

    def _quadexp_pic2grb(self, picosExpression):
        import gurobipy as gurobi

        if not isinstance(picosExpression, QuadExp):
            raise ValueError("Expression must be a quadratic expression.")

        # Import affine part of expression.
        gurobiExpression = gurobi.QuadExpr(
            self._scalar_affinexp_pic2grb(picosExpression.aff))

        # Import quadratic form.
        gurobiI, gurobiJ, gurobiV = [], [], []
        for (picosVar1, picosVar2), picosCoefficients \
            in picosExpression.quad.items():
            for sparseIndex in range(len(picosCoefficients)):
                localVar1Index = picosCoefficients.I[sparseIndex]
                localVar2Index = picosCoefficients.J[sparseIndex]
                localCoefficient = picosCoefficients.V[sparseIndex]
                gurobiI.append(self._gurobiVar[
                    picosVar1.startIndex + localVar1Index])
                gurobiJ.append(self._gurobiVar[
                    picosVar2.startIndex + localVar2Index])
                gurobiV.append(localCoefficient)
        gurobiExpression.addTerms(gurobiV, gurobiI, gurobiJ)

        return gurobiExpression

    def _import_linear_constraint(self, picosConstraint):
        import gurobipy as gurobi
        assert isinstance(picosConstraint, AffineConstraint)

        # Retrieve sense.
        if picosConstraint.is_increasing():
            gurobiSense = gurobi.GRB.LESS_EQUAL
        elif picosConstraint.is_decreasing():
            gurobiSense = gurobi.GRB.GREATER_EQUAL
        elif picosConstraint.is_equality():
            gurobiSense = gurobi.GRB.EQUAL
        else:
            assert False, "Unexpected constraint relation."

        # Append scalar constraints.
        gurobiCons = []
        for localConIndex, (gurobiLHS, gurobiRHS) in enumerate(zip(
                self._affinexp_pic2grb(picosConstraint.lhs),
                self._affinexp_pic2grb(picosConstraint.rhs))):
            if picosConstraint.name:
                gurobiName = "{}:{}".format(picosConstraint.name, localConIndex)
            else:
                gurobiName = ""

            gurobiCons.append(self.int.addConstr(
                gurobiLHS, gurobiSense, gurobiRHS, gurobiName))

        return gurobiCons

    def _import_quad_constraint(self, picosConstraint):
        import gurobipy as gurobi
        assert isinstance(picosConstraint, QuadConstraint)

        gurobiName = picosConstraint.name if picosConstraint.name else ""

        gurobiLHS = self._quadexp_pic2grb(picosConstraint.le0)
        gurobiRHS = -gurobiLHS.getLinExpr().getConstant()
        if gurobiRHS:
            gurobiLHS.getLinExpr().addConstant(gurobiRHS)

        return self.int.addQConstr(
            gurobiLHS, gurobi.GRB.LESS_EQUAL, gurobiRHS, gurobiName)

    def _import_socone_constraint(self, picosConstraint):
        import gurobipy as gurobi
        assert isinstance(picosConstraint, SOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS = picosConstraint.ub
        picosLHSLen = len(picosLHS)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        gurobiLHSVarsIndexed = self.int.addVars(
            picosLHSLen, lb = -gurobi.GRB.INFINITY, ub = gurobi.GRB.INFINITY)
        gurobiLHSVars = gurobiLHSVarsIndexed.values()
        gurobiRHSVar = self.int.addVar(lb = 0.0, ub = gurobi.GRB.INFINITY)

        # Add constraints that identify the left hand side Gurobi auxiliary
        # variables with their slice of the PICOS left hand side expression.
        gurobiLHSSlices = dict()
        for dimension, slice in enumerate(self._affinexp_pic2grb(picosLHS)):
            gurobiLHSSlices[dimension] = slice
        gurobiLHSCons = self.int.addConstrs(
            (gurobiLHSSlices[dimension] - gurobiLHSVarsIndexed[dimension] == 0 \
            for dimension in range(picosLHSLen))).values()

        # Add a constraint that identifies the right hand side Gurobi auxiliary
        # variable with the PICOS right hand side scalar expression.
        gurobiRHSExp = self._scalar_affinexp_pic2grb(picosRHS)
        gurobiRHSCon = self.int.addConstr(
            gurobiRHSVar - gurobiRHSExp, gurobi.GRB.EQUAL, 0)

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadExpr = gurobi.QuadExpr()
        quadExpr.addTerms([1.0] * picosLHSLen, gurobiLHSVars, gurobiLHSVars)
        gurobiName = picosConstraint.name if picosConstraint.name else ""
        gurobiQuadCon = self.int.addQConstr(quadExpr, gurobi.GRB.LESS_EQUAL,
            gurobiRHSVar * gurobiRHSVar, gurobiName)

        gurobiMetaCon = self.GurobiSOCC(
            LHSVars=gurobiLHSVars, RHSVar=gurobiRHSVar, LHSCons=gurobiLHSCons,
            RHSCon=gurobiRHSCon, quadCon=gurobiQuadCon)

        return gurobiMetaCon

    def _import_rscone_constraint(self, picosConstraint):
        import gurobipy as gurobi
        assert isinstance(picosConstraint, RSOCConstraint)

        picosLHS = picosConstraint.ne
        picosRHS1 = picosConstraint.ub1
        picosRHS2 = picosConstraint.ub2
        picosLHSLen = len(picosLHS)

        # Add auxiliary variables: One for every dimension of the left hand side
        # of the PICOS constraint and one for its right hand side.
        gurobiLHSVarsIndexed = self.int.addVars(
            picosLHSLen, lb = -gurobi.GRB.INFINITY, ub = gurobi.GRB.INFINITY)
        gurobiLHSVars = gurobiLHSVarsIndexed.values()
        gurobiRHSVars = self.int.addVars(
            2, lb = 0.0, ub = gurobi.GRB.INFINITY).values()

        # Add constraints that identify the left hand side Gurobi auxiliary
        # variables with their slice of the PICOS left hand side expression.
        gurobiLHSSlices = dict()
        for dimension, slice in enumerate(self._affinexp_pic2grb(picosLHS)):
            gurobiLHSSlices[dimension] = slice
        gurobiLHSCons = self.int.addConstrs(
            (gurobiLHSSlices[dimension] - gurobiLHSVarsIndexed[dimension] == 0 \
            for dimension in range(picosLHSLen))).values()

        # Add two constraints that identify the right hand side Gurobi auxiliary
        # variables with the PICOS right hand side scalar expressions.
        gurobiRHSExps = \
            self._scalar_affinexp_pic2grb(picosRHS1), \
            self._scalar_affinexp_pic2grb(picosRHS2)
        gurobiRHSCons = self.int.addConstrs(
            (gurobiRHSVars[i] - gurobiRHSExps[i] == 0 for i in (0, 1))).values()

        # Add a quadratic constraint over the auxiliary variables that
        # represents the PICOS second order cone constraint itself.
        quadExpr = gurobi.QuadExpr()
        quadExpr.addTerms([1.0] * picosLHSLen, gurobiLHSVars, gurobiLHSVars)
        gurobiName = picosConstraint.name if picosConstraint.name else ""
        gurobiQuadCon = self.int.addQConstr(quadExpr, gurobi.GRB.LESS_EQUAL,
            gurobiRHSVars[0] * gurobiRHSVars[1], gurobiName)

        gurobiMetaCon = self.GurobiRSOCC(
            LHSVars=gurobiLHSVars, RHSVars=gurobiRHSVars, LHSCons=gurobiLHSCons,
            RHSCons=gurobiRHSCons, quadCon=gurobiQuadCon)

        return gurobiMetaCon

    def _import_constraint(self, picosConstraint):
        # Import constraint based on type.
        if isinstance(picosConstraint, AffineConstraint):
            self._gurobiLinearConstraints[picosConstraint] = \
                self._import_linear_constraint(picosConstraint)
        elif isinstance(picosConstraint, QuadConstraint):
            self._gurobiQuadConstraint[picosConstraint] = \
                self._import_quad_constraint(picosConstraint)
        elif isinstance(picosConstraint, SOCConstraint):
            self._gurobiSOCC[picosConstraint] = \
                self._import_socone_constraint(picosConstraint)
        elif isinstance(picosConstraint, RSOCConstraint):
            self._gurobiRSOCC[picosConstraint] = \
                self._import_rscone_constraint(picosConstraint)
        else:
            assert False, "Constraint type belongs to unsupported problem type."

    def _remove_constraint(self, picosConstraint):
        if isinstance(picosConstraint, AffineConstraint):
            self.int.remove(
                self._gurobiLinearConstraints.pop(picosConstraint))
        elif isinstance(picosConstraint, QuadConstraint):
            self.int.remove(
                self._gurobiQuadConstraint.pop(picosConstraint))
        elif isinstance(picosConstraint, SOCConstraint):
            c = self._gurobiSOCC.pop(picosConstraint)
            self.int.remove(c.gurobiLHSCons + [c.gurobiRHSCon]
                + [c.gurobiQuadCon] + c.gurobiLHSVars + [c.gurobiRHSVar])
        elif isinstance(picosConstraint, RSOCConstraint):
            c = self._gurobiRSOCC.pop(picosConstraint)
            self.int.remove(c.gurobiLHSCons + c.gurobiRHSCons
                + [c.gurobiQuadCon] + c.gurobiLHSVars + c.gurobiRHSVars)
        else:
            assert False, "Constraint type belongs to unsupported problem type."

    def _import_objective(self):
        import gurobipy as gurobi

        picosSense, picosObjective = self.ext.objective

        # Retrieve objective sense.
        if picosSense in ("find", "min"):
            gurobiSense = gurobi.GRB.MINIMIZE
        elif picosSense == "max":
            gurobiSense = gurobi.GRB.MAXIMIZE
        else:
            raise NotImplementedError(
                "Objective sense '{0}' not supported by Gurobi."
                .format(picosSense))

        # Retrieve objective function.
        if isinstance(picosObjective, AffinExp):
            gurobiObjective = self._scalar_affinexp_pic2grb(picosObjective)
        elif isinstance(picosObjective, QuadExp):
            gurobiObjective = self._quadexp_pic2grb(picosObjective)
        else:
            raise NotImplementedError(
                "Objective of type '{0}' not supported by Gurobi."
                .format(type(picosObjective)))

        self.int.setObjective(gurobiObjective, gurobiSense)

    def _import_problem(self):
        import gurobipy as gurobi

        # Create a problem instance.
        if self.ext.options["allow_license_warnings"]:
            self.int = gurobi.Model()
        else:
            with self._enforced_verbosity():
                self.int = gurobi.Model()

        # Import variables.
        for variable in self.ext.variables.values():
            self._import_variable(variable)

        # Import constraints.
        for constraint in self.ext.constraints:
            self._import_constraint(constraint)

        # Set objective.
        self._import_objective()

    def _update_problem(self):
        for oldConstraint in self._removed_constraints():
            self._remove_constraint(oldConstraint)

        for oldVariable in self._removed_variables():
            self._remove_variable(oldVariable)

        for newVariable in self._new_variables():
            self._import_variable(newVariable)

        for newConstraint in self._new_constraints():
            self._import_constraint(newConstraint)

        if self._objective_has_changed():
            self._import_objective()

    def _solve(self):
        import gurobipy as gurobi

        # Reset options.
        self.int.resetParams()

        # Handle "verbose" option.
        self.int.Params.OutputFlag = 1 if self.verbosity() > 0 else 0

        # Handle "tol" option.
        # Note that the following Gurobi tolerances are not set:
        # FeasibilityTol, IntFeasTol, MarkowitzTol, PSDTol
        # FIXME: When computing duals for problems with quadratic constraints
        #        (which includes SOCP), tolerances more precise than 1e-7 seem
        #        to be ignored for the dual values.
        if self.ext.options["tol"] is not None:
            self.int.Params.BarConvTol = self.ext.options["tol"]
            self.int.Params.BarQCPConvTol = self.ext.options["tol"]
            self.int.Params.OptimalityTol = self.ext.options["tol"]

        # Handle "gaplim" option.
        if self.ext.options["gaplim"] is not None:
            self.int.Params.MIPGap = self.ext.options["gaplim"]

        # Handle "maxit" option.
        if self.ext.options["maxit"] is not None:
            self.int.Params.BarIterLimit = self.ext.options["maxit"]
            self.int.Params.IterationLimit = self.ext.options["maxit"]

        # Handle "lp_node_method" option.
        if self.ext.options["lp_node_method"] is not None:
            method = self.ext.options["lp_node_method"]
            if method == "psimplex":
                self.int.Params.SiftMethod = 0
            elif method == "dsimplex":
                self.int.Params.SiftMethod = 1
            elif method == "interior":
                self.int.Params.SiftMethod = 2
            else:
                self._handle_bad_option_value("lp_node_method")

        # Handle "lp_root_method" option.
        if self.ext.options["lp_root_method"] is not None:
            method = self.ext.options["lp_root_method"]
            if method == "psimplex":
                self.int.Params.Method = 0
            elif method == "dsimplex":
                self.int.Params.Method = 1
            elif method == "interior":
                self.int.Params.Method = 2
            else:
                self._handle_bad_option_value("lp_root_method")

        # Handle "timelimit" option.
        if self.ext.options["timelimit"] is not None:
            self.int.Params.TimeLimit = self.ext.options["timelimit"]

        # Handle "nbsol" option.
        if self.ext.options["nbsol"] is not None:
            self.int.Params.SolutionLimit = self.ext.options["nbsol"]

        # Handle "hotstart" option.
        if self.ext.options["hotstart"]:
            self._import_variable_values()
        else:
            self._reset_variable_values()

        # Handle Gurobi-specific options.
        for option, value in self.ext.options["gurobi_params"].items():
            if not self.int.getParamInfo(option):
                self._handle_bad_option_value("gurobi_params",
                    "Gurobi option '{}' does not exist.".format(option))
            try:
                self.int.setParam(option, value)
            except TypeError as error:
                self._handle_bad_option_value("gurobi_params",
                    "Invalid value '{}' for Gurobi option '{}': {}"
                    .format(value, option, str(error)))

        # Handle unsupported options.
        self._handle_unsupported_option("treememory")

        # Compute duals also for QPs and QCPs.
        if self.ext.is_continuous() and not self.ext.options["noduals"]:
            self.int.setParam(gurobi.GRB.Param.QCPDual, 1)

        # Attempt to solve the problem.
        with self._header(), self._stopwatch():
            try:
                self.int.optimize()
            except gurobi.GurobiError as error:
                if error.errno == gurobi.GRB.Error.Q_NOT_PSD:
                    raise NonConvexError(str(error))
                else:
                    raise

        # Retrieve primals.
        if self.ext.options["noprimals"]:
            primals = None
        else:
            primals = {}
            for varName, picosVar in self.ext.variables.items():
                try:
                    value = []
                    for localIndex in range(picosVar.dim):
                        gurobiVar = self._gurobiVar[picosVar.startIndex+localIndex]
                        scalarValue = gurobiVar.getAttr(gurobi.GRB.Attr.X)
                        value.append(scalarValue)
                except AttributeError:
                    primals[varName] = None
                else:
                    primals[varName] = value

        # Retrieve duals.
        if self.ext.options["noduals"] or not self.ext.is_continuous():
            duals = None
        else:
            duals = []
            for constraint in self.ext.constraints:
                try:
                    if isinstance(constraint, AffineConstraint):
                        gurobiCons = self._gurobiLinearConstraints[constraint]
                        gurobiDuals = []
                        for gurobiCon in gurobiCons:
                            gurobiDuals.append(
                                gurobiCon.getAttr(gurobi.GRB.Attr.Pi))
                        picosDual = cvxopt.matrix(gurobiDuals, constraint.size)

                        # Flip sign based on constraint relation.
                        if constraint.is_decreasing():
                            picosDual = -picosDual
                    elif isinstance(constraint, SOCConstraint):
                        gurobiMetaCon = self._gurobiSOCC[constraint]
                        lb = gurobiMetaCon.RHSCon.getAttr(gurobi.GRB.Attr.Pi)
                        z = [constraint.getAttr(gurobi.GRB.Attr.Pi) \
                            for constraint in gurobiMetaCon.LHSCons]
                        picosDual = cvxopt.matrix([lb] + z)
                    elif isinstance(constraint, RSOCConstraint):
                        gurobiMetaCon = self._gurobiRSOCC[constraint]
                        ab = [constraint.getAttr(gurobi.GRB.Attr.Pi) \
                            for constraint in gurobiMetaCon.RHSCons]
                        z = [constraint.getAttr(gurobi.GRB.Attr.Pi) \
                            for constraint in gurobiMetaCon.LHSCons]
                        picosDual = cvxopt.matrix(ab + z)
                    elif isinstance(constraint, QuadConstraint):
                        picosDual = None
                    else:
                        assert False, "Encountered unsupported constraint type."

                    # Flip sign based on objective sense.
                    if picosDual and self.ext.objective[0] == "min":
                        picosDual = -picosDual
                except AttributeError:
                    duals.append(None)
                else:
                    duals.append(picosDual)

        # Retrieve objective value.
        try:
            objectiveValue = self.int.getAttr(gurobi.GRB.Attr.ObjVal)
        except AttributeError:
            objectiveValue = None

        # Retrieve solution metadata.
        meta = {}

        # Set common entry "status".
        statusCode = self.int.getAttr(gurobi.GRB.Attr.Status)
        if statusCode == gurobi.GRB.Status.LOADED:
            meta["status"] = "loaded"
        elif statusCode == gurobi.GRB.Status.OPTIMAL:
            meta["status"] = "optimal"
        elif statusCode == gurobi.GRB.Status.INFEASIBLE:
            meta["status"] = "infeasible"
        elif statusCode == gurobi.GRB.Status.INF_OR_UNBD:
            meta["status"] = "infeasible or unbounded"
        elif statusCode == gurobi.GRB.Status.UNBOUNDED:
            meta["status"] = "unbounded"
        elif statusCode == gurobi.GRB.Status.CUTOFF:
            meta["status"] = "cutoff"
        elif statusCode == gurobi.GRB.Status.ITERATION_LIMIT:
            meta["status"] = "iteration limit exceeded"
        elif statusCode == gurobi.GRB.Status.NODE_LIMIT:
            meta["status"] = "node limit exceeded"
        elif statusCode == gurobi.GRB.Status.TIME_LIMIT:
            meta["status"] = "time limit exceeded"
        elif statusCode == gurobi.GRB.Status.SOLUTION_LIMIT:
            meta["status"] = "solution limit exceeded"
        elif statusCode == gurobi.GRB.Status.INTERRUPTED:
            meta["status"] = "interrupted"
        elif statusCode == gurobi.GRB.Status.NUMERIC:
            meta["status"] = "numerically problematic"
        elif statusCode == gurobi.GRB.Status.SUBOPTIMAL:
            meta["status"] = "suboptimal"
        elif statusCode == gurobi.GRB.Status.INPROGRESS:
            meta["status"] = "in progress"
        elif statusCode == gurobi.GRB.Status.USER_OBJ_LIMIT:
            meta["status"] = "objective limit reached"
        else:
            meta["status"] = "Gurobi status code {}".format(statusCode)

        return (primals, duals, objectiveValue, meta)
